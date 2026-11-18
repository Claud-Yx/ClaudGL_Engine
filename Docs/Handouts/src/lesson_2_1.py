"""Lesson 2-1 -- OpenGL as a state machine (first lesson of Part 2, mission-style handout).

The engine code this lesson builds on is written by the reader in lessons 1-1
to 1-6, so the handout points at it by function name, never by line number, and
uses the canonical names of the earlier handouts (GEngine::Init, cbUpdate,
GLogger, LOG_INFO, ASSERT). File:line is given only for library headers under
include/ (glad.h, glad.c, glfw3.h), read on READ_DATE.

Part 2 writes gl* calls directly and wraps nothing, so this handout shows no
helper classes. Lesson 1-7 (files and paths) is not needed here.

Version 2 (2026-11-19): same change as lesson 1-4 v4. Each mission step of
chapter 8 now states what must be done as plain statements and ends with a
"통과" (pass) condition, and a new last chapter 14 "할 일 목록" spells every
mission out as a task list with a way to check each task, plus a default choice
for each of the six decisions of 7.2 for when the reader is stuck. Chapters 1 to
13 keep their numbers; the eight mission steps keep their numbers and meaning.
The task list says what, never how, and does not point at wrapper classes.

Run:  python -I src/lesson_2_1.py      (from Docs/Handouts, with the handout venv)
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

ME = lesson("2-1")
OUT_PDF = ROOT / handout_name(ME["id"])
OUT_HTML = ROOT / "_build" / "lesson_2_1.html"

# Library headers (include/glad, include/GLFW) and project files were read on this day.
READ_DATE = "2026-11-18"

CHECK_HEADER = ["확인할 것", "볼 자리", "왜 보는가"]

COVER = cover(
    f"CLAUDGL ENGINE · PART {ME['part']} · {ME['id']} · v{ME['ver']}",
    Raw('gl<span class="ac">DebugMessage</span>Callback'),
    ME["title"],
    "삼각형을 그리기 전에, OpenGL이 일하는 방식과 틀렸을 때 듣는 통로를 갖춘다",
    [
        ("목표 결과물", "GL이 내는 오류와 경고가 시각과 레벨이 붙은 로그로 콘솔과 파일에 찍힌다. 시작할 때 드라이버 정보가 남는다"),
        ("핵심 개념", "컨텍스트와 상태 · 객체와 이름 · 바인드 · 오류 깃발 · 디버그 컨텍스트 · 디버그 콜백"),
        ("선수 지식", "1-1 〜 1-6강을 끝낸 네 코드. 특히 1-3강 4장(C 콜백)과 1-5강(Logger). 1-7강은 필요 없다"),
        ("예상 시간", f"읽기 1시간 + 구현 2시간 (계획서 기준 {ME['hours']}시간)"),
        ("건드릴 파일", "`Client/main.cpp`, `Engine/Core/EngineCore.h`·`.cpp`. 콜백을 둘 파일은 7.2절에서 정한다"),
        ("코드 기준", f"엔진 코드는 함수 이름으로 가리킨다. `include/`의 헤더 줄 번호는 {READ_DATE}의 파일 기준이다"),
    ],
    note=("읽는 법",
          "2 〜 4장은 OpenGL이 일하는 방식이고 5 〜 6장은 틀린 호출을 알아내는 도구다. 7장에서 결정할 것을 적은 뒤 8장의 "
          "미션을 순서대로 한다. 미션이 무엇을 하라는 것인지 분명하지 않으면 14장의 할 일 목록을 본다. 이 강부터 "
          "Part 2가 끝날 때까지 `gl*` 호출은 감싸지 않고 직접 쓴다. 코드 블록은 완성본이 아니다."),
    toc=["왜 필요한가", "컨텍스트: 상태와 객체가 사는 곳", "상태 기계", "객체, 이름, 바인드",
         "오류를 묻는 옛 방법: glGetError", "디버그 출력", "설계", "구현 미션", "흔한 함정", "완료 기준",
         "생각해 볼 질문", "해설", "용어집", "할 일 목록"],
)

# --------------------------------------------------------------------------
# figures
# --------------------------------------------------------------------------

def _panel(fig, x, title, sub, rows):
    """One group inside the context figure: a title, a small second line and name/value rows."""
    fig.box(x, 36, 146, 152, r=5)
    fig.text(x + 10, 55, title, kind="t", anchor="start", size=10.5)
    fig.text(x + 10, 70, sub, kind="s", anchor="start", size=9)
    fig.line((x + 10, 79), (x + 136, 79), kind="muted")
    for i, (name, value) in enumerate(rows):
        y = 99 + i * 22
        fig.text(x + 10, y, name, kind="mono", anchor="start", size=9)
        if value:
            fig.text(x + 136, y, value, kind="s", anchor="end", size=9)
    return fig


def _frame(fig, x, y, w, h, name, sub=None, kind="", mono=True):
    """Call-stack frame: a box with a name and an optional small second line."""
    fig.box(x, y, w, h, kind=kind)
    cx = x + w / 2
    name_kind = "mono" if mono else "t"
    if sub:
        fig.text(cx, y + h / 2 - 2.5, name, kind=name_kind, size=10.5)
        fig.text(cx, y + h / 2 + 11.5, sub, kind="s", size=9.5)
    else:
        fig.text(cx, y + h / 2 + 4, name, kind=name_kind, size=10.5)
    return fig


def _call(fig, i, title, sub, kind=""):
    """One call on the error-flag timeline."""
    x = 12 + i * 108
    fig.box(x, 24, 100, 42, kind=kind)
    light = " light" if kind == "dark" else ""
    fig.text(x + 50, 42, title, kind=("mono" + light) if kind == "dark" else "t", size=10)
    fig.text(x + 50, 57, sub, kind="s" + light, size=8.6)
    return fig


def _flag(fig, i, value, kind=""):
    """The recorded error code after call i."""
    x = 12 + i * 108
    fig.box(x, 96, 100, 26, kind=kind, r=4)
    fig.text(x + 50, 113, value, kind="mono", size=8.8)
    return fig


# 2 -- what one context holds, with the values it starts with.
FIG_CONTEXT = Fig(202)
FIG_CONTEXT.box(8, 6, 644, 190, kind="soft", r=8)
FIG_CONTEXT.text(22, 25, "OpenGL 컨텍스트 하나", kind="t", anchor="start", size=10.5)
FIG_CONTEXT.text(638, 25, "막 만들어졌을 때의 값 (일부)", kind="s", anchor="end", size=9.5)
_panel(FIG_CONTEXT, 20, "상태 값", "정해 두는 설정", [
    ("clear color", "0, 0, 0, 0"), ("viewport", "창 전체"), ("scissor box", "창 전체"), ("…", "수백 개"),
])
_panel(FIG_CONTEXT, 177, "스위치", "켜짐 또는 꺼짐", [
    ("GL_DEPTH_TEST", "꺼짐"), ("GL_BLEND", "꺼짐"), ("GL_SCISSOR_TEST", "꺼짐"), ("GL_DITHER", "켜짐"),
])
_panel(FIG_CONTEXT, 334, "바인딩 포인트", "지금 꽂힌 객체의 이름", [
    ("GL_ARRAY_BUFFER", "0"), ("GL_UNIFORM_BUFFER", "0"), ("GL_TEXTURE_2D", "0"), ("…", "0"),
])
_panel(FIG_CONTEXT, 491, "객체", "프로그램이 만드는 것", [
    ("버퍼", "없음"), ("텍스처", "없음"), ("셰이더 · 프로그램", "없음"), ("정점 배열", "없음"),
])

# 4.3 -- calls name a slot; the slot points at an object.
FIG_SLOTS = (
    Fig(196)
    .text(105, 14, "호출", kind="s", size=9.5)
    .text(340, 14, "바인딩 포인트 (슬롯)", kind="s", size=9.5)
    .text(575, 14, "버퍼 객체", kind="s", size=9.5)
    .box(10, 26, 190, 42)
    .text(105, 44, "glBufferData( GL_ARRAY_BUFFER, … )", kind="mono", size=9.5)
    .text(105, 59, "슬롯의 이름을 받는다", kind="s", size=9)
    .box(10, 112, 190, 42, kind="ghost")
    .text(105, 130, "glBindBuffer( GL_ARRAY_BUFFER, 3 )", kind="mono", size=9.5)
    .text(105, 145, "꽂힌 객체를 바꾼다", kind="s", size=9)
    .arrow((200, 44), (250, 44), kind="accent")
    .arrow((200, 133), (226, 133), (226, 57), (250, 57), kind="muted dash")
    .box(250, 28, 180, 38, kind="accent")
    .text(262, 51, "GL_ARRAY_BUFFER", kind="mono", anchor="start", size=9.5)
    .box(392, 35, 30, 24, kind="plain", r=3)
    .text(407, 52, "1", kind="mono", size=10)
    .box(250, 80, 180, 38)
    .text(262, 103, "GL_UNIFORM_BUFFER", kind="mono", anchor="start", size=9.5)
    .box(392, 87, 30, 24, kind="plain", r=3)
    .text(407, 104, "0", kind="mono", size=10)
    .box(250, 132, 180, 38, kind="ghost")
    .text(340, 155, "버퍼용 슬롯만 열 개가 넘는다", kind="s", size=9)
    .box(500, 26, 150, 38, "버퍼 1", "지금 고쳐지는 객체", kind="accent")
    .box(500, 78, 150, 38, "버퍼 2", kind="soft")
    .box(500, 130, 150, 38, "버퍼 3", kind="soft")
    .arrow((430, 44), (500, 44), kind="accent")
    .arrow((430, 58), (466, 58), (466, 149), (500, 149), kind="muted dash")
    .text(330, 189, "꽂혀 있지 않은 버퍼 2와 3은 지금 어느 호출로도 고쳐지지 않는다.", kind="s", size=9.5)
)

# 5.2 -- the error flag keeps the first code until somebody reads it.
FIG_ERRFLAG = Fig(152)
FIG_ERRFLAG.text(12, 15, "호출 (시간은 오른쪽으로 흐른다)", kind="s", anchor="start", size=9.5)
_call(FIG_ERRFLAG, 0, "호출 1", "성공")
_call(FIG_ERRFLAG, 1, "호출 2", "GL_INVALID_ENUM", kind="accent")
_call(FIG_ERRFLAG, 2, "호출 3", "성공")
_call(FIG_ERRFLAG, 3, "호출 4", "GL_INVALID_VALUE", kind="accent")
_call(FIG_ERRFLAG, 4, "호출 5", "성공")
_call(FIG_ERRFLAG, 5, "glGetError()", "여기서 처음 묻는다", kind="dark")
FIG_ERRFLAG.text(12, 88, "오류 깃발 (그 호출이 끝난 뒤)", kind="s", anchor="start", size=9.5)
_flag(FIG_ERRFLAG, 0, "NO_ERROR", kind="plain")
_flag(FIG_ERRFLAG, 1, "INVALID_ENUM", kind="accent")
_flag(FIG_ERRFLAG, 2, "INVALID_ENUM", kind="accent")
_flag(FIG_ERRFLAG, 3, "INVALID_ENUM", kind="accent")
_flag(FIG_ERRFLAG, 4, "INVALID_ENUM", kind="accent")
_flag(FIG_ERRFLAG, 5, "NO_ERROR", kind="plain")
FIG_ERRFLAG.text(386, 140, "둘째 오류는 깃발을 바꾸지 못한다", kind="accent", size=9)
FIG_ERRFLAG.text(648, 140, "INVALID_ENUM을 돌려주고 내린다", kind="s", anchor="end", size=9)

# 6.4 -- where the debugger stands when it stops inside the debug callback.
FIG_SYNC = Fig(180)
FIG_SYNC.text(20, 16, "동기 출력을 켰을 때", kind="t", anchor="start", size=10.5)
FIG_SYNC.text(350, 16, "껐을 때", kind="t", anchor="start", size=10.5)
FIG_SYNC.line((330, 6), (330, 176), kind="muted dash")
FIG_SYNC.arrow((22, 48), (56, 48), kind="accent")
_frame(FIG_SYNC, 60, 28, 250, 40, "cbGLDebugMessage( … )", "콜백 · 중단점이 선 곳", kind="accent")
_frame(FIG_SYNC, 60, 73, 250, 40, "그래픽 드라이버의 함수들", "이름 없는 칸이 몇 개 보인다", kind="soft", mono=False)
_frame(FIG_SYNC, 60, 118, 250, 40, "cbUpdate( float )", "틀린 gl* 호출이 적힌 줄")
FIG_SYNC.text(185, 173, "아래로 내려가면 틀린 호출에 닿는다", kind="s", size=9.5)
FIG_SYNC.arrow((352, 48), (386, 48), kind="accent")
_frame(FIG_SYNC, 390, 28, 250, 40, "cbGLDebugMessage( … )", "콜백 · 중단점이 선 곳", kind="accent")
_frame(FIG_SYNC, 390, 73, 250, 40, "그래픽 드라이버의 함수들", "드라이버가 만든 스레드일 수 있다", kind="soft", mono=False)
_frame(FIG_SYNC, 390, 118, 250, 40, "?", "내 코드의 칸이 없을 수 있다", kind="ghost")
FIG_SYNC.text(515, 173, "언제, 어느 스레드에서 불릴지 약속이 없다", kind="s", size=9.5)

# --------------------------------------------------------------------------

ch1 = chapter(1, "왜 필요한가", [
    h3("1.1", "지금까지 부른 GL 함수는 셋이다"),
    table([24, 20, 56], ["호출", "배운 곳", "한 일"], [
        ["`glClearColor`", "1-1강 5.3절", "지울 때 칠할 색을 컨텍스트에 적어 둔다. 화면은 바뀌지 않는다"],
        ["`glClear`", "1-1강 6장", "적어 둔 색으로 back buffer를 채운다"],
        ["`glViewport`", "1-2강 6장", "그림이 그려질 사각형을 컨텍스트에 적어 둔다"],
    ], cell_cls=["lab", "c", ""], compact=True),
    p("셋에는 공통점이 둘 있다. 어느 창에 대고 하는 일인지를 인자로 받지 않는다. 그리고 셋 중 둘은 무언가를 "
      "“적어 두기만” 하고, 실제 일은 다른 호출이 한다. 이 두 가지는 세 함수만의 버릇이 아니라 OpenGL 전체의 "
      "성질이다. 지금까지는 셋 다 틀리기 어려운 호출이라 그 성질을 몰라도 창이 떴다."),

    h3("1.2", "검은 화면은 이유를 말하지 않는다"),
    flow([
        ("버퍼", "데이터 올리기"),
        ("속성", "배치 알리기"),
        ("셰이더", "컴파일"),
        ("프로그램", "링크"),
        ("꽂기", "쓸 것을 고른다"),
        ("드로우", "그려라"),
        ("화면", "검다", "dark"),
    ], "2-2강에서 삼각형 하나가 나오기까지 지나는 칸이다. 어느 칸에서 틀려도 마지막 칸은 똑같이 검다."),
    p("2-2강에서 삼각형 하나를 그리려면 `gl*` 호출이 스무 개쯤 필요하다. 그 가운데 하나가 틀려도 OpenGL은 예외를 "
      "던지지 않고 프로그램을 멈추지도 않는다. 틀린 호출은 없던 일이 되고(5.1절) 그다음 호출들이 그대로 실행된다. "
      "보이는 것은 배경색뿐인 창이다. 틀린 호출은 두 종류이고 찾는 방법이 다르다."),
    table([30, 40, 30], ["틀린 종류", "예", "GL이 알려 주는가"], [
        ["규칙을 어긴 호출", "없는 상수를 넘겼다. 숫자가 범위 밖이다. 지금 상태에서는 할 수 없는 일이다",
         "알려 준다. 묻거나(5장), 들을 통로를 열어 두면(6장) 받는다"],
        ["규칙에는 맞지만 뜻한 것과 다른 호출", "다른 객체가 꽂혀 있었다. 켜 둔 스위치를 끄지 않았다",
         "알려 주지 않는다. GL이 보기에는 멀쩡한 호출이다"],
    ], cell_cls=["lab", "", ""]),
    p("앞의 것을 듣는 통로를 여는 일이 이 강의 결과물이다. 뒤의 것은 어떤 도구도 잡아 주지 않아서, OpenGL이 일하는 "
      "방식을 머릿속에 그릴 수 있어야 찾는다(2 〜 4장). 그래서 이 강이 삼각형보다 먼저 온다."),

    keep(h3("1.3", "네 코드에서 확인할 것"),
    p("미션의 첫 단계에서 아래 자리를 네 코드에서 찾아 적어 둔다. 함수 이름은 앞 강 자료의 이름이다."),
    table([32, 30, 38], CHECK_HEADER, [
        ["`gl`로 시작하는 호출이 지금 어디에 몇 개 있는가", "두 폴더에서 `gl[A-Z]`로 검색",
         "이 강의 출발점이다. Part 2 내내 이 목록이 길어진다 (7.4절)"],
        ["힌트를 적는 줄들, 그리고 GLAD가 끝난 바로 다음 줄", "`GEngine::Init`의 `glfwWindowHint` 호출과 `gladLoadGLLoader` 확인",
         "앞의 것은 디버그 컨텍스트를 요청할 수 있는 하나뿐인 자리이고, 뒤의 것은 `gl*`을 부를 수 있는 첫 자리다 (6장)"],
        ["한 번 할 일과 프레임마다 할 일을 적는 자리", "`main`에서 `Init`과 `Run()` 사이, 그리고 `cbUpdate`",
         "Part 2의 `gl*` 코드는 이 두 자리에 쓴다"],
        ["Logger의 최소 레벨과 flush 시점", "1-5강 2.2절, 6.2절의 셋째 결정",
         "GL의 알림을 낮은 레벨로 보내면 최소 레벨에 걸려 보이지 않을 수 있다"],
    ], cell_cls=["lab", "", ""], compact=True)),
], lead="지금까지 부른 `gl*` 함수는 셋뿐이고 셋 다 틀리기 어려웠다. 2-2강부터는 호출 수십 개가 순서대로 맞아야 "
        "삼각형 하나가 나온다. 그 전에 OpenGL이 일하는 방식과, 틀렸을 때 알려 주는 통로를 갖춘다.")

ch2 = chapter(2, "컨텍스트: 상태와 객체가 사는 곳", [
    FIG_CONTEXT.render("컨텍스트 안에 들어 있는 것. 왼쪽 세 칸이 상태이고(3장, 4.3절) 오른쪽 칸이 객체다(4장). `gl*` 호출은 "
                       "전부 이 상자 안의 무언가를 읽거나 바꾼다."),
    p("`gl*` 호출의 대상은 그 함수를 부른 스레드의 현재 컨텍스트다 (1-1강 5.1절). 컨텍스트는 `glfwCreateWindow`가 "
      "창과 함께 만들고 `glfwDestroyWindow`가 창과 함께 없앤다 (1-4강 4.2절). 창의 back buffer와 front buffer는 "
      "컨텍스트가 그리는 곳이고(1-2강 5.1절) 컨텍스트 안의 객체는 아니다."),

    h3("2.1", "컨텍스트가 정해 주는 세 가지"),
    ul([
        "**대상은 인자가 아니라 스레드가 정한다.** 현재 컨텍스트가 없는 스레드에서 `gl*` 함수를 부르면 무슨 일이 "
        "일어날지 정해져 있지 않다. 이 강의는 메인 스레드 하나에서만 `gl*`을 부른다.",
        "**객체의 수명은 컨텍스트의 수명을 넘지 못한다.** 컨텍스트가 사라지면 그 안의 객체도 함께 사라지고, 객체를 "
        "가리키던 숫자는 아무 뜻이 없어진다. 객체를 직접 지우려면 컨텍스트가 살아 있을 때 지워야 한다.",
        "**컨텍스트가 둘이면 상태도 두 벌이다.** 한쪽에서 바꾼 배경색은 다른 쪽에 보이지 않는다. 객체만은 "
        "`glfwCreateWindow`의 `share` 인자로 함께 쓰게 할 수 있다 (1-1강 4장). 이 강의는 컨텍스트 하나만 쓴다.",
    ]),

    h3("2.2", "누구의 OpenGL인가"),
    p("OpenGL은 문서로 된 약속이고, 그 약속을 실제 코드로 구현한 것은 그래픽 드라이버다 (1-1강 1장 그림의 맨 아래 칸). "
      "같은 호출이라도 드라이버에 따라 속도가 다르고, 내는 메시지의 문장이 다르고, 버그도 다르다. 그래서 프로그램은 "
      "시작할 때 “누가 구현한 어느 버전 위에서 돌고 있는가”를 로그에 남긴다."),
    fn("glGetString", "const GLubyte* glGetString(GLenum name);",
       "지금 컨텍스트를 구현한 드라이버가 자신을 소개하는 문자열을 돌려준다.",
       params=[("`name`", "무엇을 물을지 고르는 상수. `GL_VENDOR`(만든 회사), `GL_RENDERER`(그래픽 장치), "
                         "`GL_VERSION`(OpenGL 버전), `GL_SHADING_LANGUAGE_VERSION`(셰이더 언어 버전)")],
       returns="0으로 끝나는 문자열의 주소. 타입이 `const GLubyte*`, 곧 `const unsigned char*`라서"
               "(`include/glad/glad.h:95`) `const char*`를 받는 곳에 넘기려면 형 변환이 필요하다. 문자열은 GL의 것이라 "
               "해제하지 않는다",
       fails="`name`이 위 넷이 아니면 `GL_INVALID_ENUM` 오류를 내고 널 포인터를 돌려준다. 코어 프로필에서는 "
             "`GL_EXTENSIONS`도 그렇다. 확장 목록은 `glGetStringi`로 하나씩 읽는다 (`include/glad/glad.h:2325`)",
       notes=[("부르는 순서", "`gladLoadGLLoader()`가 성공한 뒤 (1-1강 5.2절)"),
              ("`GL_VERSION`의 모양", "`4.6.0`처럼 숫자로 시작하고, 그 뒤에 제조사가 덧붙인 글이 온다. 덧붙인 부분의 "
                                    "형식은 제조사마다 다르다"),
              ("선언된 곳", "`include/glad/glad.h:1636`. 상수 넷은 `:291` 〜 `:293`, `:558`")],
       lib="OpenGL"),
    box("ex", "예시: 네 줄이 찍힌 모습", [
        console(
            "GL_VENDOR                     NVIDIA Corporation\n"
            "GL_RENDERER                   NVIDIA GeForce RTX 3060/PCIe/SSE2\n"
            "GL_VERSION                    4.6.0 NVIDIA 551.86\n"
            "GL_SHADING_LANGUAGE_VERSION   4.60 NVIDIA",
            title="출력 (값은 예시. PC마다 다르다)"),
        p("내장 그래픽으로 돌리면 첫 줄이 `Intel`로, 셋째 줄이 `4.6.0 - Build 31.0.101.2125` 같은 모양으로 바뀐다. "
          "그래픽 장치가 둘인 노트북에서는 둘째 줄이 “지금 어느 쪽에서 돌고 있는가”의 답이다. 다른 PC에서만 나는 "
          "문제를 좁힐 때 로그의 이 네 줄부터 본다."),
    ]),
    box("point", "glad.h의 선언을 읽는 법",
        "`glad.h`에는 함수 선언 대신 함수 포인터 타입, 그 타입의 변수, `#define`의 세 줄이 있다 (1-1강 3.1절). "
        "이 자료의 카드는 그 타입을 보통의 함수 선언 꼴로 옮겨 적고, “선언된 곳”에는 타입이 정의된 줄을 적는다."),
    box("cs", None,
        "현재 컨텍스트는 스레드마다 하나씩 따로 있는 숨은 전역 변수다. 운영체제가 이런 변수를 위해 주는 장치가 스레드 "
        "지역 저장소(TLS)이고, C++에서는 `thread_local`로 쓴다. 전공서의 스레드와 재진입성 항목에 닿는다."),
    box("api", None,
        "DX11에는 숨은 대상이 없다. 장치 컨텍스트가 `ID3D11DeviceContext`라는 객체이고 모든 호출이 그 객체의 멤버 "
        "함수라서, 어느 컨텍스트에 대한 일인지가 코드에 적힌다. Vulkan에는 “현재”라는 것이 아예 없다. 장치와 명령 "
        "버퍼의 핸들을 호출마다 첫 인자로 넘긴다."),
], lead="1-1강 5장에서 컨텍스트를 “OpenGL의 상태와 객체가 들어 있는 곳”이라고 했다. 이 장은 그 안을 들여다본다.")

ch3 = chapter(3, "상태 기계", [
    h3("3.1", "정하는 호출과 쓰는 호출"),
    p("`glClear( GL_COLOR_BUFFER_BIT )`의 인자 어디에도 색이 없다. 색은 그 전에 `glClearColor`가 컨텍스트에 적어 둔 "
      "것을 읽어 쓴다. 호출의 결과가 인자만으로 정해지지 않고, 그때 컨텍스트에 적혀 있는 값에 달려 있다. 이런 식으로 "
      "일하는 것을 상태 기계라고 부른다."),
    box("ex", "예시: 네 호출과 그때마다의 상태", [
        table([6, 42, 26, 26], ["", "호출", "컨텍스트의 clear color", "back buffer"], [
            ["1", "`glClearColor( 0.2f, 0.3f, 0.3f, 1.f )`", "(0.2, 0.3, 0.3, 1)", "그대로"],
            ["2", "`glClear( GL_COLOR_BUFFER_BIT )`", "그대로", "짙은 청록"],
            ["3", "`glClearColor( 1.f, 0.f, 0.f, 1.f )`", "(1, 0, 0, 1)", "짙은 청록 그대로"],
            ["4", "`glClear( GL_COLOR_BUFFER_BIT )`", "그대로", "빨강"],
        ], cell_cls=["num", "lab", "c", "c"], compact=True),
        p("1번과 3번은 상태만 바꾸고 2번과 4번은 상태를 읽어 일한다. 3번이 끝난 순간에도 버퍼는 청록이다. 2번과 4번은 "
          "글자 하나 다르지 않은 호출인데 결과가 다르다. 그 차이는 호출이 아니라 호출 앞의 상태에 있다."),
    ]),
    keep(table([16, 34, 50], ["갈래", "하는 일", "예"], [
        ["값을 정한다", "상태 값 하나를 바꾼다", "`glClearColor`, `glViewport`, `glScissor`"],
        ["켜고 끈다", "스위치 하나를 바꾼다", "`glEnable`, `glDisable`"],
        ["꽂는다", "바인딩 포인트 하나를 바꾼다", "`glBindBuffer` (4장)"],
        ["쓴다", "그때의 상태를 읽어 일한다", "`glClear`, 2-2강의 드로우 호출"],
        ["읽는다", "상태를 돌려준다", "`glGetIntegerv`, `glIsEnabled`, `glGetString`"],
    ], cell_cls=["lab", "", ""], compact=True),
    p("새 함수를 만나면 다섯 갈래 가운데 어디인지부터 가린다. 위의 셋은 화면에 아무 일도 일으키지 않는다. "
      "화면이 바뀌는 것은 “쓴다”에 속한 호출이 불릴 때뿐이다.")),

    h3("3.2", "스위치와 값"),
    fn("glEnable · glDisable · glIsEnabled",
       "void      glEnable(GLenum cap);\n"
       "void      glDisable(GLenum cap);\n"
       "GLboolean glIsEnabled(GLenum cap);",
       "컨텍스트의 스위치 하나를 켜거나, 끄거나, 읽는다. 켜고 끄는 호출은 상태만 바꾸고 화면에는 아직 아무 일도 없다.",
       params=[("`cap`", "스위치의 이름(capability). `GL_DEPTH_TEST`, `GL_BLEND`, `GL_SCISSOR_TEST` 같은 상수")],
       returns="`glIsEnabled`는 켜져 있으면 `GL_TRUE`(1), 꺼져 있으면 `GL_FALSE`(0). 나머지 둘은 돌려주는 값이 없다",
       fails="`cap`이 스위치의 이름이 아니면 `GL_INVALID_ENUM` 오류가 난다",
       notes=[("남는 기간", "다시 바꿀 때까지. 프레임이 넘어가도, 다른 함수로 들어가도 그대로다. 이미 켜진 스위치를 "
                          "다시 켜는 것은 오류가 아니고 아무 일도 없다"),
              ("선언된 곳", "`include/glad/glad.h:1585`, `:1582`, `:1654`")],
       lib="OpenGL"),
    keep(table([27, 16, 39, 18], ["스위치", "처음 값", "켜면", "처음 쓰는 곳"], [
        ["`GL_DEPTH_TEST`", "꺼짐", "가까운 것이 먼 것을 가린다", "2-6강"],
        ["`GL_CULL_FACE`", "꺼짐", "뒤를 향한 삼각형을 그리지 않는다", "2-3강"],
        ["`GL_BLEND`", "꺼짐", "새 색을 이미 있던 색과 섞는다", "3-7강"],
        ["`GL_SCISSOR_TEST`", "꺼짐", "정해 둔 사각형 밖의 픽셀을 건드리지 않는다", "이 강의 미션"],
        ["`GL_DEBUG_OUTPUT`", "컨텍스트에 따라", "드라이버가 디버그 메시지를 낸다", "6.2절"],
    ], cell_cls=["lab", "c", "", "c"], compact=True),
    p("스위치는 거의 다 꺼진 채로 시작한다. 켜진 채로 시작하는 것은 `GL_DITHER`와 `GL_MULTISAMPLE` 정도다. "
      "스위치에는 대개 짝이 되는 값이 따로 있다. 가위 테스트의 짝은 아래 함수가 정하는 사각형이다.")),
    fn("glScissor", "void glScissor(GLint x, GLint y, GLsizei width, GLsizei height);",
       "가위 사각형(scissor box)을 정한다. 가위 테스트가 켜져 있는 동안, 이 사각형 밖의 픽셀은 어떤 호출로도 바뀌지 않는다.",
       params=[("`x`, `y`", "사각형의 왼쪽 아래 모서리. 프레임버퍼의 왼쪽 아래가 (0, 0)이고 단위는 픽셀이다. "
                            "`glViewport`와 같은 좌표다 (1-2강 6장)"),
               ("`width`, `height`", "사각형의 너비와 높이. 음수이면 `GL_INVALID_VALUE` 오류가 난다")],
       notes=[("짝이 되는 스위치", "`GL_SCISSOR_TEST`. 꺼져 있으면 사각형을 정해 두어도 쓰이지 않는다. 처음 값은 창 전체다"),
              ("`glClear`와의 관계", "가위 테스트가 켜져 있으면 `glClear`도 사각형 안만 채운다. 뷰포트는 `glClear`에 "
                                  "영향을 주지 않았다 (1-2강 6장)"),
              ("선언된 곳", "`include/glad/glad.h:1537`")],
       lib="OpenGL"),

    h3("3.3", "상태는 남는다"),
    p("한 번 바꾼 상태는 다음 프레임에도, 다른 함수 안에서도 그대로다. 그래서 OpenGL 코드에서 가장 흔한 실수는 "
      "틀린 호출이 아니라 ==되돌리지 않은 호출==이다."),
    code(r"""
void DrawPanel()
{
    glEnable( GL_SCISSOR_TEST );    // on for the panel ...
    // ... draw the panel ...
}                                   // ... and still on after the function returns

void DrawWorld()
{
    // ... draw the world ...       // clipped to the panel's rectangle, and nothing here says why
}
""", title="a switch that outlives the code that needed it (function names are examples)", tag="bad"),
    p("`DrawWorld`만 읽어서는 원인을 찾을 수 없다. 잘린 그림이라는 증상은 여기서 나지만 원인은 다른 함수에 있다. "
      "피하는 규칙은 둘이고, 어느 쪽에도 값이 있다."),
    table([28, 32, 40], ["규칙", "얻는 것", "내주는 것"], [
        ["바꾼 쪽이 되돌려 놓는다", "다른 코드는 처음 값을 믿고 쓸 수 있다",
         "되돌리는 줄을 하나만 잊어도 깨진다. 잊은 곳과 증상이 나는 곳이 다르다"],
        ["쓰는 쪽이 쓰기 직전에 전부 정한다", "앞에서 누가 무엇을 했든 상관없다",
         "이미 그 값인 상태를 다시 정하는 호출이 늘어난다"],
    ], cell_cls=["lab", "", ""], compact=True),
    p("Part 2에서는 어느 쪽으로 해도 된다. 하다가 불편했던 점을 7.4절의 목록에 적어 둔다. 3-7강에서 상태를 값으로 "
      "묶어 넘기는 방법을 다룬다."),

    h3("3.4", "상태 읽기"),
    fn("glGetIntegerv", "void glGetIntegerv(GLenum pname, GLint* data);",
       "정수로 된 상태 하나를 읽어 `data`가 가리키는 곳에 적는다.",
       params=[("`pname`", "읽을 상태의 이름. 상태마다 상수가 하나씩 있다 (아래 표)"),
               ("`data`", "값을 받을 곳의 주소. 상태에 따라 적히는 값의 개수가 다르다")],
       fails="`pname`이 상태의 이름이 아니면 `GL_INVALID_ENUM` 오류가 나고 `data`는 건드리지 않는다",
       notes=[("주의", "함수는 `data` 뒤에 자리가 몇 개 있는지 모른다. 값 넷을 적는 상태에 `GLint` 하나의 주소를 주어도 "
                       "컴파일되고, 실행하면 그 옆의 메모리를 덮어쓴다"),
              ("형제 함수", "`glGetFloatv`, `glGetBooleanv`. 실수인 배경색은 `glGetFloatv`에 `GL_COLOR_CLEAR_VALUE`를 "
                            "주어 읽는다 (값 넷)"),
              ("선언된 곳", "`include/glad/glad.h:1633`")],
       lib="OpenGL"),
    keep(table([40, 14, 46], ["`pname`", "값의 개수", "뜻"], [
        ["`GL_MAJOR_VERSION`, `GL_MINOR_VERSION`", "1씩", "컨텍스트의 OpenGL 버전. 4.6이면 4와 6"],
        ["`GL_VIEWPORT`, `GL_SCISSOR_BOX`", "4씩", "그 사각형의 x, y, 너비, 높이"],
        ["`GL_MAX_TEXTURE_SIZE`", "1", "이 드라이버가 받는 텍스처 한 변의 최대 픽셀 수. 예: 16384"],
        ["`GL_ARRAY_BUFFER_BINDING`", "1", "그 바인딩 포인트에 꽂힌 버퍼의 이름 (4.3절)"],
        ["`GL_CONTEXT_FLAGS`", "1", "컨텍스트의 성격을 나타내는 비트 묶음 (6.1절)"],
    ], cell_cls=["lab", "c", ""], compact=True),
    p("상태 읽기는 디버깅할 때 쓰는 도구다. 드라이버는 받은 명령을 쌓아 두었다가 처리하는데, 읽는 호출은 그 흐름을 "
      "기다리게 만들 수 있어 느리다. 프레임마다 상태를 읽어서 판단하는 코드는 쓰지 않는다.")),
    box("ue", None,
        "언리얼의 OpenGL 백엔드(`OpenGLDrv`)는 “지금 GL에 설정되어 있다고 알고 있는 상태”를 `FOpenGLContextState`라는 "
        "구조체에 따로 적어 둔다. 바꾸려는 값이 이미 그 값이면 GL 호출을 건너뛰고, 상태가 궁금할 때 GL에 되묻지 않는다. "
        "상태가 컨텍스트 안에 숨어 있어서 생긴 장치다."),
    box("api", None,
        "DX11도 장치 컨텍스트에 상태를 정해 두고 그리는 상태 기계다. 다만 깊이·블렌드 같은 상태는 미리 만들어 둔 "
        "상태 객체를 통째로 꽂고, 스위치가 낱개로 흩어져 있지 않다. DX12와 Vulkan은 상태 대부분을 파이프라인 상태 "
        "객체 하나에 미리 구워 넣는다. “그리는 순간에 남아 있는 상태”가 줄어드는 방향이다."),
], lead="OpenGL의 호출은 “정해 두는 호출”과 “정해 둔 것을 쓰는 호출”로 나뉜다. 정해 둔 것은 바꿀 때까지 남는다.")

ch4 = chapter(4, "객체, 이름, 바인드", [
    h3("4.1", "이름은 숫자다"),
    p("`glfwCreateWindow`는 창을 가리키는 포인터를 돌려주었다 (1-1강 4장). GL의 객체는 포인터가 아니라 `GLuint` "
      "정수 하나로 가리킨다(`include/glad/glad.h:99`). OpenGL은 이 정수를 객체의 이름(name)이라고 부른다. "
      "이름은 컨텍스트 안에 있는 표의 번호이고, 0은 “객체 없음”을 뜻한다."),
    table([20, 36, 44], ["", "`GLFWwindow*`", "`GLuint` 이름"], [
        ["가리키는 방법", "메모리 주소", "컨텍스트 안의 표에서 찾는 번호"],
        ["“없음”", "`nullptr`", "0"],
        ["타입 검사", "다른 타입의 포인터와 섞으면 컴파일 오류가 난다", "버퍼도 텍스처도 같은 `GLuint`다. 섞어도 컴파일된다"],
        ["통하는 범위", "프로세스 안 어디서나", "그 이름을 만든 컨텍스트 안에서만"],
    ], cell_cls=["lab", "", ""], compact=True),
    p("번호표는 객체 종류마다 따로 있다. 이름이 3인 버퍼와 이름이 3인 텍스처는 함께 있을 수 있고, 숫자가 같을 뿐 "
      "다른 객체다. 버퍼를 넘길 자리에 텍스처의 이름을 넘겨도 컴파일러는 잡아 주지 못한다."),

    h3("4.2", "받고, 꽂고, 고치고, 지운다"),
    flow([
        ("이름 받기", "숫자만 생긴다"),
        ("꽂기", "객체가 생긴다", "accent"),
        ("고치기", "꽂힌 것이 대상"),
        ("뽑기", "0을 꽂는다"),
        ("지우기", "객체가 사라진다", "dark"),
    ], "버퍼라면 차례로 `glGenBuffers`, `glBindBuffer`, 데이터를 올리는 호출(2-2강), `glBindBuffer`에 0, "
       "`glDeleteBuffers`다."),
    fn("glGenBuffers", "void glGenBuffers(GLsizei n, GLuint* buffers);",
       "아직 쓰이지 않은 버퍼 이름 `n`개를 골라 `buffers`에 적어 준다. 이름만 준다. 버퍼 객체는 그 이름을 처음 "
       "꽂을 때 생긴다.",
       params=[("`n`", "받을 이름의 개수. 음수이면 `GL_INVALID_VALUE` 오류가 난다"),
               ("`buffers`", "이름을 받을 곳. `GLuint` `n`개가 들어갈 자리가 있어야 한다. 0은 나오지 않는다")],
       notes=[("선언된 곳", "`include/glad/glad.h:1818`")],
       lib="OpenGL"),
    fn("glBindBuffer", "void glBindBuffer(GLenum target, GLuint buffer);",
       "버퍼 하나를 바인딩 포인트 하나에 꽂는다. 그 뒤로 그 바인딩 포인트를 받는 호출은 이 버퍼를 대상으로 삼는다.",
       params=[("`target`", "꽂을 바인딩 포인트. `GL_ARRAY_BUFFER`(정점 데이터) 등. 2-2강부터 하나씩 나온다"),
               ("`buffer`", "꽂을 버퍼의 이름. 0을 주면 아무것도 꽂히지 않은 상태가 된다")],
       fails="`target`이 틀리면 `GL_INVALID_ENUM`, `buffer`가 받은 적 없는 이름이면 `GL_INVALID_OPERATION` (코어 프로필)",
       notes=[("선언된 곳", "`include/glad/glad.h:1812`")],
       lib="OpenGL"),
    keep(table([38, 46, 16], ["함수", "하는 일", "선언된 곳"], [
        ["`GLboolean glIsBuffer( GLuint buffer )`", "그 숫자가 지금 버퍼 객체의 이름이면 `GL_TRUE`", "`glad.h:1821`"],
        ["`void glDeleteBuffers( GLsizei n, const GLuint* buffers )`",
         "버퍼 객체를 없앤다. 꽂혀 있던 바인딩 포인트는 0이 된다. 0이나 없는 이름은 말없이 넘어간다",
         "`glad.h:1815`"],
    ], cell_cls=["lab", "", "c"], compact=True)),
    box("ex", "예시: 이름과 객체는 다르다", [
        table([44, 20, 36], ["`id`에 대해 차례로 부른 호출", "`glIsBuffer( id )`", "일어난 일"], [
            ["`glGenBuffers( 1, &id )`", "`GL_FALSE`", "이름만 잡아 두었다. 객체는 아직 없다"],
            ["`glBindBuffer( GL_ARRAY_BUFFER, id )`", "`GL_TRUE`", "처음 꽂는 순간 객체가 만들어졌다"],
            ["`glBindBuffer( GL_ARRAY_BUFFER, 0 )`", "`GL_TRUE`", "뽑았다. 객체는 남아 있다"],
            ["`glDeleteBuffers( 1, &id )`", "`GL_FALSE`", "객체가 사라졌다. `id`의 숫자는 그대로지만 가리키는 것이 없다"],
        ], cell_cls=["lab", "c", ""], compact=True),
    ]),

    h3("4.3", "바인딩 포인트는 슬롯이다"),
    FIG_SLOTS.render("데이터를 올리는 `glBufferData`(2-2강)는 버퍼의 이름을 받지 않는다. 슬롯의 이름을 받고, 그때 그 슬롯에 "
                     "꽂혀 있는 객체를 고친다. 점선은 `glBindBuffer`를 부른 뒤에 바뀔 연결이다."),
    p("객체를 고치는 호출 대부분이 이 모양이다. 첫 인자 `target`은 객체가 아니라 슬롯을 고르고, 실제 대상은 "
      "“지금 거기 꽂혀 있는 것”이다. 그래서 OpenGL 코드는 꽂는 줄과 고치는 줄이 늘 짝으로 나온다. 객체의 종류마다 "
      "슬롯과 함수가 따로 있다."),
    keep(table([18, 32, 34, 16], ["객체", "이름을 받는 함수", "꽂는 함수", "처음 쓰는 강"], [
        ["버퍼", "`glGenBuffers`", "`glBindBuffer( target, 이름 )`", "2-2강"],
        ["정점 배열", "`glGenVertexArrays`", "`glBindVertexArray( 이름 )`", "2-2강"],
        ["셰이더 프로그램", "`glCreateProgram`", "`glUseProgram( 이름 )`", "2-2강"],
        ["텍스처", "`glGenTextures`", "`glBindTexture( target, 이름 )`", "2-5강"],
        ["프레임버퍼", "`glGenFramebuffers`", "`glBindFramebuffer( target, 이름 )`", "5-1강"],
    ], cell_cls=["lab", "", "", "c"], compact=True),
    p("함수 이름의 모양은 조금씩 다르다. 슬롯이 하나뿐인 종류는 `target` 인자가 없고, 프로그램은 `Gen`과 `Bind` 대신 "
      "`Create`와 `Use`를 쓴다. 규칙은 같다. 숫자로 된 이름을 받고, 꽂아 놓고 쓴다. OpenGL 4.5부터는 꽂지 않고 "
      "이름을 직접 넘겨 고치는 함수들(direct state access)도 있는데, 2-3강에서 다룬다.")),

    h3("4.4", "잘못 꽂힌 객체"),
    code(r"""
glBindBuffer( GL_ARRAY_BUFFER, positions );
LoadColors();                                                 // binds another buffer, leaves it bound
glBufferData( GL_ARRAY_BUFFER, size, data, GL_STATIC_DRAW );  // meant for `positions`
""", title="the data goes to whatever is bound now (names are examples)", tag="bad"),
    p("셋째 줄은 규칙에 맞는 호출이다. 슬롯에 버퍼가 꽂혀 있고 인자도 범위 안이다. 그래서 GL은 오류를 내지 않고, "
      "6장의 디버그 콜백도 조용하다. 데이터는 `LoadColors`가 꽂아 둔 버퍼로 들어가고, `positions`는 빈 채로 남는다. "
      "증상은 한참 뒤, 그릴 때 나온다. 1.2절 표의 둘째 줄이 이것이다."),
    p("이런 버그는 꽂힌 것을 직접 읽어서 찾는다. 고치는 호출 바로 앞에서 `glGetIntegerv( GL_ARRAY_BUFFER_BINDING, … )`로 "
      "읽은 값이 생각한 이름과 다르면, 그 사이에 부른 함수 가운데 하나가 슬롯을 바꾸고 돌려놓지 않은 것이다."),
    box("cs", None,
        "정수 핸들의 가장 익숙한 예는 유닉스의 파일 디스크립터다. `open()`이 돌려주는 `int`는 커널이 프로세스마다 "
        "가진 표의 번호이고, 0·1·2는 표준 입력·출력·오류로 정해져 있다. 포인터를 내주지 않으면 받는 쪽이 내용을 "
        "건드릴 수 없고, 주는 쪽은 실제 자료의 위치를 마음대로 옮길 수 있다."),
    box("api", None,
        "DX11에서 자원은 COM 객체의 포인터(`ID3D11Buffer*`)다. 내용을 고칠 때는 그 포인터를 함수에 직접 넘기고"
        "(`UpdateSubresource( buffer, … )`), 꽂는 일(`IASetVertexBuffers`)은 그릴 때만 한다. “고치려면 먼저 꽂는다”는 "
        "OpenGL만의 규칙이다. Vulkan도 핸들을 인자로 넘긴다."),
], lead="버퍼나 텍스처처럼 프로그램이 만드는 것은 컨텍스트 안에 살고, 프로그램은 그것을 가리키는 숫자만 받는다. "
        "그 숫자를 함수에 직접 넘기는 대신, 먼저 꽂아 놓고 일한다.")

ch5 = chapter(5, "오류를 묻는 옛 방법: glGetError", [
    h3("5.1", "틀린 호출은 없던 일이 된다"),
    p("규칙을 어긴 호출을 만나면 GL은 그 호출을 무시한다. 상태도 화면도 호출 전과 같고, 컨텍스트 안의 오류 깃발 "
      "하나만 선다. 프로그램은 멈추지 않으므로 그다음 호출들은 “앞의 호출이 됐다”는 틀린 전제 위에서 실행된다."),
    keep(table([34, 9, 28, 29], ["오류 코드", "값", "뜻", "예 (코어 프로필)"], [
        ["`GL_NO_ERROR`", "`0`", "마지막으로 물은 뒤로 오류가 없었다", "—"],
        ["`GL_INVALID_ENUM`", "`0x0500`", "그 인자에 쓸 수 없는 상수다", "`glEnable`에 `GL_ARRAY_BUFFER`. 스위치가 아니다"],
        ["`GL_INVALID_VALUE`", "`0x0501`", "숫자가 허용 범위 밖이다", "`glViewport`에 음수 너비"],
        ["`GL_INVALID_OPERATION`", "`0x0502`", "지금 상태에서는 할 수 없는 일이다",
         "`glBindBuffer`에 받은 적 없는 이름"],
        ["`GL_INVALID_FRAMEBUFFER_OPERATION`", "`0x0506`", "완성되지 않은 프레임버퍼를 썼다", "5-1강"],
        ["`GL_OUT_OF_MEMORY`", "`0x0505`", "메모리가 모자라 실행하지 못했다", "아주 큰 버퍼나 텍스처"],
    ], cell_cls=["lab", "c", "", ""], compact=True)),
    p("상수는 `include/glad/glad.h:177` 〜 `:181`과 `:685`에 있다. “무시한다”에는 예외가 하나 있다. "
      "`GL_OUT_OF_MEMORY`가 난 뒤의 GL 상태는 정해져 있지 않다. 1-6강 2장의 구분으로 보면 `GL_INVALID_`로 시작하는 "
      "넷은 버그이고(코드가 규칙을 어겼다) `GL_OUT_OF_MEMORY`는 실패다(맞게 쓴 프로그램에서도 일어난다)."),

    h3("5.2", "깃발을 읽는 함수"),
    fn("glGetError", "GLenum glGetError(void);",
       "기록되어 있는 오류 코드 하나를 돌려주고, 그 깃발을 내린다.",
       returns="오류 코드. 기록된 것이 없으면 `GL_NO_ERROR`(0)",
       notes=[("깃발은 남는다", "오류가 나면 코드가 기록되고, 누가 읽어 갈 때까지 그대로 있다. 그 사이에 난 다른 오류는 "
                              "이미 선 깃발을 바꾸지 못한다"),
              ("되풀이해 읽는다", "구현에 따라 깃발이 여러 개일 수 있다. 그때는 부를 때마다 하나씩 나온다. 전부 비우려면 "
                                "`GL_NO_ERROR`가 나올 때까지 부른다"),
              ("선언된 곳", "`include/glad/glad.h:1627`")],
       lib="OpenGL"),
    FIG_ERRFLAG.render("깃발은 처음 난 오류를 쥔 채 읽힐 때까지 남는다. 여섯째 칸에서 받은 `GL_INVALID_ENUM`만으로는 "
                       "앞의 다섯 호출 가운데 어느 것이 틀렸는지 알 수 없고, 호출 4가 틀렸다는 사실은 사라졌다."),

    keep(h3("5.3", "왜 이것만으로는 부족한가"),
    table([24, 76], ["약점", "실제로 일어나는 일"], [
        ["어느 호출인지 모른다", "코드 하나만 돌려준다. 묻는 줄과 지난번 물은 줄 사이의 호출 전부가 용의자다"],
        ["물어야만 안다", "호출마다 뒤에 붙이면 코드가 두 배가 되고, 빼면 놓친다. 읽는 호출이라 느리기도 하다 (3.4절)"],
        ["깃발이 남는다", "한 번 읽지 않고 지나가면 한참 뒤 다른 곳의 검사가 그 오류를 받는다. 틀리지 않은 코드를 의심하게 된다"],
        ["말이 없다", "숫자뿐이다. 어느 인자가 왜 틀렸는지 설명이 없고, 성능 경고나 폐기 예정 기능 같은 것은 대상이 아니다"],
    ], cell_cls=["lab", ""], compact=True)),
    p("그래서 OpenGL 4.3에서 디버그 출력이 표준에 들어왔다. `glGetError`는 지금도 동작하고, 4.3보다 낮은 "
      "컨텍스트에서는 확장 없이 쓸 수 있는 유일한 수단이다. 미션 4에서 한 번 직접 써 본다. 다른 API에는 오류를 나중에 따로 묻는 "
      "방식이 없다. DX와 Vulkan은 호출마다 결과 값을 돌려주고(1-4강 2.4절의 상자), 잘못 쓴 것은 디버그 레이어가 알린다."),
], lead="규칙을 어긴 호출을 GL은 조용히 무시하고 깃발 하나를 올려 둔다. 프로그램이 물어봐야 그 깃발을 알려 준다.")

ch6 = chapter(6, "디버그 출력", [
    flow([
        ("glfwInit", "GLFW를 켠다"),
        ("힌트", "디버그 컨텍스트 요청", "accent"),
        ("창 생성", "컨텍스트가 정해진다"),
        ("연결 · GLAD", "gl*을 부를 수 있다"),
        ("켜기 · 등록", "스위치와 콜백", "accent"),
        ("루프", "메시지가 온다", "dark"),
    ], "색이 든 두 칸이 이 강에서 더하는 일이다. 앞의 것은 창을 만들기 전에만, 뒤의 것은 GLAD가 끝난 뒤에만 할 수 있다."),

    h3("6.1", "디버그 컨텍스트"),
    p("드라이버는 평소에 검사를 아끼고 빠르게 돈다. 컨텍스트를 디버그용으로 만들면 드라이버가 더 많이 검사하고 "
      "메시지를 자세히 낸다. 그만큼 느려질 수 있어서 개발하는 동안에만 쓴다. 컨텍스트의 종류는 만들어질 때 "
      "정해지고 나중에 바꿀 수 없다. 그래서 요청은 창을 만들기 전에 힌트로 한다."),
    code(r"""
#define GLFW_CONTEXT_DEBUG          0x00022007
/*! @brief Legacy name for compatibility.
 *
 *  This is an alias for compatibility with earlier versions.
 */
#define GLFW_OPENGL_DEBUG_CONTEXT   GLFW_CONTEXT_DEBUG
""", title="include/GLFW/glfw3.h", tag="now", start=1067, hl=[1067, 1072]),
    p("힌트 `GLFW_CONTEXT_DEBUG`의 기본값은 `GLFW_FALSE`이고, `GLFW_TRUE`를 주면 디버그 컨텍스트를 요청한다. "
      "`GLFW_OPENGL_DEBUG_CONTEXT`는 같은 값의 옛 이름이며 인터넷의 예제는 대부분 옛 이름을 쓴다. 적는 함수는 "
      "1-1강 4장의 `glfwWindowHint`이고 그 카드의 “부르는 순서”가 그대로 적용된다. `glfwInit()` 뒤, "
      "`glfwCreateWindow()` 앞이다. 창을 만든 뒤에 적으면 오류는 나지 않는다. “다음에 만들 창”에 대한 메모가 될 뿐이고, "
      "이미 만들어진 컨텍스트는 보통 컨텍스트로 남는다. 그래서 요청이 통했는지는 실행 중에 직접 확인한다."),
    box("ex", "예시: GL_CONTEXT_FLAGS를 비트로 읽기", [
        table([48, 16, 36], ["비트", "값", "서 있으면"], [
            ["`GL_CONTEXT_FLAG_FORWARD_COMPATIBLE_BIT`", "`0x1`", "폐기 예정 기능을 뺀 컨텍스트다"],
            ["`GL_CONTEXT_FLAG_DEBUG_BIT`", "`0x2`", "디버그 컨텍스트다"],
            ["`GL_CONTEXT_FLAG_NO_ERROR_BIT`", "`0x8`", "오류 검사를 건너뛰는 컨텍스트다. 내보낼 때의 선택지"],
        ], cell_cls=["lab", "c", ""], compact=True),
        code(r"""
GLint flags = 0;
glGetIntegerv( GL_CONTEXT_FLAGS, &flags );
if ( flags & GL_CONTEXT_FLAG_FORWARD_COMPATIBLE_BIT ) { /* a forward-compatible context */ }
""", tag="syntax"),
        p("읽은 값이 3이면 `0x1`과 `0x2`가 서 있는 것이고, 2이면 `0x2` 하나, 0이면 아무것도 없는 것이다. 값 하나에 "
          "참·거짓 여러 개를 담았으므로 `&`로 비트 하나만 남겨서 본다. 상수는 `include/glad/glad.h:598`, `:1249`, "
          "`:1498`에 있다."),
    ]),

    h3("6.2", "스위치를 켜고 콜백을 등록한다"),
    p("디버그 출력은 스위치 `GL_DEBUG_OUTPUT`으로 켜고 끈다(`include/glad/glad.h:1248`). 디버그 컨텍스트에서는 처음부터 "
      "켜져 있고 보통 컨텍스트에서는 꺼져 있다. 보통 컨텍스트에서도 켤 수는 있지만 드라이버가 메시지를 훨씬 적게 "
      "내거나 내지 않아도 된다. 처음 값에 기대지 않도록 켜는 줄을 직접 적는다. 받을 함수는 아래 함수로 등록한다."),
    fn("glDebugMessageCallback",
       "void glDebugMessageCallback(GLDEBUGPROC callback, const void *userParam);",
       "디버그 메시지를 받을 함수를 등록한다. 그 뒤로 드라이버는 메시지가 생길 때마다 이 함수를 부른다. "
       "컨텍스트마다 하나만 등록되고, 다시 등록하면 앞의 것이 밀려난다.",
       params=[("`callback`", "메시지를 받을 함수. 아래의 `GLDEBUGPROC` 모양이어야 한다. `nullptr`을 주면 등록을 지운다"),
               ("`userParam`", "콜백이 불릴 때 마지막 인자로 그대로 돌아오는 포인터. GL은 보관만 한다. 필요 없으면 `nullptr`")],
       fails="OpenGL 4.3보다 낮은 컨텍스트에서는 이 함수의 포인터가 채워지지 않아(`include/glad/glad.c:1546`) 부르면 "
             "죽는다. 엔진이 4.6을 요청하므로 창이 만들어졌다면 이 함수는 있다",
       notes=[("부르는 순서", "`gladLoadGLLoader()`가 성공한 뒤. 등록하기 전에 생긴 메시지는 콜백으로 오지 않는다"),
              ("선언된 곳", "`include/glad/glad.h:3244`")],
       lib="OpenGL 4.3"),
    code(r"""
typedef void (APIENTRY *GLDEBUGPROC)( GLenum source, GLenum type, GLuint id, GLenum severity,
                                      GLsizei length, const GLchar *message, const void *userParam );
""", title="the callback type: include/glad/glad.h:129 (one line in the header, wrapped here)", tag="syntax"),
    keep(table([30, 70], ["콜백이 받는 인자", "뜻"], [
        ["`source`, `type`, `severity`", "누가, 무슨 종류로, 얼마나 심각하게 냈는가 (6.3절의 표)"],
        ["`id`", "그 메시지의 번호. 드라이버가 정한다"],
        ["`message`, `length`", "설명 문장과 그 글자 수. 문장은 0으로 끝나고, 콜백이 돌아갈 때까지만 유효하다"],
        ["`userParam`", "등록할 때 맡긴 포인터. GLFW의 user pointer와 같은 일을 한다 (1-3강 4.2절)"],
    ], cell_cls=["lab", ""], compact=True)),
    code(r"""
#if defined(_WIN32) && !defined(APIENTRY) && !defined(__CYGWIN__) && !defined(__SCITECH_SNAP__)
#define APIENTRY __stdcall
#endif
""", title="include/glad/glad.h", tag="now", start=31, hl=[32]),
    p("콜백 타입에 든 `APIENTRY`는 Windows에서 `__stdcall`이 된다. 호출 규약, 곧 인자를 어디에 싣고 스택을 누가 "
      "정리하는지에 대한 약속이다. 양쪽의 규약이 다르면 돌아올 때 스택이 어긋나므로 컴파일러는 함수 포인터의 타입에 "
      "규약을 넣어 둔다. 32비트(Win32 구성)에서는 이 낱말을 빼고 선언한 함수가 `GLDEBUGPROC`와 타입이 달라 등록하는 "
      "줄에서 컴파일되지 않는다. 64비트(x64 구성)에는 규약이 하나뿐이라 `__stdcall`이 무시되고, 빼도 컴파일된다. "
      "솔루션에 두 구성이 다 있으므로 늘 적는다."),
    p("나머지는 1-3강 4장에서 본 구조 그대로다. C 라이브러리가 부르는 함수라서 `this`가 없는 함수여야 한다"
      "(자유 함수나 `static` 멤버 함수). 콜백 안에서는 지켜야 할 것이 넷 있다."),
    keep(table([34, 66], ["콜백 안에서", "이유"], [
        ["`gl*` 함수를 부르지 않는다", "GL 호출 한가운데에서 불린 것이다. 거기서 다시 GL을 부르면 무슨 일이 일어날지 정해져 있지 않다"],
        ["`message` 포인터를 보관하지 않는다", "콜백이 돌아가면 그 메모리는 GL이 다시 쓴다. 나중에 쓸 것이면 내용을 "
                                         "복사한다. GLFW 오류 콜백의 설명 문자열과 같은 규칙이다 (1-4강 2.3절)"],
        ["예외를 밖으로 내보내지 않는다", "예외가 C로 쓰인 드라이버의 스택을 지나가게 된다 (1-6강 5.2절)"],
        ["오래 걸리는 일을 하지 않는다", "동기 출력에서는 콜백이 도는 동안 그 GL 호출이 멈춰 있다 (6.4절)"],
    ], cell_cls=["lab", ""], compact=True)),

    h3("6.3", "메시지 하나에 든 것"),
    box("ex", "예시: 콜백이 받은 것을 그대로 찍으면", [
        console(Raw(
            '<span class="dim">source</span> 0x8246  <span class="dim">type</span> 0x824C  '
            '<span class="dim">id</span> 1281  <span class="dim">severity</span> 0x9146\n'
            '<span class="err">GL_INVALID_VALUE error generated.</span> '
            '<span class="dim">(이어서 어느 인자가 왜 틀렸는지에 대한 문장)</span>\n'
            '\n'
            '<span class="dim">source</span> 0x8246  <span class="dim">type</span> 0x8251  '
            '<span class="dim">id</span> 131185  <span class="dim">severity</span> 0x826B\n'
            'Buffer detailed info: Buffer object 1 (bound to GL_ARRAY_BUFFER_ARB, usage hint is GL_STATIC_DRAW)\n'
            'will use VIDEO memory as the source for buffer object operations.'
        ), title="메시지 두 개 (한 제조사 드라이버의 예. 번호와 문장은 드라이버마다 다르다)"),
        p("숫자 넷과 문장 하나가 온다. 아래 표로 읽으면 위의 것은 API가 낸 오류이고 심각도가 높다. 아래 것은 버퍼를 "
          "어느 메모리에 두었는지 알려 주는 안내로, 종류는 OTHER, 심각도는 알림이다. 문장은 드라이버와 버전에 따라 "
          "달라지므로 코드에서 문장을 비교하지 않는다. 같은 메시지를 가리킬 때는 `id`를 쓴다."),
    ]),
    keep(table([22, 28, 23, 27], ["상수의 끝부분", "뜻", "상수의 끝부분", "뜻"], [
        Group("`source`: 누가 냈는가 — `GL_DEBUG_SOURCE_*`"),
        ["`API`", "`gl*` 호출을 처리하던 GL", "`SHADER_COMPILER`", "셰이더 컴파일러 (2-2강)"],
        ["`WINDOW_SYSTEM`", "창 시스템 (Windows는 WGL)", "`APPLICATION`", "프로그램이 넣은 것 (6.5절)"],
        ["`THIRD_PARTY`", "외부 도구나 미들웨어", "`OTHER`", "그 밖의 것"],
        Group("`type`: 무슨 종류인가 — `GL_DEBUG_TYPE_*`"),
        ["`ERROR`", "`glGetError`가 알리던 오류", "`DEPRECATED_BEHAVIOR`", "폐기 예정 기능을 썼다"],
        ["`UNDEFINED_BEHAVIOR`", "결과가 정해지지 않은 사용", "`PORTABILITY`", "드라이버마다 다를 수 있다"],
        ["`PERFORMANCE`", "되지만 느린 길로 간다", "`OTHER`", "그 밖의 것. 드라이버의 안내"],
        ["`MARKER`", "프로그램이 넣은 표시", "`PUSH_GROUP`, `POP_GROUP`", "묶음의 시작과 끝"],
        Group("`severity`: 얼마나 심각한가 — `GL_DEBUG_SEVERITY_*` (뜻은 표준이 드는 기준)"),
        ["`HIGH`", "GL 오류, 셰이더 컴파일 오류", "`MEDIUM`", "큰 성능 경고, 폐기 예정 기능"],
        ["`LOW`", "작은 성능 경고", "`NOTIFICATION`", "오류도 성능 문제도 아닌 알림"],
    ], cell_cls=["lab", "", "lab", ""], compact=True)),
    p("상수는 `include/glad/glad.h:1216` 〜 `:1237`에 있다. 숫자를 이 이름들로 바꾸는 일은 콜백이 한다. 심각도를 "
      "매기는 것은 드라이버이고 표준은 기준을 권할 뿐이라, 같은 일에 드라이버마다 다른 심각도가 붙을 수 있다."),

    h3("6.4", "동기와 비동기"),
    p("스위치가 하나 더 있다. `GL_DEBUG_OUTPUT_SYNCHRONOUS`(`include/glad/glad.h:1212`)이고 꺼진 채로 시작한다. "
      "켜면 드라이버는 메시지를 낳은 그 GL 호출이 돌아가기 전에, 그 호출을 부른 스레드에서 콜백을 부른다. 끄면 "
      "언제, 어느 스레드에서 부를지를 드라이버가 정한다."),
    FIG_SYNC.render("콜백에 중단점을 걸었을 때의 호출 스택이다. 가장 최근에 불린 함수를 맨 위에 그렸다 (1-6강 4.3절의 "
                    "그림과 같은 방식). 왼쪽에서는 스택을 내려가면 틀린 `gl*` 호출이 적힌 줄이 나온다."),
    keep(table([24, 38, 38], ["", "켰을 때 (동기)", "껐을 때 (비동기)"], [
        ["콜백이 불리는 곳과 때", "틀린 호출을 부른 스레드에서, 그 호출이 돌아가기 전", "정해져 있지 않다. 다른 스레드일 수도, 나중일 수도 있다"],
        ["호출 스택", "틀린 호출이 스택에 있다", "없을 수 있다"],
        ["비용", "드라이버가 일을 미루거나 나눠 하지 못해 느려질 수 있다", "드라이버가 가장 빠른 길로 간다"],
        ["콜백이 조심할 것", "오래 끌지 않는다", "다른 스레드와 동시에 불려도 안전해야 한다"],
    ], cell_cls=["lab", "", ""], compact=True)),
    p("마지막 줄이 엔진에 닿는다. 1-5강의 Logger는 스레드가 하나라고 보고 만들었다 (1-5강 6.4절). 동기 출력을 끈 채 "
      "콜백에서 Logger를 부르면 두 스레드가 같은 스트림에 동시에 쓰는 일이 생길 수 있다. 끈다고 반드시 다른 스레드에서 "
      "불리는 것은 아니다. 약속이 없다는 뜻이다. 틀린 호출의 위치도 동기 출력이 켜져 있어야 얻는다. 로그의 위치 "
      "칸에는 늘 콜백 안의 줄이 찍히고(1-5강 3장), 진짜 위치는 호출 스택에만 있기 때문이다."),

    box("ue", None,
        "언리얼에서 같은 자리는 RHI의 디버그 계층이다. 실행 인자 `-d3ddebug`를 주면 D3D의 디버그 레이어가 켜지고, "
        "그 메시지가 `LogD3D12RHI` 같은 카테고리의 로그로 들어온다. 장치를 만들 때 켜야 하고, 느려져서 개발 중에만 "
        "쓴다는 점이 디버그 컨텍스트와 같다."),
    box("api", None,
        "어느 API든 “만들 때 디버그를 요청하고, 메시지를 받을 곳을 등록한다”는 두 단계다. DX11은 장치를 만들 때 "
        "`D3D11_CREATE_DEVICE_DEBUG`를 주고 `ID3D11InfoQueue`로 받는다. DX12는 장치를 만들기 전에 "
        "`ID3D12Debug::EnableDebugLayer()`를 부른다. Vulkan은 검증 레이어를 켜고 `VK_EXT_debug_utils`의 콜백으로 받는다."),

    h3("6.5", "걸러 내기와 직접 넣기"),
    fn("glDebugMessageControl",
       "void glDebugMessageControl(GLenum source, GLenum type, GLenum severity,\n"
       "                           GLsizei count, const GLuint *ids, GLboolean enabled);",
       "어떤 메시지를 낼지 드라이버에 알린다. 조건에 맞는 메시지들을 한꺼번에 켜거나 끈다.",
       params=[("`source`, `type`, `severity`", "고를 조건. 6.3절의 상수를 주거나, “가리지 않는다”는 뜻의 `GL_DONT_CARE`를 준다"),
               ("`count`, `ids`", "번호로 고를 때 쓴다. `ids`는 번호 `count`개의 배열이다. 번호로 고르지 않으면 0과 `nullptr`"),
               ("`enabled`", "`GL_TRUE`면 켜고 `GL_FALSE`면 끈다. 꺼진 메시지는 만들어지지 않고 콜백도 불리지 않는다")],
       fails="번호로 고를 때(`count`가 0보다 클 때)는 `source`와 `type`을 정확히 주고 `severity`는 `GL_DONT_CARE`여야 "
             "한다. 어기면 `GL_INVALID_OPERATION`이다",
       notes=[("선언된 곳", "`include/glad/glad.h:3238`. `GL_DONT_CARE`는 `:246`")],
       lib="OpenGL 4.3"),
    box("ex", "예시: 번호 하나만 끄기", [
        code(r"""
const GLuint noisy[] = { 131185 };      // a number read from the log (the value is an example)
glDebugMessageControl( GL_DEBUG_SOURCE_API, GL_DEBUG_TYPE_OTHER, GL_DONT_CARE, 1, noisy, GL_FALSE );
""", tag="usage"),
        p("6.3절 예시의 둘째 메시지 하나만 끄고 같은 심각도의 다른 알림은 계속 받는다. 번호는 드라이버마다 다르므로 "
          "이런 줄은 그 드라이버에서만 뜻이 있다. 조건으로 고를 때는 넷째와 다섯째 인자가 0과 `nullptr`이 된다. "
          "처음에 무엇이 켜져 있는지에는 기대지 않고, 받을 범위를 이 함수로 직접 정해 둔다."),
    ]),
    fn("glDebugMessageInsert",
       "void glDebugMessageInsert(GLenum source, GLenum type, GLuint id, GLenum severity,\n"
       "                          GLsizei length, const GLchar *buf);",
       "프로그램이 디버그 메시지를 직접 하나 넣는다. 드라이버가 낸 메시지와 같은 길로 콜백에 닿고, "
       "`glDebugMessageControl`로 꺼 둔 조건에 걸리면 똑같이 걸러진다.",
       params=[("`source`", "`GL_DEBUG_SOURCE_APPLICATION` 또는 `GL_DEBUG_SOURCE_THIRD_PARTY`만 된다. 다른 값이면 "
                           "`GL_INVALID_ENUM`"),
               ("`type`, `id`, `severity`", "6.3절의 종류와 심각도, 그리고 직접 정한 번호"),
               ("`length`, `buf`", "문장과 그 글자 수. `length`가 음수이면 `buf`를 0으로 끝나는 문자열로 읽는다")],
       notes=[("쓰임새", "콜백과 거르기가 맞게 이어졌는지를 드라이버에 기대지 않고 확인한다. 내가 정한 문장이 그대로 "
                        "오기 때문이다. 예: 종류 `MARKER`, 번호 7, 문장 `\"level loading starts\"`"),
              ("선언된 곳", "`include/glad/glad.h:3241`")],
       lib="OpenGL 4.3"),
], lead="OpenGL 4.3부터 드라이버는 오류와 경고를 문장으로 써서, 프로그램이 등록해 둔 함수에 건네준다. 묻지 않아도 "
        "오고, 어느 호출이 틀렸는지도 잡을 수 있다.")

ch7 = chapter(7, "설계", [
    h3("7.1", "파일 배치"),
    tree("""
Engine/
└── Core/
    ├── EngineCore.h  #does Init() or a new setter gain a debug option? (7.2)
    └── EngineCore.cpp  #the hint goes in before glfwCreateWindow
Client/
└── main.cpp  #driver info, the temporary experiments, maybe the callback (7.2)
Docs/
└── WrapList.md +  #things you wanted to wrap (7.4, the name is an example)
"""),
    p("콜백이 어느 파일에 들어가는지는 아래 둘째 결정에 달려 있다. 메시지가 지나는 길은 어느 쪽이든 같다. `gl*` 호출, "
      "드라이버, 콜백, `GLogger::Log`, 그리고 콘솔과 파일이다. 끝났을 때의 로그는 10장에 있다."),

    keep(h3("7.2", "결정할 것"),
    table([19, 37, 44], ["결정", "선택지", "따져 볼 것"], [
        ["디버그 컨텍스트를 요청하는 방법",
         "`Init`이 Debug 구성에서 늘 요청한다 / `Init`에 인자를 하나 더한다 / `Init` 전에 부르는 설정 함수를 둔다",
         "힌트는 `glfwInit` 뒤, 창 생성 앞에서만 통하고 둘 다 `Init` 안에 있다. Client가 `glfwWindowHint`를 직접 "
         "부를 틈이 없다. 1-1강 8.3절의 `Init` 선언을 바꿀 것인가. Release에서 켜 볼 일이 있는가"],
        ["콜백이 사는 곳과 등록하는 쪽",
         "Client의 `main.cpp`에 두고 `Init` 뒤에 Client가 등록한다 / Engine에 두고 `Init`이 GLAD 직후에 등록한다",
         "Part 2의 `gl*` 코드는 Client의 임시 코드다. 이 콜백은 Part 3 뒤에도 남는다. `Init` 안의 GL 호출이 낸 "
         "메시지도 받고 싶은가"],
        ["메시지를 로그 레벨로 옮기는 기준", "심각도만 본다 / 종류를 먼저 본다 / 둘을 함께 본다",
         "6.3절의 표. 종류는 오류인데 심각도가 낮게 온 메시지는 어디로 가는가. 알림은 평소에 보이는 레벨인가 "
         "(1-5강 2.2절)"],
        ["무엇을 어디서 거르는가", "`glDebugMessageControl`로 드라이버에서 / 콜백 안의 조건문으로 / Logger의 최소 레벨로",
         "드라이버에서 끄면 콜백 호출 자체가 없다. Logger에서 거르면 최소 레벨만 내려도 다시 보인다. 심각도 하나를 "
         "통째로 끌 것인가, 번호 하나만 끌 것인가"],
        ["동기 출력", "늘 켠다 / Debug 구성에서만 켠다 / 끈다", "6.4절의 표. Logger는 스레드가 하나라고 보고 만들었다"],
        ["GL 오류에서 멈출 것인가", "로그만 남긴다 / 종류가 오류이면 그 자리에서 멈춘다",
         "GL 오류는 1-6강의 구분으로 버그다. 멈추는 문장을 어디에 두는가 (1-6강 4.3절). 동기 출력이 꺼져 있을 때 "
         "멈춘 자리는 무엇을 말해 주는가"],
    ], cell_cls=["lab", "", ""], compact=True)),
    box("decide", None,
        "여섯 가지에 정답은 없다. 미션 전에 행마다 하나를 고르고 이유를 한 줄씩 적어 둔다. 첫째와 둘째는 묶여 있다. "
        "힌트는 엔진 안에서만 적을 수 있으므로, 콜백을 Client에 두면 디버그 출력에 관한 코드가 두 프로젝트로 갈린다. "
        "그래도 되는지를 정한다. 어느 쪽을 고르든 3-2강에서 이 코드의 자리를 다시 정한다."),

    keep(h3("7.3", "선언 스케치"),
    code(r"""
// The shape is fixed by GLDEBUGPROC (include/glad/glad.h:129). The name is an example.
// On which build configuration does this stop compiling if APIENTRY is left out? (6.2)
void APIENTRY cbGLDebugMessage( GLenum source, GLenum type, GLuint id, GLenum severity,
                                GLsizei length, const GLchar* message, const void* user_param );

// Three translators: a GLenum goes in, a short text comes out.
// What do they return for a value that is not in the table of 6.3?
const char* GLDebugSourceName( GLenum source );
const char* GLDebugTypeName( GLenum type );
const char* GLDebugSeverityName( GLenum severity );

// Decision 3 of 7.2 as a function. Which of the two arguments does it look at first?
ELogLevel GLDebugLogLevel( GLenum type, GLenum severity );
""", title="the callback and its helpers (the file is decision 2 of 7.2; all names are examples)", tag="sketch"),
    p("콜백이 하는 일은 번역이다. 숫자 셋을 이름으로 바꾸고, 심각도를 `ELogLevel`로 바꾸고, 한 줄로 만들어 Logger에 "
      "넘긴다. 레벨이 실행 중에 정해진다는 점이 지금까지의 로그 호출과 다르다.")),

    keep(h3("7.4", "감싸고 싶은 것 목록"),
    p("Part 2에서는 `gl*` 호출을 클래스로 감싸지 않는다. 대신 쓰면서 불편했던 것을 목록으로 모은다. 이 목록이 3-1강의 "
      "재료다. 이 강에서 첫 줄들을 적는다."),
    table([10, 44, 36, 10], ["강", "되풀이했거나 불편했던 것", "그때 일어난 일", "횟수"], [
        ["2-1", "(예) 스위치를 켠 뒤 끄는 줄을 빼먹었다", "다음 프레임의 지우기가 사각형 안에만 먹었다", "1"],
        ["2-1", "(예) `GLenum`을 글자로 바꾸는 `switch`를 세 벌 썼다", "값 하나를 빠뜨려 `?`가 찍혔다", "3"],
    ], cell_cls=["c", "", "", "c"], compact=True),
    ul([
        "**불편했던 사실만 적는다.** 해법(클래스 이름, 함수의 모양)은 적지 않는다. 해법은 3-1강에서 목록 전체를 "
        "놓고 정한다.",
        "**같은 불편이 또 나오면 새 줄을 만들지 않고 횟수를 올린다.** 횟수가 3-1강에서 우선순위가 된다.",
        "**함수로 나누는 것은 괜찮다.** GL 객체의 이름을 멤버로 쥐는 클래스는 Part 3까지 만들지 않는다.",
    ])),

    keep(h3("7.5", "이 강에서 하지 않는 것"),
    table([32, 68], ["미루는 것", "이유"], [
        ["버퍼에 데이터를 올리고 그리기", "2-2강이다. 여기서는 이름을 받고 꽂는 데까지만 해 본다"],
        ["셰이더 컴파일 오류 읽기", "2-2강과 2-4강이다. 그 메시지도 이 강에서 만든 콜백으로 함께 들어온다"],
        ["객체에 이름표 붙이기, 메시지 묶기", "`glObjectLabel`과 `glPushDebugGroup`이 있다. 객체가 여럿 생긴 뒤에야 "
                                        "쓸모가 생긴다"],
        ["프레임을 통째로 들여다보는 외부 도구", "RenderDoc 같은 프레임 디버거는 그릴 것이 생긴 뒤에 쓴다"],
        ["GL 호출을 클래스로 감싸기", "Part 3이다 (7.4절)"],
    ], cell_cls=["lab", ""], compact=True)),
], lead="새로 만드는 것은 콜백 함수 하나와 그것을 잇는 몇 줄이다. 어디에 둘지와 무엇을 걸러 낼지는 직접 정한다.")

def steps_two_pages(items: list, on_first: int) -> Raw:
    """steps() with a page break after step `on_first`.

    With the pass conditions written out the eight steps need two pages, and the
    natural break leaves only the last two on the second one. steps() numbers
    from 1 on every call, so it cannot simply be called twice.
    """
    marker = '<div class="step">'
    parts = str(steps(items)).split(marker)
    assert len(parts) == len(items) + 1, "steps() markup changed: look at common.steps()"
    return Raw(marker.join(parts[:on_first + 1]) + pagebreak() + marker + marker.join(parts[on_first + 1:]))


ch8 = chapter(8, "구현 미션", [
    steps_two_pages([
        ("네 코드를 읽고, 드라이버 정보를 로그에 남긴다",
         "할 일은 둘이다. (가) 1.3절 표의 네 줄마다 “볼 자리”를 네 코드에서 찾아 실제 파일과 줄을 적는다. "
         "(나) `Init`이 성공한 뒤에 회사, 장치, GL 버전, 셰이더 언어 버전을 읽어 Info 로그로 남긴다. "
         "**통과:** 실행하면 네 값이 Info 레벨로 콘솔과 로그 파일 양쪽에 찍힌다.",
         ["`glGetString`이 돌려주는 타입은 `std::format`이 문자열로 받는 타입이 아니다 (2.2절 카드의 “돌려주는 값”)."]),
        ("상태가 남는 것을 눈으로 본다",
         "`cbUpdate`에서 가위 테스트를 켜고, 창보다 작은 가위 사각형을 정하고, 엔진의 배경색과 다른 색으로 지운다. "
         "되돌리는 줄 없이 먼저 실행해 창이 어떻게 보이는지 적는다. 그다음 다음 프레임이 물려받은 상태를 찾아 전부 "
         "되돌린다. **통과:** 고친 뒤에는 창 전체가 엔진의 배경색이고 작은 사각형만 다른 색이다. 깜빡이는 곳이 없다.",
         ["엔진의 지우기가 `cbUpdate`보다 먼저다 (1-2강 5장). 다음 프레임이 물려받는 상태는 하나가 아니다."]),
        ("이름, 객체, 슬롯을 확인한다",
         "4.2절 예시의 네 호출을 버퍼 대신 정점 배열 객체로 되풀이하고, 호출 하나가 끝날 때마다 그 이름이 객체인지 "
         "물어 값을 찍는다. 이어서 버퍼 이름을 하나 받아 꽂고, 그 슬롯에 꽂힌 이름을 읽는다. 끝나면 만든 것을 지운다. "
         "**통과:** 찍힌 네 값이 4.2절 예시의 표와 같은 차례이고, 슬롯에서 읽은 값이 받은 버퍼 이름과 같다.",
         ["정점 배열은 꽂는 함수에 `target`이 없다 (4.3절의 표). 묻는 함수는 `glIsVertexArray`다."]),
        ("`glGetError`로 오류를 잡아 본다",
         "5.1절 표의 둘째 〜 넷째 줄의 세 코드를, 표의 예와 다른 호출로 하나씩 낸다. 낼 때마다 바로 `glGetError`를 "
         "읽어 값을 찍는다. 그다음 틀린 호출 둘을 연달아 내고 한 번만 읽은 뒤, 조금 뒤에 다시 읽는다. **통과:** 하나씩 "
         "냈을 때 찍힌 값이 5.1절 표의 값과 같다. 둘을 연달아 냈을 때 두 번의 읽기에 나온 값을 적어 두었다.",
         ["이미 아는 함수의 인자를 망가뜨린다. 음수 크기, 뜻 없는 비트, 다른 종류의 상수. 값은 `{:#x}`로 찍는다."]),
        ("디버그 컨텍스트를 요청하고 확인한다",
         "창을 만들기 전에 `GLFW_CONTEXT_DEBUG` 힌트로 디버그 컨텍스트를 요청한다. 누가 언제 요청하게 할지는 7.2절의 "
         "첫째 결정이다. 컨텍스트의 비트를 읽어 디버그 컨텍스트인지 아닌지를 로그 한 줄로 남긴다. 힌트를 창 생성 뒤로 "
         "옮겨 그 줄이 어떻게 바뀌는지 적고, 제자리로 돌린다. **통과:** Debug 구성으로 실행하면 그 줄이 “맞다”로 찍힌다.",
         ["6.1절 예시는 다른 비트를 읽는다. 표에서 맞는 비트를 고른다."]),
        ("콜백을 등록하고 첫 메시지를 받는다",
         "`GL_DEBUG_OUTPUT`을 켜고, 7.3절의 모양으로 콜백을 만들어 등록한다. 콜백은 출처·종류·심각도를 이름으로 "
         "바꾸고 번호와 문장을 붙여 한 줄로 Logger에 넘긴다. 콜백을 둘 곳과 등록하는 쪽은 7.2절의 둘째 결정이고, 로그 "
         "레벨을 정하는 기준은 셋째 결정이다. **통과:** `glDebugMessageInsert`로 직접 넣은 문장이 출처·종류·심각도의 "
         "이름과 함께 로그에 찍힌다. 아무것도 오지 않으면 9장의 첫 줄부터 본다.",
         ["레벨이 실행 중에 정해진다. 레벨별 매크로 대신 `GLogger::Log()`를 직접 부르는 길이 있다 (1-5강 1.2절)."]),
        ("일부러 틀리고, 틀린 줄을 찾는다",
         "4단계의 틀린 호출 하나를 다시 넣어, 콜백으로 온 메시지를 읽는다. 동기 출력을 켜고 콜백에 중단점을 걸어 호출 "
         "스택에서 그 호출이 적힌 줄을 찾는다. 끄고 같은 일을 해서 달라진 점을 적는다. 끝나면 동기 출력과, GL 오류에서 "
         "멈출지를 7.2절의 다섯째·여섯째 결정대로 둔다. **통과:** 출처, 종류, 심각도, 번호, 문장이 붙은 줄이 정한 "
         "레벨과 색으로 찍힌다. 동기 출력을 켠 채로는 호출 스택을 내려가 틀린 호출이 적힌 줄에 닿는다.",
         ["드라이버의 칸들을 지나 아래로 내려간다 (6.4절의 그림). 꺼도 같은 스택이 보일 수 있다. 약속이 없을 뿐이다."]),
        ("걸러 내고, 목록을 시작하고, 묶는다",
         "알림 심각도의 메시지를 직접 넣어 7.2절의 넷째 결정대로 걸러지는지 본다. 2 〜 4단계의 실험 코드, 7단계의 "
         "틀린 호출, `glGetError`를 지운다. 7.4절의 목록에 세 줄 이상 적고, 7.2절의 여섯 결정과 이유가 적혀 있는지 본 "
         "뒤 커밋 하나로 묶는다. **통과:** 10장의 여섯 줄을 확인하고 커밋했다.",
         ["지금은 드라이버가 조용할 수 있다. 버퍼를 만드는 2-2강부터 알림이 늘어난다."]),
    ], on_first=5),
], lead="2 〜 4단계는 눈으로 확인하고 지우는 실험이다. 한 번 할 일은 `main`의 `Init`과 `Run()` 사이에, 프레임마다 할 "
        "일은 `cbUpdate`에 쓴다. 단계마다 “통과”에 적힌 것이 보이면 다음으로 간다. 무엇을 하라는 것인지 분명하지 "
        "않으면 맨 뒤 14장에 단계별로 풀어 적은 목록이 있다.", pb=True)

ch9 = chapter(9, "흔한 함정", [
    table([26, 40, 34], ["증상", "원인", "확인 방법"], [
        ["콜백이 한 번도 불리지 않는다", "디버그 컨텍스트가 아니다. 힌트를 창 생성 뒤에 적었거나 빠뜨렸다. 또는 "
                               "`GL_DEBUG_OUTPUT`이 꺼져 있다",
         "`GL_CONTEXT_FLAGS`의 비트, 그리고 `GL_DEBUG_OUTPUT` 스위치. 그다음 메시지를 직접 넣어 본다"],
        ["콜백을 넘기는 줄에서 형 변환 오류 (C2664)", "마지막 인자를 `void*`로 적었다(`const`가 빠졌다). Win32 구성이라면 "
                                              "`APIENTRY`가 빠졌다. 또는 `static`이 아닌 멤버 함수를 넘겼다",
         "6.2절의 콜백 타입과 한 낱말씩 맞춰 본다. 1-3강 4.1절"],
        ["창의 일부만 지워지고 나머지가 깜빡이거나 남는다", "가위 테스트를 켠 채로 프레임이 넘어갔다",
         "프레임 첫머리에서 `GL_SCISSOR_TEST`를 `glIsEnabled`로 읽어 찍어 본다"],
        ["틀리지 않은 호출 뒤에서 `glGetError`가 오류를 준다", "앞에서 난 오류를 아무도 읽지 않아 깃발이 남아 있었다",
         "5.2절의 그림. 의심하는 호출 바로 앞에서 깃발을 한 번 비운다"],
        ["콜백에 중단점이 걸렸는데 호출 스택에 내 코드가 없다", "동기 출력이 꺼져 있다",
         "`GL_DEBUG_OUTPUT_SYNCHRONOUS`를 `glIsEnabled`로 읽는다"],
        ["같은 알림이 프레임마다 찍힌다", "프레임마다 나는 메시지를 평소에 보이는 레벨로 찍고 있다",
         "그 메시지의 번호를 보고 7.2절의 넷째 결정을 적용한다"],
    ], compact=True),
], lead="증상에서 거꾸로 찾는 표다.", pb=True)

ch10 = chapter(10, "완료 기준", [
    checklist([
        "시작할 때 회사, 장치, GL 버전, 셰이더 언어 버전이 Info 로그로 콘솔과 파일에 남는다.",
        "디버그 컨텍스트인지 아닌지가 로그 한 줄로 남고, Debug 구성에서는 “맞다”로 나온다.",
        "일부러 틀린 `gl*` 호출을 하나 넣으면 출처, 종류, 심각도, 번호, 문장이 붙은 줄이 정한 레벨과 색으로 찍힌다.",
        "동기 출력을 켠 채 콜백에 중단점을 걸면, 호출 스택을 내려가 틀린 호출이 적힌 줄에 닿는다.",
        "`Engine/`과 `Client/`에서 `glDebugMessageCallback`을 검색하면 한 줄만 나온다. `glGetError`와 실험용 "
        "틀린 호출은 검색되지 않는다.",
        "7.2절의 여섯 가지에 고른 것과 이유가 적혀 있고, 감싸고 싶은 것 목록에 세 줄 이상이 있다. 커밋 하나로 묶였다.",
    ]),
    console(Raw(
        '<span class="dim">[14:02:07.318]</span> <span class="ok">[Info ]</span> [GL   ] Renderer: '
        '<span class="dim">(드라이버가 준 문자열)</span>\n'
        '<span class="dim">[14:02:07.318]</span> <span class="ok">[Info ]</span> [GL   ] Version: 4.6.0 '
        '<span class="dim">(…)</span> / GLSL 4.60 <span class="dim">(…)</span>\n'
        '<span class="dim">[14:02:07.319]</span> <span class="ok">[Info ]</span> [GL   ] Debug context: yes, '
        'synchronous output: on\n'
        '<span class="dim">[14:02:09.774]</span> <span class="err">[Error]</span> [GL   ] API / Error / High / #1281: '
        '<span class="dim">(드라이버가 쓴 문장)</span>'
    ), title="기대하는 출력 (형식, 카테고리 이름, 레벨의 대응은 예시. 드라이버가 쓴 부분은 PC마다 다르다)"),
], lead="전부 눈이나 검색으로 확인할 수 있는 조건이다.")

ch11 = chapter(11, "생각해 볼 질문", [
    exgroup("A", "코드를 쓰지 않고 답하시오", "한두 문장으로, 이유까지"),
    qlist([
        "`glClearColor`를 `Init`에서 한 번만 불렀는데 프레임마다 그 색으로 지워진다. 왜인가? `cbUpdate`가 지우는 색을 "
        "바꾸고 되돌리지 않으면 다음 프레임에 무슨 일이 생기는가?",
        "`glGenBuffers`로 받은 이름을 한 번도 꽂지 않고 `glIsBuffer`에 넘기면 무엇이 나오는가? 왜인가?",
        "`gl*` 호출 다섯 개 뒤에 `glGetError`를 한 번 불렀더니 `GL_INVALID_ENUM`이 나왔다. 어느 호출이 틀렸는지 알 수 "
        "있는가? 다섯 개 가운데 틀린 호출이 둘이었다면 둘째 오류는 어떻게 되는가?",
        "`GLFW_CONTEXT_DEBUG` 힌트를 `glfwCreateWindow` 다음 줄에 적었다. 컴파일 오류도 GLFW 오류도 없다. 무슨 일이 "
        "일어났고, 실행 중에 어떻게 알아채는가?",
        "동기 출력을 끈 채 콜백에 중단점을 걸었다. 호출 스택에서 틀린 호출을 찾지 못할 수 있는 이유는 무엇인가? "
        "이때 1-5강의 Logger에는 어떤 문제가 생길 수 있는가?",
        "버퍼 A에 넣으려던 데이터가 버퍼 B에 들어갔다. 디버그 콜백은 조용했다. GL은 왜 이것을 오류로 보지 않는가?",
        "1-6강의 구분으로 `GL_INVALID_OPERATION`은 버그인가 실패인가? `GL_OUT_OF_MEMORY`는 어느 쪽인가?",
    ], lines=2),
], lead="답을 보기 전에 소리 내어 설명해 본다. 막히는 문항이 다시 읽을 장이다.", pb=True)

ch12 = chapter(12, "해설", [
    answers("질문 A", [
        ("색이 컨텍스트의 상태로 남아 있기 때문이다. 되돌리지 않으면 다음 프레임의 엔진 쪽 지우기도 바뀐 색을 쓴다.",
         "`glClear`는 색을 인자로 받지 않고 그때의 상태를 읽는다. 상태는 프레임이 넘어가도 그대로다. 가위 스위치까지 "
         "켜 둔 채라면 엔진의 지우기도 그 사각형 안만 채운다. (3.1절, 3.3절)"),
        ("`GL_FALSE`가 나온다.",
         "`glGenBuffers`는 이름만 잡아 둔다. 버퍼 객체는 그 이름을 처음 꽂을 때 만들어지고, `glIsBuffer`는 객체가 "
         "있는지를 묻는다. (4.2절)"),
        ("알 수 없다. 둘째 오류는 이미 선 깃발을 바꾸지 못해 사라진다.",
         "`glGetError`는 코드만 돌려준다. 깃발은 처음 난 오류를 쥔 채 읽힐 때까지 남는다. 구현에 따라 둘째 오류가 "
         "다른 깃발에 남기도 하므로 `GL_NO_ERROR`가 나올 때까지 읽는다. (5.2절, 5.3절)"),
        ("힌트는 “다음에 만들 창”에 대한 메모라서 이미 만든 창에는 닿지 않는다. 보통 컨텍스트가 만들어졌다.",
         "`GL_CONTEXT_FLAGS`를 읽어 `GL_CONTEXT_FLAG_DEBUG_BIT`가 서 있는지 본다. 일부러 틀린 호출을 넣어도 콜백이 "
         "조용한 것이 첫 신호다. (6.1절, 1-1강 4장)"),
        ("콜백이 틀린 호출 안에서, 같은 스레드에서 불린다는 약속이 없기 때문이다.",
         "드라이버가 다른 스레드에서, 또는 나중에 부를 수 있다. 그러면 호출 스택에 내 코드가 없다. Logger는 스레드가 "
         "하나라고 보고 만들어서, 두 스레드가 같은 스트림에 동시에 쓸 수 있다. (6.4절, 1-5강 6.4절)"),
        ("호출 하나하나는 규칙에 맞기 때문이다.",
         "GL이 검사하는 것은 “그 슬롯에 버퍼가 꽂혀 있는가, 인자가 범위 안인가”까지다. 꽂힌 것이 뜻한 버퍼인지는 "
         "GL이 알 수 없다. 이런 버그는 바인딩을 읽어 보거나 호출 순서를 따라가서 찾는다. (1.2절, 4.4절)"),
        ("`GL_INVALID_OPERATION`은 버그이고 `GL_OUT_OF_MEMORY`는 실패다.",
         "앞의 것은 코드가 규칙을 어겼을 때만 난다. 고칠 것은 코드다. 뒤의 것은 맞게 쓴 프로그램에서도 메모리가 "
         "모자라면 난다. (1-6강 2장, 5.1절)"),
    ]),
])

ch13 = glossary_chapter(13, [
    ("상태 기계", "state machine", "정해 둔 값이 바꿀 때까지 남아서 뒤의 호출에 쓰이는 방식"),
    ("스위치", "capability", "`glEnable`과 `glDisable`로 켜고 끄는 기능 하나"),
    ("가위 테스트", "scissor test", "정해 둔 사각형 밖의 픽셀을 건드리지 않게 하는 스위치"),
    ("객체", "OpenGL object", "버퍼, 텍스처처럼 컨텍스트 안에 만들어지는 것"),
    ("이름", "object name, `GLuint`", "객체를 가리키는 정수. 0은 “없음”이다"),
    ("바인드", "bind", "객체를 바인딩 포인트에 꽂는 일"),
    ("바인딩 포인트", "binding point, target", "“지금 쓰는 객체”의 이름이 들어가는 칸. 이 자료에서는 슬롯이라고 불렀다"),
    ("오류 깃발", "error flag, `glGetError`", "틀린 호출이 남기는 코드. 읽어 갈 때까지 남는다"),
    ("디버그 컨텍스트", "debug context", "드라이버가 검사를 더 하고 메시지를 자세히 내도록 만든 컨텍스트"),
    ("디버그 출력", "debug output", "드라이버가 오류와 경고를 문장으로 콜백에 건네주는 기능. OpenGL 4.3부터 표준"),
    ("디버그 콜백", "`GLDEBUGPROC`", "디버그 메시지를 받도록 등록하는 함수"),
    ("동기 출력", "synchronous debug output", "메시지를 낳은 호출 안에서, 같은 스레드에서 콜백을 부르게 하는 스위치"),
    ("심각도", "severity", "디버그 메시지에 드라이버가 매긴 네 단계의 무게"),
    ("호출 규약", "calling convention, `APIENTRY`", "인자를 어디에 싣고 스택을 누가 정리하는지에 대한 약속"),
    ("스레드 지역 저장소", "thread-local storage", "스레드마다 따로 있는 변수. 현재 컨텍스트가 이렇게 기억된다"),
    ("직접 상태 접근", "direct state access, DSA", "꽂지 않고 이름을 직접 넘겨 객체를 고치는 OpenGL 4.5의 함수들 (2-3강)"),
], pb=False)


def todo(mission: str, rows: list) -> Raw:
    """One mission of the task list: a heading and a small table kept on one page."""
    return keep(h4(mission),
                table([6, 54, 40], ["", "할 일", "됐는지 보는 법"], rows, cell_cls=["num", "", ""], compact=True))


ch14 = chapter(14, "할 일 목록", [
    keep(h3("14.1", "결정이 막히면"),
    p("7.2절의 여섯 가지를 고르지 못해 미션이 멈출 때 쓰는 기본 선택이다. 정답이 아니라 앞 강까지의 코드를 가장 덜 "
      "고치고 나중에 바꾸기 쉬운 쪽이다. 다른 선택을 해도 미션의 “통과”만 맞으면 된다."),
    table([36, 64], ["결정", "막혔을 때의 기본 선택"], [
        ["디버그 컨텍스트를 요청하는 방법", "`Init`이 Debug 구성에서 늘 요청한다. `Init`의 선언은 그대로 둔다"],
        ["콜백이 사는 곳과 등록하는 쪽", "Client의 `main.cpp`에 두고, `Init`이 성공한 뒤 Client가 등록한다"],
        ["메시지를 로그 레벨로 옮기는 기준", "심각도만 본다"],
        ["무엇을 어디서 거르는가", "Logger의 최소 레벨로 거른다. 알림은 평소에 보이지 않는 레벨로 보낸다"],
        ["동기 출력", "늘 켠다"],
        ["GL 오류에서 멈출 것인가", "로그만 남긴다"],
    ], cell_cls=["lab", ""], compact=True)),

    h3("14.2", "미션별 할 일"),
    todo("미션 1 — 네 코드를 읽고, 드라이버 정보를 로그에 남긴다", [
        ["1", "1.3절 표의 네 줄마다 네 코드에서 그 자리를 찾아 파일과 줄 번호를 적는다. 첫째 줄에는 `gl*` 호출의 "
              "개수를, 넷째 줄에는 지금의 최소 레벨과 flush 시점을 적는다", "빈 칸이 없다"],
        ["2", "`Init`이 성공한 뒤에 `glGetString`으로 회사, 장치, GL 버전, 셰이더 언어 버전을 읽는다",
         "중단점에서 보면 넷 다 널 포인터가 아니다"],
        ["3", "읽은 네 값을 Info 로그로 남긴다", "콘솔과 로그 파일 양쪽에 네 값이 Info 레벨로 찍힌다"],
    ]),
    todo("미션 2 — 상태가 남는 것을 눈으로 본다", [
        ["1", "`cbUpdate`에서 가위 테스트를 켜고, 창보다 작은 가위 사각형을 정하고, 엔진의 배경색과 다른 색으로 지운다",
         "창 안에 다른 색 사각형이 보인다"],
        ["2", "되돌리는 줄 없이 실행해 창이 어떻게 보이는지 적는다", "본 것이 글로 적혀 있다"],
        ["3", "다음 프레임이 물려받은 상태를 찾는다. 하나가 아니다 (힌트 1)", "찾은 상태가 전부 적혀 있다"],
        ["4", "찾은 것을 전부 되돌린다", "창 전체가 엔진의 배경색이고 작은 사각형만 다른 색이다. 깜빡이는 곳이 없다"],
    ]),
    todo("미션 3 — 이름, 객체, 슬롯을 확인한다", [
        ["1", "정점 배열 이름을 하나 받고, 꽂고, 뽑고, 지운다. 4.2절 예시의 네 호출과 같은 차례다. 호출 하나가 끝날 "
              "때마다 `glIsVertexArray`의 값을 찍는다", "찍힌 네 값이 4.2절 예시의 표와 같은 차례다"],
        ["2", "버퍼 이름을 하나 받아 슬롯에 꽂고, 그 슬롯에 꽂힌 이름을 읽는다. 읽는 상수는 3.4절의 표에 있다",
         "읽은 값이 받은 이름과 같다"],
        ["3", "만든 버퍼도 지운다", "`glIsBuffer`가 `GL_FALSE`를 돌려준다"],
    ]),
    todo("미션 4 — glGetError로 오류를 잡아 본다", [
        ["1", "`GL_INVALID_ENUM`, `GL_INVALID_VALUE`, `GL_INVALID_OPERATION`을 낼 호출을 하나씩 정한다. 5.1절 표의 "
              "예와 다른 호출이어야 한다", "세 호출이 적혀 있다"],
        ["2", "하나를 내고 바로 `glGetError`를 읽어 값을 찍는다. 셋 모두에 대해 한다", "찍힌 값이 5.1절 표의 “값” 칸과 같다"],
        ["3", "틀린 호출 둘을 연달아 낸 뒤 `glGetError`를 한 번만 읽어 찍는다", "둘 가운데 어느 코드가 나왔는지 적혀 있다"],
        ["4", "조금 뒤, 다른 호출을 몇 개 지난 자리에서 다시 읽어 찍는다", "나온 값이 적혀 있고, 5.2절의 그림으로 설명할 수 있다"],
    ]),
    todo("미션 5 — 디버그 컨텍스트를 요청하고 확인한다", [
        ["1", "`glfwInit()` 뒤, `glfwCreateWindow()` 앞에서 `GLFW_CONTEXT_DEBUG` 힌트로 디버그 컨텍스트를 요청한다. "
              "누가 언제 요청하게 할지는 7.2절의 첫째 결정이다", "힌트를 적는 줄이 두 호출 사이에 있다"],
        ["2", "`GL_CONTEXT_FLAGS`를 읽어 디버그 컨텍스트인지 가린다. 어느 비트를 볼지는 6.1절의 표에서 고른다",
         "중단점에서 읽은 값을 표의 비트로 풀 수 있다"],
        ["3", "디버그 컨텍스트인지 아닌지를 로그 한 줄로 남긴다", "Debug 구성으로 실행하면 “맞다”로 찍힌다"],
        ["4", "힌트를 창 생성 뒤로 옮겨 실행하고, 그 줄이 어떻게 바뀌는지 적는다", "바뀐 것이 글로 적혀 있다"],
        ["5", "힌트를 제자리로 돌린다", "다시 “맞다”로 찍힌다"],
    ]),
    todo("미션 6 — 콜백을 등록하고 첫 메시지를 받는다", [
        ["1", "`GLDEBUGPROC`와 같은 모양의 콜백을 선언한다 (7.3절). 둘 파일은 7.2절의 둘째 결정이다",
         "선언에 `APIENTRY`가 있고 마지막 인자에 `const`가 있다"],
        ["2", "출처·종류·심각도의 숫자를 이름으로 바꾼다. 6.3절의 표에 없는 값이 왔을 때 무엇을 내놓을지도 정한다 "
              "(7.3절의 질문)", "6.3절 표의 상수마다 이름이 하나씩 있다"],
        ["3", "종류와 심각도에서 로그 레벨을 정한다. 기준은 7.2절의 셋째 결정이다", "심각도 넷이 각각 어느 레벨이 되는지 말할 수 있다"],
        ["4", "콜백은 이름 셋, 번호, 문장을 한 줄로 만들어 그 레벨로 Logger에 넘긴다. 6.2절의 “콜백 안에서” 표를 지킨다",
         "콜백 안에 `gl*` 호출이 없고, `message` 포인터를 보관하지 않는다"],
        ["5", "`GL_DEBUG_OUTPUT`을 켜고 콜백을 `glDebugMessageCallback`으로 등록한다. 누가 등록하는가는 둘째 결정이다",
         "`Engine/`과 `Client/`에서 `glDebugMessageCallback`을 검색하면 한 줄이다"],
        ["6", "등록한 뒤에 `glDebugMessageInsert`로 메시지 하나를 직접 넣는다",
         "넣은 문장이 출처·종류·심각도의 이름, 번호와 함께 로그에 찍힌다"],
    ]),
    todo("미션 7 — 일부러 틀리고, 틀린 줄을 찾는다", [
        ["1", "미션 4에서 쓴 틀린 호출 하나를 다시 넣고 실행한다", "출처, 종류, 심각도, 번호, 문장이 붙은 줄이 정한 레벨과 색으로 찍힌다"],
        ["2", "동기 출력을 켜고 콜백에 중단점을 건다", "틀린 호출에서 중단점에 걸린다"],
        ["3", "호출 스택을 아래로 내려가 그 호출이 적힌 줄을 찾는다", "틀린 호출이 적힌 줄에 닿는다"],
        ["4", "동기 출력을 끄고 2 〜 3번을 되풀이해 달라진 점을 적는다. 같게 보여도 본 대로 적는다 (힌트 1)",
         "켰을 때와 껐을 때 본 것이 적혀 있다"],
        ["5", "동기 출력을 7.2절의 다섯째 결정대로 둔다", "`GL_DEBUG_OUTPUT_SYNCHRONOUS`를 `glIsEnabled`로 읽은 값이 결정과 맞다"],
        ["6", "GL 오류에서 멈출지를 여섯째 결정대로 둔다", "틀린 호출을 넣으면 결정한 대로 멈추거나 로그만 남는다"],
    ]),
    todo("미션 8 — 걸러 내고, 목록을 시작하고, 묶는다", [
        ["1", "무엇을 어디서 거를지를 7.2절의 넷째 결정대로 넣고, 알림 심각도의 메시지를 `glDebugMessageInsert`로 "
              "직접 넣는다", "넷째 결정에서 정한 대로 걸러진다"],
        ["2", "미션 2 〜 4의 실험 코드와 미션 7의 틀린 호출을 지운다. 드라이버 정보, 디버그 컨텍스트를 확인하는 줄, "
              "콜백과 그 등록은 남긴다", "창이 처음처럼 한 색으로 지워지고, 시작할 때의 로그는 그대로 찍힌다"],
        ["3", "`glGetError` 호출을 전부 지운다", "`Engine/`과 `Client/`에서 `glGetError`가 검색되지 않는다"],
        ["4", "7.4절의 목록에 이 강에서 되풀이했거나 불편했던 것을 세 줄 이상 적는다. 해법은 적지 않는다", "목록에 세 줄 이상 있다"],
        ["5", "7.2절의 여섯 결정마다 고른 것과 이유가 적혀 있는지 보고, 커밋 하나로 묶는다", "10장의 여섯 줄이 모두 맞다"],
    ]),
], lead="미션의 문장만으로 무엇을 하라는 것인지 분명하지 않을 때 보는 목록이다. 미션마다 할 일을 한 줄씩 풀고, 됐는지 "
        "보는 법을 옆에 적었다. 어떻게 하는지는 적지 않았다. 그것은 2 〜 6장과 미션의 힌트에 있다.", pb=True)

if __name__ == "__main__":
    info = build(
        {"title": f"ClaudGL Engine {ME['id']} {ME['title']} v{ME['ver']}",
         "footer": f"ClaudGL Engine · {ME['id']} {ME['title']} · v{ME['ver']}"},
        COVER, [ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8, ch9, ch10, ch11, ch12, ch13, ch14], OUT_HTML,
    )
    pages = render(OUT_HTML, OUT_PDF)
    print(f"pdf: {OUT_PDF} ({pages} pages)")
    print(f"tables: {info['tables']}  diagrams: {info['diagrams']}  code blocks: {info['code_blocks']}")
    print(f"issues: {info['issues']}")
