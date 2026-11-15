"""Lesson 1-3 -- input system (handout written after the code; it quotes the repository).

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

COVER = cover(
    f"CLAUDGL ENGINE · PART {ME['part']} · {ME['id']} · v{ME['ver']}",
    Raw('M<span class="ac">Input</span>Manager'),
    ME["title"],
    "키보드의 한 번 누름이 `IsKeyPressed`의 `true`가 되기까지",
    [
        ("다루는 범위", "`EKey` 열거형, 키 콜백에서 상태 배열까지, Pressed·Held·Released 판정"),
        ("핵심 개념", "이벤트와 폴링 · 정적 콜백과 user pointer · 엣지 검출 · `enum class`"),
        ("관련 파일", "`Engine/Enum/InputKeys.h`, `Engine/Manager/InputManager.h`·`.cpp`, "
                  "`Engine/Core/EngineCore.cpp`, `Client/main.cpp`"),
        ("읽는 시간", "약 40분"),
        ("코드 기준", f"커밋 `{CODE_COMMIT}` — {CODE_READ_DATE}에 읽음"),
    ],
    note=("읽는 법",
          "1-2강의 루프에서 75행(이벤트 처리)과 79행(입력 넘기기)이 이 자료의 두 기둥이다. 코드 블록 왼쪽 숫자는 "
          "실제 줄 번호다. 7장은 다시 보니 걸리는 곳이고, 고치는 일은 1-4강에서 한다."),
    toc=["한 장으로 보기", "이벤트를 상태로 바꾼다", "정적 콜백과 user pointer", "Pressed · Held · Released",
         "EKey: 키에 이름 붙이기", "쓰는 쪽", "다시 보면 걸리는 곳", "스스로 설명해 보기", "해설", "용어집"],
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
], lead="입력 시스템이 하는 일은 한 가지다. 운영체제가 알려 주는 “방금 눌렸다”를, 게임 코드가 묻는 “지금 눌려 있나”로 "
        "바꾸는 것이다.")

ch2 = chapter(2, "이벤트를 상태로 바꾼다", [
    cards([
        ("이벤트", "순간에 일어난 일", "“A가 눌렸다”, “A가 떼졌다”. 일어난 때에 한 번 전달되고 사라진다.",
         "운영체제와 GLFW가 주는 것"),
        ("상태", "지금의 모습", "“A가 눌려 있다”. 언제 물어도 답이 있다.", "게임 코드가 프레임마다 묻는 것"),
    ]),
    code(r"""
void MInputManager::cbSetKey( GLFWwindow* window, int key, int scancode, int action, int mods )
{
    if ( key == GLFW_KEY_UNKNOWN ) return;

    auto engine  = static_cast<GEngine*>(glfwGetWindowUserPointer( window ));

    if ( action == GLFW_PRESS )
    {
        engine->GetInputManager()->_current_keys[key] = true;
    }
    else if ( action == GLFW_RELEASE )
    {
        engine->GetInputManager()->_current_keys[key] = false;
    }
}
""", title="Engine/Manager/InputManager.cpp", tag="now", start=12),
    table([24, 76], ["줄", "하는 일"], [
        ["14", "GLFW가 알아보지 못한 키는 `key`가 `-1`(`GLFW_KEY_UNKNOWN`)로 온다. 배열의 `-1`번 칸을 건드리지 않도록 먼저 거른다."],
        ["16", "창에 달아 둔 포인터에서 엔진을 꺼낸다 (3장)."],
        ["18〜21", "눌렸으면 그 키의 칸을 `true`로."],
        ["22〜25", "떼졌으면 `false`로."],
    ], cell_cls=["num", ""]),
    p("`action`에는 값이 하나 더 있다. 키를 누르고 있으면 운영체제가 되풀이해 보내는 `GLFW_REPEAT`다. 두 조건 어디에도 "
      "걸리지 않으므로 무시되고, 칸은 `true`인 채로 남는다. 누르고 있는 상태를 표현하는 데는 그것으로 충분하다."),
    box("point", None,
        "콜백은 아무 때나 불리지 않는다. `glfwPollEvents()` 안에서만 불린다(`Engine/Core/EngineCore.cpp:75`). "
        "그래서 한 프레임 동안 `_current_keys`는 변하지 않고, 같은 프레임 안에서는 몇 번을 물어도 답이 같다."),
    p("창이 포커스를 잃을 때 눌려 있던 키는 어떻게 될까. GLFW는 그 순간 눌린 키 전부에 대해 뗌 이벤트를 만들어 "
      "보내 준다. 그래서 다른 창으로 넘어간 사이 키를 떼도 칸이 `true`로 남지 않는다."),
], lead="운영체제는 일이 일어난 순간에만 알려 준다. 그 순간들을 받아 적어 두어야 나중에 물을 수 있다.")

ch3 = chapter(3, "정적 콜백과 user pointer", [
    h3("3.1", "왜 static인가"),
    p("GLFW는 C 라이브러리다. `glfwSetKeyCallback`이 받는 것은 평범한 함수의 주소이고, C++ 클래스의 멤버 함수는 "
      "받지 못한다. 멤버 함수는 보이지 않는 첫 인자로 `this`를 받기 때문에, 겉보기 매개변수가 같아도 호출하는 "
      "방법이 다르다. `static` 멤버 함수는 `this`가 없어서 평범한 함수와 똑같이 부를 수 있다."),
    code(r"""
    static void cbSetKey( GLFWwindow* window, int key, int scancode, int action, int mods );
""", title="Engine/Manager/InputManager.h", tag="now", start=13),

    h3("3.2", "this가 없으면 어느 객체인지 어떻게 아는가"),
    p("`static` 함수 안에서는 “내 배열”이 없다. 어느 `MInputManager`의 배열에 적을지 밖에서 찾아와야 한다. "
      "GLFW는 이럴 때 쓰라고 창마다 포인터 하나를 맡아 준다."),
    flow([
        ("맡긴다", "Init 36행", "accent"),
        ("GLFW가 보관", "창마다 포인터 하나"),
        ("꺼낸다", "콜백 16행", "accent"),
        ("엔진을 거쳐", "입력 관리자로"),
        ("적는다", "현재 배열에"),
    ], "맡길 때는 `glfwSetWindowUserPointer`, 꺼낼 때는 `glfwGetWindowUserPointer`다."),
    code(r"""
    glfwSetWindowUserPointer( _main_window, this );

    // init manager
    _input_manager = std::make_unique<MInputManager>();
    glfwSetKeyCallback( _main_window, MInputManager::cbSetKey );
""", title="Engine/Core/EngineCore.cpp", tag="now", start=36, hl=[36, 40]),
    p("맡기는 것은 `GEngine*`이고(36행), 꺼낼 때는 `void*`로 나오므로 원래 타입으로 되돌린다"
      "(`Engine/Manager/InputManager.cpp:16`의 `static_cast<GEngine*>`). 맡긴 타입과 꺼내는 타입이 다르면 "
      "컴파일러는 잡아 주지 못한다."),
    p("`cbSetKey`가 `private` 멤버인 `_current_keys`를 건드릴 수 있는 것은 같은 클래스의 멤버 함수이기 때문이다. "
      "접근 제한은 객체 단위가 아니라 클래스 단위로 걸린다."),
    box("cs", None,
        "“함수 포인터와 함께 `void*` 하나를 맡겨 두었다가 콜백에서 돌려받는” 방식은 C 라이브러리의 오랜 관용구다. "
        "C에는 객체와 멤버 함수가 없으니, 호출 대상(`this`)을 직접 들고 다니는 것이다."),
    box("api", None,
        "Win32로 창을 직접 만들면 같은 문제가 `WndProc`에서 나온다. 해법도 같다. `SetWindowLongPtr`로 창에 포인터를 "
        "달아 두고 메시지 처리 함수에서 `GetWindowLongPtr`로 꺼낸다. 키 이벤트는 `WM_KEYDOWN`·`WM_KEYUP` 메시지로 온다."),
], lead="C 라이브러리의 콜백에 C++ 객체를 잇는 방법이다. 두 가지 장치가 짝으로 쓰인다.")

ch4 = chapter(4, "Pressed · Held · Released", [
    p("“눌려 있다”만으로는 부족할 때가 많다. 점프는 누른 순간 한 번만, 차지는 떼는 순간에 일어나야 한다. "
      "순간을 알아내려면 지금과 직전을 비교해야 하고, 그래서 배열이 둘이다(`Engine/Manager/InputManager.h:24` 〜 `:25`)."),
    table([20, 20, 30, 30], ["직전 프레임", "이번 프레임", "판정", "참이 되는 함수"], [
        ["꺼짐", "켜짐", "방금 눌렸다", "`IsKeyPressed`"],
        ["켜짐", "켜짐", "계속 누르고 있다", "`IsKeyHeld`"],
        ["켜짐", "꺼짐", "방금 떼졌다", "`IsKeyReleased`"],
        ["꺼짐", "꺼짐", "아무 일 없다", "—"],
    ], cell_cls=["", "", "lab", ""]),
    code(r"""
bool MInputManager::IsKeyPressed( EKey key )
{
    if ( !IsValidKey( key ) ) return false; // need log
    int code = static_cast<int>(key);
    return _current_keys[code] && !_previous_keys[code];
}

bool MInputManager::IsKeyHeld( EKey key )
{
    if ( !IsValidKey( key ) ) return false; // need log
    int code = static_cast<int>(key);
    return _current_keys[code] && _previous_keys[code];
}
""", title="Engine/Manager/InputManager.cpp", tag="now", start=33, hl=[37, 44]),
    p("`IsKeyReleased`(47〜52행)는 같은 모양에 조건만 `!_current_keys[code] && _previous_keys[code]`다."),

    h3("4.1", "프레임을 따라가 보기"),
    table([11, 19, 14, 14, 14, 14, 14], ["프레임", "이벤트", "현재", "직전", "Pressed", "Held", "Released"], [
        ["1", "—", "꺼짐", "꺼짐", "", "", ""],
        ["2", "A 눌림", "켜짐", "꺼짐", "==참==", "", ""],
        ["3", "—", "켜짐", "켜짐", "", "==참==", ""],
        ["4", "—", "켜짐", "켜짐", "", "==참==", ""],
        ["5", "A 떼짐", "꺼짐", "켜짐", "", "", "==참=="],
        ["6", "—", "꺼짐", "꺼짐", "", "", ""],
    ], cell_cls=["num", "", "", "", "c", "c", "c"]),
    p("2프레임을 보면 누른 첫 프레임에는 `IsKeyHeld`가 거짓이다. “누르는 동안 이동”을 `IsKeyHeld` 하나로 쓰면 "
      "첫 프레임이 빠진다."),

    h3("4.2", "직전 상태는 언제 갱신되는가"),
    code(r"""
void MInputManager::Update()
{
    _previous_keys = _current_keys;
}
""", title="Engine/Manager/InputManager.cpp", tag="now", start=28),
    p("이 함수는 프레임의 끝, 게임 코드가 다 돈 뒤에 불린다(`Engine/Core/EngineCore.cpp:79`). 배열 349칸을 통째로 "
      "복사하지만 349바이트라서 비용은 없다시피 하다. 위 표에서 “직전” 칸이 한 프레임 늦게 “현재”를 따라가는 것이 "
      "이 한 줄의 효과다."),
    box("cs", None,
        "컴퓨터구조 수업의 엣지 검출 회로와 같은 구조다. `_previous_keys`는 직전 값을 붙들고 있는 D 플립플롭이고, "
        "`Update()`는 값을 넘겨받는 클록이다. Pressed는 상승 엣지(`현재 AND NOT 직전`), Released는 하강 엣지"
        "(`NOT 현재 AND 직전`)다. 프레임이 클록 주기인 셈이다."),
    box("ue", None,
        "Enhanced Input의 `ETriggerEvent`가 같은 구분이다. `Started`가 Pressed, `Triggered`가 누르는 동안, "
        "`Completed`가 Released에 해당한다. 예전 방식의 `BindAction`에서는 `IE_Pressed`와 `IE_Released`였다."),
], lead="키 하나의 상태를 프레임 두 개에 걸쳐 보면 네 가지 경우가 나온다. 그중 셋에 이름을 붙였다.")

ch5 = chapter(5, "EKey: 키에 이름 붙이기", [
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

    h3("5.1", "enum class"),
    table([30, 35, 35], ["", "`enum`", "`enum class`"], [
        ["이름의 범위", "바깥으로 새어 나온다 (`A`)", "타입 안에 갇힌다 (`EKey::A`)"],
        ["정수로 바뀌는가", "저절로 바뀐다", "`static_cast`를 써야 한다"],
        ["바탕 타입 (적지 않으면)", "컴파일러가 고른다", "`int`"],
    ], cell_cls=["lab", "", ""]),
    p("그래서 배열 인덱스로 쓰려면 `static_cast<int>(key)`가 필요하다(`Engine/Manager/InputManager.cpp:36`). "
      "번거롭지만 `IsKeyPressed( 65 )`처럼 아무 숫자나 넘기는 실수를 컴파일러가 막아 준다."),

    h3("5.2", "값이 GLFW와 같다"),
    p("`Space = 32`, `A = 65`, `Escape = 256`, `Menu = 348`. 전부 GLFW의 키 코드와 같은 숫자다. 덕분에 콜백은 변환 없이 "
      "GLFW가 준 `key`를 그대로 인덱스로 쓴다(`Engine/Manager/InputManager.cpp:20`). 배열의 크기는 "
      "`RangeMax`, 곧 349다(`Engine/Manager/InputManager.h:22`)."),
    cards([
        ("얻은 것", "변환 표가 없다", "GLFW 숫자 → `EKey` 변환 코드가 한 줄도 없다. 콜백이 짧다.", ""),
        ("내준 것", "GLFW에 묶였다", "Engine의 공개 열거형이 GLFW의 숫자 체계를 그대로 따른다. 창 계층을 바꾸면 "
                               "거기서 변환 표를 만들어야 한다.", "3-2강에서 다시 본다"),
    ]),
    code(r"""
bool MInputManager::IsValidKey( EKey key )
{
    int code = static_cast<int>(key);
    return code >= 0 && code < kKeyRangeMax;
}
""", title="Engine/Manager/InputManager.cpp", tag="now", start=6),
    p("`IsValidKey`는 `EKey::Unknown`(-1)이 배열 인덱스가 되는 것을 막는다. 조회하는 세 함수가 모두 이것을 먼저 부른다."),
], lead="게임 코드가 숫자 65 대신 `EKey::A`라고 쓸 수 있게 해 주는 열거형이다. 값을 어떻게 정했는지가 요점이다.")

ch6 = chapter(6, "쓰는 쪽", [
    code(r"""
void cbUpdate( float delta_time )
{
    if ( GEngine::Get().GetInputManager()->IsKeyPressed( EKey::A ) )
    {
        glClearColor( 0.f, 1.f, 0.f, 1.f );
    }
    else if ( GEngine::Get().GetInputManager()->IsKeyPressed( EKey::S ) )
    {
        glClearColor( 0.f, 0.f, 1.f, 1.f );
    }
    else if ( GEngine::Get().GetInputManager()->IsKeyPressed( EKey::D ) )
    {
        glClearColor( 1.f, 0.f, 0.f, 1.f );
    }
}
""", title="Client/main.cpp", tag="now", start=27),
    p("A, S, D를 누르는 순간 배경색이 초록, 파랑, 빨강으로 바뀐다. 색은 다음 프레임의 `glClear`에서 적용된다."),
    table([40, 60], ["호출 조각", "돌려주는 것"], [
        ["`GEngine::Get()`", "엔진 인스턴스의 참조 (1-1강)"],
        ["`.GetInputManager()`", "`MInputManager*`. 엔진이 `unique_ptr`로 들고 있는 것을 빌려준다 (`Engine/Core/EngineCore.cpp:14` 〜 `:17`)"],
        ["`->IsKeyPressed( EKey::A )`", "이번 프레임에 A가 방금 눌렸는가"],
    ], cell_cls=["lab", ""]),
    box("point", None,
        "주인은 `GEngine` 하나다. `unique_ptr`가 그것을 타입으로 적어 둔다(`Engine/Core/EngineCore.h:28`). "
        "`GetInputManager()`가 내주는 맨 포인터는 “잠깐 쓰라”는 뜻이고, 받은 쪽은 `delete`하지 않는다. "
        "소유와 빌림을 타입으로 가르는 이 습관은 1-8강 Resource Manager에서 그대로 다시 나온다."),
], lead="지금 입력을 쓰는 곳은 `cbUpdate` 하나다. 호출 한 줄에 1-1 〜 1-3강의 내용이 다 들어 있다.")

ch7 = chapter(7, "다시 보면 걸리는 곳", [
    table([38, 50, 12], ["위치", "관찰", "이어지는 강"], [
        ["`Engine/Manager/InputManager.h:24` 〜 `:25`",
         "두 배열에 초기값이 없다. 지금은 `std::make_unique<MInputManager>()`의 값 초기화"
         "(`Engine/Core/EngineCore.cpp:39`)가 0으로 채워 주지만, 만드는 방식이 바뀌면 쓰레기 값으로 시작한다.", "1-4강"],
        ["`Engine/Manager/InputManager.cpp:20`, `:24`",
         "콜백은 `key`의 위쪽 범위를 검사하지 않고 인덱스로 쓴다. `IsValidKey`는 조회 쪽에만 있다. GLFW가 348을 넘는 "
         "값을 주지 않는 동안은 안전하다.", "1-4강"],
        ["`Engine/Manager/InputManager.h:17` 〜 `:19`",
         "“지금 눌려 있는가”만 묻는 함수가 없다. `IsKeyHeld`는 누른 첫 프레임에 거짓이라 (4.1절) 이동 같은 입력에 "
         "그대로 쓰면 한 프레임이 빠진다.", "1-4강"],
        ["`Engine/Manager/InputManager.h:17` 〜 `:19`",
         "조회 함수 셋이 `const`가 아니다. 상태를 바꾸지 않는 함수들이다.", "1-4강"],
        ["`Engine/Manager/InputManager.cpp:35`, `:42`, `:49`",
         "`// need log` 주석 셋. 잘못된 키가 들어오면 조용히 `false`를 돌려준다.", "1-5강"],
        ["`Engine/Manager/InputManager.cpp:12` 〜 `:26`",
         "폴링 방식의 한계로, 한 번의 `glfwPollEvents()` 안에서 눌렸다 떼진 키는 Pressed가 한 번도 참이 되지 않는다.", "—"],
        ["`Engine/Enum/InputKeys.h`, `Engine/Manager/InputManager.cpp:20`",
         "`EKey`의 값과 콜백의 인덱싱이 GLFW 키 코드에 묶여 있다 (5.2절).", "3-2강"],
        ["`Engine/Manager/InputManager.h`",
         "키보드뿐이다. 마우스 위치·버튼·휠이 없다.", "4-2강"],
    ]),
], lead=f"{CODE_READ_DATE}에 다시 읽으며 적었다. A·S·D로 배경색을 바꾸는 지금의 쓰임에서는 드러나지 않는 것들이다. "
        "고치는 방법은 여기 적지 않는다.", pb=True)

ch8 = chapter(8, "스스로 설명해 보기", [
    exgroup("A", "코드를 보지 않고 답하시오", "한두 문장으로, 이유까지"),
    qlist([
        "키를 누른 바로 그 프레임에 `IsKeyHeld`는 참인가?",
        "`cbSetKey`에서 `static`을 떼면 `glfwSetKeyCallback`에 넘길 수 있는가?",
        "`GLFW_REPEAT`도 `GLFW_PRESS`처럼 처리하도록 바꾸면 `IsKeyPressed`의 결과가 달라지는가?",
        "`_previous_keys = _current_keys;`를 프레임의 맨 앞, `glfwPollEvents()`보다 앞으로 옮기면 판정은 어떻게 되는가?",
        "A를 아주 짧게 쳐서 눌림과 뗌이 같은 `glfwPollEvents()` 안에서 처리되면 `IsKeyPressed( EKey::A )`는 어떻게 되는가?",
        "`EKey`를 `enum class`가 아닌 `enum`으로 바꾸면 `IsKeyPressed( 65 )`는 컴파일되는가?",
    ]),
], lead="답을 보기 전에 소리 내어 설명해 본다. 막히는 문항이 다시 읽을 장이다.", pb=True)

ch9 = chapter(9, "해설", [
    answers("질문 A", [
        ("거짓이다.", "그 프레임에는 직전 상태가 꺼짐이라 `IsKeyPressed`만 참이다. 다음 프레임부터 `IsKeyHeld`가 참이 된다. (4.1절)"),
        ("넘길 수 없다. 컴파일 오류가 난다.",
         "멤버 함수는 `this`를 받아야 해서 평범한 함수 포인터와 타입이 다르다. (3.1절)"),
        ("달라지지 않는다.",
         "REPEAT이 올 때 그 칸은 이미 `true`다. 다시 `true`를 적어도 직전 상태와의 비교 결과는 같다. (2장)"),
        ("그대로 올바르게 동작한다.",
         "복사한 뒤에 이벤트가 들어와 현재만 바뀌므로, 게임 코드가 돌 때 현재와 직전이 제대로 다르다. 깨지는 자리는 "
         "`glfwPollEvents()`와 게임 코드 사이 하나뿐이다. (4.2절, 1-2강의 5장)"),
        ("한 번도 참이 되지 않는다.",
         "칸이 `true`가 되었다가 같은 호출 안에서 `false`로 돌아가, 게임 코드가 볼 때는 눌린 적이 없는 것과 같다. (7장)"),
        ("컴파일되지 않는다.",
         "`enum`은 정수로 저절로 바뀌지만 정수가 `enum`으로 저절로 바뀌지는 않는다. `enum class`로 달라지는 것은 "
         "반대 방향, 곧 `_current_keys[key]`에 `static_cast`가 필요해지는 쪽이다. (5.1절)"),
    ]),
])

ch10 = glossary_chapter(10, [
    ("이벤트", "event", "일어난 순간에 한 번 전달되는 알림. 키 눌림, 키 뗌"),
    ("폴링", "polling", "필요할 때마다 현재 상태를 물어보는 방식"),
    ("엣지 검출", "edge detection", "직전 값과 현재 값을 비교해 바뀌는 순간을 찾는 것"),
    ("user pointer", "glfwSetWindowUserPointer", "GLFW가 창마다 맡아 주는 `void*` 하나"),
    ("정적 멤버 함수", "static member function", "`this` 없이 불리는 멤버 함수. 평범한 함수처럼 주소를 넘길 수 있다"),
    ("범위 있는 열거형", "enum class", "이름이 타입 안에 갇히고 정수로 저절로 바뀌지 않는 열거형"),
    ("키 반복", "key repeat (GLFW_REPEAT)", "키를 누르고 있을 때 운영체제가 되풀이해 보내는 이벤트"),
    ("값 초기화", "value-initialization", "`T()`처럼 빈 괄호로 만드는 초기화. 조건에 따라 0으로 채운다"),
], pb=False)

if __name__ == "__main__":
    info = build(
        {"title": f"ClaudGL Engine {ME['id']} {ME['title']} v{ME['ver']}",
         "footer": f"ClaudGL Engine · {ME['id']} {ME['title']} · v{ME['ver']}"},
        COVER, [ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8, ch9, ch10], OUT_HTML,
    )
    pages = render(OUT_HTML, OUT_PDF)
    print(f"pdf: {OUT_PDF} ({pages} pages)")
    print(f"tables: {info['tables']}  diagrams: {info['diagrams']}  code blocks: {info['code_blocks']}")
    print(f"issues: {info['issues']}")
