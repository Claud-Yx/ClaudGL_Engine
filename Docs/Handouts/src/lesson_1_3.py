"""Lesson 1-3 -- input system, written from scratch.

Version 4 replaces the "re-read your own code" handout (v2/v3). The engine code
was removed on 2026-11-16 (first pass kept at tag first-pass-2026-04), so this
lesson has missions and never quotes the first-pass code. Class and function
names follow the first pass so that later handouts still match.

Run:  python -I src/lesson_1_3.py      (from Docs/Handouts, with the handout venv)
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

ME = lesson("1-3")
OUT_PDF = ROOT / handout_name(ME["id"])
OUT_HTML = ROOT / "_build" / "lesson_1_3.html"

# Library headers, framework.h and InputKeys.h were read on this day.
READ_DATE = "2026-11-16"

COVER = cover(
    f"CLAUDGL ENGINE · PART {ME['part']} · {ME['id']} · v{ME['ver']}",
    Raw('M<span class="ac">Input</span>Manager'),
    ME["title"],
    "키보드의 한 번 누름이 `IsKeyPressed`의 `true`가 되기까지",
    [
        ("목표 결과물", "A·S·D를 누르는 순간 배경색이 바뀐다. 꾹 눌러도 “눌렸다”는 한 번만 참이 된다"),
        ("핵심 개념", "이벤트와 상태 · 키 콜백 · 정적 함수와 user pointer · 엣지 검출 · `enum class`"),
        ("선수 지식", "1-2강을 끝낸 코드(`Run` 루프와 Update 콜백). 1-1강 5.2절의 콜백"),
        ("예상 시간", f"읽기 1시간 + 구현 2시간 (계획서 기준 {ME['hours']}시간)"),
        ("건드릴 파일", "`Engine/Manager/InputManager.h`·`.cpp`(새 파일), `Engine/Core/EngineCore.h`·`.cpp`, "
                   "`Client/main.cpp`"),
        ("시작 상태", f"1-2강을 끝낸 저장소. `Engine/Enum/InputKeys.h`는 이미 있다 ({READ_DATE}에 읽음)"),
    ],
    note=("읽는 법",
          "처음부터 직접 쓰는 자료다. 2 〜 5장이 개념과 함수이고, 6장에서 이미 있는 `EKey`를 읽는다. 7장의 모양을 "
          "확인한 뒤 8장의 미션을 순서대로 구현한다. 코드 블록은 완성본이 아니다."),
    toc=["한 장으로 보기", "이벤트와 상태", "GLFW의 키 콜백", "C 콜백에 객체를 잇기", "Pressed · Held · Released",
         "EKey: 키에 이름 붙이기", "설계", "구현 미션", "흔한 함정", "완료 기준", "생각해 볼 질문", "해설", "용어집"],
)

# --------------------------------------------------------------------------

ch1 = chapter(1, "한 장으로 보기", [
    flow([
        ("키보드", "누름 · 뗌"),
        ("운영체제", "이벤트 큐"),
        ("glfwPollEvents", "큐를 비운다"),
        ("cbSetKey", "콜백", "accent"),
        ("_current_keys", "지금 상태"),
        ("IsKeyPressed", "Client가 묻는다", "dark"),
    ], "왼쪽 넷은 “일이 일어났다”는 이벤트의 세계이고, 오른쪽 둘은 “지금 어떤가”라는 상태의 세계다."),
    layers([
        ("CLIENT", [("cbUpdate", "`IsKeyPressed( EKey::A )`")]),
        ("ENGINE", [("MInputManager", "배열 둘: 현재 · 직전", "accent"), ("GEngine", "`unique_ptr`로 소유")]),
        ("LIBRARY", [("GLFW", "키 콜백을 불러 준다", "dark")]),
    ], "`MInputManager`는 GLFW가 주는 이벤트를 받아, Client가 프레임마다 물을 수 있는 상태로 바꿔 들고 있다."),
    table([24, 76], ["", "무엇이 있는가"], [
        ["이미 있는 것", "1-2강까지의 `GEngine`: `Init`, `Run` 루프, Update 콜백. 그리고 `Engine/Enum/InputKeys.h`의 `EKey` "
                    "열거형. `Engine/framework.h:15`가 이 헤더를 포함하고 있어서 pch를 쓰는 모든 파일에서 이미 보인다"],
        ["이 강에서 만드는 것", "`Engine/Manager/InputManager.h`와 `.cpp`의 `MInputManager` 클래스, `GEngine`이 그것을 "
                        "소유하는 멤버와 접근 함수, `Init`과 `Run`에 더하는 몇 줄, `Client/main.cpp`의 `cbUpdate`"],
        ["끝나면 보이는 것", "A·S·D를 누르는 순간 배경색이 바뀐다. 꾹 누르고 있어도 “눌렸다”는 한 번만 참이 된다"],
    ], cell_cls=["lab", ""]),
], lead="입력 시스템이 하는 일은 한 가지다. 운영체제가 알려 주는 “방금 눌렸다”를, 게임 코드가 묻는 “지금 눌려 있나”로 "
        "바꾸는 것이다.")

ch2 = chapter(2, "이벤트와 상태", [
    cards([
        ("이벤트", "순간에 일어난 일", "“A가 눌렸다”, “A가 떼졌다”. 일어난 때에 한 번 전달되고 사라진다.",
         "운영체제와 GLFW가 주는 것"),
        ("상태", "지금의 모습", "“A가 눌려 있다”. 언제 물어도 답이 있다.", "게임 코드가 프레임마다 묻는 것"),
    ]),
    p("운영체제는 키보드에서 일이 일어난 **순간**에만 알려 준다. 누르면 한 번, 떼면 한 번이다. 그 사이에 “아직 누르고 "
      "있다”는 소식은 따로 오지 않는다(되풀이해 오는 것이 있지만 성격이 다르다. 3.2절). 게임 코드는 반대로 묻는다. "
      "프레임마다 “지금 W가 눌려 있는가”를 알고 싶어 한다. 순간의 소식을 받아 적어 두는 곳이 있어야 그 물음에 답할 수 있다."),
    table([40, 60], ["게임 코드가 묻는 것", "답하는 데 필요한 것"], [
        ["지금 W가 눌려 있는가 (이동)", "지금의 상태"],
        ["방금 Space가 눌렸는가 (점프는 한 번만)", "지금의 상태와 직전 프레임의 상태 (5장)"],
        ["방금 떼었는가 (모아서 쏘기)", "지금의 상태와 직전 프레임의 상태 (5장)"],
    ], cell_cls=["lab", ""]),
    box("point", None,
        "키 콜백은 아무 때나 불리지 않는다. `glfwPollEvents()` 안에서만 불린다 (1-1강 6장). 그래서 한 프레임 동안 "
        "받아 적은 상태는 변하지 않고, 같은 프레임 안에서는 몇 번을 물어도 답이 같다."),
    box("cs", None,
        "장치가 CPU에 알리는 방법은 둘이다. 일이 생기면 장치가 끼어드는 인터럽트와, CPU가 주기적으로 물어보는 폴링이다. "
        "키 입력은 인터럽트로 운영체제에 들어와 이벤트 큐에 쌓이고, 게임은 프레임마다 그 큐를 비운다. 하드웨어 쪽은 "
        "인터럽트, 게임 쪽은 폴링이고 큐가 둘 사이를 잇는다. 운영체제 책의 입출력 장에 닿는다."),
], lead="운영체제는 일이 일어난 순간에만 알려 준다. 그 순간들을 받아 적어 두어야 나중에 물을 수 있다.")

ch3 = chapter(3, "GLFW의 키 콜백", [
    p("GLFW에 “키 이벤트가 오면 이 함수를 불러 달라”고 등록해 둔다. 함수를 인자로 넘기는 방법은 1-1강 5.2절에서 "
      "`gladLoadGLLoader`에 `glfwGetProcAddress`를 넘길 때 이미 썼다. 이번에는 넘기는 함수를 직접 쓴다."),
    fn("glfwSetKeyCallback",
       "typedef void (* GLFWkeyfun)(GLFWwindow* window, int key, int scancode, int action, int mods);\n"
       "GLFWkeyfun glfwSetKeyCallback(GLFWwindow* window, GLFWkeyfun callback);",
       "그 창에 키 콜백을 단다. 이후 그 창에서 키 이벤트가 처리될 때마다 `callback`이 불린다.",
       params=[("`window`", "콜백을 달 창"),
               ("`callback`", "키 이벤트마다 불릴 함수. 모양은 `GLFWkeyfun`과 같아야 한다. `nullptr`을 주면 콜백을 뗀다")],
       returns="이전에 달려 있던 콜백. 없었으면 `nullptr`",
       notes=[("불리는 때", "`glfwPollEvents()` 안에서, 키 이벤트 하나에 한 번"),
              ("개수", "한 창에 키 콜백은 하나다. 다시 달면 앞의 것은 떼어진다"),
              ("선언된 곳", "`include/GLFW/glfw3.h:1897`, `:5198`")],
       lib="GLFW 3.4"),

    h3("3.1", "콜백이 받는 다섯 인자"),
    table([16, 84], ["인자", "들어오는 값"], [
        ["`window`", "이벤트가 일어난 창. 창이 여럿일 때 구별하는 값이고, 4장에서는 엔진을 되찾는 열쇠로 쓴다"],
        ["`key`", "키 코드. `GLFW_KEY_A`(65), `GLFW_KEY_ESCAPE`(256)처럼 미국 표준 자판의 자리에 붙인 번호다. GLFW가 모르는 "
                  "키는 `GLFW_KEY_UNKNOWN`(-1)으로 온다 (`include/GLFW/glfw3.h:367`)"],
        ["`scancode`", "키보드 하드웨어가 보낸 번호. 기기와 운영체제마다 다르다. 이 강에서는 쓰지 않는다"],
        ["`action`", "`GLFW_PRESS`(1), `GLFW_RELEASE`(0), `GLFW_REPEAT`(2) 가운데 하나 (`include/GLFW/glfw3.h:331` 〜 `:345`)"],
        ["`mods`", "함께 눌린 Shift·Ctrl·Alt 등을 비트로 담은 값. `GLFW_MOD_SHIFT`는 `0x0001`이다. 이 강에서는 쓰지 않는다"],
    ], cell_cls=["lab", ""]),

    h3("3.2", "action의 세 값"),
    Fig(112)
    .box(130, 14, 350, 24, "키를 누르고 있는 동안", kind="accent")
    .line((40, 62), (612, 62))
    .arrow((604, 62), (624, 62))
    .text(634, 66, "시간", kind="s", anchor="start", size=9.5)
    .dot(130, 62, 4, kind="accent")
    .dot(250, 62, 3).dot(292, 62, 3).dot(334, 62, 3).dot(376, 62, 3).dot(418, 62, 3).dot(460, 62, 3)
    .dot(480, 62, 4, kind="accent")
    .line((130, 38), (130, 58), kind="accent dash")
    .line((480, 38), (480, 58), kind="accent dash")
    .text(130, 84, "GLFW_PRESS", kind="mono accent", size=9.5)
    .text(355, 84, "GLFW_REPEAT  ×  여러 번", kind="mono", size=9.5)
    .text(490, 84, "GLFW_RELEASE", kind="mono accent", anchor="start", size=9.5)
    .text(190, 54, "첫 반복까지의 지연", kind="s", size=9)
    .render("누를 때 `GLFW_PRESS`가 한 번, 누르고 있으면 잠시 뒤부터 `GLFW_REPEAT`이 되풀이되고, 뗄 때 `GLFW_RELEASE`가 "
            "한 번 온다. 반복의 지연과 간격은 운영체제의 키보드 설정을 따른다."),
    p("`GLFW_REPEAT`은 글자를 입력할 때 “aaaa”가 찍히게 하려는 운영체제의 기능이다. 게임 입력에서는 대개 방해가 된다."),
    box("ex", "예시: REPEAT을 PRESS처럼 다루면", [
        code(r"""
int g_jump_count = 0;

void OnKey( GLFWwindow* window, int key, int scancode, int action, int mods )
{
    if ( action != GLFW_RELEASE ) ++g_jump_count;    // PRESS and REPEAT both land here
}
""", title="counting key presses the naive way", tag="bad"),
        p("Space를 한 번 눌러 2초쯤 붙들고 있으면 `g_jump_count`는 1이 아니라 수십이 된다. “한 번 눌렀다”를 세려면 "
          "`GLFW_PRESS`만 세어야 한다. 이 강처럼 상태를 받아 적는 방식에서는 `GLFW_REPEAT`을 어떻게 다뤄도 결과가 "
          "같은데, 왜 그런지가 11장의 3번 문항이다."),
    ]),
    p("창이 포커스를 잃을 때 눌려 있던 키는 어떻게 될까. GLFW는 그 순간 눌린 키 전부에 대해 뗌 이벤트를 만들어 보내 준다. "
      "그래서 다른 창으로 넘어간 사이에 키를 떼어도 “눌려 있다”는 상태가 남지 않는다."),

    h3("3.3", "받아 적지 않고 물어보는 방법도 있다"),
    fn("glfwGetKey", "int glfwGetKey(GLFWwindow* window, int key);",
       "그 창에서 그 키가 마지막으로 보고된 상태를 돌려준다. GLFW가 안에서 받아 적어 둔 값을 읽는 것이다.",
       params=[("`window`", "물어볼 창"),
               ("`key`", "키 코드. `GLFW_KEY_A` 같은 상수")],
       returns="`GLFW_PRESS` 또는 `GLFW_RELEASE`. `GLFW_REPEAT`은 나오지 않는다",
       fails="`GLFW_KEY_UNKNOWN`을 주면 `GLFW_INVALID_ENUM` 오류가 난다",
       notes=[("알 수 없는 것", "지금 상태만 안다. 방금 눌렸는지, 방금 떼었는지는 알려 주지 않는다"),
              ("선언된 곳", "`include/GLFW/glfw3.h:4901`")],
       lib="GLFW 3.4"),
    table([26, 37, 37], ["", "`glfwGetKey`로 물어본다", "콜백으로 받아 적는다"], [
        ["상태를 드는 곳", "GLFW 안", "엔진의 배열"],
        ["게임 코드가 부르는 것", "GLFW 함수와 GLFW 키 코드", "엔진의 함수와 `EKey`"],
        ["방금 눌림·뗌", "직전 값을 따로 기억해야 한다", "직전 값을 따로 기억해야 한다 (5장)"],
        ["같은 방식으로 받는 것", "키뿐이다", "마우스, 창 크기, GL 디버그 메시지도 콜백으로 온다"],
    ], cell_cls=["lab", "", ""]),
    p("이 강은 콜백으로 받아 적는 쪽으로 간다. Client가 GLFW를 직접 부르지 않게 되고, 여기서 익히는 “C 콜백에 C++ 객체를 "
      "잇는 방법”(4장)을 2-1강의 GL 디버그 콜백에서 그대로 다시 쓴다."),
    box("ue", None,
        "언리얼에서는 플랫폼 계층이 운영체제의 키 메시지를 받아 `FSlateApplication`으로 넘기고, 키는 `FKey`(`EKeys::A`)라는 "
        "이름으로 다닌다. 게임 코드는 Enhanced Input의 `BindAction`으로 콜백을 건다. 운영체제의 이벤트를 엔진이 받아 "
        "자기 이름으로 바꾼 뒤 게임 코드에 넘기는 구조가 이 강에서 만드는 것과 같다."),
], lead="키 이벤트를 받는 통로는 콜백 하나다. 그 콜백이 무엇을 받고 언제 불리는지부터 본다.")

ch4 = chapter(4, "C 콜백에 객체를 잇기", [
    h3("4.1", "왜 static인가"),
    p("GLFW는 C 라이브러리다. `glfwSetKeyCallback`이 받는 것은 평범한 함수의 주소이고, C++ 클래스의 멤버 함수는 "
      "받지 못한다. 멤버 함수는 보이지 않는 첫 인자로 `this`를 받기 때문에, 겉보기 매개변수가 같아도 호출하는 "
      "방법이 다르다."),
    p("`static` 멤버 함수는 `this`가 없어서 평범한 함수와 똑같이 부를 수 있다."),
    box("ex", "예시: 두 함수의 주소는 타입이 다르다", [
        code(r"""
struct Sample
{
    void        Member( int x );    // hidden first argument: Sample* this
    static void Shared( int x );    // no this
};

void ( *plain )( int )          = &Sample::Shared;    // an ordinary function pointer
void ( Sample::*member )( int ) = &Sample::Member;    // a pointer to member: a different kind of thing
""", tag="syntax"),
        p("GLFW가 받는 것은 `plain` 꼴뿐이다. `member` 꼴은 객체와 함께 불러야 하는데, GLFW는 우리 객체를 모른다."),
    ]),

    h3("4.2", "this가 없으면 어느 객체인지 어떻게 아는가"),
    p("`static` 함수 안에서는 “내 배열”이 없다. 어느 `MInputManager`의 배열에 적을지 밖에서 찾아와야 한다. "
      "GLFW는 이럴 때 쓰라고 창마다 포인터 하나를 맡아 준다. 콜백은 인자로 받은 `window`에서 그 포인터를 꺼낸다."),
    Fig(174)
    .text(20, 14, "준비: Init에서 한 번", kind="s", anchor="start", size=9.5)
    .box(20, 24, 130, 50, "GEngine", "this", kind="accent")
    .arrow((150, 49), (270, 49), kind="accent")
    .text(210, 41, "맡긴다", kind="accent", size=9.5)
    .box(270, 20, 170, 66, kind="soft")
    .text(355, 38, "GLFWwindow", kind="t")
    .box(285, 48, 140, 28, "user pointer", kind="plain")
    .text(20, 108, "키 이벤트마다", kind="s", anchor="start", size=9.5)
    .box(20, 118, 130, 50, "GLFW", "glfwPollEvents 안", kind="dark")
    .arrow((150, 143), (270, 143))
    .text(210, 135, "window와 함께", kind="s", size=9.5)
    .box(270, 118, 170, 50, "cbSetKey", "static: this가 없다")
    .arrow((355, 86), (355, 118), kind="accent")
    .text(364, 106, "꺼낸다: void* → GEngine*", kind="s", anchor="start", size=9.5)
    .arrow((440, 143), (520, 143))
    .text(480, 135, "엔진을 거쳐", kind="s", size=9.5)
    .box(520, 118, 122, 50, "MInputManager", "_current_keys", kind="accent")
    .render("위쪽은 한 번 해 두는 준비이고 아래쪽은 키 이벤트마다 일어나는 일이다. 콜백이 받는 `window`가 두 줄을 잇는다."),
    fn("glfwSetWindowUserPointer", "void glfwSetWindowUserPointer(GLFWwindow* window, void* pointer);",
       "창마다 하나씩 있는 `void*` 칸에 포인터를 맡긴다. GLFW는 그 값을 보관만 하고 들여다보지 않는다.",
       params=[("`window`", "칸의 주인인 창"),
               ("`pointer`", "맡길 주소. 어떤 타입의 포인터든 `void*`로 바뀌어 들어간다")],
       returns="없다",
       notes=[("처음 값", "아무것도 맡기지 않았으면 `nullptr`"),
              ("주의", "맡긴 주소의 객체가 창보다 먼저 사라지면 안 된다. GLFW는 그 객체가 살아 있는지 모른다"),
              ("선언된 곳", "`include/GLFW/glfw3.h:4176`")],
       lib="GLFW 3.4"),
    fn("glfwGetWindowUserPointer", "void* glfwGetWindowUserPointer(GLFWwindow* window);",
       "그 창의 칸에 맡겨 둔 포인터를 돌려준다.",
       params=[("`window`", "칸의 주인인 창")],
       returns="맡겨 둔 값. 맡긴 적이 없으면 `nullptr`",
       notes=[("타입", "`void*`로 나온다. 맡길 때의 타입으로 되돌리는 일은 부르는 쪽의 책임이다"),
              ("선언된 곳", "`include/GLFW/glfw3.h:4197`")],
       lib="GLFW 3.4"),
    fn("static_cast", "static_cast< T >( expression )",
       "컴파일러가 아는 변환 규칙으로 값의 타입을 `T`로 바꾼다. 이 강에서는 두 가지 변환에 쓴다.",
       params=[("`T`", "바꿀 목표 타입. `void*`를 되돌릴 때는 맡길 때의 포인터 타입, `EKey`를 인덱스로 쓸 때는 `int`"),
               ("`expression`", "바꿀 값. `glfwGetWindowUserPointer`가 돌려준 `void*`, 또는 `EKey` 값 (6.1절)")],
       fails="맡긴 타입과 다른 타입으로 되돌려도 컴파일러는 잡지 못한다. 실행 중에 엉뚱한 메모리를 읽게 된다",
       lib="C++"),
    p("콜백이 `private` 멤버인 배열을 건드릴 수 있는 것은 같은 클래스의 멤버 함수이기 때문이다. 접근 제한은 객체 단위가 "
      "아니라 클래스 단위로 걸린다. `static` 멤버 함수도 그 클래스의 다른 객체의 `private` 멤버에 닿을 수 있다."),

    h3("4.3", "입력 관리자의 주인"),
    p("`MInputManager` 객체는 엔진이 만들고 엔진이 없앤다. 그 관계를 타입으로 적는 도구가 `std::unique_ptr`다."),
    fn("std::make_unique",
       "template< class T, class... Args >\n"
       "std::unique_ptr<T> make_unique( Args&&... args );",
       "`T` 객체 하나를 힙에 만들고, 그것을 소유하는 `std::unique_ptr<T>`를 돌려준다.",
       params=[("`args`", "`T`의 생성자에 넘길 인자들. 없으면 비워 둔다")],
       returns="새 객체의 유일한 주인인 `std::unique_ptr<T>`",
       fails="메모리가 모자라면 `std::bad_alloc` 예외가 난다",
       notes=[("헤더", "`<memory>`. `Engine/framework.h:11`이 이미 포함한다")],
       lib="C++14"),
    table([22, 78], ["`std::unique_ptr<T>`", "하는 일"], [
        ["소멸자", "사라질 때 가리키던 객체를 `delete`한다. 엔진이 사라지면 입력 관리자도 사라진다"],
        ["복사", "할 수 없다. 주인이 둘이 되기 때문이다. 넘겨주려면 `std::move`로 옮긴다"],
        ["`get()`", "가리키는 객체의 맨 포인터를 돌려준다. 소유는 그대로다. “잠깐 쓰라”고 빌려줄 때 쓴다"],
        ["`->`, `*`", "가리키는 객체를 맨 포인터처럼 쓴다"],
    ], cell_cls=["lab", ""]),
    box("point", "소유와 빌림",
        "`std::unique_ptr` 멤버는 “이 객체의 주인은 나 하나”라는 뜻이다. 접근 함수가 맨 포인터를 내주는 것은 “잠깐 쓰라”는 "
        "뜻이고, 받은 쪽은 `delete`하지 않는다. 소유와 빌림을 타입으로 가르는 이 습관은 3-5강 Resource Manager에서 "
        "그대로 다시 나온다."),
    box("cs", None,
        "“함수 포인터와 함께 `void*` 하나를 맡겨 두었다가 콜백에서 돌려받는” 방식은 C 라이브러리의 오랜 관용구다. "
        "C에는 객체와 멤버 함수가 없으니, 호출 대상(`this`)을 직접 들고 다니는 것이다. C++의 멤버 함수 호출도 컴파일된 "
        "뒤에는 같은 일을 한다. 첫 인자로 객체의 주소를 넘긴다."),
    box("api", None,
        "Win32로 창을 직접 만들면 같은 문제가 `WndProc`에서 나온다. 해법도 같다. `SetWindowLongPtr`로 창에 포인터를 "
        "달아 두고 메시지 처리 함수에서 `GetWindowLongPtr`로 꺼낸다. 키 이벤트는 `WM_KEYDOWN`·`WM_KEYUP` 메시지로 온다."),
], lead="C 라이브러리의 콜백에 C++ 객체를 잇는 방법이다. 정적 함수와 user pointer, 두 장치가 짝으로 쓰인다.")

ch5 = chapter(5, "Pressed · Held · Released", [
    p("“눌려 있다”만으로는 부족하다. 점프는 누른 순간 한 번만, 모아서 쏘기는 떼는 순간에 일어나야 한다. 순간을 알려면 "
      "지금과 직전을 비교해야 하고, 그래서 배열이 둘이다. 이번 프레임의 상태와 직전 프레임의 상태다."),
    box("ex", "예시: 두 값으로 만드는 네 경우", [
        table([20, 20, 30, 30], ["직전 프레임", "이번 프레임", "뜻", "참이 되는 함수"], [
            ["꺼짐", "켜짐", "방금 눌렸다", "`IsKeyPressed`"],
            ["켜짐", "켜짐", "계속 누르고 있다", "`IsKeyHeld`"],
            ["켜짐", "꺼짐", "방금 떼었다", "`IsKeyReleased`"],
            ["꺼짐", "꺼짐", "아무 일 없다", "—"],
        ], cell_cls=["", "", "lab", ""], compact=True),
        p("값 둘의 조합은 이 넷뿐이다. 세 함수는 이 표의 한 줄씩을 그대로 옮긴 것이다."),
    ]),

    h3("5.1", "프레임을 따라가 보기"),
    Fig(226)
    .text(191, 14, "프레임 1", kind="s", size=9.5).text(273, 14, "2", kind="s", size=9.5)
    .text(355, 14, "3", kind="s", size=9.5).text(437, 14, "4", kind="s", size=9.5)
    .text(519, 14, "5", kind="s", size=9.5).text(601, 14, "6", kind="s", size=9.5)
    .line((232, 20), (232, 220), kind="muted dash").line((314, 20), (314, 220), kind="muted dash")
    .line((396, 20), (396, 220), kind="muted dash").line((478, 20), (478, 220), kind="muted dash")
    .line((560, 20), (560, 220), kind="muted dash")
    .text(20, 40, "이벤트", anchor="start", size=10)
    .text(273, 40, "PRESS", kind="mono accent", size=9.5)
    .text(519, 40, "RELEASE", kind="mono accent", size=9.5)
    .text(20, 68, "현재  _current_keys", anchor="start", size=10)
    .box(154, 52, 74, 24, "꺼짐", kind="plain").box(236, 52, 74, 24, "켜짐", kind="dark")
    .box(318, 52, 74, 24, "켜짐", kind="dark").box(400, 52, 74, 24, "켜짐", kind="dark")
    .box(482, 52, 74, 24, "꺼짐", kind="plain").box(564, 52, 74, 24, "꺼짐", kind="plain")
    .text(20, 100, "직전  _previous_keys", anchor="start", size=10)
    .box(154, 84, 74, 24, "꺼짐", kind="plain").box(236, 84, 74, 24, "꺼짐", kind="plain")
    .box(318, 84, 74, 24, "켜짐", kind="dark").box(400, 84, 74, 24, "켜짐", kind="dark")
    .box(482, 84, 74, 24, "켜짐", kind="dark").box(564, 84, 74, 24, "꺼짐", kind="plain")
    .line((20, 122), (640, 122), kind="muted")
    .text(20, 148, "IsKeyPressed", kind="mono", anchor="start", size=10)
    .box(236, 132, 74, 24, "참", kind="accent")
    .text(20, 178, "IsKeyHeld", kind="mono", anchor="start", size=10)
    .box(318, 162, 74, 24, "참", kind="accent").box(400, 162, 74, 24, "참", kind="accent")
    .text(20, 208, "IsKeyReleased", kind="mono", anchor="start", size=10)
    .box(482, 192, 74, 24, "참", kind="accent")
    .render("가로는 프레임이다. A를 2프레임에 눌러 5프레임에 떼었다. 직전 줄은 현재 줄을 한 칸 늦게 따라간다. "
            "두 줄이 어긋나는 칸이 Pressed와 Released이고, 둘 다 켜진 칸이 Held다."),
    p("2프레임을 보면 누른 첫 프레임에는 `IsKeyHeld`가 거짓이다. “누르는 동안 이동”을 `IsKeyHeld` 하나로 쓰면 첫 프레임이 "
      "빠진다. “지금 눌려 있는가”만 묻는 함수가 따로 있으면 좋겠다는 생각이 여기서 든다. 그 일은 1-4강으로 미룬다 (7.4절)."),

    h3("5.2", "직전 상태는 언제 갱신되는가"),
    p("직전 줄이 현재 줄을 한 칸 늦게 따라가게 만드는 것이 입력 관리자의 `Update()`다. 프레임에 한 번, 현재 배열을 "
      "직전 배열로 통째로 넘긴다. 문제는 그 한 번을 프레임의 **어디에** 두느냐다."),
    Fig(170)
    .text(20, 13, "맞는 순서", kind="t", anchor="start", size=10)
    .box(20, 22, 140, 46, "이벤트 처리", "콜백이 현재를 고친다")
    .arrow((160, 45), (186, 45))
    .box(186, 22, 140, 46, "게임 코드", "현재와 직전을 비교")
    .arrow((326, 45), (352, 45))
    .box(352, 22, 140, 46, "입력 넘기기", "직전 ← 현재", kind="accent")
    .arrow((492, 45), (518, 45))
    .box(518, 22, 122, 46, "화면", "버퍼를 내보낸다")
    .text(20, 99, "깨지는 순서", kind="accent", anchor="start", size=10)
    .box(20, 108, 140, 46, "이벤트 처리", "콜백이 현재를 고친다")
    .arrow((160, 131), (186, 131))
    .box(186, 108, 140, 46, "입력 넘기기", "직전 ← 현재", kind="accent")
    .arrow((326, 131), (352, 131))
    .box(352, 108, 140, 46, "게임 코드", "두 배열이 이미 같다", kind="soft")
    .arrow((492, 131), (518, 131))
    .box(518, 108, 122, 46, "화면", "버퍼를 내보낸다")
    .render("한 프레임 안의 순서다. 입력 넘기기가 이벤트 처리와 게임 코드 사이에 끼면, 게임 코드가 볼 때는 두 배열이 늘 "
            "같아서 Pressed와 Released가 한 번도 참이 되지 않는다."),
    box("cs", None,
        "컴퓨터구조 수업의 엣지 검출 회로와 같은 구조다. 직전 배열은 직전 값을 붙들고 있는 D 플립플롭이고, 입력 관리자의 "
        "`Update()`는 값을 넘겨받는 클록이다. Pressed는 상승 엣지(`현재 AND NOT 직전`), Released는 하강 엣지"
        "(`NOT 현재 AND 직전`)다. 프레임이 클록 주기인 셈이다."),
    box("ue", None,
        "Enhanced Input의 `ETriggerEvent`가 같은 구분이다. 기본 트리거에서 `Started`가 Pressed, `Triggered`가 누르는 동안, "
        "`Completed`가 Released에 해당한다. 예전 방식의 `BindAction`에서는 `IE_Pressed`와 `IE_Released`였다."),

    h3("5.3", "배열 둘을 담는 그릇"),
    p("두 배열은 크기가 같고, 프레임마다 한쪽을 다른 쪽으로 통째로 넘긴다. 그 일에 맞는 표준 라이브러리 타입이 "
      "`std::array`다."),
    fn("std::array",
       "template< class T, std::size_t N >\n"
       "struct array;",
       "크기가 컴파일할 때 정해지는 배열. 원소 `N`개가 객체 안에 그대로 들어 있다. 힙을 쓰지 않는다.",
       params=[("`T`", "원소의 타입"),
               ("`N`", "원소의 개수. 컴파일할 때 알려진 상수여야 한다")],
       notes=[("`operator[]`", "범위를 검사하지 않고 꺼낸다. 범위 밖의 인덱스는 정의되지 않은 동작이다"),
              ("`at()`", "범위를 벗어나면 `std::out_of_range` 예외를 던진다"),
              ("대입 `a = b`", "원소 전체를 복사한다. C 배열로는 할 수 없는 일이다"),
              ("헤더", "`<array>`")],
       lib="C++11"),
    box("ex", "예시: C 배열과 다른 점", [
        code(r"""
std::array<int, 3> a{ 1, 2, 3 };
std::array<int, 3> b{};         // every element is zero
b = a;                          // copies all three elements

int c[3] = { 1, 2, 3 };
int d[3];
// d = c;                       // error: a plain array cannot be assigned
""", tag="syntax"),
        p("칸은 349개이고 MSVC에서 `bool` 하나는 1바이트이므로 배열 하나는 349바이트다. 프레임마다 통째로 복사해도 "
          "비용은 없다시피 하다."),
    ]),
], lead="키 하나의 상태를 프레임 두 개에 걸쳐 보면 네 가지 경우가 나온다. 그중 셋에 이름을 붙인다.")

ch6 = chapter(6, "EKey: 키에 이름 붙이기", [
    code(r"""
enum class EKey : int
{
    // Unknown
    Unknown = -1,

    // Printable keys
    Space        = 32,
""", title="Engine/Enum/InputKeys.h — 앞부분", tag="now", start=3),
    code(r"""
    Menu         = 348,

    Last     = Menu,
    RangeMax = Last + 1
};
""", title="Engine/Enum/InputKeys.h — 끝부분", tag="now", start=134),
    p("이 파일은 저장소에 이미 있다. 키 120개의 이름과 번호를 적은 표라서 다시 치지 않는다. 읽어 둘 것은 "
      "타입의 종류(`enum class`)와 번호를 정한 방식이다."),

    h3("6.1", "enum class"),
    table([30, 35, 35], ["", "`enum`", "`enum class`"], [
        ["이름의 범위", "바깥으로 새어 나온다 (`A`)", "타입 안에 갇힌다 (`EKey::A`)"],
        ["정수로 바뀌는가", "저절로 바뀐다", "`static_cast`를 써야 한다"],
        ["바탕 타입 (적지 않으면)", "컴파일러가 고른다", "`int`"],
    ], cell_cls=["lab", "", ""]),
    box("ex", "예시: enum class와 정수 사이", [
        code(r"""
enum class Color : int { Red = 1, Green = 2 };

int   n = static_cast<int>( Color::Green );    // 2
Color c = static_cast<Color>( 1 );             // Color::Red
// int bad = Color::Green;                     // error: no implicit conversion
""", tag="syntax"),
        p("그래서 `EKey` 값을 배열 인덱스로 쓰려면 `static_cast<int>`가 필요하다. 번거롭지만 `IsKeyPressed( 65 )`처럼 아무 "
          "숫자나 넘기는 실수를 컴파일러가 막아 준다."),
    ]),

    h3("6.2", "값이 GLFW와 같다"),
    table([22, 39, 39], ["키", "`EKey`의 값", "GLFW의 키 코드"], [
        ["Space", "32 (`Engine/Enum/InputKeys.h:9`)", "`GLFW_KEY_SPACE` 32 (`include/GLFW/glfw3.h:396`)"],
        ["A", "65 (`:27`)", "`GLFW_KEY_A` 65 (`:414`)"],
        ["Escape", "256 (`:61`)", "`GLFW_KEY_ESCAPE` 256 (`:448`)"],
        ["Menu (마지막)", "348 (`:134`)", "`GLFW_KEY_MENU` 348 (`:517`)"],
        ["알 수 없는 키", "`Unknown` -1 (`:6`)", "`GLFW_KEY_UNKNOWN` -1 (`:367`)"],
    ], cell_cls=["lab", "", ""], compact=True),
    p("전부 같은 숫자다. 덕분에 콜백은 GLFW가 준 `key`를 변환 없이 그대로 배열의 인덱스로 쓸 수 있다. 배열의 크기는 "
      "`RangeMax`, 곧 349다 (`Engine/Enum/InputKeys.h:137`). 가장 큰 키 코드 348까지 칸이 있다."),
    cards([
        ("얻은 것", "변환 표가 없다", "GLFW 숫자를 `EKey`로 바꾸는 코드가 한 줄도 필요 없다. 콜백이 짧아진다.", ""),
        ("내준 것", "GLFW에 묶였다", "Engine의 공개 열거형이 GLFW의 숫자 체계를 그대로 따른다. 창 계층을 바꾸면 "
                               "거기서 변환 표를 만들어야 한다.", "3-2강에서 다시 본다"),
    ]),
    box("warn", "-1은 인덱스가 될 수 없다",
        "증상: 엉뚱한 메모리가 바뀌거나 프로그램이 죽는다. 배열의 `-1`번 칸은 배열 바깥이다. -1이 들어오는 길은 둘이다. "
        "GLFW가 모르는 키를 콜백에 `GLFW_KEY_UNKNOWN`으로 알릴 때, 그리고 누군가 조회 함수에 `EKey::Unknown`을 넘길 때다. "
        "두 길 모두 인덱스로 쓰기 전에 걸러야 한다. 조회 쪽의 검사를 한 곳에 모은 것이 `IsValidKey`다."),
], lead="게임 코드가 숫자 65 대신 `EKey::A`라고 쓸 수 있게 해 주는 열거형이다. 값을 어떻게 정했는지가 요점이다.")

ch7 = chapter(7, "설계", [
    h3("7.1", "파일 배치"),
    tree("""
Engine/
├── Core/
│   ├── EngineCore.h  #owns the manager, hands it out
│   └── EngineCore.cpp  #Init and Run each gain a few lines
├── Enum/
│   └── InputKeys.h  #already there: enum class EKey
└── Manager/
    ├── InputManager.h +  #class MInputManager
    └── InputManager.cpp +
Client/
└── main.cpp  #cbUpdate asks for A, S, D
"""),

    h3("7.2", "선언 스케치"),
    code(r"""
#pragma once
#include <array>
#include "Enum/InputKeys.h"

class MInputManager
{
public:
    MInputManager()  = default;
    ~MInputManager() = default;

    static bool IsValidKey( EKey key );     // which values must never become an index? (6.2)

    // GLFW fixes this signature (chapter 3). Why static, and how does it find the arrays? (chapter 4)
    static void cbSetKey( GLFWwindow* window, int key, int scancode, int action, int mods );

    void Update();                          // once per frame: where in the frame, and why there? (5.2)

    bool IsKeyPressed( EKey key );          // one row each of the table in chapter 5
    bool IsKeyHeld( EKey key );
    bool IsKeyReleased( EKey key );

private:
    static constexpr int kKeyRangeMax{ static_cast<int>(EKey::RangeMax) };

    std::array<bool, kKeyRangeMax> _current_keys;     // who writes this, and when?
    std::array<bool, kKeyRangeMax> _previous_keys;    // who writes this, and when?
};
""", title="Engine/Manager/InputManager.h", tag="sketch"),
    code(r"""
class GEngine
{
public:
    MInputManager* GetInputManager();    // who owns the manager, and who only borrows it? (4.3)

private:
    std::unique_ptr<class MInputManager> _input_manager;    // "class": a forward declaration
};
""", title="Engine/Core/EngineCore.h — what this lesson adds (the rest stays)", tag="sketch"),
    p("`<class MInputManager>`의 `class`는 이름만 알리는 전방 선언이다. 덕분에 `EngineCore.h`는 `InputManager.h`를 "
      "포함하지 않는다. 대신 그 객체를 만들고, 없애고, 멤버를 부르는 `.cpp`는 클래스의 전체 모양을 알아야 한다 (9장)."),

    keep(h3("7.3", "Init과 Run에 더해지는 일"),
    table([30, 26, 44], ["더할 일", "쓰는 것", "순서에서 따져 볼 것"], [
        ["창에 엔진의 주소를 맡긴다", "`glfwSetWindowUserPointer`", "콜백이 처음 불리기 전에 끝나 있어야 한다"],
        ["입력 관리자를 만든다", "`std::make_unique`", "콜백이 그 배열에 적기 전에 있어야 한다"],
        ["키 콜백을 단다", "`glfwSetKeyCallback`", "위의 둘이 끝난 뒤. 창이 있어야 달 수 있다"],
        ["프레임마다 직전 상태를 넘긴다", "`MInputManager::Update`", "5.2절의 그림"],
    ], cell_cls=["lab", "", ""], compact=True)),
    code(r"""
void cbUpdate( float delta_time )
{
    if ( GEngine::Get().GetInputManager()->IsKeyPressed( EKey::A ) )
    {
        // change the clear color; S and D each get a color of their own
    }
}
""", title="Client/main.cpp when this lesson is done", tag="usage"),

    keep(h3("7.4", "이 강에서 남겨 두는 것"),
    p("이름과 인자는 7.2절의 선언 그대로 쓴다. 1-4강부터의 자료가 그 선언을 기준으로 쓰여 있다. 바꾸고 싶은 점은 적어만 "
      "둔다. 아래는 이미 뒤 강의 일로 잡혀 있는 것들이다."),
    table([24, 58, 18], ["남겨 두는 것", "이 강을 끝냈을 때의 상태", "다루는 곳"], [
        ["입력 상태 배열의 초기값", "두 배열의 선언에 초기값이 없다. 무엇으로 시작하는지는 만드는 방법에 달려 있다", "1-4강 5.3절"],
        ["콜백의 범위 검사", "콜백은 `GLFW_KEY_UNKNOWN`만 거르고 `key`의 위쪽 범위는 보지 않는다", "1-4강 6.4절"],
        ["“지금 눌려 있는가”", "그것만 묻는 함수가 없다. `IsKeyHeld`는 누른 첫 프레임에 거짓이다 (5.1절)", "1-4강 6.4절"],
        ["조회 함수의 const", "상태를 바꾸지 않는 조회 함수 셋이 `const`가 아니다", "1-4강 6.4절"],
        ["잘못된 키를 알리기", "유효하지 않은 키가 들어오면 조용히 `false`를 돌려준다", "1-5강, 1-6강"],
        ["GLFW 숫자에 묶인 `EKey`", "6.2절의 “내준 것”", "3-2강"],
        ["마우스", "키보드뿐이다. 마우스 위치, 버튼, 휠이 없다", "4-2강"],
    ], cell_cls=["lab", "", "c"], compact=True)),
], lead="새로 만드는 클래스는 하나다. 모양은 정해져 있고, 본체를 채우는 것이 이 강의 일이다.")

ch8 = chapter(8, "구현 미션", [
    steps([
        ("키 이벤트를 눈으로 본다",
         "`main`에서 임시 콜백을 달아 `key`와 `action`을 `std::cout`으로 찍는다. A를 눌렀다 떼고, 꾹 눌러 보고, "
         "다른 창을 눌러 포커스를 옮겨 본다.",
         ["콜백의 모양은 3장의 `GLFWkeyfun`이다. 창을 가리키는 값은 `GetMainWindow()`로 얻는다."]),
        ("`MInputManager`의 파일과 선언을 만든다",
         "`Engine/Manager/`에 `.h`와 `.cpp`를 더하고 7.2절의 선언을 옮긴다. 본체는 비워 두고(조회 함수는 우선 `false`) "
         "빌드되는지 본다.",
         ["새 `.cpp`의 첫 줄은 `#include \"pch.h\"`다. `.vcxproj`의 새 항목이 한 줄인지 확인한다 (1-1강 10장)."]),
        ("엔진이 입력 관리자를 소유한다",
         "`GEngine`에 멤버와 `GetInputManager()`를 더하고 `Init`에서 만든다. `main`에서 받아 `nullptr`이 아닌지 확인한다.",
         ["`undefined type`이나 `incomplete type` 오류가 나면 그 `.cpp`가 무엇을 포함해야 하는지 본다 (7.2절, 9장)."]),
        ("콜백이 현재 상태를 적는다",
         "user pointer를 맡기고, 1단계의 임시 콜백을 지우고 `cbSetKey`를 단다. 콜백은 엔진을 거쳐 `_current_keys`의 "
         "그 키 칸을 켜고 끈다.",
         ["7.3절의 표가 `Init` 안에서의 순서를 알려 준다.",
          "`action`의 세 값 가운데 무엇에 반응할지, -1로 오는 `key`를 어떻게 할지 정한다 (3장, 6.2절)."]),
        ("`IsValidKey`와 조회 함수 셋을 쓴다",
         "5장의 표를 한 줄씩 옮긴다. `cbUpdate`에서 `IsKeyPressed( EKey::A )`가 참이면 배경색을 바꾸고 `std::cout`으로 한 줄을 "
         "찍는다. A를 꾹 누르면 몇 줄이 찍히는지 본다. 아직 `Update()`가 없어서 기대와 다르다. 이유를 적어 둔다.",
         ["`EKey`는 그대로 인덱스가 되지 못한다 (6.1절)."]),
        ("`Update()`로 직전 상태를 넘긴다",
         "본체를 쓰고 `Run` 안에서 프레임마다 부른다. A를 꾹 눌러도 한 줄만 찍히는지 본다.",
         ["부를 자리는 5.2절의 그림에 있다. 본체는 `std::array`의 성질 하나면 된다 (5.3절)."]),
        ("A·S·D로 색을 바꾸고, 일부러 틀려 본다",
         "세 키에 색을 하나씩 붙인다. 그 뒤 하나씩 해 보고 찍히는 줄 수를 본 뒤 되돌린다. (가) `IsKeyPressed`를 "
         "`IsKeyHeld`로 바꾼다. (나) `Update()` 호출을 이벤트 처리 바로 뒤로 옮긴다.",
         ["(나)의 결과는 5.2절 그림의 아랫줄이다."]),
        ("확인하고 커밋한다",
         "확인용 출력을 지우고, 10장의 기준을 하나씩 확인한 뒤 커밋한다. 그 뒤에 4월의 코드와 비교한다 (10.1절)."),
    ]),
], lead="한 단계가 끝날 때마다 빌드해서 눈으로 확인한다. 힌트는 막혔을 때 위에서부터 하나씩만 본다.", pb=True)

ch9 = chapter(9, "흔한 함정", [
    table([35, 43, 22], ["증상", "원인", "확인 방법"], [
        ["콜백을 넘기는 줄에서 컴파일 오류 `C3867`", "`cbSetKey`가 `static`이 아니다", "4.1절"],
        ["`use of undefined type` 또는 `can't delete an incomplete type`",
         "전방 선언만 보이는 `.cpp`에서 입력 관리자를 만들거나, 없애거나, 그 멤버를 불렀다", "그 `.cpp`의 `#include`"],
        ["키를 누르는 순간 접근 위반으로 죽는다", "user pointer를 맡기지 않았거나, 입력 관리자가 아직 없다", "콜백 첫 줄의 중단점"],
        ["키를 눌러도 아무 일이 없다", "콜백을 달지 않았거나, 다른 창에 포커스가 있다", "8장 1단계의 출력"],
        ["`EKey`를 `[ ]` 안에 쓰면 컴파일 오류", "`enum class`는 정수로 저절로 바뀌지 않는다", "6.1절"],
        ["누르는 동안 `IsKeyPressed`가 계속 참이다", "`Update()`를 부르지 않아 직전 상태가 늘 꺼짐이다", "8장 5 〜 6단계"],
        ["`IsKeyPressed`가 한 번도 참이 되지 않는다", "`Update()`가 이벤트 처리와 게임 코드 사이에 있다", "5.2절의 그림"],
        ["누르지 않은 키가 눌린 것으로 나온다", "배열이 정해지지 않은 값으로 시작했다", "7.4절의 첫 줄"],
        ["아주 짧게 친 키를 놓친다", "눌림과 뗌이 같은 `glfwPollEvents()` 안에서 처리됐다. 이 방식의 한계다", "11장의 5번"],
    ], compact=True),
], lead="증상에서 거꾸로 찾는 표다.")

ch10 = chapter(10, "완료 기준", [
    checklist([
        "A, S, D를 누르는 순간 배경색이 각각 다른 색으로 바뀐다.",
        "키를 꾹 누르고 있어도 `IsKeyPressed`는 한 번만 참이 된다. 8장 6단계의 출력으로 확인했다.",
        "`Client/`에서 `glfwSetKeyCallback`과 `glfwGetKey`가 검색되지 않는다. 입력은 엔진을 거쳐서만 묻는다.",
        "8장 1단계의 임시 콜백과 확인용 `std::cout` 출력이 남아 있지 않다.",
        "`Update()`를 프레임의 그 자리에서 부르는 이유를 한 문장으로 말할 수 있다.",
        "`Engine/Engine.vcxproj`에서 `InputManager.cpp` 항목이 한 줄이고, 커밋 하나로 묶였다.",
    ]),

    h3("10.1", "끝낸 뒤에: 4월의 코드와 비교한다"),
    code(r"""
git diff first-pass-2026-04 -- Engine/Manager Engine/Core Client/main.cpp
""", lang="text", title="run in the repository root", tag="usage"),
    p("태그 `first-pass-2026-04`의 1차 코드와 지금 코드를 나란히 보는 명령이다. `--` 뒤는 비교할 경로다. 다른 곳이 왜 "
      "다른지 설명할 수 있으면 된다. 1차 코드를 줄 단위로 해설한 자료가 `Legacy/ClaudGL_1-3_Input_v3.pdf`다."),
], lead="전부 눈이나 검색으로 확인할 수 있는 조건이다.")

ch11 = chapter(11, "생각해 볼 질문", [
    exgroup("A", "코드를 보지 않고 답하시오", "한두 문장으로, 이유까지"),
    qlist([
        "키를 누른 바로 그 프레임에 `IsKeyHeld`는 참인가?",
        "`cbSetKey`에서 `static`을 떼면 `glfwSetKeyCallback`에 넘길 수 있는가?",
        "콜백이 `GLFW_REPEAT`도 `GLFW_PRESS`처럼 처리하도록 바꾸면 `IsKeyPressed`의 결과가 달라지는가?",
        "입력 관리자의 `Update()`를 프레임의 맨 앞, `glfwPollEvents()`보다 앞으로 옮기면 판정은 어떻게 되는가?",
        "A를 아주 짧게 쳐서 눌림과 뗌이 같은 `glfwPollEvents()` 안에서 처리되면 `IsKeyPressed( EKey::A )`는 어떻게 되는가?",
        "user pointer에 `GEngine*`가 아니라 `MInputManager*`를 맡겼다면 무엇이 달라지는가? 얻는 것과 잃는 것은?",
    ], lines=3),
], lead="답을 보기 전에 소리 내어 설명해 본다. 막히는 문항이 다시 읽을 장이다.", pb=True)

ch12 = chapter(12, "해설", [
    answers("질문 A", [
        ("거짓이다.",
         "그 프레임에는 직전 상태가 꺼짐이라 `IsKeyPressed`만 참이다. 다음 프레임부터 `IsKeyHeld`가 참이 된다. (5.1절)"),
        ("넘길 수 없다. 컴파일 오류가 난다.",
         "멤버 함수는 `this`를 받아야 해서 평범한 함수 포인터와 타입이 다르다. (4.1절)"),
        ("달라지지 않는다.",
         "`GLFW_REPEAT`이 올 때 그 칸은 이미 켜져 있다. 다시 켜도 직전 상태와 비교한 결과는 같다. 3.2절의 예시가 "
         "깨진 것은 상태가 아니라 횟수를 세었기 때문이다. (3.2절)"),
        ("그대로 올바르게 동작한다.",
         "넘긴 뒤에 이벤트가 들어와 현재만 바뀌므로, 게임 코드가 돌 때 현재와 직전이 제대로 다르다. 깨지는 자리는 "
         "이벤트 처리와 게임 코드 사이 하나뿐이다. (5.2절)"),
        ("한 번도 참이 되지 않는다.",
         "칸이 켜졌다가 같은 호출 안에서 꺼져서, 게임 코드가 볼 때는 눌린 적이 없는 것과 같다. 놓치지 않으려면 "
         "이벤트 자체를 큐에 쌓아 두는 방식이 필요하다. (9장)"),
        ("콜백이 엔진을 거치지 않고 입력 관리자에 바로 닿는다. 대신 그 칸을 다른 용도로 쓸 수 없다.",
         "칸은 창마다 하나뿐이다. 나중에 창 크기나 마우스 콜백이 엔진의 다른 부분에 닿아야 할 때, 엔진을 맡겨 두었다면 "
         "같은 칸으로 모두 갈 수 있다. (4.2절)"),
    ]),
])

ch13 = glossary_chapter(13, [
    ("이벤트", "event", "일어난 순간에 한 번 전달되는 알림. 키 눌림, 키 뗌"),
    ("상태", "state", "지금의 모습. 언제 물어도 답이 있다"),
    ("폴링", "polling", "필요할 때마다 현재 상태를 물어보는 방식"),
    ("키 코드", "key code, GLFW_KEY_*", "키의 자리에 붙인 번호. 미국 표준 자판 기준이다"),
    ("키 반복", "key repeat, GLFW_REPEAT", "키를 누르고 있을 때 운영체제가 되풀이해 보내는 이벤트"),
    ("엣지 검출", "edge detection", "직전 값과 현재 값을 비교해 바뀌는 순간을 찾는 것"),
    ("user pointer", "glfwSetWindowUserPointer", "GLFW가 창마다 맡아 주는 `void*` 하나"),
    ("정적 멤버 함수", "static member function", "`this` 없이 불리는 멤버 함수. 주소를 평범한 함수처럼 넘긴다"),
    ("범위 있는 열거형", "enum class", "이름이 타입 안에 갇히고 정수로 저절로 바뀌지 않는 열거형"),
    ("소유", "ownership", "객체를 없앨 책임. `std::unique_ptr`는 주인이 하나라고 적는 타입이다"),
    ("전방 선언", "forward declaration", "클래스의 이름만 먼저 알리는 선언. 전체 모양은 다른 곳에 있다"),
], pb=False)

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
