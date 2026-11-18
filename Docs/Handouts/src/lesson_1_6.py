"""Lesson 1-6 -- Assert and the error-handling policy (v2, lecture style).

Written for the code Claud has after lessons 1-4 and 1-5. That code is not in
the repository yet (the project was restarted from a libraries-only baseline on
2026-11-16), so engine code is referred to by function name only: no quotes
from the first pass and no file:line for engine files. Line numbers of project
settings (.vcxproj) and library declarations were read on READ_DATE.

Version 4 (2026-11-19): the reader found the missions vague and scattered.
Each mission step now states what must be done as plain statements and ends
with a "통과" (pass) condition, and a new last chapter 13 "할 일 목록" spells
every mission out as a task list with a way to check each task, plus a default
choice for each of the eight decisions of 6.2 for when the reader is stuck.
Chapters 1 to 12 keep their numbers; the eight mission steps keep their
numbers and meaning.

Run:  python -I src/lesson_1_6.py      (from Docs/Handouts, with the handout venv)
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

ME = lesson("1-6")
OUT_PDF = ROOT / handout_name(ME["id"])
OUT_HTML = ROOT / "_build" / "lesson_1_6.html"

# The day the project settings (.vcxproj) and the library headers were read.
READ_DATE = "2026-11-16"
# Toolchain of the PC the declarations were read on (the other PC may differ).
MSVC_VER = "MSVC 14.38"
SDK_VER = "Windows SDK 10.0.26100.0"

COVER = cover(
    f"CLAUDGL ENGINE · PART {ME['part']} · {ME['id']} · v{ME['ver']}",
    Raw('<span class="ac">ASSERT</span>( cond )'),
    ME["title"],
    "일어나면 안 되는 일이 일어난 바로 그 줄에서 멈춘다",
    [
        ("목표 결과물", "조건이 깨지면 식·파일·줄이 로그에 남고 디버거가 그 줄에서 멈춘다. 오류를 알리는 규칙이 한 쪽에 적혀 있다"),
        ("핵심 개념", "버그와 실패의 구분 · 전제 조건과 불변식 · assert 매크로 · `__debugbreak`와 `std::abort` · 오류 코드와 예외"),
        ("선수 지식", "1-4강(실패를 알리는 `Init`)과 1-5강(로그 매크로)을 끝낸 뒤에 한다"),
        ("예상 시간", f"읽기 1시간 + 구현 2시간 남짓 (계획서 기준 {ME['hours']}시간)"),
        ("건드릴 파일", "`Engine/Core/Assert.h`(새 파일), `Engine/Core/Logger.h`·`.cpp`, `Engine/Core/EngineCore.cpp`, "
                   "`Engine/Manager/InputManager.cpp`"),
        ("코드 기준", "1-4·1-5강을 끝낸 네 코드. 엔진 코드는 줄 번호가 아니라 함수 이름으로 가리킨다 (1.3절)"),
    ],
    note=("읽는 법",
          "2 〜 5장을 읽고 6장에서 결정을 적은 뒤 7장의 미션을 한다. 미션이 분명하지 않으면 13장의 할 일 목록을 본다."),
    toc=["왜 필요한가", "버그와 실패는 다르다", "assert가 하는 일", "멈추는 방법", "실패를 알리는 방법", "설계",
         "구현 미션", "흔한 함정", "완료 기준", "생각해 볼 질문", "해설", "용어집", "할 일 목록"],
)

# --------------------------------------------------------------------------
# figures
# --------------------------------------------------------------------------

def _frame(fig, x, y, w, h, name, sub=None, kind=""):
    """Call-stack frame: a box with a monospace name and an optional small second line."""
    fig.box(x, y, w, h, kind=kind)
    cx = x + w / 2
    if sub:
        fig.text(cx, y + h / 2 - 2.5, name, kind="mono", size=11)
        fig.text(cx, y + h / 2 + 11.5, sub, kind="s", size=9.5)
    else:
        fig.text(cx, y + h / 2 + 4, name, kind="mono", size=11)
    return fig


def _chip(fig, x, y, w, label, on=True):
    """One step of a macro: solid when the build keeps it, dashed when it is compiled out."""
    fig.box(x, y, w, 28, kind="accent" if on else "ghost")
    fig.text(x + w / 2, y + 18, label, kind="" if on else "s", size=10.5)
    return fig


def _kind_row(fig, y, name, english, off_eval, off_stop):
    """One macro kind: what is left in a build with checks on (left) and off (right)."""
    fig.box(20, y, 90, 40, name, english, kind="soft")
    for x0, ev, stop in ((125, True, True), (395, off_eval, off_stop)):
        _chip(fig, x0, y + 6, 105, "식을 계산한다", ev)
        _chip(fig, x0 + 125, y + 6, 120, "거짓이면 멈춘다", stop)
        if ev and stop:
            fig.arrow((x0 + 105, y + 20), (x0 + 125, y + 20))
        else:
            fig.line((x0 + 105, y + 20), (x0 + 125, y + 20), kind="muted dash")
    return fig


# 2.1 -- data from outside is validated once at the edge; inside, the promise is an assert.
FIG_BOUNDARY = (
    Fig(204)
    .text(20, 16, "프로그램 바깥", kind="s", anchor="start", size=10)
    .box(20, 26, 120, 34, "설정 파일")
    .box(20, 68, 120, 34, "사용자 입력")
    .box(20, 110, 120, 34, "네트워크")
    .box(250, 24, 390, 124, kind="soft")
    .text(628, 42, "프로그램 안쪽", kind="s", anchor="end", size=10)
    .text(250, 16, "경계", kind="t", size=10.5)
    .box(190, 58, 120, 54, "검증", "경계에서 한 번", kind="accent")
    .arrow((140, 43), (190, 72))
    .arrow((140, 85), (190, 85))
    .arrow((140, 127), (190, 98))
    .arrow((310, 85), (350, 85), kind="accent")
    .text(330, 77, "맞는 값", kind="s", size=9.5)
    .box(350, 66, 80, 38, "함수 A")
    .arrow((430, 85), (450, 85))
    .box(450, 66, 80, 38, "함수 B")
    .arrow((530, 85), (550, 85))
    .box(550, 66, 80, 38, "함수 C")
    .text(390, 120, "assert", kind="accent", size=9.5)
    .text(490, 120, "assert", kind="accent", size=9.5)
    .text(590, 120, "assert", kind="accent", size=9.5)
    .text(490, 138, "약속: 여기까지 온 값은 이미 검증되었다", kind="s", size=9.5)
    .arrow((205, 112), (205, 158))
    .text(198, 140, "틀린 값", kind="s", anchor="end", size=9.5)
    .box(130, 158, 150, 40, "실패로 처리", "반환값 · 로그 · 기본값", kind="dark")
    .text(445, 172, "이 약속이 깨졌다면 버그다", kind="t", size=10.5)
    .text(445, 188, "검증이 틀렸거나, 경계를 거치지 않은 길이 있다", kind="s", size=9.5)
)

# 3.4 -- what each macro kind leaves behind in the two builds.
FIG_KINDS = Fig(176)
FIG_KINDS.text(247, 16, "검사를 켠 빌드", kind="t").text(517, 16, "검사를 뺀 빌드", kind="t")
FIG_KINDS.line((382, 4), (382, 172), kind="muted dash")
_kind_row(FIG_KINDS, 26, "검사", "check", False, False)
_kind_row(FIG_KINDS, 76, "검증", "verify", True, False)
_kind_row(FIG_KINDS, 126, "항상", "always", True, True)

# 4.2 -- report, flush, stop: where the last log line is when the process dies.
FIG_ORDER = (
    Fig(162)
    .text(20, 15, "보고하고, flush하고, 멈출 때", kind="t", anchor="start", size=10.5)
    .box(20, 24, 130, 44, "보고", "글자가 버퍼에 들어간다")
    .arrow((150, 46), (180, 46))
    .box(180, 24, 130, 44, "flush", "버퍼에서 파일로 나간다", kind="accent")
    .arrow((310, 46), (340, 46))
    .box(340, 24, 130, 44, "멈춤", "프로세스가 끝난다", kind="dark")
    .arrow((470, 46), (500, 46), kind="muted")
    .box(500, 24, 140, 44, "로그 파일", "마지막 줄이 있다", kind="soft")
    .text(20, 99, "flush 없이 멈출 때", kind="t", anchor="start", size=10.5)
    .box(20, 108, 130, 44, "보고", "글자가 버퍼에 들어간다")
    .line((150, 130), (180, 130), kind="muted dash")
    .box(180, 108, 130, 44, "flush", "하지 않았다", kind="ghost")
    .arrow((310, 130), (340, 130), kind="muted dash")
    .box(340, 108, 130, 44, "멈춤", "버퍼도 함께 사라진다", kind="dark")
    .arrow((470, 130), (500, 130), kind="muted")
    .box(500, 108, 140, 44, "로그 파일", "마지막 줄이 없다", kind="ghost")
)

# 4.3 -- where the debugger stands: break inside a helper function vs inside the macro.
FIG_STACK = Fig(172)
FIG_STACK.text(20, 16, "멈추는 문장이 함수 안에 있을 때", kind="t", anchor="start", size=10.5)
FIG_STACK.text(350, 16, "멈추는 문장이 매크로 안에 있을 때", kind="t", anchor="start", size=10.5)
FIG_STACK.line((330, 6), (330, 168), kind="muted dash")
FIG_STACK.arrow((22, 48), (56, 48), kind="accent")
_frame(FIG_STACK, 60, 28, 250, 40, "Check( bool ok )", "보고 함수의 파일 · __debugbreak()가 적힌 줄", kind="accent")
_frame(FIG_STACK, 60, 73, 250, 40, "GetSlot( int index )", "Inventory.cpp · Check( index < count ) 줄")
_frame(FIG_STACK, 60, 118, 250, 28, "main()", kind="soft")
FIG_STACK.text(185, 163, "보고 싶은 줄은 둘째 칸이다. 매번 한 칸 옮겨 가야 한다", kind="s", size=9.5)
FIG_STACK.arrow((352, 48), (386, 48), kind="accent")
_frame(FIG_STACK, 390, 28, 250, 40, "GetSlot( int index )", "Inventory.cpp · ASSERT( index < count ) 줄", kind="accent")
_frame(FIG_STACK, 390, 73, 250, 28, "main()", kind="soft")
FIG_STACK.text(515, 163, "맨 위 칸이 곧 깨진 조건이 적힌 줄이다", kind="s", size=9.5)

# 5.2 -- an exception thrown in a callback has to cross a C frame.
FIG_EXC = (
    Fig(176)
    .text(20, 16, "호출 스택 (위가 가장 최근)", kind="s", anchor="start", size=10)
    .box(20, 26, 270, 42, "키 콜백 (C++)", "여기서 throw", kind="accent")
    .box(20, 76, 270, 42, "glfwPollEvents() 안쪽 (C)", "catch도 소멸자도 없다. 예외라는 것을 모른다", kind="dark")
    .box(20, 126, 270, 42, "main() (C++)", "catch ( … )", kind="soft")
    .arrow((290, 47), (318, 47), (318, 147), (290, 147), kind="accent")
    .text(328, 86, "예외가 지나가는 길", kind="accent", anchor="start", size=9.5)
    .text(328, 101, "C 프레임을 지나는 동작은", kind="s", anchor="start", size=9.5)
    .text(328, 115, "C++ 표준이 정하지 않는다", kind="s", anchor="start", size=9.5)
    .text(480, 16, "대신 할 수 있는 것", kind="s", anchor="start", size=10)
    .box(480, 26, 160, 42, "콜백 안에서 잡는다", "예외가 밖으로 나가지 않는다")
    .box(480, 76, 160, 42, "기록하고 돌아간다", "루프로 돌아온 뒤 처리한다")
)

# --------------------------------------------------------------------------

ch1 = chapter(1, "왜 필요한가", [
    h3("1.1", "잘못 불러도 조용히 넘어간다"),
    p("1-3강에서 만든 입력 조회 함수에 `EKey`에 없는 숫자를 넘기면 무슨 일이 일어나는가. 함수가 할 수 있는 일은 둘 중 "
      "하나다. 범위를 검사해서 `false`를 돌려주거나, 검사 없이 배열을 읽는다. 앞쪽은 “안 눌렸다”와 구별되지 않는 값이고, "
      "뒤쪽은 배열 밖의 메모리를 읽는 정의되지 않은 동작이다. 어느 쪽이든 ==잘못 부른 쪽은 아무것도 모른 채 계속 간다==."),
    p("이런 자리는 입력에만 있지 않다. 아래 세 자리를 네 코드에서 찾아 지금 어떻게 되어 있는지 확인한다. 함수 이름은 "
      "앞 강 자료의 이름이다."),
    table([30, 30, 40], ["네 코드에서 확인할 것", "볼 자리", "왜 문제인가"], [
        ["잘못된 키를 받은 조회 함수는 무엇을 돌려주는가", "`MInputManager`의 `IsKeyPressed`, `IsKeyHeld`, `IsKeyReleased`",
         "`false`를 돌려준다면 잘못 부른 것과 “안 눌렸다”가 같은 값이다. 로그를 찍어도 프로그램은 계속 가고, "
         "누가 불렀는지는 남지 않는다"],
        ["`Init` 전에 입력 관리자를 달라고 하면 무엇이 나오는가", "`GEngine::GetInputManager`",
         "`nullptr`이 나온다면 죽는 곳은 받아 쓴 쪽의 `->`이고, 원인은 여기다"],
        ["키 콜백은 user pointer에서 꺼낸 값을 확인하고 쓰는가",
         "`MInputManager::cbSetKey`, 그리고 `GEngine::Init`에서 user pointer와 콜백을 다는 두 줄",
         "user pointer를 다는 줄이 빠지거나 그 전에 콜백이 불리면, 콜백 안에서 `nullptr`을 역참조한다"],
    ], cell_cls=["", "", ""]),
    box("ex", "예시: 원인과 증상 사이의 거리", [
        code(r"""
int FindSlot( int item_id );      // returns -1 when the id is unknown

int slot = FindSlot( 9999 );      // the bug is here: 9999 is a typo for 999
_counts[slot] += 1;               // writes to _counts[-1], and nothing visible happens
// ... much later a nearby variable holds a strange value, and nothing points back here
""", title="the cause and the symptom are far apart", tag="bad"),
        p("틀린 곳은 `FindSlot( 9999 )`를 부른 줄인데, 이상한 값이 눈에 띄는 것은 한참 뒤 다른 변수에서다. 그때의 호출 "
          "스택에는 이 줄이 없다. 배열에 쓰기 전에 “`slot`은 0 이상이다”라는 검사가 있었다면, 틀린 바로 그 자리에서 "
          "호출 스택과 지역 변수가 그대로 남은 채 멈춘다. 이 강에서 만드는 것이 그 검사다."),
    ]),
    p("표의 세 자리는 모두 “코드를 맞게 썼다면 일어나지 않는 일”이다. 이런 일을 값 하나로 돌려주거나 로그 한 줄로 "
      "흘려보내면, 원인에서 먼 곳에서 다른 모습으로 나타난다. 일어난 그 줄에서 멈추고 호출 스택이 살아 있을 때 "
      "들여다보는 편이 싸다."),

    keep(h3("1.2", "앞 강에서 넘어온 것"),
    table([46, 28, 26], ["미뤄 둔 것", "어디서", "이 자료에서"], [
        ["조건이 깨지면 그 자리에서 멈추기", "1-4강 6.5절", "3장, 4장"],
        ["`Fatal` 로그에서 멈추기", "1-5강 6.4절", "4.2절, 6.2절"],
        ["엔진 전체의 오류 정책 (오류 코드인가 예외인가)", "1-4강 2.4절, 6.5절", "5장, 6.2절"],
    ], cell_cls=["", "c", "c"])),

    h3("1.3", "이 자료의 코드 기준"),
    p(f"이 자료는 ==1-4강과 1-5강을 끝낸 뒤의 네 코드==를 기준으로 쓴다. 그 코드는 이 자료를 쓰는 날({READ_DATE})에는 "
      "아직 저장소에 없다. 그래서 엔진 코드는 `파일:줄`이 아니라 함수 이름으로 가리키고, 인용하는 대신 "
      "“네 코드에서 확인할 것” 표로 적는다 (1.1절, 6.4절). 파일 경로는 앞 강 자료의 배치를 따랐다. 네 배치가 "
      "다르면 네 것이 맞다."),
    p("`파일:줄`로 적은 것은 지금 저장소에 실제로 있는 파일뿐이다. 프로젝트 설정의 줄 번호(`Engine/Engine.vcxproj:145`, "
      f"`:149`, `:159`, `:163`, `Client/Client.vcxproj:135`, `:154`)는 {READ_DATE}의 파일 기준이다. 설정을 고치면 줄이 "
      "밀리므로, 쓰기 전에 값의 이름(`PreprocessorDefinitions`, `WarningLevel`)으로 다시 찾는다. 표준 라이브러리와 "
      f"Windows의 선언은 이 자료를 만든 PC의 {MSVC_VER}과 {SDK_VER}에서 읽었고, 카드에는 줄 번호 대신 헤더 이름을 적었다."),
], lead="엔진은 잘못된 호출을 받아도 값 하나를 돌려주고 계속 간다. 그래서 버그가 원인에서 먼 곳에서 드러난다.")

ch2 = chapter(2, "버그와 실패는 다르다", [
    table([18, 41, 41], ["", "실패", "버그"], [
        ["무엇인가", "맞게 쓴 프로그램에서도 일어나는 일", "코드가 틀렸을 때만 일어나는 일"],
        ["예", "파일이 없다, 드라이버가 요청한 GL 버전을 만들지 못한다, 디스크가 찼다",
         "범위를 벗어난 인덱스, `Init` 전에 쓴 포인터, 있을 수 없는 열거형 값"],
        ["원인이 있는 곳", "프로그램 바깥 (환경, 사용자, 데이터)", "프로그램 안 (호출한 코드)"],
        ["고치는 사람", "사용자나 운영 환경. 프로그램은 알리고 물러난다", "프로그래머. 코드를 고친다"],
        ["다루는 도구", "반환값, 예외, 로그 (1-4강, 5장)", "assert (3장)"],
        ["릴리스 빌드에서", "반드시 처리한다", "검사를 뺄 수 있다 (3.4절)"],
    ], cell_cls=["lab", "", ""]),
    p("1-4강의 초기화 실패는 왼쪽 칸이다. `glfwCreateWindow`가 `nullptr`을 돌려주는 일은 코드를 아무리 맞게 써도 "
      "일어난다. 1.1절 표의 세 자리는 오른쪽 칸의 후보다."),
    p("둘을 섞으면 양쪽으로 다 곤란해진다. 실패를 버그처럼 다루면, 사용자의 PC에 파일 하나가 없다는 이유로 프로그램이 "
      "죽거나, 검사를 뺀 빌드에서 틀린 값이 그대로 들어온다. 버그를 실패처럼 다루면, 틀린 코드는 고쳐지지 않은 채 남고 "
      "부르는 쪽마다 일어날 수 없는 경우를 처리하는 코드가 붙는다."),

    h3("2.1", "어느 쪽인지 가르는 질문"),
    p("기준은 하나다. **그 값은 어디서 왔는가.** 코드 안에서 만들어진 값이 틀렸으면 버그이고, 바깥에서 들어온 값이 "
      "틀렸으면 실패다."),
    keep(table([40, 16, 44], ["경우", "어느 쪽", "이유"], [
        ["셰이더 파일이 그 경로에 없다 (2-4강)", "실패", "파일은 프로그램 바깥에 있다. 배포한 폴더에서 빠질 수 있다"],
        ["키 콜백에 `GLFW_KEY_UNKNOWN`(-1)이 들어왔다", "둘 다 아니다",
         "GLFW가 모르는 키를 알리는 정상 값이다 (`include/GLFW/glfw3.h:367`). 걸러 내는 코드가 있으면 된다"],
        ["`switch`가 모든 `ELogLevel`을 다뤘는데 `default`에 닿았다", "버그",
         "있을 수 없는 값이다. 열거형에 값을 더하고 `switch`를 잊었거나 메모리가 깨졌다"],
        ["`EKey`에 없는 숫자를 `IsKeyPressed`에 넘겼다", "==직접 판단==",
         "그 숫자가 코드에 적힌 상수인가, 설정 파일에서 읽은 값인가 (10장의 6번)"],
        ["Client가 Update 콜백을 달지 않고 `Run()`을 불렀다", "==직접 판단==",
         "엔진이 콜백 없이 도는 것을 허용하는가. 허용하면 정상이고, 아니면 전제 조건을 어긴 것이다"],
    ], cell_cls=["", "c", ""])),
    box("warn", "바깥에서 온 값은 assert로 검사하지 않는다",
        "파일 내용, 사용자 입력, 네트워크로 받은 값은 틀릴 수 있는 것이 정상이다. 이런 값을 assert로 검사하면 "
        "검사를 뺀 빌드에서(3.4절) 틀린 값이 그대로 안으로 들어온다. 경계에서 한 번 검증해 실패로 처리하고, "
        "그 안쪽에서는 “이미 검증된 값”이라는 약속을 assert로 적는다."),
    FIG_BOUNDARY.render("바깥의 값은 경계에서 한 번 검증한다. 틀리면 실패로 처리하고, 맞으면 안으로 들인다. 안쪽의 "
                        "assert는 값을 다시 거르는 것이 아니라 “검증을 지나온 값”이라는 약속을 적는 것이다."),
    box("ex", "예시: 같은 값 0, 다른 도구", [
        table([40, 22, 38], ["상황", "값이 온 곳", "하는 일"], [
            ["설정 파일에서 읽은 창 너비가 0이다", "바깥 (파일)", "실패다. 경고를 남기고 기본값을 쓰거나 실행을 거절한다"],
            ["검증을 통과한 너비를 받은 함수 안에서 0이다", "안 (검증을 지난 값)",
             "버그다. assert로 멈춘다. 검증 코드가 틀렸거나 경계를 거치지 않은 길이 있다"],
            ["코드에 직접 적은 `Resize( 0, 600 )`", "안 (소스 코드의 상수)", "버그다. assert로 멈춘다. 고칠 것은 그 줄이다"],
        ], cell_cls=["", "c", ""], compact=True),
        p("숫자는 셋 다 0인데 다루는 도구가 다르다. 가르는 것은 값이 아니라 값이 지나온 길이다."),
    ]),

    keep(h3("2.2", "약속의 세 종류"),
    table([18, 34, 48], ["종류", "뜻", "예 (네 코드에서 찾아 본다)"], [
        ["전제 조건", "부르는 쪽이 지켜야 하는 것", "`IsKeyPressed( key )`에 넘기는 `key`는 `EKey`에 있는 값이다"],
        ["사후 조건", "함수가 끝났을 때 보장하는 것", "`Init`이 성공을 돌려주면 창과 입력 관리자가 만들어져 있다"],
        ["불변식", "객체가 살아 있는 동안 늘 참인 것", "`Run()`이 도는 동안 창 핸들을 담은 멤버는 `nullptr`이 아니다"],
    ], cell_cls=["lab", "", ""])),
    p("assert는 이 약속을 코드에 적는 방법이다. 주석으로 적은 약속은 깨져도 아무 일이 없지만, assert로 적은 약속은 "
      "깨지는 순간 알려 준다. 그래서 assert는 실행되는 문서이기도 하다."),
    box("ex", "예시: 고정 크기 스택의 세 약속", [
        table([46, 18, 36], ["약속", "종류", "깨졌다면 틀린 코드는"], [
            ["`Pop()`은 비어 있지 않을 때만 부른다", "전제 조건", "`Pop()`을 부른 쪽"],
            ["`Push( v )`가 끝나면 `Top()`은 `v`이고 개수는 1 늘어 있다", "사후 조건", "`Push` 자신"],
            ["개수는 늘 0 이상 `kCapacity` 이하다", "불변식", "멤버를 건드리는 함수 가운데 하나"],
        ], cell_cls=["", "c", ""], compact=True),
        p("어떤 약속이 깨졌는지를 알면 어느 코드를 열어야 하는지가 정해진다. 전제 조건이 깨졌으면 그 함수 안이 아니라 "
          "부른 쪽을 본다. 디버거가 멈췄을 때 호출 스택에서 호출한 쪽의 칸으로 옮겨 가는 이유다."),
    ]),
    box("ue", None,
        "`check( 조건 )`이 이 강의 assert다. 거짓이면 멈춘다. `verify( 식 )`은 검사를 뺀 빌드에서도 식은 실행한다. "
        "`ensure( 조건 )`은 멈추지 않고 호출 스택을 보고한 뒤 계속 가며, 같은 자리에서는 한 번만 보고한다. "
        "`checkf`와 `ensureMsgf`는 형식 문자열로 메시지를 붙인다. Shipping 빌드에서는 `check`가 기본으로 빠진다."),
    box("cs", None,
        "전제 조건·사후 조건·불변식은 “계약에 의한 설계(Design by Contract)”의 용어다. 자료구조 책의 루프 불변식, "
        "이진 탐색 트리의 “왼쪽은 작고 오른쪽은 크다”가 같은 종류의 문장이다. 정확성을 증명할 때 쓰는 문장을 "
        "실행 중에 검사하는 것이 assert다."),
], lead="둘은 원인이 있는 곳이 다르고, 그래서 다루는 도구가 다르다.")

ch3 = chapter(3, "assert가 하는 일", [
    h3("3.1", "표준 assert"),
    p("C++에는 이미 두 가지가 있다. 실행 중에 검사하는 `assert`와 컴파일할 때 검사하는 `static_assert`다. 직접 만들기 "
      "전에 이 둘이 정확히 무엇을 하는지부터 본다."),
    fn("assert",
       "assert( expression );          // function-like macro, defined by <cassert>",
       "`expression`이 참이면 아무 일도 하지 않는다. 거짓이면 식의 글자, 파일 이름, 줄 번호를 알리고 `std::abort()`를 부른다.",
       params=[("`expression`", "참이어야 하는 조건. `bool`로 바뀔 수 있는 식이면 된다. 포인터를 그대로 넣으면 "
                               "`nullptr`이 아닌지를 본다")],
       returns="없다. 전체가 `void` 식이라 값을 받아 쓸 수 없다",
       notes=[("거짓이면", "`Assertion failed: 식, file 파일, line 줄` 꼴의 글을 내보낸 뒤 `std::abort()`(4.1절)를 부른다. "
                        "글은 콘솔 프로그램이면 `stderr`로, 창 프로그램이면 대화상자로 나간다"),
              ("`NDEBUG`가 있으면", "`((void)0)`으로 바뀐다. `expression`은 ==계산조차 되지 않는다=="),
              ("주의", "`NDEBUG`는 `<cassert>`를 포함하는 순간의 것을 본다. 포함할 때마다 `assert`가 다시 정의된다"),
              ("헤더", "`<cassert>`. MSVC에서 실제 정의는 Windows SDK의 `ucrt/assert.h`에 있다")],
       lib="C++ 표준 라이브러리"),
    p("이 프로젝트의 Debug 구성은 `_DEBUG`를, Release 구성은 `NDEBUG`를 정의한다 (`Engine/Engine.vcxproj:145`, `:163`, "
      "`Client/Client.vcxproj:135`, `:154`). 두 이름은 짝이 아니다. `NDEBUG`는 표준이 `assert`를 끄는 스위치로 정한 "
      "이름이고, `_DEBUG`는 MSVC가 디버그용 런타임 라이브러리를 쓸 때 정의하는 이름이다. 둘 다 없는 빌드도 만들 수 있다."),
    p("MSVC는 실패 메시지를 `stderr`에 찍을지 대화상자로 띄울지를 프로그램 종류와 런타임 설정(`_set_error_mode`)에 "
      "따라 정한다. 실제로 무엇이 보이는지는 미션 1에서 직접 본다."),
    box("ex", "예시: `assert`가 펼쳐진 모습", [
        code(r"""
assert( hp <= max_hp );                        // what you write: Player.cpp, line 27

// NDEBUG not defined: the condition runs; only when it is false, _wassert() reports and aborts
((void)( (!!( hp <= max_hp )) || ( _wassert( L"hp <= max_hp", L"Player.cpp", 27 ), 0 ) ));

// NDEBUG defined: nothing is left, hp and max_hp are not even read
((void)0);
""", title="what the preprocessor hands to the compiler (MSVC, simplified)", tag="syntax"),
        p("가운데 줄을 안쪽부터 읽는다. `!!( 조건 )`은 조건을 `bool`로 바꾼다. `A || B`는 `A`가 참이면 `B`를 계산하지 "
          "않으므로(단락 평가), 보고 함수 `_wassert`는 조건이 거짓일 때만 불린다. 맨 앞의 `(void)`는 결과 값을 버린다. "
          "`if` 문이 아니라 식 하나로 만든 것은, 식이 들어갈 수 있는 자리 어디에나 쓸 수 있게 하려는 것이다."),
        p("`L\"hp <= max_hp\"`는 조건의 글자이고(3.3절의 `#`), 파일 이름과 줄 번호는 `__FILE__`과 `__LINE__`이 펼쳐진 "
          "값이다. 파일 이름이 경로를 어디까지 담는지는 컴파일 옵션에 따라 다르다."),
    ]),
    fn("static_assert",
       "static_assert( constant_expression, \"message\" );\n"
       "static_assert( constant_expression );                // since C++17",
       "컴파일하는 동안 조건을 검사한다. 거짓이면 그 줄에서 컴파일이 멈춘다. 매크로도 함수도 아닌 키워드라서 헤더가 "
       "필요 없다.",
       params=[("`constant_expression`", "컴파일할 때 값이 정해지는 조건. `sizeof`, `constexpr` 상수, 타입 검사 같은 것"),
               ("`\"message\"`", "오류에 함께 나올 문자열 리터럴. C++17부터 생략할 수 있다 (이 프로젝트는 C++20이다, "
                               "`Engine/Engine.vcxproj:149`)")],
       returns="없다. 실행 파일에 아무것도 남기지 않는다",
       notes=[("거짓이면", "컴파일 오류가 난다. MSVC의 번호는 C2338이고, 메시지를 생략했으면 C2607이다"),
              ("쓸 수 있는 곳", "함수 안, 클래스 안, 파일 범위 어디에나 선언처럼 쓴다"),
              ("`NDEBUG`", "영향을 받지 않는다. 모든 구성에서 검사한다")],
       lib="C++ 언어 (C++11)"),
    p("컴파일할 때 이미 알 수 있는 조건은 `static_assert`에 맡긴다. 빌드에서 걸리고 실행 비용이 없다."),
    box("ex", "예시: 언제 알 수 있는 조건인가", [
        table([42, 22, 36], ["조건", "값이 정해지는 때", "맞는 도구"], [
            ["`sizeof( FileHeader ) == 16`", "컴파일할 때", "`static_assert`"],
            ["`kMaxSlots <= 256` (`constexpr` 상수)", "컴파일할 때", "`static_assert`"],
            ["`index < count`", "실행 중", "`assert`"],
            ["`file.is_open()`", "실행 중", "둘 다 아니다. 버그가 아니라 실패다 (2장)"],
        ], cell_cls=["", "c", ""], compact=True),
    ]),

    h3("3.2", "직접 만드는 이유"),
    p("표준 `assert`로 충분하다면 만들 이유가 없다. 엔진이 자기 것을 만드는 이유는 아래 네 줄이다."),
    table([22, 38, 40], ["", "표준 `assert`", "직접 만든 매크로"], [
        ["메시지", "식의 글자뿐이다", "형식 문자열로 그때의 값을 함께 남길 수 있다"],
        ["나가는 곳", "`stderr` 또는 대화상자", "엔진의 Logger. 콘솔과 파일에 같이 남는다"],
        ["멈추는 자리", "런타임 라이브러리 안 (`abort`)", "조건이 적힌 줄 (4.3절)"],
        ["빌드별 동작", "`NDEBUG` 하나로 전부 켜고 끈다", "종류를 나누어 다르게 정할 수 있다 (3.4절)"],
    ], cell_cls=["lab", "", ""]),

    h3("3.3", "매크로의 구성"),
    flow([
        ("조건 평가", "거짓일 때만 계속"),
        ("수집", "식의 글자 · 파일 · 줄", "accent"),
        ("보고", "Logger로"),
        ("flush", "파일까지"),
        ("멈춤", "그 줄에서", "dark"),
    ], "함수가 아니라 매크로여야 하는 조각이 있다. 식의 글자와 호출한 줄은 호출한 자리에서만 얻을 수 있다."),
    p("함수 `Check( index < count )`가 받는 것은 `false`라는 값 하나다. 어떤 식이 거짓이었는지는 함수 안에서 알 길이 "
      "없다. 매크로는 컴파일 전에 글자를 바꿔 넣는 장치라서, 호출한 자리의 글자와 위치를 붙잡을 수 있다. "
      "`std::source_location`(1-5강)을 쓰면 파일과 줄은 함수로도 받을 수 있지만, 식의 글자와 “그 줄에서 멈추기”(4.3절)는 "
      "매크로만 할 수 있다."),
    code(r"""
#define TEXT_OF( x ) #x              // the # operator turns the argument into a string literal

const char* s = TEXT_OF( a + b );    // "a + b"
""", tag="syntax"),
    p("`#`은 매크로 인자를 글자 그대로 문자열 리터럴로 바꾼다. 조건이 깨졌을 때 `index < count`라는 글자를 로그에 "
      "찍을 수 있는 것은 이 연산자 덕이다. `__FILE__`과 `__LINE__`이 호출한 자리의 값이 되는 이유는 1-5강 3.1절과 같다."),
    box("ex", "예시: 실제 조건을 글자로 바꾸면", [
        table([40, 30, 30], ["쓴 것", "결과", "읽는 법"], [
            ["`TEXT_OF( hp <= max_hp )`", "`\"hp <= max_hp\"`", "쓴 그대로다"],
            ["`TEXT_OF( items.size() < MAX_SLOTS )`", "`\"items.size() < MAX_SLOTS\"`", "매크로 이름도 펼쳐지지 않고 남는다"],
            ["`TEXT_OF( ptr )`", "`\"ptr\"`", "이름뿐이다. 값은 담기지 않는다"],
        ], cell_cls=["", "", ""], compact=True),
        p("셋째 줄이 3.2절의 첫 행이다. 식의 글자만으로는 `index`가 몇이었는지 알 수 없어서 메시지를 받는 매크로가 "
          "따로 필요해진다. 이 문자열들은 실행 파일 안에 들어가고, 검사를 뺀 빌드에서는 함께 사라진다."),
    ]),
    keep(table([28, 72], ["매크로라서 생기는 일", "assert에서 나타나는 모습"], [
        ["인자가 사라질 수 있다", "`ASSERT( ++count < 10 )`. 검사를 뺀 빌드에서는 `++count`도 사라진다. "
                           "Debug에서만 맞게 도는 프로그램이 된다"],
        ["쉼표가 인자를 가른다", "`ASSERT( Is<int, float>() )`. 전처리기는 `<>`를 괄호로 치지 않아 인자를 둘로 센다. "
                         "조건을 `( )`로 한 번 더 감싼다"],
        ["문장 하나로 보여야 한다", "`if ( x ) ASSERT( y ); else …`. 1-5강 3.1절의 `do { … } while ( 0 )`이 "
                            "여기서도 필요하다"],
        ["검사에만 쓰는 변수", "검사를 뺀 빌드에서 그 변수는 쓰이지 않는 변수가 된다 (8장)"],
    ], cell_cls=["lab", ""])),
    box("ex", "예시: 쉼표가 든 조건", [
        table([40, 20, 40], ["쓴 것", "센 인자", "결과"], [
            ["`ASSERT( Max( a, b ) > 0 )`", "1개", "된다. `( )` 안의 쉼표는 세지 않는다"],
            ["`ASSERT( IsSame<int, float>() )`", "2개", "경고 C4002, 이어서 문법 오류가 난다"],
            ["`ASSERT( v == Vec2{ 1, 2 } )`", "2개", "위와 같다. `{ }`도 괄호로 치지 않는다"],
            ["`ASSERT( ( IsSame<int, float>() ) )`", "1개", "된다. 조건 전체를 `( )`로 감쌌다"],
        ], cell_cls=["", "c", ""], compact=True),
        p("전처리기가 인자를 셀 때 아는 괄호는 `( )` 하나뿐이다. 둘째 줄은 `IsSame<int`와 `float>()` 두 조각이 된다."),
    ]),

    keep(h3("3.4", "빌드에 따라 달라지는 것"),
    table([14, 27, 27, 32], ["종류", "검사를 켠 빌드", "검사를 뺀 빌드", "쓰는 곳"], [
        ["검사", "식을 계산하고, 거짓이면 멈춘다", "식도 검사도 없다", "비용이 드는 내부 점검. 식에 부작용이 없어야 한다"],
        ["검증", "식을 계산하고, 거짓이면 멈춘다", "식은 계산하고 결과는 버린다", "해야 하는 일을 하면서 그 결과도 확인할 때"],
        ["항상", "식을 계산하고, 거짓이면 멈춘다", "똑같이 한다", "싸고, 깨지면 더 갈 수 없는 조건"],
    ], cell_cls=["lab", "", "", ""])),
    FIG_KINDS.render("점선은 그 빌드에서 사라지는 조각이다. 검사는 식까지 사라지고, 검증은 식만 남고, 항상은 그대로 남는다."),
    p("세 종류를 다 둘 필요는 없다. 무엇을 둘지, 그리고 “검사를 뺀 빌드”를 무엇으로 가를지(`_DEBUG`인가, `NDEBUG`인가, "
      "따로 만든 스위치인가)는 6.2절에서 정한다."),
    box("cs", None,
        "Debug와 Release는 최적화만 다른 것이 아니다. 정의된 매크로가 다르고, 링크하는 런타임 라이브러리가 다르고, "
        "assert가 사라지면 실행되는 코드 자체가 달라진다. “Debug에서는 되는데 Release에서 안 된다”의 상당수가 "
        "여기서 나온다. 컴파일러 책의 조건부 컴파일과 최적화 장에 닿는다."),
], lead="assert는 조건이 거짓일 때 무엇이 어디서 깨졌는지 알리고 멈추는 매크로다. 표준에 하나가 있고, 엔진은 보통 "
        "자기 것을 만든다.")

ch4 = chapter(4, "멈추는 방법", [
    keep(h3("4.1", "네 가지 끝"),
    table([18, 36, 23, 23], ["방법", "일어나는 일", "디버거가 붙어 있으면", "디버거가 없으면"], [
        ["`__debugbreak`", "그 자리에서 중단점 예외를 일으킨다 (MSVC 내장 함수)", "그 줄에서 멈춘다. 이어서 실행할 수 있다",
         "처리되지 않은 예외로 프로세스가 끝난다"],
        ["`std::abort`", "정리 없이 끝낸다. 지역·정적 객체의 소멸자와 `atexit` 함수가 불리지 않는다",
         "런타임 라이브러리 안에서 멈춘다", "디버그용 런타임에서는 종료 코드 3으로 끝난다 (MSVC)"],
        ["`std::terminate`", "잡지 않은 예외나 `noexcept` 위반 때 불린다. 기본 동작은 `abort()`다", "`abort()`와 같다",
         "`abort()`와 같다"],
        ["`std::exit`", "정적 객체의 소멸자와 `atexit` 함수는 불린다. 지역 객체의 소멸자는 불리지 않는다",
         "멈추지 않고 끝난다", "준 코드로 끝난다"],
    ], cell_cls=["lab", "", "", ""], compact=True)),
    p("표의 행마다 함수를 하나씩 본다. 앞의 둘은 디버거와 이야기하는 함수이고, 뒤의 셋은 프로세스를 끝내는 함수다."),

    h4("디버거와 이야기하는 함수"),
    fn("__debugbreak", "void __debugbreak(void);",
       "이 줄에서 중단점 예외를 일으킨다. 소스 코드에 박아 넣은 중단점이다.",
       returns="없다. 디버거에서 ‘계속’을 누르면 바로 다음 문장부터 이어서 실행된다",
       notes=[("디버거가 붙어 있으면", "디버거가 이 줄에 선다. 호출 스택과 지역 변수가 그대로 보인다"),
              ("디버거가 없으면", "아무도 받지 않는 예외가 되어 프로세스가 끝난다. 종료 코드는 예외 번호 `0x80000003`이다. "
                             "설정에 따라 디버거를 붙일지 묻는 창이 먼저 뜰 수 있다"),
              ("종류", "함수처럼 보이지만 컴파일러 내장 함수다. 호출이 아니라 CPU 명령 하나(x64에서는 `int 3`)로 바뀐다"),
              ("헤더", "`<intrin.h>`. MSVC 전용이다")],
       lib="MSVC 내장 함수"),
    fn("IsDebuggerPresent", "BOOL IsDebuggerPresent(void);",
       "이 함수를 부른 프로세스에 디버거가 붙어 있는지 알려 준다.",
       returns="붙어 있으면 0이 아닌 값, 아니면 0. `BOOL`은 `int`의 다른 이름이라 `if`에 그대로 쓸 수 있다",
       notes=[("보는 범위", "사용자 모드 디버거. Visual Studio에서 F5로 실행했거나, 실행 중인 프로세스에 디버거를 붙인 경우다"),
              ("값이 바뀐다", "실행 도중에 디버거를 붙이거나 떼면 그때부터 값이 달라진다. 한 번 물어 저장해 둔 값은 낡을 수 있다"),
              ("헤더", "`<Windows.h>` (선언은 `debugapi.h`). 무거운 헤더이고 `min`, `max` 같은 매크로를 함께 들여온다. "
                     "어느 파일에서 포함할지 따져 본다 (6.3절)")],
       lib="Windows API"),
    p("Visual Studio에서 F5는 디버거를 붙여 실행하고 Ctrl+F5는 붙이지 않고 실행한다. `__debugbreak()`의 결과가 둘에서 "
      "다르다. 디버거 없이 만나면 창이 말없이 사라진 것처럼 보이므로, 그 경우에 무엇을 보여 줄지 정해야 한다 (6.2절). "
      "`__debugbreak()`는 MSVC 전용이다. 멈추는 문장을 매크로 하나 뒤에 두면 다른 컴파일러로 갈 때 바꿀 곳이 한 줄이다. "
      "C++26의 `<debugging>`에 `std::breakpoint()`와 `std::is_debugger_present()`가 들어오지만 지금 설정(C++20)에서는 "
      "쓸 수 없다."),

    h4("프로세스를 끝내는 함수"),
    fn("std::abort", "[[noreturn]] void abort() noexcept;",
       "프로그램을 정리 없이 끝낸다. 정상이 아닌 종료를 알리는 방법이다.",
       returns="돌아오지 않는다 (`[[noreturn]]`)",
       notes=[("하지 않는 일", "지역 객체와 정적 객체의 소멸자, `atexit`로 등록한 함수를 부르지 않는다. 열린 스트림을 "
                           "비우는지도 표준이 보장하지 않는다"),
              ("디버거가 붙어 있으면", "멈추는 곳은 런타임 라이브러리 안이다. 깨진 조건을 보려면 호출 스택에서 내 코드의 "
                                "칸을 찾아가야 한다"),
              ("디버거가 없으면", "MSVC의 디버그용 런타임은 `abort() has been called`라는 글을 보여 주고 종료 코드 3으로 "
                             "끝낸다. 릴리스용 런타임은 글 없이 끝낸다 (아래 예시)"),
              ("헤더", "`<cstdlib>`")],
       lib="C++ 표준 라이브러리"),
    fn("std::terminate", "[[noreturn]] void terminate() noexcept;",
       "더 진행할 수 없을 때 C++ 런타임이 부르는 함수다. 직접 부르기보다 불리는 것을 보게 된다.",
       returns="돌아오지 않는다",
       notes=[("불리는 때", "던진 예외를 아무도 잡지 않았을 때, `noexcept` 함수 밖으로 예외가 나갈 때, 예외를 처리하는 "
                         "도중의 소멸자가 또 예외를 던질 때, `join`도 `detach`도 하지 않은 `std::thread`가 파괴될 때"),
              ("하는 일", "등록된 종료 처리기를 부른다. 기본 처리기는 `std::abort()`를 부르므로 그 뒤는 `std::abort`와 같다"),
              ("바꾸려면", "`std::set_terminate( 함수 )`로 처리기를 바꾼다. 처리기는 돌아오면 안 된다. 마지막 로그를 "
                        "남기고 끝내는 데 쓴다"),
              ("헤더", "`<exception>`")],
       lib="C++ 표준 라이브러리"),
    fn("std::exit", "[[noreturn]] void exit( int exit_code );",
       "프로그램을 정상 종료 절차로 끝낸다. `main`에서 `return`한 뒤에 일어나는 일과 같은 절차다.",
       params=[("`exit_code`", "운영체제에 남길 종료 코드. 0이나 `EXIT_SUCCESS`는 성공, `EXIT_FAILURE`는 실패를 뜻한다")],
       returns="돌아오지 않는다",
       notes=[("하는 일", "정적 객체의 소멸자와 `atexit`로 등록한 함수를 등록의 역순으로 부르고, 열린 C 스트림을 비우고 닫는다"),
              ("하지 않는 일", "==지역 객체의 소멸자는 부르지 않는다.== 호출 스택을 거슬러 올라가지 않기 때문이다. `main`의 "
                           "지역 변수가 쥔 자원(RAII, 1-4강 3.1절)은 소멸자를 거치지 않는다"),
              ("디버거", "붙어 있어도 멈추지 않는다. 조용히 끝난다"),
              ("헤더", "`<cstdlib>`")],
       lib="C++ 표준 라이브러리"),
    box("ex", "예시: 끝난 방법은 종료 코드에 남는다", [
        table([36, 20, 44], ["끝낸 방법", "종료 코드", "숫자가 온 곳"], [
            ["`std::exit( 2 )`", "2", "내가 준 값. `main`의 `return 2;`도 같다"],
            ["`std::abort()`, 디버그용 런타임", "3", "런타임이 정한 값이다 (`_exit( 3 )`)"],
            ["`std::abort()`, 릴리스용 런타임", "`0xC0000409`", "빠른 실패(`__fastfail`)의 상태 코드다"],
            ["`__debugbreak()`, 디버거 없이", "`0x80000003`", "중단점 예외의 번호다 (`STATUS_BREAKPOINT`)"],
        ], cell_cls=["", "c", ""], compact=True),
        p("0이 성공이라는 것은 관례다. Visual Studio는 출력 창의 마지막 줄(`… has exited with code 3 (0x3).`)에, 명령 "
          "프롬프트는 실행한 바로 다음의 `echo %ERRORLEVEL%`에 이 숫자를 보여 준다. 디버거 없이 죽은 프로그램이 남기는 "
          "것은 이 숫자와 로그 파일뿐이다. `std::abort()`의 두 행은 런타임 소스(`ucrt/startup/abort.cpp`)에서 읽었다."),
    ]),

    h3("4.2", "멈추기 전에 남긴다"),
    p("멈추는 순간 프로세스 안의 버퍼는 사라질 수 있다. `abort()`가 열린 스트림을 비워 주는지는 표준이 보장하지 않는다. "
      "그래서 순서는 ==보고 → flush → 멈춤==이다. 1-5강 5.2절에서 flush를 “`Shutdown()`에서만” 하기로 했다면 "
      "마지막 줄은 파일에 없다."),
    FIG_ORDER.render("로그 한 줄은 먼저 프로세스 안의 버퍼에 들어가고, flush해야 파일로 나간다. 멈추는 순간 버퍼는 "
                     "프로세스와 함께 사라진다."),
    p("1-5강이 미뤄 둔 질문도 여기서 정한다. `Fatal` 레벨의 로그는 찍기만 하는가, 찍고 멈추는가. 멈추게 하면 `Fatal`을 "
      "부른 곳마다 assert와 같은 일이 일어나고, 찍기만 하게 두면 멈추는 일은 assert 매크로만 맡는다."),

    h3("4.3", "멈추는 문장은 매크로 안에 둔다"),
    code(r"""
void Check( bool ok )
{
    if ( !ok ) __debugbreak();    // the debugger stops HERE, inside Check()
}

Check( index < count );           // the line you wanted to see is in the caller's frame
""", title="a function cannot stop on the caller's line", tag="bad"),
    FIG_STACK.render("Visual Studio의 호출 스택 창처럼 가장 최근에 불린 함수를 맨 위에 그렸다. 화살표가 가리키는 칸이 "
                     "디버거가 서는 곳이다."),
    p("멈추는 문장이 함수 안에 있으면 디버거는 그 함수 안에서 멈춘다. 깨진 조건이 적힌 줄은 호출한 쪽으로 한 칸 옮겨 "
      "가야 보인다. `__debugbreak()`가 매크로 본문에 있으면 호출한 자리에 펼쳐지므로 디버거가 바로 그 줄에 선다. "
      "보고하는 일(문자열을 만들고 로그를 부르는 일)은 함수로 빼도 된다. 호출부마다 펼쳐지는 코드가 줄어든다."),
    box("ue", None,
        "언리얼의 `check`도 같은 구조다. 보고는 `FDebug`의 함수가, 멈추는 일은 매크로 본문의 `PLATFORM_BREAK()`가 맡아서 "
        "디버거가 `check`를 쓴 줄에 선다. 디버거가 붙었는지는 `FPlatformMisc::IsDebuggerPresent()`로 묻는다."),
], lead="멈추는 방법은 여럿이고, 같은 방법도 디버거가 붙어 있는지에 따라 다르게 보인다.")

ch5 = chapter(5, "실패를 알리는 방법", [
    keep(h3("5.1", "방법들"),
    table([25, 22, 30, 23], ["방법", "호출한 쪽의 모습", "무시하면", "이유를 담는가"], [
        ["`bool` 반환", "`if ( !Load() ) …`", "조용히 지나간다. `[[nodiscard]]`로 경고를 받는다 (1-4강 2.4절)", "담지 못한다"],
        ["오류 코드 열거형", "`if ( code != … ) …`", "위와 같다", "값의 종류만큼 담는다"],
        ["`std::optional<T>`", "값이 있거나 없다", "빈 값에 `value()`는 예외, `*`는 정의되지 않은 동작이다", "담지 못한다"],
        ["예외", "성공하는 길만 적힌다", "무시할 수 없다. 잡지 않으면 `std::terminate()`", "예외 객체에 담는다"],
        ["`std::expected<T, E>`", "값 또는 오류", "값을 꺼내려면 확인해야 한다", "담는다. C++23이라 지금 설정에서는 못 쓴다"],
    ], cell_cls=["lab", "", "", ""], compact=True)),
    box("ex", "예시: 같은 함수를 다섯 가지로 선언하면", [
        code(r"""
bool                             ParseInt( std::string_view text, int& out );
EParseError                      ParseInt( std::string_view text, int& out );
std::optional<int>               ParseInt( std::string_view text );
int                              ParseInt( std::string_view text );   // throws std::invalid_argument
std::expected<int, EParseError>  ParseInt( std::string_view text );   // C++23
""", title="one job, five ways to report a failure (a real program picks one)", tag="syntax"),
        p("글자를 정수로 바꾸는 함수다. `ParseInt( \"12a\" )`가 실패했을 때 부른 쪽이 받는 것은 차례로 `false`, "
          "`EParseError::InvalidChar` 같은 열거형 값, 빈 `optional`, 날아오는 예외, 오류를 담은 `expected`다. 위의 둘은 "
          "결과를 출력 인자 `out`으로 돌려주므로, 실패했을 때 `out`에 무엇이 들어 있는지도 정해 두어야 한다."),
    ]),

    h3("5.2", "예외를 고를 때 따져 볼 것"),
    ul([
        "**생성자에는 반환값이 없다.** 생성자가 실패를 알리는 표준 방법은 예외뿐이다. 예외를 쓰지 않기로 하면 "
        "1-4강처럼 `Init`을 따로 두는 모양이 따라온다.",
        "**C 코드를 지나갈 수 없다.** GLFW는 C 라이브러리다. 키 콜백 안에서 던진 예외가 `glfwPollEvents()`의 스택을 "
        "거슬러 올라가는 동작은 C++ 표준이 정하지 않는다. 콜백 안에서는 던지지 않거나, 던진 것을 콜백 안에서 잡는다.",
        "**표준 라이브러리는 어차피 던진다.** `new`는 `std::bad_alloc`을, `std::vector::at`은 `std::out_of_range`를, "
        "빈 `std::function` 호출은 `std::bad_function_call`을 던진다. “엔진은 예외를 쓰지 않는다”고 정해도 이 예외들은 남는다.",
        "**비용이 드는 곳이 다르다.** 던지지 않는 동안은 거의 비용이 없고 던질 때는 비싸다. 프레임마다 일어날 수 있는 "
        "실패에는 맞지 않는다.",
        "**지나가는 모든 코드가 준비되어 있어야 한다.** 예외가 지나가는 함수는 중간에 빠져나가도 자원이 새지 않게 "
        "써야 한다. RAII(1-4강 3.1절)가 그 준비다.",
    ]),
    FIG_EXC.render("둘째 항목(C 코드를 지나갈 수 없다)의 그림이다. 콜백을 부른 것은 GLFW이므로, 콜백에서 던진 예외가 "
                   "`main`의 `catch`에 닿으려면 C로 쓰인 GLFW의 칸을 지나야 한다."),
    p("이 프로젝트는 Visual Studio의 기본 설정대로 C++ 예외가 켜져 있다(`/EHsc`). 프로젝트 파일에 이 설정을 따로 적은 "
      "줄은 없다."),
    box("ue", None,
        "언리얼 엔진의 코드는 C++ 예외를 쓰지 않는다. 모듈은 기본으로 예외를 끈 채 컴파일되고(`bEnableExceptions`), "
        "실패는 `bool`, `nullptr`인 포인터, 출력 인자로 알린다."),
    box("cs", None,
        "예외가 던져지면 런타임은 호출 스택을 거슬러 올라가며 각 함수의 지역 객체를 파괴하고 맞는 `catch`를 찾는다. "
        "스택 풀기(stack unwinding)다. 컴퓨터구조에서 본 호출 스택과 반환 주소, 운영체제의 예외 처리(Windows의 SEH)에 "
        "닿는다. `noexcept`를 붙인 함수 밖으로 예외가 나가면 `std::terminate()`가 불린다."),
], lead="버그는 멈춰서 고치고, 실패는 호출한 쪽에 알린다. 알리는 방법이 여럿이라 하나를 규칙으로 정해 둔다.")

ch6 = chapter(6, "설계", [
    h3("6.1", "파일 배치와 완성된 뒤의 모습"),
    tree("""
Engine/
├── Core/
│   ├── Assert.h +  #the assert macros; what does this header include?
│   ├── Logger.h  #Fatal: print only, flush, or stop?
│   ├── Logger.cpp
│   └── EngineCore.cpp  #which checks are asserts, which are failures?
└── Manager/
    └── InputManager.cpp  #invalid key: bug or failure?
Docs/
└── ErrorPolicy.md +  #one page with the decisions of 6.2 (name is an example)
"""),
    code(r"""
ASSERT( index < count );
ASSERT_MSG( window != nullptr, "window is gone before {}", stage_name );
VERIFY( _handles.erase( id ) == 1 );    // the erase must still run when checks are off
""", title="the call site when this lesson is done (names and kinds are examples)", tag="usage"),

    keep(h3("6.2", "결정할 것"),
    table([20, 38, 42], ["결정", "선택지", "따져 볼 것"], [
        ["매크로의 종류", "검사 하나 / 검사와 검증 / 항상 켜진 것까지 셋",
         "3.4절의 표. 종류가 늘면 “여기는 어느 것인가”를 매번 골라야 한다"],
        ["검사를 빼는 기준", "`_DEBUG`가 없을 때 / `NDEBUG`가 있을 때 / 따로 만든 스위치",
         "Release에서도 검사를 켜 보고 싶을 때가 있는가. 스위치는 어디에 정의하는가"],
        ["보고하는 통로", "Logger의 `Fatal` / `std::cerr`에 직접 / 둘 다",
         "Logger가 아직 `Init` 전이면 어떻게 되는가. Logger 안에서 깨진 조건은 누가 보고하는가"],
        ["멈추는 방법", "`__debugbreak()`만 / 디버거가 없으면 `std::abort()` / 물어본다",
         "4.1절의 표. Ctrl+F5로 실행한 사람에게 무엇이 보여야 하는가"],
        ["`Fatal` 로그의 뜻", "찍기만 한다 / 찍고 flush한다 / 찍고 멈춘다", "4.2절. 멈추게 하면 `Fatal`과 assert가 하는 일이 겹친다"],
        ["실패를 알리는 기본 규칙", "반환값과 `[[nodiscard]]` / 예외 / 경계를 정해 섞는다",
         "5.1절과 5.2절. 1-4강에서 `Init`에 고른 방식과 맞는가"],
        ["표준 라이브러리의 예외", "`main`에서 잡아 로그를 남긴다 / 잡지 않는다",
         "잡지 않으면 `std::terminate()`다. 그때 로그 파일에는 무엇이 남는가"],
        ["매크로 이름", "`ASSERT` / 접두사를 붙인 이름", "매크로에는 범위가 없다 (1-5강 3.1절). 다른 헤더의 같은 이름과 부딪힐 수 있다"],
    ], cell_cls=["lab", "", ""], compact=True)),
    box("decide", None,
        "여덟 가지에 정답은 없다. 미션 전에 행마다 하나를 고르고 이유를 한 줄씩 적는다. 그 기록을 다듬은 한 쪽짜리 "
        "문서가 이 강의 결과물 절반이다. 앞으로 함수의 모양을 정할 때마다 그 문서를 본다."),

    h3("6.3", "선언 스케치"),
    code(r"""
#pragma once

// What does this header include, and what does that cost every file that asserts?
// The build switch: _DEBUG, NDEBUG, or a symbol of your own?

#define ASSERT( cond )            /* checks off: is `cond` still compiled? evaluated? */
#define ASSERT_MSG( cond, ... )    /* how do the format arguments reach the logger? */
#define VERIFY( cond )             /* `cond` runs in every build; what is left of the check? */

// A reporting function, declared here and defined in a .cpp:
//   - What does it receive? (expression text, file, line, message)
//   - Why is it a function while the break stays in the macro? (4.3)
//   - Can it be called before the logger is initialized?
""", title="Engine/Core/Assert.h", tag="sketch"),

    keep(h3("6.4", "어디에 넣을 것인가"),
    p("assert를 넣을지 따져 볼 자리들이다. 위의 셋은 1.1절에서 확인한 자리이고, 아래 둘은 1-4·1-5강을 거치며 생긴 "
      "자리다. 오른쪽 칸은 답이 아니라 판단할 때 던질 질문이다."),
    table([30, 30, 40], ["네 코드에서 찾을 자리", "지켜져야 하는 것", "판단할 것"], [
        ["`MInputManager`의 조회 함수 셋", "`key`가 유효한 범위다",
         "버그인가 실패인가 (2.1절). 프레임마다 불리는 함수다. 검사 비용은 괜찮은가"],
        ["`GEngine::GetInputManager`", "`Init`이 성공한 뒤다", "여기서 검사하는가, 받아 쓰는 쪽에서 하는가. 반환 타입이 참조였다면 어땠는가"],
        ["`MInputManager::cbSetKey`", "user pointer가 `nullptr`이 아니다. `key`가 배열 범위 안이다",
         "`key`는 GLFW가 준 값이다. 코드 안의 값인가 바깥의 값인가"],
        ["`GEngine::Run`", "`Init`이 성공했고 창이 있다", "1-4강에서 `Init`의 결과를 무시하지 못하게 했다면 이 검사는 필요한가"],
        ["레벨을 글자로 바꾸는 `switch` (1-5강)", "모든 `ELogLevel`을 다뤘다",
         "`default`에 닿는 것은 어떤 종류의 일인가. Logger 안의 assert는 무엇으로 보고하는가"],
    ], cell_cls=["lab", "", ""])),
    box("point", "미션 전에: 자기 코드를 읽는다",
        "다섯 자리를 네 코드에서 찾아 파일 이름과 줄 번호를 적어 둔다. 이름이나 모양이 앞 강 자료와 달라졌다면 네 코드가 "
        "기준이다. 같은 종류로 보이는 자리가 더 있으면 표에 더한다."),

    keep(h3("6.5", "이 강에서 하지 않는 것"),
    table([30, 70], ["미루는 것", "이유"], [
        ["호출 스택을 로그에 찍기", "`<stacktrace>`는 C++23이다. 지금은 디버거의 호출 스택 창을 쓴다"],
        ["크래시 덤프 남기기", "디버거 없이 죽은 프로세스의 상태를 파일로 남기는 일은 따로 다룰 만한 주제다"],
        ["GL 오류를 assert로 잇기", "OpenGL이 내는 오류를 받는 통로는 2-1강(디버그 콜백)에서 만든다"],
    ], cell_cls=["lab", ""], compact=True)),
], lead="새로 만드는 것은 헤더 하나와 문서 한 쪽이다. 나머지는 이미 있는 코드의 어느 자리가 어느 쪽인지 가르는 일이다.")

ch7 = chapter(7, "구현 미션", [
    steps([
        ("표준 `assert`가 깨지는 것을 본다",
         "`main`의 맨 앞에 일부러 거짓인 표준 `assert`를 하나 두고, Debug 구성에서 F5와 Ctrl+F5로 한 번씩 실행한다. "
         "실행마다 실패를 알리는 글이 나온 곳(콘솔인가 대화상자인가)을 적고, F5에서는 디버거가 선 곳도 적는다. "
         "**통과:** 두 실행의 기록이 있고, 나온 글에서 식·파일·줄을 짚을 수 있다.",
         ["`<cassert>`가 필요하다. Release 구성에서는 아무 일도 일어나지 않는다 (3.1절 카드의 `NDEBUG`).",
          "글에서 식, 파일, 줄을 찾기 어려우면 3.1절 `assert` 카드의 “거짓이면” 칸과 견준다."]),
        ("`__debugbreak()`만으로 멈춰 본다",
         "1단계의 `assert`를 `__debugbreak()` 한 줄로 바꾸고 F5와 Ctrl+F5로 한 번씩 실행한다. F5에서 디버거가 선 곳, "
         "Ctrl+F5에서 보인 것과 종료 코드를 적고 1단계의 기록과 견준다. **통과:** 1단계와 다른 점이 적혀 있고, 적은 "
         "종료 코드를 4.1절 예시의 표와 맞춰 보았다.",
         ["F5에서 멈춘 뒤 ‘계속’을 누르면 어떻게 되는가. `abort()`와 갈리는 지점이다 (4.1절)."]),
        ("첫 매크로: 거짓이면 그 줄에서 멈춘다",
         "`Engine/Core/Assert.h`를 새로 만들고 조건 하나를 받는 매크로를 쓴다. 조건이 참이면 아무 일도 하지 않고, "
         "거짓이면 매크로를 쓴 그 줄에서 멈춘다. 매크로의 이름은 6.2절의 여덟째 결정이다. **통과:** 거짓인 조건을 넣고 "
         "F5로 실행하면 호출 스택 창의 맨 위가 매크로를 쓴 줄이다. 참인 조건으로 바꾸면 멈추지 않는다.",
         ["멈추는 문장을 함수로 옮기면 맨 위가 어디로 바뀌는지도 한 번 본다 (4.3절).",
          "`if`와 `else` 사이에 중괄호 없이 넣어도 컴파일되는가 (1-5강 3.1절)."]),
        ("무엇이 깨졌는지 남긴다",
         "매크로는 멈추기 전에 깨진 식의 글자, 조건을 적은 파일의 이름과 줄 번호를 보고한다. 그 보고는 멈추는 순간에 "
         "로그 파일까지 나가 있다. 보고하는 통로는 6.2절의 셋째 결정이고, 디버거 없이 실행했을 때 어떻게 멈추는가는 "
         "넷째 결정이다. **통과:** F5로 멈춘 직후 정한 통로에 식·파일·줄이 있다. Ctrl+F5로 실행하면 넷째 "
         "결정에서 정한 대로 동작한다.",
         ["식을 글자로 바꾸는 연산자는 3.3절에 있다.",
          "1-5강의 로그 매크로를 그대로 부르면 위치가 어디로 찍히는가. 매크로를 쓴 자리인가, `Assert.h`인가.",
          "로그 파일에 그 줄이 없으면 4.2절의 그림에서 빠진 칸을 찾는다."]),
        ("메시지를 받는다",
         "조건 뒤에 형식 문자열과 값을 더 받는 매크로를 하나 더 만든다. 쓰는 모습은 6.1절 사용 예의 둘째 줄과 같다. "
         "조건이 거짓이면 4단계의 보고와 함께 값이 채워진 메시지가 남고, 매크로를 쓴 줄에서 멈춘다. **통과:** 값 "
         "하나를 넣어 깨뜨리면 정한 통로의 메시지에 그 값이 보인다.",
         ["1-5강 미션 6에서 가변 인자를 넘긴 방법이 그대로 통한다.",
          "조건이 참일 때 메시지의 인자들은 계산되는가. 계산되면 곤란한 이유가 있는가."]),
        ("검사를 뺀 빌드를 만든다",
         "검사를 뺀 빌드에서는 검사 종류의 매크로가 멈추지도, 식을 계산하지도 않는다. 두 빌드를 가르는 기준은 6.2절의 "
         "둘째 결정이다. 첫째 결정에서 검사 말고 다른 종류도 두기로 했다면 그 매크로를 여기서 만든다. **통과:** 검사를 "
         "뺀 빌드에서, 사라지기로 한 매크로의 식은 계산되지 않고 남기로 한 매크로의 식은 계산된다.",
         ["식 안에서 카운터를 올리고, 검사를 뺀 빌드에서 그 값이 어떻게 되는지 찍어 본다.",
          "Release 구성으로 빌드하려면 1-4강 6.4절의 “Release의 링크 입력”이 끝나 있어야 한다.",
          "검사에만 쓰던 변수가 경고를 내는가 (8장)."]),
        ("엔진 코드에 넣는다",
         "6.4절 표의 자리마다 버그인지 실패인지 판단하고 이유를 한 줄씩 적는다. 버그라고 판단한 자리에는 assert를 "
         "넣는다. 실패라고 판단한 자리는 6.2절의 여섯째 결정대로 알린다. `Fatal` 로그는 다섯째 결정대로 동작하게 "
         "한다. **통과:** 자리마다 판단과 이유가 적혀 있고, 매크로 이름을 검색하면 버그로 판단한 자리가 모두 "
         "나온다. `Fatal` 로그를 한 줄 찍으면 정한 대로 동작한다.",
         ["판단이 어려운 자리는 2.1절로 돌아간다. 그 값은 어디서 왔는가.",
          "assert를 넣은 자리의 `return false`는 남기는가. 검사를 뺀 빌드에서 그 줄에 닿으면 무슨 일이 생기는가."]),
        ("문서를 쓰고 검증한다",
         "6.2절의 여덟 결정과 이유를 한 쪽짜리 문서로 정리한다 (6.1절의 `Docs/ErrorPolicy.md`, 이름은 예시). "
         "7단계에서 넣은 조건을 하나씩 일부러 깨뜨려 9장의 기준을 확인하고, 시험하려고 넣은 코드를 지운 뒤 커밋 "
         "하나로 묶는다. **통과:** 9장의 여덟 줄이 모두 맞다."),
    ]),
], lead="먼저 6.4절 표의 자리를 네 코드에서 찾는다. 단계마다 빌드해서 확인하고, “통과”에 적힌 것이 보이면 다음으로 "
        "간다. 힌트는 막혔을 때 하나씩만 본다. 무엇을 하라는 것인지 그래도 분명하지 않으면 맨 뒤 13장에 단계별로 "
        "풀어 적은 목록이 있다.", pb=True)

ch8 = chapter(8, "흔한 함정", [
    table([30, 38, 32], ["증상", "원인", "확인 방법"], [
        ["Debug에서는 맞게 도는데 Release에서 값이 다르다", "assert 안에 부작용이 있는 식을 넣었다. 검사를 뺀 빌드에서 "
                                                  "식이 통째로 사라졌다", "`ASSERT(`를 검색해 `++`, `=`, 함수 호출이 든 것을 본다"],
        ["디버거가 `Assert.h`나 보고 함수 안에서 멈춘다", "멈추는 문장이 함수 안에 있다", "호출 스택 창의 맨 위 줄"],
        ["Ctrl+F5로 실행하면 창이 말없이 사라진다", "디버거 없이 `__debugbreak()`를 만났다", "로그 파일의 마지막 줄. 6.2절의 넷째 결정"],
        ["로그 파일에 깨진 조건이 없다", "flush하기 전에 멈췄다", "멈춘 직후 파일을 연다 (4.2절)"],
        ["매크로 인자가 너무 많다는 경고 (C4002)", "조건 안의 쉼표를 전처리기가 인자 구분으로 읽었다", "조건을 `( )`로 한 번 더 감싼다"],
        ["보고하다가 다시 assert가 깨져 끝없이 반복된다", "Logger 안의 assert가 Logger로 보고한다", "보고 함수에 중단점을 걸고 호출 스택을 본다"],
        ["Release에서 “초기화했지만 참조하지 않은 지역 변수” 경고 (C4189)", "그 변수를 assert에서만 썼다",
         "`/W4`에서 나오는 경고다. 지금은 `Level3`이다 (`Engine/Engine.vcxproj:159`)"],
    ], compact=True),
], lead="증상에서 거꾸로 찾는 표다.")

ch9 = chapter(9, "완료 기준", [
    checklist([
        "Debug 구성에서 F5로 실행해 조건을 일부러 깨뜨리면, 디버거가 그 조건이 적힌 줄에서 멈춘다.",
        "그때 6.2절의 셋째 결정에서 정한 통로에 깨진 식, 파일 이름, 줄 번호가 남아 있다 (Logger라면 콘솔과 로그 파일).",
        "Ctrl+F5로 실행했을 때의 동작이 6.2절에서 정한 대로다.",
        "검사를 뺀 빌드에서, 사라지기로 한 매크로의 식은 계산되지 않는다. 남기로 한 식은 계산된다.",
        "`Engine/`과 `Client/`에서 `__debugbreak`를 검색하면 `Assert.h` 한 파일만 나온다.",
        "6.4절 표의 자리마다 “버그인가 실패인가”의 판단과 이유가 적혀 있다.",
        "6.2절의 여덟 가지 결정이 한 쪽짜리 문서로 정리되어 있다.",
        "커밋 하나로 묶였다.",
    ]),
    console(Raw(
        '<span class="dim">[14:02:09.774]</span> <span class="err">[Fatal]</span> [Core ] '
        'Assertion failed: code &lt; kKeyRangeMax  <span class="dim">(InputManager.cpp:36)</span>\n'
        '<span class="dim">[14:02:09.774]</span> <span class="err">[Fatal]</span> [Core ] key code was 512'
    ), title="기대하는 출력 (형식과 문구는 예시)"),
], lead="전부 눈이나 검색으로 확인할 수 있는 조건이다.")

ch10 = chapter(10, "생각해 볼 질문", [
    exgroup("A", "코드를 쓰지 않고 답하시오", "한두 문장으로, 이유까지"),
    qlist([
        "로그 파일을 여는 줄 바로 뒤에 `ASSERT( _log_file.is_open() )`을 두었다. 무엇이 잘못되었는가?",
        "`ASSERT( ++_frame_count > 0 );`을 넣고 검사를 뺀 빌드로 실행했다. Debug와 무엇이 달라지는가?",
        "`__debugbreak()`를 보고 함수 안으로 옮겼다. 디버거는 어디에서 멈추는가? 무엇이 불편해지는가?",
        "`Fatal` 로그를 찍고 바로 `std::abort()`를 불렀는데 로그 파일에 그 줄이 없다. 왜 그럴 수 있는가?",
        "GLFW의 키 콜백 `cbSetKey` 안에서 예외를 던지기로 했다. 무엇이 문제인가?",
        "키 설정을 파일에서 읽어 `IsKeyPressed`에 넘기는 기능이 생긴다고 하자. 범위 검사는 어디에, 무엇으로 두는가?",
        "`static_assert( index < count );`는 왜 컴파일되지 않는가? 거꾸로 `assert( sizeof( Header ) == 16 );`은 "
        "컴파일되는데, 무엇이 아쉬운가?",
        "`main`의 지역 변수가 로그 파일을 쥐고 있는데, 깊은 곳의 함수가 `std::exit( 1 )`을 불렀다. 그 변수의 소멸자는 "
        "불리는가?",
    ], lines=2),
], lead="답을 보기 전에 소리 내어 설명해 본다. 막히는 문항이 다시 읽을 장이다.", pb=True)

ch11 = chapter(11, "해설", [
    answers("질문 A", [
        ("실패를 assert로 검사했다.",
         "파일을 열지 못하는 일은 맞게 쓴 프로그램에서도 일어난다. 검사를 뺀 빌드에서는 이 줄이 사라져, 열리지 않은 "
         "파일에 쓰는 코드가 그대로 돈다. 반환값이나 로그로 알리고 처리할 일이다. (2장, 1-5강 5.3절)"),
        ("`_frame_count`가 늘지 않는다.",
         "검사를 뺀 빌드에서 매크로의 인자는 계산되지 않으므로 `++`도 사라진다. 해야 하는 일은 assert 밖에 적고, "
         "그 결과만 assert로 확인한다. 식을 남겨야 한다면 검증 종류를 쓴다. (3.3절, 3.4절)"),
        ("보고 함수 안에서 멈춘다.",
         "멈추는 문장이 있는 자리에서 멈추기 때문이다. 깨진 조건을 보려면 매번 호출 스택에서 호출한 쪽으로 한 칸 "
         "옮겨 가야 한다. 매크로 본문에 두면 호출한 줄에 펼쳐진다. (4.3절)"),
        ("버퍼에 남은 글자가 파일로 가기 전에 프로세스가 끝났다.",
         "`abort()`는 소멸자와 `atexit` 함수를 부르지 않고, 열린 스트림을 비우는지는 표준이 보장하지 않는다. "
         "보고한 뒤 flush하고 나서 멈춰야 한다. (4.2절, 1-5강 5.2절)"),
        ("예외가 C로 쓰인 GLFW의 스택을 지나 올라가야 한다.",
         "그 동작은 C++ 표준이 정하지 않는다. GLFW는 자기 상태를 정리할 기회 없이 건너뛰어진다. 콜백 안에서는 "
         "던지지 않고, 일어난 일을 기록해 두었다가 `glfwPollEvents()`가 돌아온 뒤에 처리한다. (5.2절)"),
        ("파일을 읽는 곳에서 한 번 검증해 실패로 처리하고, `IsKeyPressed` 안에서는 assert로 둔다.",
         "파일의 값은 바깥에서 온 것이라 틀릴 수 있다. 경계에서 걸러 내면 그 안쪽으로는 유효한 `EKey`만 들어온다는 "
         "약속이 생기고, 그 약속이 깨지는 것은 코드의 버그다. (2.1절)"),
        ("`index`와 `count`는 실행 중에 정해지는 값이라 상수식이 아니다.",
         "`static_assert`는 컴파일할 때 값이 정해지는 조건만 받는다. 뒤쪽은 컴파일은 되지만, 빌드할 때 알 수 있는 "
         "잘못을 그 줄이 실행될 때까지 미루고, `NDEBUG`가 있는 빌드에서는 검사가 사라진다. (3.1절)"),
        ("불리지 않는다.",
         "`std::exit`는 정적 객체의 소멸자와 `atexit` 함수만 부르고 호출 스택은 풀지 않는다. 소멸자에서 하려던 "
         "마지막 flush도 일어나지 않는다. 지역 객체까지 정리하는 길은 `main`까지 돌아가 `return`하는 것이다. (4.1절)"),
    ]),
])

ch12 = glossary_chapter(12, [
    ("assert", "assertion", "“여기서는 이것이 참이다”라는 약속을 코드로 적은 것. 거짓이면 알리고 멈춘다"),
    ("버그", "bug, programmer error", "코드가 틀려서 생기는 일. 고치는 사람은 프로그래머다"),
    ("실패", "failure, runtime error", "맞게 쓴 프로그램에서도 일어나는 일. 호출한 쪽에 알린다"),
    ("전제 조건", "precondition", "함수를 부르는 쪽이 지켜야 하는 조건"),
    ("사후 조건", "postcondition", "함수가 끝났을 때 보장하는 조건"),
    ("불변식", "invariant", "객체가 살아 있는 동안 늘 참인 조건"),
    ("문자열화 연산자", "stringizing operator, #", "매크로 인자를 문자열 리터럴로 바꾸는 전처리기 연산자"),
    ("단락 평가", "short-circuit evaluation", "`A || B`에서 `A`가 참이면 `B`를 계산하지 않는 규칙"),
    ("조건부 컴파일", "conditional compilation", "`#if`, `#ifdef`로 빌드에 따라 코드의 일부를 넣거나 빼는 일"),
    ("정의되지 않은 동작", "undefined behavior", "표준이 결과를 정하지 않은 코드. 무슨 일이 일어날지 약속된 것이 없다"),
    ("중단점 예외", "breakpoint exception, `__debugbreak`", "디버거에게 “여기서 멈춰라”를 알리는 예외"),
    ("내장 함수", "intrinsic function", "호출이 아니라 CPU 명령으로 바로 바뀌는, 컴파일러가 아는 함수"),
    ("호출 스택의 칸", "stack frame", "함수 호출 하나가 호출 스택에서 차지하는 자리. 지역 변수와 돌아갈 주소가 든다"),
    ("비정상 종료", "abnormal termination, `std::abort`", "소멸자와 `atexit` 함수를 부르지 않고 프로세스를 끝내는 일"),
    ("종료 코드", "exit code", "프로세스가 끝나며 운영체제에 남기는 정수. 0이 성공이라는 관례다"),
    ("스택 풀기", "stack unwinding", "예외가 올라가며 지나는 함수의 지역 객체를 파괴하는 과정"),
    ("오류 정책", "error-handling policy", "실패를 어떻게 알리고 버그를 어떻게 다룰지 정한 엔진의 규칙"),
], pb=False)


def todo(mission: str, rows: list) -> Raw:
    """One mission of the task list: a heading and a small table kept on one page."""
    return keep(h4(mission),
                table([6, 54, 40], ["", "할 일", "됐는지 보는 법"], rows, cell_cls=["num", "", ""], compact=True))


ch13 = chapter(13, "할 일 목록", [
    keep(h3("13.1", "결정이 막히면"),
    p("6.2절의 여덟 가지를 고르지 못해 미션이 멈출 때 쓰는 기본 선택이다. 정답이 아니라 6.3절의 스케치에서 가장 덜 "
      "벗어나고 나중에 바꾸기 쉬운 쪽이다. 다른 선택을 해도 미션의 “통과”만 맞으면 된다."),
    table([28, 72], ["결정", "막혔을 때의 기본 선택"], [
        ["매크로의 종류", "검사와 검증 둘. 6.3절 스케치의 `ASSERT`·`ASSERT_MSG`와 `VERIFY`다"],
        ["검사를 빼는 기준", "`NDEBUG`가 있을 때 뺀다. 표준 `assert`와 같은 기준이다"],
        ["보고하는 통로", "Logger의 `Fatal`"],
        ["멈추는 방법", "`__debugbreak()`만 쓴다. 디버거 없이 실행하면 보고가 로그에 남고 프로세스가 끝난다"],
        ["`Fatal` 로그의 뜻", "찍고 flush한다. 멈추는 일은 assert 매크로만 맡는다"],
        ["실패를 알리는 기본 규칙", "반환값과 `[[nodiscard]]`. 엔진 코드는 예외를 던지지 않는다"],
        ["표준 라이브러리의 예외", "잡지 않는다"],
        ["매크로 이름", "스케치의 이름 그대로 쓴다. 다른 헤더의 이름과 부딪히면 그때 접두사를 붙인다"],
    ], cell_cls=["lab", ""], compact=True)),

    h3("13.2", "미션별 할 일"),
    todo("미션 전에 — 결정을 적고 네 코드를 읽는다", [
        ["1", "1.1절 표의 세 자리를 네 코드에서 찾아, 지금 무엇을 돌려주고 무엇을 확인하는지 적는다", "세 행에 지금의 동작이 적혀 있다"],
        ["2", "6.2절의 여덟 행마다 하나를 고르고 이유를 한 줄씩 적는다", "여덟 행에 고른 것과 이유가 있다"],
        ["3", "6.4절 표의 다섯 자리를 네 코드에서 찾아 파일 이름과 줄 번호를 적는다. 같은 종류의 자리가 더 있으면 표에 더한다",
         "다섯 행에 파일과 줄이 있다"],
    ]),
    todo("미션 1 — 표준 assert가 깨지는 것을 본다", [
        ["1", "Debug 구성에서 `main`의 맨 앞에 일부러 거짓인 `assert`를 둔다", "빌드된다"],
        ["2", "F5로 실행한다. 실패를 알리는 글이 나온 곳(콘솔인가 대화상자인가)과 디버거가 선 곳을 적는다",
         "나온 글에서 식, 파일, 줄을 짚을 수 있다"],
        ["3", "Ctrl+F5로 실행한다. 글이 나온 곳과 프로그램이 끝난 모습을 적는다", "F5 때와 다른 점을 말할 수 있다"],
    ]),
    todo("미션 2 — __debugbreak()만으로 멈춰 본다", [
        ["1", "1단계의 `assert` 줄을 `__debugbreak()` 한 줄로 바꾼다", "빌드된다"],
        ["2", "F5로 실행해 디버거가 선 곳을 적는다", "1단계의 F5 기록과 다른 점이 적혀 있다"],
        ["3", "Ctrl+F5로 실행해 화면에 보인 것과 종료 코드를 적는다", "적은 종료 코드를 4.1절 예시의 표와 맞춰 보았다"],
    ]),
    todo("미션 3 — 첫 매크로: 거짓이면 그 줄에서 멈춘다", [
        ["1", "`Engine/Core/Assert.h`를 새로 만든다. 무엇을 포함할지는 6.3절 스케치의 첫 질문이다", "프로젝트에 들어 있고 빌드된다"],
        ["2", "조건 하나를 받는 매크로를 쓴다. 조건이 참이면 아무 일도 하지 않는다. 이름은 6.2절의 여덟째 결정이다",
         "참인 조건을 넣으면 멈추지 않고 지나간다"],
        ["3", "조건이 거짓이면 멈춘다. 멈추는 문장은 함수가 아니라 매크로 본문에 있다 (4.3절)",
         "거짓인 조건을 넣고 F5로 실행하면 호출 스택 창의 맨 위가 매크로를 쓴 줄이다"],
        ["4", "매크로는 문장 하나처럼 쓰인다 (3.3절의 표)", "`if`와 `else` 사이에 중괄호 없이 넣어도 컴파일된다"],
    ]),
    todo("미션 4 — 무엇이 깨졌는지 남긴다", [
        ["1", "조건이 거짓이면 멈추기 전에 식의 글자, 파일 이름, 줄 번호를 보고한다. 통로는 6.2절의 셋째 결정이다",
         "F5로 깨뜨리면 콘솔에 세 가지가 보인다"],
        ["2", "보고에 찍히는 파일과 줄은 조건을 적은 자리의 것이다", "찍힌 줄 번호가 편집기에서 매크로를 쓴 줄과 같다"],
        ["3", "보고는 멈추기 전에 로그 파일까지 나간다. 순서는 4.2절에 있다", "디버거가 멈춘 채로 로그 파일을 열면 그 줄이 있다"],
        ["4", "디버거 없이 실행했을 때 멈추는 방법을 6.2절의 넷째 결정대로 만든다",
         "Ctrl+F5로 깨뜨리면 정한 대로 동작하고, 로그 파일에 보고가 남아 있다"],
    ]),
    todo("미션 5 — 메시지를 받는다", [
        ["1", "조건 뒤에 형식 문자열과 값을 더 받는 매크로를 하나 더 만든다", "6.1절 사용 예의 둘째 줄과 같은 모양의 호출이 컴파일된다"],
        ["2", "조건이 거짓이면 4단계의 보고와 함께, 값이 채워진 메시지를 남긴다", "값 하나를 넣어 깨뜨리면 정한 통로에 그 값이 보인다"],
        ["3", "거짓이면 멈추는 자리는 3단계와 같다", "호출 스택 창의 맨 위가 매크로를 쓴 줄이다"],
    ]),
    todo("미션 6 — 검사를 뺀 빌드를 만든다", [
        ["1", "검사를 켠 빌드와 뺀 빌드에서 매크로가 다르게 펼쳐지게 한다. 두 빌드를 가르는 기준은 6.2절의 둘째 결정이다",
         "검사를 뺀 빌드가 빌드되고 실행된다"],
        ["2", "검사를 뺀 빌드에서 검사 종류의 매크로는 멈추지도, 식을 계산하지도 않는다",
         "식 안에서 카운터를 올리고 찍어 보면 값이 그대로다"],
        ["3", "6.2절의 첫째 결정에서 검증이나 항상 켜진 종류를 두기로 했다면 그 매크로를 만든다. 무엇이 남는지는 3.4절의 표다",
         "같은 시험에서 카운터의 값이 늘어 있다"],
    ]),
    todo("미션 7 — 엔진 코드에 넣는다", [
        ["1", "6.4절 표의 자리마다 “판단할 것”의 질문에 답하고, 버그인지 실패인지와 이유를 한 줄씩 적는다",
         "행마다 판단과 이유가 있다"],
        ["2", "버그라고 판단한 자리에 assert를 넣는다. 조건은 표의 “지켜져야 하는 것”이다", "매크로 이름을 검색하면 그 자리가 모두 나온다"],
        ["3", "실패라고 판단한 자리는 6.2절의 여섯째 결정대로 호출한 쪽에 알린다", "그 자리에는 assert가 없다"],
        ["4", "`Fatal` 레벨의 로그가 6.2절의 다섯째 결정대로 동작하게 한다", "`Fatal` 로그를 한 줄 찍어 보면 정한 대로다"],
    ]),
    todo("미션 8 — 문서를 쓰고 검증한다", [
        ["1", "6.2절의 여덟 결정과 이유를 한 쪽짜리 문서로 정리한다 (6.1절의 `Docs/ErrorPolicy.md`, 이름은 예시)",
         "문서에 여덟 항목이 있다"],
        ["2", "7단계에서 넣은 조건을 하나씩 일부러 깨뜨려 본다", "깨뜨릴 때마다 9장의 첫 세 줄이 맞다"],
        ["3", "1 〜 6단계에서 시험하려고 넣은 코드와 깨뜨린 조건을 지운다", "`__debugbreak`를 검색하면 `Assert.h` 한 파일만 나온다"],
        ["4", "9장의 여덟 줄을 확인하고 커밋 하나로 묶는다", "9장의 여덟 줄이 모두 맞다"],
    ]),
], lead="미션의 문장만으로 무엇을 하라는 것인지 분명하지 않을 때 보는 목록이다. 미션마다 할 일을 한 줄씩 풀고, 됐는지 "
        "보는 법을 옆에 적었다. 어떻게 하는지는 적지 않았다. 그것은 2 〜 5장과 미션의 힌트에 있다.", pb=True)

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
