"""Lesson 1-7 -- files and paths (mission-style handout, lecture format).

Written for the code a reader has after lessons 1-1 to 1-6 of the handouts.
Engine code is referred to by function name only. Quotes (tag "now") are limited
to files the reader did not write: project settings and Engine/framework.h.
Standard-library and Win32 behaviour was checked against the headers and
sources named in section 1.4, not by building the project.

Version 2 (2026-11-19): the mission format of lesson 1-4 v4. Each mission step
now states what must be done as plain statements and ends with a "통과" (pass)
condition, and a new last chapter 13 "할 일 목록" spells every mission out as a
task list with a way to check each task, plus a default choice for each of the
eight decisions of 6.3 for when the reader is stuck. Chapters 1 to 12 keep their
numbers; the eight mission steps keep their numbers and meaning.

Run:  python -I src/lesson_1_7.py      (from Docs/Handouts, with the handout venv)
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_engine"))
sys.path.insert(0, str(ROOT / "src"))

from common import *          # noqa: E402,F403
from curriculum import *      # noqa: E402,F403
from render import render     # noqa: E402

ME = lesson("1-7")
OUT_PDF = ROOT / handout_name(ME["id"])
OUT_HTML = ROOT / "_build" / "lesson_1_7.html"

# Project files, library headers and runtime sources were read on this day.
READ_DATE = "2026-11-18"
# Toolchain of the PC the declarations and sources were read on (another PC may differ).
MSVC_VER = "MSVC 14.44"
SDK_VER = "Windows SDK 10.0.26100.0"

CHECK_HEADER = ["확인할 것", "볼 자리", "왜 문제인가"]

COVER = cover(
    f"CLAUDGL ENGINE · PART {ME['part']} · {ME['id']} · v{ME['ver']}",
    Raw('FileSystem::<span class="ac">ReadText</span>'),
    ME["title"],
    "어디서 실행하든 같은 파일을 찾아, 디스크에 있는 그대로 읽는다",
    [
        ("목표 결과물", "Client가 `Assets/` 아래의 텍스트 파일과 바이너리 파일을 하나씩 읽어 로그로 알린다. 어디서 "
                    "실행해도 결과가 같다"),
        ("핵심 개념", "작업 디렉터리 · `std::filesystem` · 텍스트 모드와 바이너리 모드 · 통째로 읽기 · 인코딩과 BOM"),
        ("선수 지식", "1-4강(실패를 알리는 `Init`), 1-5강(로그 매크로), 1-6강(오류 정책)을 끝낸 뒤에 한다"),
        ("예상 시간", f"읽기 1시간 + 구현 2시간 남짓 (계획서 기준 {ME['hours']}시간)"),
        ("건드릴 파일", "`Engine/Core/FileSystem.h`·`.cpp`(새 파일), `Assets/`(새 폴더), `Client/main.cpp`"),
        ("코드 기준", f"엔진 코드는 함수 이름으로 가리킨다. 설정과 라이브러리는 {READ_DATE}에 확인했다 (1.4절)"),
    ],
    note=("읽는 법",
          "2장이 이 강의 문제이고 3 〜 5장이 도구다. 6장에서 에셋 폴더를 찾는 방법을 고른 뒤 7장의 미션을 순서대로 "
          "한다. 미션이 무엇을 하라는 것인지 분명하지 않으면 13장의 할 일 목록을 본다. 예시 상자는 미션과 다른 값으로 "
          "든 작은 예다. 코드 블록은 완성본이 아니다."),
    toc=["왜 필요한가", "작업 디렉터리와 실행 파일의 위치", "std::filesystem: 경로를 값으로", "파일 읽기: 텍스트와 바이너리",
         "인코딩: 바이트와 글자", "설계", "구현 미션", "흔한 함정", "완료 기준", "생각해 볼 질문", "해설", "용어집",
         "할 일 목록"],
)

# --------------------------------------------------------------------------
# figures
# --------------------------------------------------------------------------

def _pbox(fig, x, y, w, h, mono, sub=None, kind="", size=10):
    """Box whose first line is monospace (a path or an identifier), with an optional small second line."""
    fig.box(x, y, w, h, kind=kind)
    cx = x + w / 2
    if sub:
        fig.text(cx, y + h / 2 - 2.5, mono, kind="mono", size=size)
        fig.text(cx, y + h / 2 + 11.5, sub, kind="s", size=9.5)
    else:
        fig.text(cx, y + h / 2 + 4, mono, kind="mono", size=size)
    return fig


def _cell(fig, x, y, w, label, kind="", h=26, size=10.5):
    """One memory or file cell with a monospace label."""
    fig.box(x, y, w, h, kind=kind, r=3)
    fig.text(x + w / 2, y + h / 2 + 4, label, kind="mono", size=size)
    return fig


# 1.1 -- the same relative path lands in three places.
FIG_CWD = Fig(188)
FIG_CWD.text(89, 13, "실행하는 방법", kind="s", size=9.5)
FIG_CWD.text(291, 13, "프로세스가 받는 작업 디렉터리", kind="s", size=9.5)
FIG_CWD.text(532, 13, "Assets/Text/hello.txt 를 열면 찾아가는 곳", kind="s", size=9.5)
for _y, _how, _how_sub, _cwd, _cwd_sub, _hit, _hit_sub, _kind in (
    (22, "Visual Studio", "F5 · Ctrl+F5", "C:\\Dev\\ClaudGL\\Client\\", "프로젝트 폴더",
     "…\\Client\\Assets\\Text\\hello.txt", "그런 파일은 없다", "ghost"),
    (78, "탐색기", "Client.exe를 더블클릭", "C:\\Dev\\ClaudGL\\Debug\\x64\\", "실행 파일이 있는 폴더",
     "…\\Debug\\x64\\Assets\\Text\\hello.txt", "그런 파일은 없다", "ghost"),
    (134, "명령 프롬프트", "저장소 폴더에 선 채로 실행", "C:\\Dev\\ClaudGL\\", "셸이 있던 폴더",
     "C:\\Dev\\ClaudGL\\Assets\\Text\\hello.txt", "실제 파일", "accent"),
):
    FIG_CWD.box(14, _y, 150, 44, _how, _how_sub)
    FIG_CWD.arrow((164, _y + 22), (192, _y + 22))
    _pbox(FIG_CWD, 192, _y, 198, 44, _cwd, _cwd_sub, kind="soft")
    FIG_CWD.arrow((390, _y + 22), (418, _y + 22), kind="accent" if _kind == "accent" else "muted")
    _pbox(FIG_CWD, 418, _y, 228, 44, _hit, _hit_sub, kind=_kind, size=9.5)

# 3.1 -- the pieces of one path.
FIG_PATH = Fig(150)
FIG_PATH.text(249, 22, "parent_path()", kind="mono", size=10)
FIG_PATH.line((110, 38), (110, 30), (388, 30), (388, 38), kind="muted")
FIG_PATH.text(493, 22, "filename()", kind="mono", size=10)
FIG_PATH.line((426, 38), (426, 30), (560, 30), (560, 38), kind="muted")
for _x, _w, _label, _kind in ((110, 50, "C:", "soft"), (164, 30, "/", ""), (198, 190, "Game/Assets/Shaders", "soft"),
                              (392, 30, "/", ""), (426, 70, "basic", "accent"), (500, 60, ".vert", "accent")):
    _cell(FIG_PATH, _x, 42, _w, _label, kind=_kind, h=30, size=12)
FIG_PATH.line((135, 72), (135, 82), kind="muted").text(135, 94, "root_name()", kind="mono", size=9.5)
FIG_PATH.line((179, 72), (179, 100), kind="muted").text(179, 112, "root_directory()", kind="mono", size=9.5)
FIG_PATH.line((461, 72), (461, 82), kind="muted").text(461, 94, "stem()", kind="mono", size=9.5)
FIG_PATH.line((530, 72), (530, 82), kind="muted").text(530, 94, "extension()", kind="mono", size=9.5)
FIG_PATH.line((198, 120), (198, 128), (560, 128), (560, 120), kind="muted")
FIG_PATH.text(379, 142, "relative_path()", kind="mono", size=9.5)

# 4.2 -- the same eight bytes read in text mode and in binary mode.
_DISK = ["48", "69", "0D", "0A", "4F", "4B", "0D", "0A"]
_GLYPH = ["H", "i", "\\r", "\\n", "O", "K", "\\r", "\\n"]
_X0, _STEP = 240, 48
FIG_MODE = Fig(166)
FIG_MODE.text(14, 30, "디스크에 있는 바이트", kind="t", anchor="start", size=10.5)
FIG_MODE.text(14, 45, "8바이트", kind="s", anchor="start", size=9.5)
for _i, _b in enumerate(_DISK):
    _cell(FIG_MODE, _X0 + _i * _STEP, 16, 44, _b, kind="accent" if _b in ("0D", "0A") else "")
    FIG_MODE.text(_X0 + _i * _STEP + 22, 55, _GLYPH[_i], kind="s", size=9)
FIG_MODE.text(14, 88, "텍스트 모드로 읽은 것", kind="t", anchor="start", size=10.5)
FIG_MODE.text(14, 103, "6글자. 0D 0A가 0A 하나가 된다", kind="s", anchor="start", size=9.5)
for _i in (0, 1, 4, 5):
    _cell(FIG_MODE, _X0 + _i * _STEP, 74, 44, _DISK[_i])
for _i in (2, 6):
    FIG_MODE.arrow((_X0 + _i * _STEP + 46, 60), (_X0 + _i * _STEP + 46, 73), kind="accent")
    _cell(FIG_MODE, _X0 + _i * _STEP, 74, 92, "0A", kind="accent")
FIG_MODE.text(14, 142, "바이너리 모드로 읽은 것", kind="t", anchor="start", size=10.5)
FIG_MODE.text(14, 157, "8바이트. 디스크와 같다", kind="s", anchor="start", size=9.5)
for _i, _b in enumerate(_DISK):
    _cell(FIG_MODE, _X0 + _i * _STEP, 128, 44, _b)

# 4.4 -- a vector owns the bytes, a span only points at a run of them.
FIG_SPAN = Fig(150)
FIG_SPAN.text(448, 22, "vector가 잡은 메모리 (10바이트)", kind="s", size=9.5)
_pbox(FIG_SPAN, 20, 30, 170, 46, "std::vector<byte>", "주인: 메모리를 잡고 놓는다", kind="accent")
FIG_SPAN.arrow((190, 53), (256, 53), kind="accent")
for _i in range(10):
    _cell(FIG_SPAN, 258 + _i * 38, 40, 36, f"{_i:02X}", kind="accent" if 3 <= _i <= 7 else "", size=10)
FIG_SPAN.line((372, 70), (372, 78), (560, 78), (560, 70), kind="muted")
_pbox(FIG_SPAN, 20, 96, 170, 46, "std::span<const byte>", "빌린 쪽: 주소와 개수만", kind="soft")
FIG_SPAN.arrow((190, 119), (466, 119), (466, 80))
FIG_SPAN.text(328, 112, "data()  ·  size() == 5", kind="mono", size=9.5)
FIG_SPAN.text(480, 104, "span이 가리키는 구간", kind="s", anchor="start", size=9.5)

# 6.2 -- walking up from the executable's folder.
FIG_WALK = Fig(206)
FIG_WALK.text(20, 11, "폴더 (위가 루트)", kind="s", anchor="start", size=9.5)
FIG_WALK.text(340, 11, "그 폴더 바로 아래에 Assets\\ 가 있는가", kind="s", anchor="start", size=9.5)
_pbox(FIG_WALK, 20, 18, 250, 36, "C:\\", "여기까지 올라와도 없으면", kind="ghost")
_pbox(FIG_WALK, 20, 66, 250, 36, "C:\\Dev\\ClaudGL\\", "3  한 칸 더 위", kind="accent")
_pbox(FIG_WALK, 20, 114, 250, 36, "C:\\Dev\\ClaudGL\\Debug\\", "2  한 칸 위")
_pbox(FIG_WALK, 20, 162, 250, 36, "C:\\Dev\\ClaudGL\\Debug\\x64\\", "1  실행 파일이 있는 폴더에서 출발", kind="soft")
FIG_WALK.arrow((145, 162), (145, 151))
FIG_WALK.arrow((145, 114), (145, 103))
FIG_WALK.arrow((145, 66), (145, 55), kind="muted dash")
FIG_WALK.text(153, 160, "parent_path()", kind="mono", anchor="start", size=8.5)
FIG_WALK.arrow((270, 180), (338, 180), kind="muted dash")
FIG_WALK.arrow((270, 132), (338, 132), kind="muted dash")
FIG_WALK.arrow((270, 84), (338, 84), kind="accent")
_pbox(FIG_WALK, 340, 162, 300, 36, "…\\Debug\\x64\\Assets\\", "없다", kind="ghost")
_pbox(FIG_WALK, 340, 114, 300, 36, "…\\Debug\\Assets\\", "없다", kind="ghost")
_pbox(FIG_WALK, 340, 66, 300, 36, "C:\\Dev\\ClaudGL\\Assets\\", "있다. 이 폴더가 에셋 루트다", kind="accent")
FIG_WALK.text(340, 33, "무엇을 할지 정해 두어야 한다.", kind="s", anchor="start", size=9.5)
FIG_WALK.text(340, 47, "반복이 끝나는 조건도 여기에 있다 (3.2절).", kind="s", anchor="start", size=9.5)

# --------------------------------------------------------------------------

ch1 = chapter(1, "왜 필요한가", [
    h3("1.1", "같은 경로, 다른 곳"),
    p("`\"Assets/Text/hello.txt\"`처럼 드라이브나 루트에서 시작하지 않는 경로를 상대 경로라고 한다. 상대 경로는 "
      "혼자서는 완전하지 않다. 운영체제가 ==작업 디렉터리==라는 폴더 뒤에 이어 붙여야 실제 위치가 된다. 그리고 작업 "
      "디렉터리는 프로그램이 정하지 않는다. 프로그램을 실행시킨 쪽이 정한다."),
    FIG_CWD.render("에셋 폴더를 저장소 폴더 바로 아래에 두었을 때다 (폴더 이름은 예시). 글자가 같은 경로가 실행하는 "
                   "방법마다 다른 곳을 가리키고, 셋 가운데 하나만 맞는다."),
    code(r"""
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Debug|x64'">
    <OutDir>$(SolutionDir)$(Configuration)\$(PlatformTarget)\</OutDir>
""", lang="xml", title="Client/Client.vcxproj", tag="now", start=85, hl=[86]),
    p("실행 파일은 저장소 폴더 아래의 `Debug\\x64\\`에 만들어진다(86행). 프로젝트 파일은 `Client\\`에 있고, "
      "Visual Studio는 따로 정하지 않으면 그 폴더를 작업 디렉터리로 준다 (2.2절). 탐색기는 실행 파일이 있는 폴더를 "
      "준다. 그래서 그림의 위 두 줄은 서로 다른 폴더에서 출발하고, 어느 쪽도 에셋 폴더에 닿지 못한다."),

    h3("1.2", "이미 한 번 겪었다"),
    keep(h4("네 코드에서 확인할 것"),
    table([28, 32, 40], CHECK_HEADER, [
        ["`GLogger::Init`에 넘기는 파일 이름", "1-5강 6.2절에서 자리를 정한, `GLogger::Init`을 부르는 줄",
         "`\"ClaudGL.log\"`처럼 이름뿐이면 상대 경로다. 로그 파일이 실행하는 방법마다 다른 폴더에 생긴다 (1-5강 5.3절)"],
        ["지금 로그 파일이 있는 곳", "저장소 폴더 전체에서 `*.log` 검색",
         "`Client/`와 `Debug/x64/`에 하나씩 있다면 두 가지 방법으로 실행해 본 것이다"],
        ["파일을 여는 코드가 있는 곳", "`Engine/`과 `Client/`에서 `fstream`, `fopen` 검색",
         "지금은 Logger 한 곳일 것이다. 읽는 코드가 여기저기 생기기 전에 한 파일로 모을 자리를 만든다"],
    ], cell_cls=["lab", "", ""])),
    p("로그 파일은 어느 폴더에 생겨도 프로그램이 돌았다. 읽을 파일은 그렇지 않다. 엉뚱한 폴더에서 찾으면 열리지 않고, "
      "그 실패는 IDE에서 실행할 때는 보이지 않다가 실행 파일을 직접 띄운 날에 처음 나타난다."),

    keep(h3("1.3", "뒤의 강이 여기서 가져가는 것"),
    table([12, 28, 60], ["강", "읽을 파일", "이 강에서 준비하는 것"], [
        ["2-4강", "셰이더 소스 (글자)", "텍스트 파일을 통째로 `std::string`에 담기. 줄 끝과 BOM을 어떻게 할지 (4.2절, 5.2절)"],
        ["2-5강", "이미지 (바이너리)", "에셋의 전체 경로, 그리고 파일의 바이트 전체 (4.3절)"],
        ["3-5강", "셰이더와 텍스처의 캐시", "같은 파일을 가리키는 두 경로를 같은 글자로 만드는 방법 (3.3절)"],
        ["4-3강", "OBJ 모델 (글자)", "텍스트를 읽어 줄 단위로 다루는 출발점 (4.3절)"],
    ], cell_cls=["lab", "", ""], compact=True)),

    h3("1.4", "이 자료의 기준"),
    p("엔진 코드는 1-1 〜 1-6강 자료의 선언을 기준으로 삼고 함수 이름으로 가리킨다. 네 코드의 이름이 다르면 네 것이 "
      f"맞다. 줄 번호까지 적은 것은 저장소에 처음부터 있던 파일뿐이다 (`Client/Client.vcxproj`, `Engine/framework.h`, "
      f"`.gitignore`. {READ_DATE} 기준). 표준 라이브러리와 Windows의 동작은 이 자료를 만든 PC의 {MSVC_VER}"
      f"(`<filesystem>`, `<fstream>`과 그 소스)와 {SDK_VER}(`libloaderapi.h`, C 런타임 소스 `ucrt/lowio/read.cpp`)에서 "
      "읽었다. 4.2절의 표는 C 런타임을 직접 불러 확인했다. 프로젝트를 빌드해서 확인한 것은 없다."),
], lead="지금까지 엔진이 디스크에서 읽은 파일은 없다. Part 2부터는 셰이더와 이미지와 모델을 읽는다. 그 전에 풀 문제가 "
        "하나 있다. 글자가 같은 경로가 실행하는 방법에 따라 다른 곳을 가리킨다.")

ch2 = chapter(2, "작업 디렉터리와 실행 파일의 위치", [
    h3("2.1", "프로세스의 작업 디렉터리"),
    p("운영체제는 프로세스마다 작업 디렉터리를 하나씩 기억한다. 파일을 여는 함수에 상대 경로를 주면 운영체제가 그 "
      "앞에 작업 디렉터리를 붙여 절대 경로로 만든다. 처음 값은 프로세스를 만든 쪽이 정하고, 따로 정하지 않으면 "
      "만든 쪽의 작업 디렉터리를 그대로 물려받는다."),
    table([34, 66], ["실행시킨 쪽", "프로세스가 받는 작업 디렉터리"], [
        ["탐색기에서 실행 파일을 더블클릭", "그 실행 파일이 있는 폴더"],
        ["바로 가기(`.lnk`)", "바로 가기 속성의 “시작 위치” 칸에 적힌 폴더"],
        ["명령 프롬프트, PowerShell", "셸이 지금 서 있는 폴더. 프롬프트에 보이는 경로다"],
        ["Visual Studio의 F5, Ctrl+F5", "프로젝트 속성에 적힌 폴더 (2.2절)"],
        ["다른 프로그램 (런처, 배치 파일)", "그 프로그램이 정해 준 폴더. 정하지 않았으면 그 프로그램의 작업 디렉터리"],
    ], cell_cls=["lab", ""], compact=True),
    fn("std::filesystem::current_path",
       "path current_path();\n"
       "void current_path(const path& p);\n"
       "// each also has an overload with a trailing std::error_code& parameter (3.4)",
       "인자 없이 부르면 지금의 작업 디렉터리를 돌려준다. 경로를 주면 작업 디렉터리를 그곳으로 바꾼다.",
       params=[("`p`", "새 작업 디렉터리로 삼을 폴더")],
       returns="읽는 쪽은 절대 경로를 담은 `path`. 바꾸는 쪽은 없다",
       fails="바꾸는 쪽은 그 폴더가 없으면 실패한다. 실패를 알리는 방법은 3.4절의 두 가지다",
       notes=[("바꿀 때의 주의", "프로세스 전체에 하나뿐인 값이다. 바꾼 뒤에 여는 파일은 모두 새 기준으로 풀린다. 이미 열어 "
                              "둔 로그 파일은 그대로다"),
              ("헤더", "`<filesystem>`")],
       lib="C++17"),
    box("ex", "예시: 같은 프로그램을 세 번 실행하면", [
        p("작업 디렉터리를 한 줄 찍고 끝나는 `Where.exe`가 `D:\\Tools\\`에 있다고 하자."),
        console(Raw(
            '<span class="dim">D:\\Tools&gt;</span> Where.exe\n'
            "D:\\Tools\n"
            '<span class="dim">D:\\&gt;</span> Tools\\Where.exe\n'
            "D:\\\n"
            '<span class="dim">D:\\Tools\\Sub&gt;</span> ..\\Where.exe\n'
            "D:\\Tools\\Sub"
        ), title="명령 프롬프트"),
        p("실행 파일은 한 번도 움직이지 않았다. 달라진 것은 셸이 서 있던 폴더뿐이다."),
    ]),

    h3("2.2", "Visual Studio가 정하는 값"),
    p("F5나 Ctrl+F5로 실행할 때의 작업 디렉터리는 프로젝트 속성 → 디버깅 → 작업 디렉터리 칸에 있다. 기본값은 "
      "`$(ProjectDir)`, 곧 프로젝트 파일이 있는 폴더다. 실행 파일이 만들어지는 `$(OutDir)`가 아니다."),
    keep(table([20, 42, 38], ["매크로", "저장소가 `C:\\Dev\\ClaudGL\\`에 있을 때의 값", "뜻"], [
        ["`$(SolutionDir)`", "`C:\\Dev\\ClaudGL\\`", "`.sln` 파일이 있는 폴더"],
        ["`$(ProjectDir)`", "`C:\\Dev\\ClaudGL\\Client\\`", "`.vcxproj` 파일이 있는 폴더. 작업 디렉터리의 기본값"],
        ["`$(OutDir)`", "`C:\\Dev\\ClaudGL\\Debug\\x64\\`", "결과물이 만들어지는 폴더 (`Client/Client.vcxproj:86`)"],
        ["`$(TargetPath)`", "`C:\\Dev\\ClaudGL\\Debug\\x64\\Client.exe`", "만들어진 실행 파일. F5가 실행하는 것"],
    ], cell_cls=["lab", "", ""], compact=True)),
    p("속성 창에서 이 칸을 고치면 값은 `Client.vcxproj`가 아니라 그 옆의 `Client.vcxproj.user`에 "
      "`LocalDebuggerWorkingDirectory`라는 이름으로 저장된다. 사용자마다 따로 두는 설정 파일이고, 이 저장소의 "
      "`.gitignore`는 `*.user`를 올리지 않는다(9행). 그래서 ==속성 창에서 고친 작업 디렉터리는 그 PC에만 남는다==. "
      "저장소를 새로 받은 PC에서는 다시 기본값이다."),
    p("같은 이름의 속성을 `Client.vcxproj`의 `OutDir`가 적힌 `PropertyGroup`에 손으로 적어 저장소에 올릴 수도 있다 "
      "(CMake가 만드는 프로젝트 파일이 그렇게 한다. 실행해서 확인하지는 않았다). 기본값은 Visual Studio 2022의 "
      "`Microsoft.Cpp.Common.props`에서 읽었다. 다른 IDE는 기본값이 다를 수 있다. 그래서 미션의 첫 단계는 짐작하지 "
      "않고 직접 찍어 보는 것이다."),

    h3("2.3", "실행 파일이 있는 곳"),
    p("실행 파일의 위치는 실행하는 방법에 따라 바뀌지 않는다. 그래서 “실행 파일에서부터 센 경로”는 흔들리지 않는 "
      "기준이 된다. 그런데 C++ 표준에는 실행 파일의 경로를 알려 주는 함수가 없다. 운영체제에 물어야 한다."),
    table([30, 26, 44], ["방법", "주는 것", "걸리는 점"], [
        ["`main`의 `argv[0]`", "프로그램을 부를 때 쓴 이름",
         "실행시킨 쪽이 적어 준 글자다. 명령 프롬프트에서 `Client`라고만 쳤다면 그것이 들어온다"],
        ["`current_path()`", "작업 디렉터리", "실행 파일의 위치가 아니다 (2.1절)"],
        ["Windows: `GetModuleFileNameW`", "실행 파일의 전체 경로", "Windows에서만 쓸 수 있다. 버퍼 크기를 직접 다룬다"],
        ["Linux: `/proc/self/exe` 링크, macOS: `_NSGetExecutablePath`", "같은 것", "운영체제마다 다른 코드가 필요하다"],
    ], cell_cls=["lab", "", ""], compact=True),
    fn("GetModuleFileNameW",
       "DWORD GetModuleFileNameW(HMODULE hModule, LPWSTR lpFilename, DWORD nSize);",
       "모듈(실행 파일이나 DLL)이 로드된 파일의 전체 경로를 버퍼에 적는다.",
       params=[("`hModule`", "경로를 알고 싶은 모듈. `nullptr`을 주면 이 프로세스의 실행 파일이다"),
               ("`lpFilename`", "경로를 받을 `wchar_t` 버퍼"),
               ("`nSize`", "버퍼의 크기. 바이트 수가 아니라 `wchar_t` 글자 수다")],
       returns="버퍼에 적은 글자 수. 끝의 널 문자는 세지 않는다",
       fails="0을 돌려준다. 이유는 `GetLastError()`로 묻는다",
       notes=[("버퍼가 작으면", "경로를 `nSize`에 맞춰 자르고 `nSize`를 돌려준다. 그때 `GetLastError()`는 "
                              "`ERROR_INSUFFICIENT_BUFFER`(122)다. 반환값이 `nSize`와 같으면 잘린 경로다"),
              ("버퍼의 크기", "`MAX_PATH`(260)가 오랜 관례지만 경로는 그보다 길 수 있다. 잘렸을 때 무엇을 할지 정한다"),
              ("`W`와 `A`", "`W`는 `wchar_t`(UTF-16)로, `A`는 현재 코드 페이지의 `char`로 준다. `A`는 그 코드 페이지에 "
                           "없는 글자를 잃는다. `W`가 준 문자열은 `std::filesystem::path`에 그대로 넣을 수 있다 (5.3절)"),
              ("헤더", "`<Windows.h>` (선언은 `libloaderapi.h`). 이 헤더를 포함할 때의 주의는 1-5강 8장에 있다")],
       lib="Win32"),
    box("ex", "예시: 실행 파일이 `D:\\Games\\Demo\\Demo.exe`일 때", [
        table([16, 16, 32, 36], ["`nSize`", "반환값", "버퍼의 내용", "읽는 법"], [
            ["260", "21", "`D:\\Games\\Demo\\Demo.exe`", "21글자를 다 적었다"],
            ["8", "8", "`D:\\Game`", "7글자와 널 문자. 반환값이 `nSize`와 같으니 잘렸다"],
        ], cell_cls=["c", "c", "", ""], compact=True),
        p("얻은 경로에서 파일 이름을 떼면 실행 파일이 있는 폴더다 (3.2절). 운영체제에 묻는 호출은 `.cpp` 파일 하나 안에 "
          "둔다. 콘솔 모드를 바꾸는 Win32 함수와 `Windows.h`를 `Logger.cpp` 안에 가두는 것(1-5강 8장)과 같은 이유다."),
    ]),
    box("ue", None,
        "언리얼은 실행 파일이 있는 폴더를 기준으로 삼는다. `FPlatformProcess::BaseDir()`가 그 폴더(`Binaries/Win64/`)이고, "
        "엔진은 시작할 때 작업 디렉터리를 그곳으로 바꿔 둔다. `FPaths::EngineDir()`가 돌려주는 `../../../Engine/` 같은 "
        "상대 경로는 거기서부터 센 것이다. 게임 코드는 `FPaths::ProjectContentDir()` 같은 함수로 폴더를 얻는다."),
    box("cs", None,
        "작업 디렉터리는 환경 변수, 열린 파일 목록과 함께 운영체제가 프로세스마다 들고 있는 속성이다. 자식 프로세스는 "
        "이것들을 부모에게서 물려받는다. 운영체제 책의 프로세스 생성과 프로세스 제어 블록(PCB) 항목에 닿는다."),
], lead="프로세스마다 “지금 서 있는 폴더”가 하나 있다. 상대 경로의 출발점이다. 실행 파일이 놓인 폴더와는 다른 것이고, "
        "둘을 구별하는 데서 이 강이 시작한다.")

ch3 = chapter(3, "std::filesystem: 경로를 값으로", [
    h3("3.1", "path"),
    p("`std::filesystem::path`는 경로를 조각들의 줄로 본다. 드라이브, 루트, 폴더들, 파일 이름이 조각이고, 멤버 함수가 "
      "조각을 꺼내 준다."),
    FIG_PATH.render("`path`의 멤버 함수가 잘라 주는 조각들 (`C:/Game/Assets/Shaders/basic.vert`). 모두 글자만 보고 자른다. "
                    "`extension()`은 점을 포함한다."),
    fn("std::filesystem::path",
       "class path;                                               // namespace std::filesystem\n"
       "template<class Source> path(const Source& source, format fmt = auto_format);\n"
       "friend path operator/(const path& lhs, const path& rhs);",
       "경로 하나를 담는 값 타입이다. 글자열을 들고 있을 뿐 디스크를 건드리지 않는다. 그 경로에 파일이 실제로 있는지는 "
       "모른다.",
       params=[("`source`", "`const char*`, `std::string`, `std::wstring`, `u8\"…\"` 같은 문자열. `fmt`는 기본값 그대로 둔다"),
               ("`lhs / rhs`", "두 경로를 구분자 하나로 잇는다. `/=`는 왼쪽을 바꾼다")],
       notes=[("구분자", "Windows에서는 `/`와 `\\`를 둘 다 구분자로 읽는다. 코드에는 `/`로 적어 두면 다른 운영체제에서도 통한다. "
                        "`/` 연산자가 새로 끼우는 구분자는 Windows에서 `\\`다"),
              ("`/`의 예외", "오른쪽이 절대 경로면 왼쪽을 버리고 오른쪽이 결과가 된다. 오른쪽이 `/`로 시작해도 왼쪽의 "
                           "폴더가 버려진다"),
              ("글자로 꺼내기", "`string()`, `wstring()`, `u8string()`, 그리고 구분자를 `/`로 통일한 `generic_string()`. "
                              "`c_str()`은 Windows에서 `const wchar_t*`를 준다"),
              ("헤더", "`<filesystem>`")],
       lib="C++17"),
    box("ex", "예시: `/` 연산자가 하는 일 (Windows)", [
        table([42, 26, 32], ["식", "결과", "읽는 법"], [
            ["`path( \"Data\" ) / \"Maps\" / \"town.map\"`", "`Data\\Maps\\town.map`", "구분자를 하나씩 끼워 잇는다"],
            ["`path( \"D:/Demo/Data/\" ) / \"a.txt\"`", "`D:/Demo/Data/a.txt`", "이미 구분자로 끝나면 더 끼우지 않는다"],
            ["`path( \"D:/Demo\" ) / \"Data\"`", "`D:/Demo\\Data`", "두 구분자가 섞여 보여도 같은 경로다"],
            ["`path( \"D:/Demo\" ) / \"E:/Other\"`", "`E:/Other`", "오른쪽이 절대 경로라 왼쪽이 버려졌다"],
            ["`path( \"D:/Demo/Data\" ) / \"/a.txt\"`", "`D:/a.txt`", "오른쪽이 `/`로 시작해 드라이브만 남았다"],
            ["`path( \"town\" ) += \".map\"`", "`town.map`", "`+=`는 구분자 없이 글자만 잇는다"],
        ], cell_cls=["lab", "", ""], compact=True),
        p("넷째와 다섯째 줄은 오류가 아니라 정해진 동작이다. 바깥에서 받은 글자를 오른쪽에 놓을 때 조심할 자리다."),
    ]),

    h3("3.2", "한 칸 위로: parent_path"),
    p("`parent_path()`는 마지막 조각을 뗀 경로를 돌려준다. 실행 파일의 경로에서 폴더를 얻을 때, 폴더에서 한 칸씩 "
      "위로 올라갈 때 쓴다. 이것도 글자만 다루므로 실제로 그런 폴더가 있는지는 보지 않는다."),
    box("ex", "예시: `parent_path()`를 거듭 부르면", [
        table([34, 30, 36], ["경로", "`parent_path()`", "메모"], [
            ["`D:/Demo/Bin/Demo.exe`", "`D:/Demo/Bin`", "파일 이름이 떨어졌다"],
            ["`D:/Demo/Bin`", "`D:/Demo`", "한 칸 위"],
            ["`D:/Demo/Bin/`", "`D:/Demo/Bin`", "구분자로 끝나면 마지막 조각이 빈 이름이다. 한 번으로는 올라가지 않는다"],
            ["`D:/`", "`D:/`", "루트의 부모는 자기 자신이다"],
            ["`Demo.exe`", "빈 경로", "더 뗄 것이 없다"],
        ], cell_cls=["lab", "", ""], compact=True),
    ]),

    h3("3.3", "파일 시스템에 묻는 함수"),
    p("`path`는 글자다. 그 자리에 무엇이 있는지, 얼마나 큰지는 운영체제에 물어야 안다. 묻는 함수는 `path`의 멤버가 "
      "아니라 `std::filesystem` 안의 자유 함수다. 상대 경로를 주면 작업 디렉터리 기준으로 풀린다. 2장의 문제가 "
      "여기에도 그대로 있다."),
    fn("std::filesystem::exists · is_regular_file · file_size",
       "bool           exists(const path& p);\n"
       "bool           is_regular_file(const path& p);\n"
       "std::uintmax_t file_size(const path& p);\n"
       "// each also has an overload: (const path& p, std::error_code& ec) noexcept",
       "그 경로에 무엇이 있는지, 얼마나 큰지 운영체제에 묻는다. 파일의 내용은 읽지 않는다.",
       params=[("`p`", "물어볼 경로")],
       returns="`exists`는 무엇이든 있으면 `true`. `is_regular_file`은 보통 파일이면 `true`이고 폴더면 `false`다 "
               "(폴더는 `is_directory`). `file_size`는 바이트 수를 부호 없는 64비트 정수로 준다",
       fails="`exists`와 `is_regular_file`에게 “없다”는 실패가 아니라 `false`라는 답이다. `file_size`는 파일이 없으면 "
             "실패하고, `ec`를 받는 쪽은 `static_cast<std::uintmax_t>( -1 )`을 돌려준다",
       notes=[("주의", "물어본 순간의 답이다. 확인한 직후에 파일이 지워질 수 있으므로, 여는 쪽의 실패 확인은 그대로 있어야 한다"),
              ("크기와 글자 수", "`file_size`는 디스크의 바이트 수다. 텍스트 모드로 읽은 글자 수와 다를 수 있다 (4.2절). "
                              "`std::size_t`나 `std::streamsize`로 넘길 때는 `static_cast`가 필요하다"),
              ("헤더", "`<filesystem>`")],
       lib="C++17"),
    p("경로를 절대 경로로 바꾸거나 `.`과 `..`를 정리해 주는 함수도 넷 있다. 로그에 경로를 찍을 때 쓴다. 상대 경로만 "
      "찍힌 로그로는 어느 폴더에서 찾았는지 알 수 없다."),
    keep(table([26, 44, 30], ["함수", "하는 일", "없는 파일의 경로를 주면"], [
        ["`absolute( p )`", "상대 경로 앞에 작업 디렉터리를 세운다. 디스크를 보지 않는다. `..`까지 정리하는지는 구현마다 "
                           "다르다 (MSVC는 정리한다)", "그대로 바꿔 준다"],
        ["`weakly_canonical( p )`", "실제로 있는 앞부분은 링크까지 풀고, 없는 뒷부분은 글자만 정리한다", "된다. 첫 조각부터 없으면 결과도 상대 경로다"],
        ["`canonical( p )`", "`.`, `..`, 링크를 모두 푼 절대 경로를 만든다", "실패한다"],
        ["`p.lexically_normal()`", "`path`의 멤버. 디스크를 보지 않고 `.`과 `..`만 글자로 정리한다", "된다. 상대 경로는 상대 경로로 남는다"],
    ], cell_cls=["lab", "", ""], compact=True)),
    p("작업 디렉터리가 `D:\\Demo\\Bin`일 때 MSVC에서 `absolute( \"../Data/a.txt\" )`는 `D:\\Demo\\Data\\a.txt`다. "
      "`D:\\Demo\\Data\\`가 있고 그 안에 `none.txt`가 없다면 `weakly_canonical( \"../Data/none.txt\" )`는 "
      "`D:\\Demo\\Data\\none.txt`를 주고, `canonical`은 실패한다."),

    h3("3.4", "실패를 알리는 두 가지 모양"),
    p("`<filesystem>`의 함수는 거의 모두 두 벌로 나와 있다. 같은 일을 하고, 실패를 알리는 방법만 다르다."),
    keep(table([22, 39, 39], ["", "던지는 쪽", "`std::error_code&`를 받는 쪽"], [
        ["부르는 모양", "`file_size( p )`", "`file_size( p, ec )`"],
        ["실패하면", "`std::filesystem::filesystem_error`를 던진다", "`ec`에 오류를 담고 정해진 값(`false`, 빈 `path`, 최댓값)을 돌려준다"],
        ["성공하면", "결과를 돌려준다", "결과를 돌려주고 `ec`를 비운다"],
        ["확인을 잊으면", "잡지 않은 예외가 되어 `std::terminate()`가 불린다 (1-6강 4.1절)", "아무 일 없이 지나간다"],
        ["오류에서 꺼낼 것", "`what()`, `code()`, 문제가 된 경로 `path1()`", "`ec.value()`, `ec.message()`, `if ( ec )`"],
    ], cell_cls=["lab", "", ""], compact=True)),
    box("ex", "예시: 없는 파일의 크기를 두 가지로 물으면", [
        code(r"""
std::error_code ec;                                                      // <system_error>
std::uintmax_t  a = std::filesystem::file_size( "D:/Demo/none.bin", ec );
// no exception: a == static_cast<std::uintmax_t>( -1 ), bool( ec ) == true, ec.value() == 2 on Windows

std::uintmax_t  b = std::filesystem::file_size( "D:/Demo/none.bin" );    // throws filesystem_error
""", tag="syntax"),
        p("`std::error_code`는 오류 번호 하나를 담는 작은 값이고, 오류가 없으면 0이다. MSVC의 `<filesystem>`은 Windows의 "
          "오류 번호를 그대로 담는다 (파일이 없으면 2, 중간 폴더부터 없으면 3). 운영체제와 무관하게 가리려면 "
          "`std::errc::no_such_file_or_directory`와 비교한다."),
    ]),
    p("어느 쪽을 부를지는 1-6강에서 정한 규칙이 정한다. 반환값으로 알리기로 했다면 `ec`를 받는 쪽을 쓰고, 예외를 "
      "쓰기로 했다면 던지는 쪽을 쓰되 잡을 곳을 정해 둔다. 규칙과 반대쪽을 부르면 그 호출 하나가 규칙의 구멍이 된다. "
      "그리고 파일이 없는 것은 버그가 아니라 실패다 (1-6강 2.1절 표의 첫 줄)."),
    box("ue", None,
        "언리얼에서 이 자리는 `FPaths`다. `FPaths::Combine`, `GetExtension`, `GetBaseFilename`, `GetPath`, "
        "`ConvertRelativePathToFull`, `FileExists`가 이 장의 함수들과 짝이 맞는다. `FString`에도 경로를 잇는 "
        "`/` 연산자가 있다. 실패는 `bool`로 알리고 예외는 쓰지 않는다 (1-6강 5.2절)."),
    box("cs", None,
        "파일 시스템은 폴더가 가지인 나무이고 경로는 뿌리에서 잎까지 가는 길이다. 파일의 크기와 시각은 내용과 따로 "
        "적혀 있어서(NTFS의 MFT 레코드, 유닉스의 inode) `file_size`는 내용을 읽지 않고 답한다. 운영체제 책의 파일 "
        "시스템 구현 장에 닿는다."),
], lead="경로를 `std::string`으로 다루면 구분자를 손으로 붙이고 자르게 된다. `<filesystem>`은 경로를 타입으로 만들고, "
        "파일 시스템에 묻는 함수를 준다.")

ch4 = chapter(4, "파일 읽기: 텍스트와 바이너리", [
    h3("4.1", "열기"),
    fn("std::ifstream (생성자)",
       "explicit ifstream(const std::filesystem::path& filename,\n"
       "                  std::ios_base::openmode mode = std::ios_base::in);",
       "파일을 읽기용으로 연다. 열려 있는 동안 파일을 쥐고 있다가 소멸자에서 닫는다.",
       params=[("`filename`", "열 파일. `path`를 그대로 받는다. 상대 경로면 작업 디렉터리 기준이다"),
               ("`mode`", "`std::ios::binary`를 주면 바이너리 모드로 연다. 주지 않으면 텍스트 모드다 (4.2절)")],
       fails="예외를 던지지 않는다. 스트림이 실패 상태가 되고 그 뒤의 읽기는 아무것도 읽지 않는다. `is_open()`이나 "
             "`if ( !file )`로 확인한다",
       notes=[("실패한 이유", "스트림은 왜 못 열었는지 말해 주지 않는다. 이유를 남기려면 3.3절의 함수로 직접 묻는다"),
              ("닫기", "소멸자가 닫는다 (RAII, 1-4강 3.1절). 함수가 어느 길로 나가도 닫힌다"),
              ("헤더", "`<fstream>`. 쓰는 쪽 `std::ofstream`은 1-5강 5.3절에서 썼다")],
       lib="C++17"),

    h3("4.2", "텍스트 모드와 바이너리 모드"),
    p("Windows의 텍스트 파일은 줄 끝을 `0D 0A` 두 바이트(CR LF)로 적는다. C와 C++ 코드에서 줄 끝은 `'\\n'`(`0A`) "
      "하나다. 텍스트 모드는 그 사이를 맞춰 준다. 읽을 때 `0D 0A`를 `0A` 하나로 줄이고, 쓸 때 `0A`를 `0D 0A`로 늘린다. "
      "바이너리 모드는 아무것도 바꾸지 않는다."),
    FIG_MODE.render("`Hi`와 `OK` 두 줄이 든 8바이트 파일이다. 텍스트 모드에서는 읽은 글자 수가 파일 크기보다 작다."),
    keep(table([26, 37, 37], ["", "텍스트 모드 (기본값)", "바이너리 모드 (`std::ios::binary`)"], [
        ["읽을 때 `0D 0A`", "`0A` 하나가 된다", "두 바이트 그대로"],
        ["읽을 때 `1A`", "파일의 끝으로 여긴다. 그 뒤는 읽히지 않는다", "보통 바이트"],
        ["짝 없는 `0D`나 `0A`", "그대로", "그대로"],
        ["읽은 수와 파일 크기", "읽은 글자 수가 더 작을 수 있다", "같다"],
        ["쓸 때 `0A`", "`0D 0A`가 된다", "그대로"],
    ], cell_cls=["lab", "", ""], compact=True)),
    p("둘째 줄이 바이너리 파일을 텍스트 모드로 열었을 때 생기는 일이다. `41 1A 42 43` 네 바이트를 텍스트 모드로 읽으면 "
      "`41` 하나만 읽힌다. 이미지나 모델 안에는 `1A`라는 값이 얼마든지 들어 있고, 오류 없이 앞부분만 읽힌다. 이 변환은 "
      "운영체제가 아니라 C 런타임 라이브러리가 한다. Linux와 macOS의 런타임은 아무것도 바꾸지 않아서 두 모드가 똑같이 "
      "동작한다. Windows에서만 드러나는 버그가 여기서 나온다."),
    p("규칙은 둘이다. ==글자가 아닌 파일은 반드시 바이너리 모드로 연다.== 글자인 파일은 어느 모드로도 읽을 수 있고, "
      "차이를 알고 고른다. 텍스트 모드는 `\\r`을 없애 주는 대신 크기가 어긋나고, 바이너리 모드는 크기가 맞는 대신 "
      "줄마다 끝에 `\\r`이 남는다."),

    h3("4.3", "통째로 읽기"),
    flow([
        ("경로", "어디의 파일인가"),
        ("열기", "모드를 고른다", "accent"),
        ("크기", "얼마나 읽을까"),
        ("버퍼", "자리를 잡는다"),
        ("읽기", "한 번에"),
        ("확인", "다 읽혔는가", "dark"),
    ], "셰이더, 이미지, 모델은 모두 작아서 한 번에 메모리로 올린다. 칸마다 실패할 수 있고, 실패하면 거기서 멈춘다."),
    p("가운데 세 칸(크기, 버퍼, 읽기)을 하는 방법이 셋 있다. 첫째 방법이 쓰는 `read`는 표 다음의 카드에 있다."),
    keep(table([22, 32, 22, 24], ["방법", "모양", "얻는 것", "내주는 것"], [
        ["크기를 알고 한 번에", "`file_size` → 버퍼의 `resize` → `read` → `gcount`", "메모리를 한 번만 잡는다. 빠르다",
         "텍스트 모드에서는 크기가 어긋난다"],
        ["반복자 한 쌍으로", "`std::istreambuf_iterator<char>` 둘로 `std::string`을 만든다", "크기를 몰라도 된다. 어느 모드든 맞다",
         "글자를 하나씩 옮기고 버퍼가 여러 번 다시 잡힌다"],
        ["스트림 버퍼째로", "`std::ostringstream`에 `file.rdbuf()`를 넣고 `str()`", "짧다. 어느 모드든 맞다",
         "문자열이 한 번 더 복사된다"],
    ], cell_cls=["lab", "", "", ""], compact=True)),
    code(r"""
std::istreambuf_iterator<char> first( file ), last;    // "last", default-constructed, marks the end
std::string from_iterators( first, last );             // row 2: everything between the two iterators

std::ostringstream buffer;  buffer << file.rdbuf();    // row 3: pour the stream in, then buffer.str()
""", title="the idioms of rows 2 and 3 (headers: <iterator>, <sstream>)", tag="syntax"),
    fn("std::istream::read · gcount",
       "std::istream&  read(char* s, std::streamsize count);\n"
       "std::streamsize gcount() const;",
       "`read`는 스트림에서 `count`글자를 꺼내 `s`가 가리키는 곳에 차례로 적는다. 글자의 뜻은 해석하지 않는다. "
       "`gcount`는 바로 앞의 `read`가 실제로 꺼낸 글자 수다.",
       params=[("`s`", "받을 버퍼의 시작 주소. `count`글자를 담을 자리가 이미 있어야 한다. 끝에 `'\\0'`을 붙여 주지 않는다"),
               ("`count`", "꺼낼 글자 수. 부호 있는 정수다")],
       returns="`read`는 스트림 자신. `if ( !file.read( … ) )`처럼 바로 확인할 수 있다",
       fails="`count`글자를 채우기 전에 파일이 끝나면 `eofbit`와 `failbit`가 함께 선다. 그때까지 읽은 글자는 버퍼에 들어 있다",
       notes=[("버퍼의 타입", "`char*`만 받는다. `unsigned char`나 `std::byte` 버퍼에 읽으려면 주소를 "
                             "`reinterpret_cast<char*>`로 바꿔 넘긴다"),
              ("헤더", "`<istream>`. `<fstream>`을 포함하면 따라온다")],
       lib="C++"),
    box("ex", "예시: 요청한 것보다 적게 읽혔을 때", [
        code(r"""
char buf[16]{};             // sixteen zeros
file.read( buf, 16 );       // but the file holds only 10 bytes
// file.fail() == true, file.eof() == true, file.gcount() == 10; buf[10] .. buf[15] are still zero
""", tag="syntax"),
        p("실패 상태가 됐지만 읽힌 10바이트는 버퍼에 있다. 텍스트 모드로 연 파일을 `file_size`만큼 읽으라고 했을 때 "
          "정확히 이 일이 일어난다. 줄어든 `0D`의 수만큼 모자란다."),
    ]),
    keep(p("바이트를 담을 타입도 골라야 한다. `read`가 `char*`만 받는다는 점과, 0x80 이상의 값이 어떻게 보이는지가 갈린다."),
    table([19, 21, 22, 38], ["타입", "`read`에 넘길 때", "0x80 이상의 값", "메모"], [
        ["`char`", "그대로", "MSVC에서 음수가 된다", "`std::string`의 원소 타입. 글자에 맞다"],
        ["`unsigned char`", "`reinterpret_cast`", "128 〜 255 그대로",
         "C 라이브러리들이 바이트에 쓰는 타입. 이 프로젝트의 `byte`와 `uint8`이 이 타입의 별칭이다 "
         "(`Engine/framework.h:25`, `:21`)"],
        ["`std::byte`", "`reinterpret_cast`", "정수가 아니다",
         "산술을 할 수 없고 `std::to_integer`로 꺼낸다. “글자도 수도 아닌 바이트”라는 뜻이 타입에 적힌다 (`<cstddef>`, C++17)"],
    ], cell_cls=["lab", "", "", ""], compact=True)),
    p("`framework.h`의 두 별칭은 `unsigned __int8`로 적혀 있고, MSVC에서 그것은 `unsigned char`와 같은 타입이다. pch를 "
      "거쳐 모든 파일에서 보인다. 줄 단위로 읽는 `std::getline`은 4-3강에서 OBJ를 읽을 때 쓴다. 바이너리 모드로 연 "
      "CRLF 파일을 `std::getline`으로 자르면 줄마다 끝에 `\\r`이 남는다는 것만 기억해 둔다."),

    h3("4.4", "읽은 바이트를 넘기기: std::span"),
    p("통째로 읽은 바이트는 `std::vector`가 들고 있다. 그 일부를 다른 함수에 보여 줄 때 벡터를 복사하면 낭비이고, "
      "포인터와 길이를 따로 넘기면 둘이 어긋날 수 있다. C++20의 `std::span`은 그 둘을 한 값으로 묶은 것이다."),
    FIG_SPAN.render("`span`은 원소를 들고 있지 않다. 남의 메모리의 한 구간을 가리키는 주소와 개수뿐이다."),
    fn("std::span",
       "template<class T, std::size_t Extent = std::dynamic_extent>\n"
       "class span;",
       "연속으로 놓인 원소들의 한 구간을 가리키는 값이다. 시작 주소와 개수만 들고, 원소를 소유하지 않는다.",
       params=[("`T`", "원소의 타입. `const`를 붙이면 읽기만 하는 구간이 된다. `Extent`는 개수를 컴파일할 때 고정할 "
                      "때만 적는다")],
       notes=[("만들기", "`std::vector`, `std::array`, C 배열에서 저절로 만들어진다. 포인터와 개수로도 만든다"),
              ("주요 멤버", "`size()` · `size_bytes()` · `data()` · `[i]` · 범위 기반 `for` · 일부만 가리키는 새 `span`을 주는 "
                          "`first( n )`, `last( n )`, `subspan( offset, n )`. 범위는 검사하지 않는다"),
              ("수명", "빌린 것이다 (1-4강 5.2절). 원본 `vector`가 사라지거나 크기가 바뀌어 메모리를 옮기면 댕글링이 된다"),
              ("헤더", "`<span>`")],
       lib="C++20"),
    box("ex", "예시: 300바이트를 헤더와 본문으로 나눠 보여 주기", [
        code(r"""
std::uint32_t Checksum( std::span<const std::uint8_t> bytes );    // accepts any run of bytes

std::vector<std::uint8_t>     file_bytes( 300 );
std::span<const std::uint8_t> all    = file_bytes;                // 300 bytes, nothing is copied
std::span<const std::uint8_t> header = all.first( 12 );           // bytes 0 .. 11
std::span<const std::uint8_t> body   = all.subspan( 12 );         // bytes 12 .. 299
""", tag="usage"),
        p("`Checksum`은 전체로도, 헤더만으로도, 본문만으로도 부를 수 있고 복사는 한 번도 일어나지 않는다. 받는 쪽은 "
          "그 바이트가 `vector`에 있는지 배열에 있는지 알 필요가 없다."),
    ]),
    box("api", None,
        "OpenGL은 셰이더를 GLSL 글자로 받는다. 텍스트 읽기가 필요한 이유다 (2-4강). DX11·DX12는 보통 미리 컴파일한 "
        "바이트코드 파일을, Vulkan은 SPIR-V 바이너리를 받는다. 그쪽은 바이너리 읽기다. 두 가지를 다 만들어 두면 "
        "어느 API로 가도 Core는 그대로 쓴다."),
    box("ue", None,
        "`FFileHelper::LoadFileToString( Result, Filename )`과 `FFileHelper::LoadFileToArray( Result, Filename )`이 "
        "이 장의 두 함수다. 둘 다 결과를 출력 인자로 채우고 성공 여부를 `bool`로 돌려준다. `std::span`의 자리에는 "
        "`TArrayView`와 `TConstArrayView`가 있다."),
], lead="파일은 바이트가 늘어선 줄이다. 텍스트와 바이너리는 파일의 종류가 아니라 ==여는 방식==의 이름이다.")

ch5 = chapter(5, "인코딩: 바이트와 글자", [
    h3("5.1", "UTF-8"),
    p("ASCII는 영문자와 숫자, 기호를 0x00 〜 0x7F의 한 바이트로 적는다. UTF-8은 그 범위를 그대로 두고 나머지 글자를 "
      "2 〜 4바이트로 적는다. 한글 한 글자는 3바이트다. 같은 글자도 인코딩이 다르면 다른 바이트가 된다."),
    keep(table([20, 26, 26, 28], ["글자", "UTF-8", "CP949 (한국어 Windows)", "메모"], [
        ["`A`", "`41`", "`41`", "ASCII 범위는 어디서나 같다"],
        ["`가`", "`EA B0 80`", "`B0 A1`", "같은 글자, 다른 바이트"],
        ["`한`", "`ED 95 9C`", "`C7 D1`", ""],
    ], cell_cls=["c", "", "", ""], compact=True)),
    p("`std::string`은 `char`가 늘어선 줄일 뿐 인코딩을 모른다. `size()`는 글자 수가 아니라 바이트 수다. `가나`를 "
      "UTF-8로 담으면 `size()`는 6이다. 파일의 바이트를 그대로 `std::string`에 담아 두는 동안에는 아무 문제도 없다. "
      "문제는 그 바이트를 글자로 해석하는 자리에서 생긴다. 콘솔에 찍을 때와 경로로 쓸 때다."),
    box("cs", None,
        "글자에 번호를 매긴 표(유니코드의 코드 포인트)와 그 번호를 바이트로 적는 방법(UTF-8, UTF-16)은 별개의 층이다. "
        "UTF-8은 첫 바이트의 윗자리 비트로 그 글자가 몇 바이트인지 알리는 가변 길이 부호다."),

    h3("5.2", "BOM"),
    p("UTF-8 파일의 맨 앞에 `EF BB BF` 세 바이트가 붙어 있을 수 있다. “이 파일은 UTF-8이다”라는 표식이고 BOM이라고 "
      "부른다. Windows의 편집기들은 저장 옵션에 따라 이것을 붙인다 (옵션 이름은 `UTF-8 with BOM`, "
      "`UTF-8 with signature` 같은 식이다). `std::ifstream`은 BOM을 떼어 주지 않는다. 읽은 문자열의 처음 세 글자가 된다."),
    box("ex", "예시: 같은 한 줄을 두 가지로 저장하면", [
        console(Raw(
            '<span class="dim">PS&gt;</span> Format-Hex plain.glsl\n'
            "00000000   23 76 65 72 73 69 6F 6E 20 34 36 30 0D 0A        #version 460..\n"
            '<span class="dim">PS&gt;</span> Format-Hex with_bom.glsl\n'
            '00000000   <span class="warn">EF BB BF</span> 23 76 65 72 73 69 6F 6E 20 34 36 30 0D  '
            "ï»¿#version 460.\n"
            "00000010   0A                                               ."
        ), title="PowerShell (출력 형식은 버전마다 조금 다르다)"),
        p("`Format-Hex`는 파일의 바이트를 16진수로 보여 주는 PowerShell 명령이다. 아래 파일은 3바이트가 더 크고, "
          "글자로 읽는 쪽은 `#` 앞에서 모르는 글자 셋을 만난다. 2-4강의 GLSL 컴파일러는 대개 여기서 오류를 낸다. "
          "줄 끝의 `0D 0A`도 눈으로 확인할 수 있다."),
    ]),

    h3("5.3", "Windows의 경로와 글자"),
    p("Windows의 파일 이름은 UTF-16이고 C++에서는 `wchar_t` 문자열이다. `std::filesystem::path`도 Windows에서는 안에 "
      "`wchar_t` 문자열을 들고 있다. `char` 문자열로 `path`를 만들면 표준 라이브러리가 `wchar_t`로 바꾸는데, MSVC는 "
      "그때 UTF-8이 아니라 시스템의 현재 코드 페이지(한국어 Windows에서는 CP949)로 해석한다."),
    keep(table([36, 22, 42], ["`path`를 만드는 재료", "해석", "한글이 든 경로에서"], [
        ["`wchar_t` 문자열 (`L\"…\"`, `GetModuleFileNameW`가 준 것)", "그대로", "안전하다"],
        ["`char8_t` 문자열 (`u8\"…\"`, C++20)", "UTF-8", "안전하다"],
        ["`char` 문자열 (`\"…\"`, `std::string`)", "현재 코드 페이지", "그 바이트가 실제로 그 코드 페이지일 때만 맞다. UTF-8 바이트를 넣으면 다른 이름이 된다"],
        ["거꾸로: `path::string()`", "현재 코드 페이지로", f"그 코드 페이지에 없는 글자가 있으면 예외(`std::system_error`)가 난다 ({MSVC_VER})"],
    ], cell_cls=["lab", "", ""], compact=True)),
    ul([
        "**에셋의 폴더와 파일 이름은 ASCII로만 짓는다.** 코드에 적는 에셋 경로가 어떤 인코딩에서도 같은 바이트가 된다.",
        "**경로는 `path`끼리 잇는다.** 중간에 `std::string`으로 바꿨다가 다시 `path`로 만들지 않는다. 실행 파일의 폴더에는 "
        "사용자 이름처럼 한글이 들어 있을 수 있고, 그 부분은 `wchar_t`인 채로 두면 안전하다.",
        "**글자로 바꾸는 자리는 로그뿐이다.** `std::format`의 `{}`에는 `path`를 바로 넣을 수 없어서(C++26부터 된다) "
        "`string()`이나 `generic_string()`으로 바꿔야 하고, 변환은 그 자리에서 일어난다.",
    ]),
    p("콘솔에 한글이 맞게 보이는지는 콘솔의 코드 페이지에 달린 또 다른 문제이고, 소스 파일의 인코딩과 컴파일러 옵션도 "
      "얽혀 있다. 이 강에서는 다루지 않는다. 에셋 이름을 ASCII로 지으면 그 문제들을 만나지 않고 지나갈 수 있다."),
], lead="텍스트 파일도 디스크에서는 바이트다. 어느 바이트가 어느 글자인지 정한 약속이 인코딩이다. 여기서는 문제를 "
        "피해 갈 만큼만 본다.")

ch6 = chapter(6, "설계", [
    h3("6.1", "파일 배치와 완성된 뒤의 모습"),
    tree("""
ClaudGL_Engine/
├── Assets/ +  #where this folder lives is the first decision of 6.3
│   ├── Text/
│   │   └── hello.txt +  #three lines of ASCII text, CRLF line ends, UTF-8 without BOM
│   └── Data/
│       └── ramp.bin +  #256 bytes: 00 01 02 ... FF
├── Engine/
│   └── Core/
│       ├── FileSystem.h +  #the declarations of 6.4
│       └── FileSystem.cpp +  #every std::ifstream of the engine lives here
├── Client/
│   └── main.cpp  #a temporary read test, reported through the logger
└── Debug/x64/Client.exe  #build output, not in the repository
"""),
    code(r"""
New-Item -ItemType Directory -Force Assets\Text, Assets\Data
[IO.File]::WriteAllBytes( "$PWD\Assets\Data\ramp.bin", [byte[]](0..255) )
Format-Hex Assets\Data\ramp.bin
""", lang="powershell", title="PowerShell, in the folder that will hold Assets/", tag="usage"),
    p("`ramp.bin`은 위치와 값이 같은 256바이트다. 어디가 잘못 읽혔는지 값만 보고 알 수 있고, `00`, `0A`, `0D`, `1A`가 "
      "모두 들어 있다. `$PWD`를 붙인 것은 PowerShell이 `cd`로 옮겨 다니는 위치와 PowerShell 프로세스의 작업 디렉터리가 "
      "별개이고, `[IO.File]`은 뒤쪽을 기준으로 상대 경로를 풀기 때문이다. 2장의 문제를 도구에서 다시 만난 것이다."),
    code(r"""
// after the logger is ready, before the engine starts
if ( /* FileSystem::Init() failed */ )
    return EXIT_FAILURE;    // reported already, or is reporting this branch's job? (lesson 1-4, 6.2)
LOG_INFO( "File", "asset root: {}", FileSystem::GetAssetRoot().generic_string() );

const std::filesystem::path text_path = FileSystem::GetAssetPath( "Text/hello.txt" );
// FileSystem::ReadText   -> log the size on disk, the characters read, the number of lines
const std::filesystem::path data_path = FileSystem::GetAssetPath( "Data/ramp.bin" );
// FileSystem::ReadBinary -> log the size, the first 8 bytes in hex, and whether byte i == i for all i
""", title="Client/main.cpp when this lesson is done (log macro names as in lesson 1-5, 6.1)", tag="usage"),

    h3("6.2", "에셋 루트를 찾는 네 가지 방법"),
    p("에셋 폴더의 절대 경로를 에셋 루트라고 부르자. 루트만 알면 나머지는 `루트 / 상대 경로`다. 문제는 루트를 "
      "어떻게 아느냐이고, 방법마다 통하는 범위가 다르다."),
    keep(table([33, 13, 13, 15, 26], ["방법", "IDE에서", "더블클릭", "다른 폴더에서", "폴더째 다른 PC로 옮기면"], [
        ["**A** 작업 디렉터리에 맡긴다", "설정한 PC만", "×", "×", "실행하는 사람이 폴더를 맞춰야 한다"],
        ["**B** 실행 파일의 폴더에서 위로 올라가며 찾는다", "○", "○", "○", "○ (에셋이 그 폴더나 위쪽에 있으면)"],
        ["**C** 빌드할 때 경로를 코드에 넣는다", "○", "○", "○", "× (빌드한 PC의 경로다)"],
        ["**D** 빌드한 뒤 실행 파일 옆으로 복사한다", "○", "○", "○", "○"],
    ], cell_cls=["lab", "c", "c", "c", ""], compact=True)),
    FIG_WALK.render("방법 **B**의 그림. 실행 파일의 폴더에서 출발해 한 칸씩 올라가며 묻는다. 폴더 이름은 예시다."),
    keep(table([8, 40, 52], ["", "드는 것", "내주는 것"], [
        ["**A**", "코드는 없다. 디버깅의 작업 디렉터리를 에셋 폴더의 부모로 바꾼다 (2.2절)",
         "설정이 `.vcxproj.user`에 있어 저장소로 가지 않는다. IDE 밖에서 실행하면 통하지 않는다"],
        ["**B**", "운영체제에 묻는 호출 하나(2.3절)와 올라가는 반복",
         "이름만 보고 찾으면 위쪽의 엉뚱한 `Assets`를 잡을 수 있다. 실행 파일만 저장소 밖으로 옮기면 못 찾는다"],
        ["**C**", "프로젝트 설정의 전처리기 정의 한 줄 (아래)",
         "저장소 폴더를 옮기면 다시 빌드해야 한다. 실행 파일 안에 개발 PC의 폴더 이름이 남는다"],
        ["**D**", "빌드 후 이벤트의 복사 명령 한 줄(아래)과, 실행 파일의 폴더를 아는 방법",
         "에셋이 두 벌이 된다. 에셋만 고치고 실행하면 빌드가 일어나지 않아 복사도 일어나지 않는다. 지운 파일이 복사본에 남는다"],
    ], cell_cls=["c", "", ""], compact=True)),
    code(r"""
ENGINE_ASSET_ROOT=R"($(SolutionDir)Assets)"
xcopy "$(SolutionDir)Assets" "$(OutDir)Assets" /E /I /Y /D
""", lang="text", title="line 1: a preprocessor definition (C)   line 2: a post-build command (D)", tag="syntax"),
    p("첫 줄은 그 매크로를 쓰는 `.cpp`가 속한 프로젝트의 C/C++ → 전처리기 → 전처리기 정의에 더한다(이름은 예시). "
      "원시 문자열 리터럴 `R\"( … )\"`는 안의 `\\`를 이스케이프로 읽지 않는다. 보통 문자열로 적으면 경로의 `\\`가 "
      "이스케이프의 시작으로 읽힌다. 둘째 줄은 Client 프로젝트의 빌드 이벤트 → 빌드 후 이벤트 → 명령줄에 적는다. "
      "`/E`는 하위 폴더까지, `/I`는 대상을 폴더로, `/Y`는 묻지 않고 덮어쓰기, `/D`는 더 새로운 파일만 복사한다는 "
      "뜻이다. 두 줄 모두 빌드해서 확인하지는 않았다. 언리얼은 둘을 섞어 쓴다. 에디터는 프로젝트 폴더의 `Content/`를 "
      "그 자리에서 읽고(B에 가깝다), 패키징할 때는 에셋을 묶어 실행 파일과 함께 내보낸다(D)."),

    keep(h3("6.3", "결정할 것"),
    table([21, 37, 42], ["결정", "선택지", "따져 볼 것"], [
        ["`Assets/`를 두는 곳", "저장소 폴더 바로 아래 (이 자료의 그림) / `Client/` 아래 / 실행 파일 옆",
         "엔진이 쓸 기본 셰이더와 게임의 에셋이 같은 폴더에 사는가. 고른 자리가 둘째 결정의 난이도를 바꾼다"],
        ["루트를 찾는 방법", "6.2절의 A / B / C / D, 또는 순서를 정해 여럿",
         "9장의 기준은 세 가지 실행 방법을 모두 요구한다. 여럿을 쓰면 어느 것이 통했는지 로그에 남는가"],
        ["찾는 때와 부르는 곳", "시작할 때 한 번 (`main`, 또는 `GEngine::Init` 안) / 처음 필요할 때",
         "못 찾은 것을 언제 알게 되는가. 시작할 때인가, 한참 뒤 첫 파일을 읽을 때인가"],
        ["읽기가 실패를 알리는 모양", "1-6강에서 정한 규칙대로. 6.4절에 세 가지 모양이 있다",
         "이유는 누가 찍는가. 같은 실패가 두 번 찍히지 않는가 (1-4강 6.2절의 둘째 결정)"],
        ["바이트의 타입", "`char` / `unsigned char`(`byte`) / `std::byte`", "4.3절의 표. 받아 쓸 쪽(2-5강의 이미지 읽기)은 어떤 타입을 원하는가"],
        ["`ReadText`의 모드와 다듬기", "텍스트 모드 / 바이너리 모드로 읽고 그대로 / 읽은 뒤 `\\r`과 BOM을 뗀다",
         "4.2절과 5.2절. 다듬는 일은 읽는 함수의 몫인가, 받아 쓰는 쪽의 몫인가"],
        ["로그 파일을 두는 곳", "작업 디렉터리 (지금) / 실행 파일 옆 / 따로 정한 폴더",
         "Logger는 엔진보다 먼저 켜진다 (1-5강 6.2절). 경로를 알려면 무엇이 먼저 준비되어야 하는가"],
        ["유틸리티의 모양", "이름 공간의 자유 함수 (6.4절의 스케치) / `GLogger` 같은 싱글턴 클래스",
         "들고 있을 상태는 에셋 루트 하나다. 그 값은 어디에 살고 누가 채우는가"],
    ], cell_cls=["lab", "", ""], compact=True)),
    box("decide", None,
        "여덟 가지에 정답은 없다. 미션 전에 행마다 하나를 고르고 이유를 한 줄씩 적는다. 1-6강에서 쓴 오류 정책 문서에 "
        "이어 적으면 된다. 6.1절의 그림은 첫째에서, 6.4절의 스케치는 여덟째에서 한쪽을 골라 그렸다. 그대로 가도 되고 바꿔도 된다."),

    h3("6.4", "선언 스케치"),
    p("읽는 함수가 실패를 어떻게 알릴지는 1-6강에서 정한 규칙을 따른다. 같은 함수가 규칙에 따라 아래 셋 가운데 "
      "하나의 모양이 된다 (1-6강 5.1절)."),
    code(r"""
// "path" stands for std::filesystem::path
[[nodiscard]] bool                        ReadText( const path& file, std::string& out_text );
[[nodiscard]] std::optional<std::string>  ReadText( const path& file );
              std::string                 ReadText( const path& file );     // throws on failure
""", title="one job, three shapes: return value, optional, exception", tag="syntax"),
    code(r"""
#pragma once
// Which standard headers does this file use directly? Does <Windows.h> belong here or in the .cpp?

namespace FileSystem
{
    // RESULT is not a type. Write the shape your error policy gives (the three lines above).

    // Finds the asset root once and remembers it. Which way of 6.2? What happens when it is not found?
    /* RESULT */ Init();

    // Calling these before Init() has succeeded: a bug or a failure? (lesson 1-6, 2.1)
    const std::filesystem::path& GetAssetRoot();
    std::filesystem::path        GetAssetPath( const std::filesystem::path& relative_path );
    // What if relative_path is absolute, or starts with a slash? (3.1)

    // The whole file at once. Which open mode for text? Is a BOM kept or skipped? (4.2, 5.2)
    /* RESULT with std::string */       ReadText( const std::filesystem::path& file );
    /* RESULT with a vector of bytes */ ReadBinary( const std::filesystem::path& file );
}
// In FileSystem.cpp only: where the asset root lives between calls, and the one function that asks
// the operating system where the executable is (2.3).
""", title="Engine/Core/FileSystem.h", tag="sketch"),
    p("`Shutdown`이 없는 것은 놓을 자원이 없어서다. 파일은 읽는 함수 안에서 열리고 그 함수가 끝나기 전에 닫힌다. "
      "이름과 인자는 뒤의 자료가 그대로 부른다. 2-4강은 `GetAssetPath`와 `ReadText`로 셰이더를 읽는다."),
    layers([
        ("CLIENT", [("main.cpp", "에셋의 상대 경로만 안다")]),
        ("ENGINE CORE", [("FileSystem", "루트를 찾고, 통째로 읽는다", "accent"), ("GLogger", "결과와 실패를 적는다")]),
        ("표준 · 플랫폼", [("<filesystem> · <fstream>", "경로와 스트림"), ("Win32", "실행 파일의 위치", "dark")]),
    ], "`<fstream>`과 Win32 호출은 `FileSystem.cpp` 안에만 둔다. 그 위의 코드는 `path`와 읽은 결과만 주고받는다."),

    keep(h3("6.5", "이 강에서 하지 않는 것"),
    table([30, 70], ["미루는 것", "이유"], [
        ["파일의 내용 해석", "셰이더는 2-4강, 이미지는 2-5강, OBJ는 4-3강이다. 여기서는 바이트를 메모리로 올리는 데까지다"],
        ["같은 파일을 두 번 읽지 않기", "캐시는 3-5강(Resource Manager)이다"],
        ["파일 쓰기, 폴더 훑기", "로그 말고는 아직 쓸 것이 없다. `directory_iterator`도 필요해지는 강에서 꺼낸다"],
        ["묶음 파일과 비동기 읽기", "에셋을 한 파일로 묶거나 다른 스레드에서 읽는 일은 이 강의의 범위 밖이다"],
    ], cell_cls=["lab", ""], compact=True)),
], lead="새로 만드는 것은 폴더 하나와 파일 둘이다. 코드보다 먼저 정할 것이 있다. 에셋 폴더를 어디에 두고, 엔진이 "
        "그 폴더를 어떻게 찾는가.")

ch7 = chapter(7, "구현 미션", [
    steps([
        ("작업 디렉터리를 세 번 찍는다",
         "`main`의 맨 앞에서 작업 디렉터리를 로그로 한 줄 찍는다. 같은 `Client.exe`를 세 가지로 실행한다. IDE에서, "
         "탐색기에서 더블클릭해서, 터미널에서 다른 폴더에 선 채로다. 실행마다 찍힌 값과 로그 파일이 생긴 폴더를 적는다. "
         "**통과:** 세 번 모두 그 줄이 찍히고, 세 값과 로그 파일의 세 자리가 적혀 있다.",
         ["`path`는 로그 매크로의 `{}`에 바로 들어가지 않는다 (5.3절)."]),
        ("에셋 폴더와 시험 파일 둘을 만든다",
         "6.3절의 첫째 결정으로 고른 자리에 `Assets/Text/hello.txt`와 `Assets/Data/ramp.bin`을 만든다 (6.1절). "
         "`hello.txt`는 ASCII 글자 세 줄이고 줄 끝은 CRLF, BOM은 없다. `ramp.bin`은 `00`부터 `FF`까지 차례로 든 "
         "256바이트다. **통과:** 16진수로 보면 `hello.txt`는 `EF BB BF`로 시작하지 않고 줄마다 `0D 0A`로 끝나며, "
         "`ramp.bin`은 `00`에서 `FF`까지 이어진다. `git status -u`에 두 파일이 보인다.",
         ["16진수로 보는 명령은 `Format-Hex`다 (5.2절의 예시). `git status`는 `-u`를 붙여야 새 폴더 안의 파일을 하나씩 "
          "보여 준다. 보이지 않는 파일이 있으면 8장의 마지막 줄을 본다."]),
        ("상대 경로로 열어 본다",
         "`main`에서 상대 경로 `\"Assets/Text/hello.txt\"`를 `std::ifstream`에 그대로 주어 열고, 열렸는지를 로그로 "
         "찍는다. 1단계의 세 방법으로 실행해 결과를 적는다. 이 코드는 8단계에서 지운다. **통과:** 세 번 모두 열렸는지가 "
         "찍히고, 세 결과가 1단계의 세 작업 디렉터리 옆에 적혀 있다.",
         ["열리지 않았을 때 그 경로를 `absolute()`로 바꿔 찍으면 찾아간 곳이 보인다 (3.3절)."]),
        ("에셋 루트를 찾는다",
         "`FileSystem.h`와 `.cpp`를 Engine 프로젝트에 더하고 6.4절의 `Init`, `GetAssetRoot`, `GetAssetPath`를 만든다. "
         "`Init`은 에셋 루트를 찾아 기억하고, 찾지 못하면 실패로 알린다. 찾은 루트는 절대 경로로 로그에 찍는다. 찾는 "
         "방법은 6.3절의 둘째 결정이고, 찾는 때와 부르는 곳은 셋째 결정이다. **통과:** 세 방법으로 실행하면 작업 "
         "디렉터리 줄은 달라도 에셋 루트 줄은 세 번 모두 같은 절대 경로다.",
         ["실행 파일의 위치를 쓴다면 2.3절의 카드를, 위로 올라간다면 3.2절 예시의 넷째 줄을 본다.",
          "`<Windows.h>`는 `.cpp` 하나에만 둔다 (1-5강 8장의 두 줄). 못 찾은 것이 버그가 아니라 실패인 까닭은 "
          "1-6강 2.1절에 있다."]),
        ("텍스트 파일을 통째로 읽는다",
         "`ReadText`를 만든다. 파일 하나를 통째로 읽어 `std::string`으로 준다. `main`에서 `GetAssetPath`로 얻은 "
         "`hello.txt`의 경로를 읽고 디스크의 크기, 읽은 글자 수, 줄 수를 찍는다. 없는 파일을 주면 실패를 알리고, 찾아간 "
         "절대 경로를 로그에 남긴다. 여는 모드와 다듬기는 6.3절의 여섯째 결정이고, 실패를 알리는 모양은 넷째 결정이다. "
         "**통과:** 크기가 탐색기의 속성에 보이는 값과 같고 줄 수가 3이다. 없는 이름을 주면 실패가 전해지고 그 절대 "
         "경로가 찍힌다.",
         ["읽는 방법은 4.3절의 표에서 고른다. 크기와 글자 수가 다르면 4.2절이다."]),
        ("바이너리 파일을 통째로 읽는다",
         "`ReadBinary`를 만든다. 파일의 바이트 전체를 하나도 바꾸지 않고 읽어 바이트의 `std::vector`로 준다. 바이트의 "
         "타입은 6.3절의 다섯째 결정이다. `main`에서 `ramp.bin`을 읽고 크기, 처음 8바이트의 16진수, 모든 바이트가 자기 "
         "위치와 같은 값인지를 찍는다. **통과:** 256바이트, `00 01 02 03 04 05 06 07`, 모두 같다는 결과가 찍힌다. 세 "
         "방법으로 실행해도 5단계와 이 단계의 줄이 똑같다.",
         ["바이트를 찍는 함수는 `std::span`으로 받게 만든다. 앞의 8개만 넘기는 방법이 4.4절에 있다.",
          "16진수 두 자리는 1-5강 4.1절 표의 두 줄을 합치면 된다."]),
        ("일부러 깨뜨린다",
         "하나씩 해 보고 결과를 적은 뒤 되돌린다. (가) `ramp.bin`을 `std::ios::binary` 없이 읽는다. (나) `hello.txt`를 "
         "BOM이 붙는 UTF-8로 저장한다. (다) `Assets`의 이름을 바꾼다. (라) `Client.exe`만 바탕 화면에 복사해 실행한다. "
         "**통과:** 네 결과가 적혀 있다. (다)에서는 못 찾은 이유가 로그에 남고, 시작할 때 찾기로 했다면 종료 코드가 "
         "0이 아니다. 넷을 되돌린 뒤에는 5·6단계의 출력이 그대로 다시 나온다.",
         ["(가)에서 읽힌 바이트 수를 16진수로 바꿔 본다. (다)와 (라)에서는 로그의 마지막 줄과 종료 코드를 본다."]),
        ("정리하고 묶는다",
         "3단계의 임시 코드를 지운다. 로그 파일의 자리를 6.3절의 일곱째 결정대로 맞춘다. 여덟 결정과 이유, 7단계의 네 "
         "결과가 적혀 있는지 본 뒤 9장의 기준을 확인하고 커밋 하나로 묶는다. **통과:** `Engine/`과 `Client/`에서 "
         "`ifstream`을 검색하면 `FileSystem.cpp` 한 파일만 나오고, 9장의 여섯 줄이 모두 맞다."),
    ]),
], lead="한 단계가 끝날 때마다 빌드해서 눈으로 확인한다. 단계마다 “통과”에 적힌 것이 보이면 다음으로 간다. 힌트는 "
        "막혔을 때 위에서부터 하나씩만 본다. 무엇을 하라는 것인지 그래도 분명하지 않으면 맨 뒤 13장에 단계별로 "
        "풀어 적은 목록이 있다.", pb=True)

ch8 = chapter(8, "흔한 함정", [
    table([30, 42, 28], ["증상", "원인", "확인 방법"], [
        ["IDE에서는 파일을 찾는데 실행 파일을 직접 띄우면 못 찾는다", "상대 경로가 작업 디렉터리 기준으로 풀렸다", "`current_path()`를 찍는다 (2장)"],
        ["읽은 글자 수가 파일 크기보다 작고 문자열 끝에 `\\0`이 남아 있다",
         "텍스트 모드로 열고 `file_size`만큼 읽으라고 했다. `0D 0A`가 한 글자가 되어 모자란다", "`gcount()`와 크기를 나란히 찍는다 (4.3절)"],
        ["바이너리 파일이 앞부분만 읽힌다", "`std::ios::binary`를 빼먹었다. `1A`에서 멈췄다", "읽은 크기와 `file_size`를 비교한다 (4.2절)"],
        ["첫 줄 앞에 모르는 글자 셋이 있다", "파일이 BOM으로 시작한다", "`Format-Hex`로 처음 세 바이트를 본다"],
        ["`path`를 넘긴 로그 호출이 컴파일되지 않는다", "C++20의 `std::format`은 `path`를 모른다", "`generic_string()` 등으로 바꿔 넘긴다 (5.3절)"],
        ["`byte`가 모호하다는 컴파일 오류 (C2872)", "`using namespace std;`가 있어 `std::byte`와 `Engine/framework.h:25`의 `byte`가 부딪힌다",
         "그 `using` 줄을 지운다"],
        ["다른 PC에서 받은 저장소에 에셋 파일이 없다",
         "`.gitignore`가 걸렀다. `*.obj`(79행)는 OBJ 모델도 거르고, `[Bb]in/`(31행)은 `Bin`이라는 폴더를 통째로 거른다",
         "`git check-ignore -v <경로>`"],
    ], compact=True),
], lead="증상에서 거꾸로 찾는 표다.")

ch9 = chapter(9, "완료 기준", [
    checklist([
        "IDE에서, `Client.exe`를 더블클릭해서, 다른 폴더의 터미널에서 실행해도 로그에 같은 에셋 루트가 절대 경로로 찍힌다.",
        "세 경우 모두 `hello.txt`와 `ramp.bin`의 크기와 내용이 똑같이 찍힌다. 크기는 탐색기의 속성에 보이는 값과 같다.",
        "없는 파일을 읽으라고 하면 1-6강에서 정한 방식대로 실패가 전해지고, 찾아간 절대 경로가 로그에 남는다.",
        "`Assets` 폴더의 이름을 바꾸고 실행하면 이유가 로그에 남는다. 시작할 때 찾기로 했다면 종료 코드가 0이 아니다.",
        "`Engine/`과 `Client/`에서 `ifstream`을 검색하면 `FileSystem.cpp` 한 파일만 나온다.",
        "미션 7의 네 가지 결과와 6.3절의 여덟 가지 결정이 이유와 함께 적혀 있고, 커밋 하나로 묶였다.",
    ]),
    console(Raw(
        '<span class="dim">[14:02:07.101]</span> <span class="ok">[Info ]</span> [File ] working directory: '
        "C:/Dev/ClaudGL/Client\n"
        '<span class="dim">[14:02:07.102]</span> <span class="ok">[Info ]</span> [File ] asset root: C:/Dev/ClaudGL/Assets\n'
        '<span class="dim">[14:02:07.104]</span> <span class="ok">[Info ]</span> [File ] Text/hello.txt: 46 bytes on disk, '
        "43 characters, 3 lines\n"
        '<span class="dim">[14:02:07.105]</span> <span class="ok">[Info ]</span> [File ] Data/ramp.bin: 256 bytes, '
        "first 8: 00 01 02 03 04 05 06 07, ramp ok\n"
        '<span class="dim">--- the same Client.exe, started by a double click ---</span>\n'
        '<span class="dim">[14:05:31.440]</span> <span class="ok">[Info ]</span> [File ] working directory: '
        '<span class="warn">C:/Dev/ClaudGL/Debug/x64</span>\n'
        '<span class="dim">[14:05:31.441]</span> <span class="ok">[Info ]</span> [File ] asset root: C:/Dev/ClaudGL/Assets'
    ), title="기대하는 출력 (형식, 문구, 숫자는 예시. 텍스트 모드로 읽었다면 글자 수가 크기보다 줄 수만큼 작다)"),
], lead="전부 눈이나 검색으로 확인할 수 있는 조건이다. 작업 디렉터리가 달라져도 그 아래 줄들은 같아야 한다.")

ch10 = chapter(10, "생각해 볼 질문", [
    exgroup("A", "코드를 쓰지 않고 답하시오", "한두 문장으로, 이유까지"),
    qlist([
        "에셋 폴더를 `Client/Assets/`에 두고 `\"Assets/Text/hello.txt\"`로 열었다. Visual Studio에서는 열리는데 "
        "`Client.exe`를 더블클릭하면 열리지 않는다. 두 실행에서 무엇이 달랐는가?",
        "프로젝트 속성에서 작업 디렉터리를 고쳐 위 문제를 풀었다. 이 저장소를 다른 PC에서 받아 빌드하고 F5를 누르면 "
        "어떻게 되는가? 그 PC에서 실행 파일을 더블클릭하면?",
        "에셋 루트가 `C:/Dev/ClaudGL/Assets`일 때 `root / \"/Shaders/basic.vert\"`는 어떤 경로가 되는가? 왜 그런가?",
        "줄이 10개이고 줄 끝이 CRLF인 300바이트 텍스트 파일을 텍스트 모드로 열어, 0으로 채운 300글자 버퍼에 300글자를 "
        "읽으라고 했다. `gcount()`는 얼마인가? 스트림의 상태와 버퍼의 마지막 10글자는?",
        "`ramp.bin`을 텍스트 모드로 읽었더니 26바이트가 읽혔다. 왜 26인가? `0A`와 `0D`도 들어 있는데 그 둘은 왜 "
        "영향을 주지 않았는가?",
        "`ReadBinary`가 준 `std::vector`로 `std::span`을 만들어 멤버 변수에 넣어 두었다. 그 뒤 벡터에 `push_back`을 "
        "했다. 그 `span`을 쓰면 어떻게 되는가?",
        "`Init`보다 먼저 `GetAssetRoot()`를 불렀다. 또 다른 날에는 `Assets` 폴더가 없어서 `Init`이 루트를 찾지 못했다. "
        "둘은 각각 버그인가 실패인가? 각각 무엇으로 다루는가?",
    ], lines=2),
], lead="답을 보기 전에 소리 내어 설명해 본다. 막히는 문항이 다시 읽을 장이다.", pb=True)

ch11 = chapter(11, "해설", [
    answers("질문 A", [
        ("작업 디렉터리가 달랐다.",
         "Visual Studio는 프로젝트 폴더 `Client/`를 주어서 `Client/Assets/…`가 맞았다. 탐색기는 실행 파일이 있는 "
         "`Debug/x64/`를 주어서 `Debug/x64/Assets/…`를 찾았다. 코드의 경로는 같고 출발점이 달랐다. (1.1절, 2.2절)"),
        ("F5에서도 다시 열리지 않는다. 더블클릭은 처음부터 풀린 적이 없다.",
         "속성 창의 값은 `.vcxproj.user`에 저장되고 `.gitignore`가 그 파일을 올리지 않는다. 새 PC는 기본값으로 "
         "돌아간다. 그리고 이 설정은 IDE가 실행할 때만 쓰인다. (2.2절)"),
        ("`C:/Shaders/basic.vert`가 된다.",
         "`/` 연산자는 오른쪽이 루트 디렉터리로 시작하면 왼쪽에서 드라이브만 남기고 폴더를 버린다. 에셋 경로를 "
         "바깥에서 받는다면 `GetAssetPath`가 이 경우를 어떻게 할지 정해야 한다. (3.1절)"),
        ("`gcount()`는 290이다. `eofbit`와 `failbit`가 서고, 마지막 10글자는 0인 채로 남는다.",
         "텍스트 모드가 `0D 0A` 열 쌍을 열 글자로 줄여서 읽을 수 있는 글자가 290뿐이다. 300을 채우기 전에 파일이 "
         "끝났으므로 실패 상태가 된다. (4.2절, 4.3절)"),
        ("27번째 바이트가 `1A`이고, 텍스트 모드는 그 값을 파일의 끝으로 여긴다.",
         "그 앞의 `00` 〜 `19` 스물여섯 개만 읽혔다. `0A`와 `0D`는 붙어 있지 않아서 줄어들지 않았다. 텍스트 모드가 "
         "줄이는 것은 `0D 0A`가 이 순서로 붙어 있을 때뿐이다. (4.2절)"),
        ("댕글링이 될 수 있다. 그대로 쓰면 정의되지 않은 동작이다.",
         "`span`은 주소와 개수만 든다. `push_back`으로 벡터가 메모리를 새로 잡으면 옛 주소는 이미 놓인 메모리다. "
         "빌린 것은 오래 들고 있지 않는다. (4.4절, 1-4강 5.2절)"),
        ("앞은 버그이고 뒤는 실패다.",
         "`Init` 전에 부른 것은 코드의 순서가 틀린 것이므로 전제 조건을 assert로 적는다. 폴더가 없는 것은 맞게 쓴 "
         "프로그램에서도 일어나므로 1-6강에서 정한 방식으로 알린다. (1-6강 2.1절, 2.2절)"),
    ]),
])

# The glossary shares a page with the answers, so it is built with a compact table
# (glossary_chapter() of the engine uses the roomier one).
_TERMS = [
    ("작업 디렉터리", "working directory", "프로세스마다 하나 있는, 상대 경로의 출발점이 되는 폴더"),
    ("상대 경로 · 절대 경로", "relative / absolute path", "작업 디렉터리에서 센 경로와, 드라이브부터 다 적은 경로"),
    ("에셋 루트", "asset root", "에셋 폴더의 절대 경로. 에셋의 상대 경로를 여기에 잇는다"),
    ("텍스트 모드", "text mode", "읽고 쓸 때 C 런타임이 줄 끝을 바꿔 주는 방식"),
    ("바이너리 모드", "binary mode", "바이트를 아무것도 바꾸지 않고 읽고 쓰는 방식"),
    ("CRLF", "carriage return, line feed", "`0D 0A` 두 바이트로 된 줄 끝. Windows의 텍스트 파일이 쓴다"),
    ("span", "span (C++20)", "연속된 원소의 한 구간을 가리키는 주소와 개수. 소유하지 않는다"),
    ("인코딩", "encoding", "글자를 바이트로 적는 약속. UTF-8, UTF-16, CP949"),
    ("BOM", "byte order mark", "파일 맨 앞에 붙는 인코딩 표식. UTF-8에서는 `EF BB BF`"),
    ("코드 페이지", "code page", "Windows가 `char` 문자열을 해석할 때 쓰는 인코딩의 번호"),
]
ch12 = chapter(12, "용어집", [
    table([22, 26, 52], ["용어", "원어·식별자", "뜻"], sorted(_TERMS, key=lambda t: t[0].lower()),
          cell_cls=["lab", "", ""], compact=True),
])


def todo(mission: str, rows: list) -> Raw:
    """One mission of the task list: a heading and a small table kept on one page."""
    return keep(h4(mission),
                table([6, 54, 40], ["", "할 일", "됐는지 보는 법"], rows, cell_cls=["num", "", ""], compact=True))


ch13 = chapter(13, "할 일 목록", [
    keep(h3("13.1", "결정이 막히면"),
    p("6.3절의 여덟 가지를 고르지 못해 미션이 멈출 때 쓰는 기본 선택이다. 정답이 아니라 이 자료의 스케치와 사용 "
      "예에서 가장 덜 벗어나고 나중에 바꾸기 쉬운 쪽이다. 다른 선택을 해도 미션의 “통과”만 맞으면 된다."),
    table([28, 72], ["결정", "막혔을 때의 기본 선택"], [
        ["`Assets/`를 두는 곳", "저장소 폴더 바로 아래. 6.1절의 배치와 이 자료의 그림이 이 자리다"],
        ["루트를 찾는 방법", "**B** 하나. 실행 파일의 폴더에서 위로 올라가며 `Assets`를 찾는다. 프로젝트 설정은 고치지 않는다"],
        ["찾는 때와 부르는 곳", "시작할 때 한 번. `main`이 Logger를 켠 다음, 엔진을 시작하기 전에 부른다 (6.1절의 사용 예)"],
        ["읽기가 실패를 알리는 모양", "1-6강에서 정한 규칙 그대로. 반환값으로 알리기로 했다면 6.4절의 세 모양 가운데 첫째"
                              "(`bool`과 출력 인자)다. 이유와 찾아간 경로는 읽는 함수가 찍는다"],
        ["바이트의 타입", "`unsigned char`. `Engine/framework.h`에 이미 있는 별칭 `byte`로 적는다"],
        ["`ReadText`의 모드와 다듬기", "바이너리 모드로 읽고 그대로 준다. `\\r`과 BOM을 떼는 일은 받아 쓰는 쪽이 생길 때 다시 정한다"],
        ["로그 파일을 두는 곳", "지금처럼 작업 디렉터리. Logger의 코드는 고치지 않는다"],
        ["유틸리티의 모양", "이름 공간의 자유 함수. 6.4절의 스케치 그대로다"],
    ], cell_cls=["lab", ""], compact=True)),

    h3("13.2", "미션별 할 일"),
    todo("미션 1 — 작업 디렉터리를 세 번 찍는다", [
        ["1", "`main`의 맨 앞에서 작업 디렉터리를 로그로 한 줄 찍는다", "실행하면 그 줄이 보인다"],
        ["2", "같은 `Client.exe`를 세 가지로 실행한다. IDE에서, 탐색기에서 더블클릭해서, 터미널에서 다른 폴더에 선 채로다",
         "찍힌 값 셋이 적혀 있다"],
        ["3", "실행마다 로그 파일이 어느 폴더에 생겼는지 찾는다", "세 자리가 세 값 옆에 적혀 있다"],
    ]),
    todo("미션 2 — 에셋 폴더와 시험 파일 둘을 만든다", [
        ["1", "6.3절의 첫째 결정으로 고른 자리에 `Assets/Text/`와 `Assets/Data/`를 만든다", "탐색기에 두 폴더가 보인다"],
        ["2", "`Text/hello.txt`를 만든다. ASCII 글자 세 줄이고 줄 끝은 CRLF, BOM 없는 UTF-8이다",
         "`Format-Hex`의 출력이 `EF BB BF`로 시작하지 않고, 줄마다 `0D 0A`로 끝난다"],
        ["3", "`Data/ramp.bin`을 만든다. `00`부터 `FF`까지 차례로 든 256바이트다 (6.1절의 명령)",
         "`Format-Hex`의 출력이 `00`에서 `FF`까지 차례로 이어진다"],
        ["4", "git이 두 파일을 거르지 않는지 본다", "`git status -u`에 두 파일이 보인다"],
    ]),
    todo("미션 3 — 상대 경로로 열어 본다", [
        ["1", "`main`에서 상대 경로 `\"Assets/Text/hello.txt\"`를 `std::ifstream`에 그대로 주어 연다", "빌드된다"],
        ["2", "열렸는지 아닌지를 로그로 한 줄 찍는다", "실행하면 그 줄이 보인다"],
        ["3", "미션 1의 세 가지 방법으로 실행한다", "세 결과가 미션 1의 세 작업 디렉터리 옆에 적혀 있다"],
    ]),
    todo("미션 4 — 에셋 루트를 찾는다", [
        ["1", "`Engine/Core/FileSystem.h`와 `FileSystem.cpp`를 만들어 Engine 프로젝트에 더한다", "Engine 프로젝트에 두 파일이 보이고 빌드된다"],
        ["2", "`FileSystem::Init`이 에셋 루트를 찾아 기억한다. 찾는 방법은 6.3절의 둘째 결정이다",
         "`Init`의 끝에 건 중단점에서 기억한 값이 `Assets` 폴더의 절대 경로다"],
        ["3", "`GetAssetRoot`는 기억한 루트를 돌려주고, `GetAssetPath`는 루트에 상대 경로를 이은 경로를 돌려준다",
         "`GetAssetPath( \"Text/hello.txt\" )`의 결과가 `hello.txt`의 절대 경로다"],
        ["4", "루트를 찾지 못하면 실패로 알리고 이유를 로그에 남긴다. 시작할 때 찾기로 했다면 `main`이 0이 아닌 종료 코드로 끝난다",
         "`Assets`의 이름을 잠깐 바꿔 실행하면 이유가 찍힌다 (미션 7의 (다)에서 다시 본다)"],
        ["5", "`Init`을 부를 자리를 정해 부른다 (6.3절의 셋째 결정). 찾은 루트를 절대 경로로 로그에 찍는다", "로그에 에셋 루트 줄이 보인다"],
        ["6", "미션 1의 세 가지 방법으로 실행한다", "작업 디렉터리 줄은 달라도 에셋 루트 줄은 세 번 모두 같다"],
        ["7", "운영체제에 묻는 호출을 쓴다면 그 호출과 `<Windows.h>`를 `FileSystem.cpp` 안에만 둔다", "`FileSystem.h`에 `Windows.h`가 없다"],
    ]),
    todo("미션 5 — 텍스트 파일을 통째로 읽는다", [
        ["1", "`FileSystem::ReadText`를 만든다. 파일 하나를 통째로 읽어 `std::string`으로 준다. 여는 모드와 다듬기는 6.3절의 "
              "여섯째 결정이다", "빌드된다"],
        ["2", "`main`에서 `GetAssetPath`로 얻은 `hello.txt`의 경로를 `ReadText`로 읽는다", "중단점에서 본 문자열이 `hello.txt`의 내용이다"],
        ["3", "디스크의 크기, 읽은 글자 수, 줄 수를 로그로 찍는다", "크기가 탐색기의 속성에 보이는 값과 같고 줄 수가 3이다"],
        ["4", "없는 파일을 주었을 때 실패를 알린다. 알리는 모양은 6.3절의 넷째 결정이다",
         "없는 이름을 주면 부른 쪽에서 실패를 다루는 줄의 중단점에 걸린다"],
        ["5", "실패를 알릴 때 찾아간 절대 경로를 로그에 남긴다", "그 실행의 로그에 절대 경로가 보인다"],
    ]),
    todo("미션 6 — 바이너리 파일을 통째로 읽는다", [
        ["1", "`FileSystem::ReadBinary`를 만든다. 파일의 바이트 전체를 바꾸지 않고 읽어 바이트의 `std::vector`로 준다. "
              "바이트의 타입은 6.3절의 다섯째 결정이다", "빌드된다"],
        ["2", "`main`에서 `GetAssetPath`로 얻은 `ramp.bin`의 경로를 읽고 크기를 찍는다", "256이 찍힌다"],
        ["3", "바이트 묶음을 16진수 두 자리씩 찍는 함수를 만든다. 인자는 `std::span`으로 받는다",
         "앞의 8개만 넘기면 `00 01 02 03 04 05 06 07`이 찍힌다"],
        ["4", "모든 바이트가 자기 위치와 같은 값인지 확인해 결과를 찍는다", "같다는 결과가 찍힌다"],
        ["5", "미션 1의 세 가지 방법으로 실행한다", "`hello.txt`의 줄과 `ramp.bin`의 줄이 세 번 모두 같다"],
    ]),
    todo("미션 7 — 일부러 깨뜨린다", [
        ["1", "(가) `ramp.bin`을 `std::ios::binary` 없이 읽고, 읽힌 바이트 수를 적은 뒤 되돌린다", "되돌리면 다시 256이 찍힌다"],
        ["2", "(나) `hello.txt`를 BOM이 붙는 UTF-8로 저장해 실행하고, 달라진 것을 적은 뒤 BOM 없이 다시 저장한다",
         "`Format-Hex`의 출력이 다시 `EF BB BF`로 시작하지 않는다"],
        ["3", "(다) `Assets` 폴더의 이름을 바꿔 실행하고, 로그의 마지막 줄과 종료 코드를 적은 뒤 이름을 되돌린다",
         "이유가 로그에 남는다. 시작할 때 찾기로 했다면 종료 코드가 0이 아니다"],
        ["4", "(라) `Client.exe`만 바탕 화면에 복사해 실행하고, 로그의 마지막 줄과 종료 코드를 적은 뒤 복사본을 지운다",
         "결과가 적혀 있다"],
        ["5", "넷을 모두 되돌린 뒤 한 번 더 실행한다", "미션 5와 6의 출력이 그대로 다시 나온다"],
    ]),
    todo("미션 8 — 정리하고 묶는다", [
        ["1", "미션 3에서 `main`에 넣은 임시 코드를 지운다",
         "`Engine/`과 `Client/`에서 `ifstream`을 검색하면 `FileSystem.cpp` 한 파일만 나온다"],
        ["2", "로그 파일의 자리를 6.3절의 일곱째 결정대로 맞춘다. 지금 자리에 두기로 했다면 고칠 것이 없다",
         "실행하면 로그 파일이 고른 자리에 생긴다"],
        ["3", "6.3절의 여덟 결정과 이유, 미션 7의 네 결과가 적혀 있는지 본다", "빠진 줄이 없다"],
        ["4", "9장의 기준을 확인하고 커밋 하나로 묶는다", "9장의 여섯 줄이 모두 맞다"],
    ]),
], lead="미션의 문장만으로 무엇을 하라는 것인지 분명하지 않을 때 보는 목록이다. 미션마다 할 일을 한 줄씩 풀고, 됐는지 "
        "보는 법을 옆에 적었다. 어떻게 하는지는 적지 않았다. 그것은 2 〜 6장과 미션의 힌트에 있다.", pb=True)

if __name__ == "__main__":
    info = build(
        {"title": f"ClaudGL Engine {ME['id']} {ME['title']} v{ME['ver']}",
         "footer": f"ClaudGL Engine · {ME['id']} {ME['title']} · v{ME['ver']}"},
        COVER, [ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8, ch9, ch10, ch11, ch12, ch13], OUT_HTML,
    )
    pages = render(OUT_HTML, OUT_PDF)
    print(f"pdf: {OUT_PDF} ({pages} pages)")
    print(f"tables: {info['tables']}  diagrams: {info['diagrams']}  code blocks: {info['code_blocks']}")
    print(f"issues: {info['issues']}")
