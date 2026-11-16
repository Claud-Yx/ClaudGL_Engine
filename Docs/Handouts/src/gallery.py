"""Component gallery -- every lesson building block on a few pages.

Not a lesson. Rebuild it after changing common.py or base.css to see that
nothing broke, and copy from it when writing a new lesson file.

Run:  python -I src/gallery.py      (from Docs/Handouts, with the handout venv)
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_engine"))
sys.path.insert(0, str(ROOT / "src"))

from common import *          # noqa: E402,F403
from render import render     # noqa: E402

OUT_PDF = ROOT / "_build" / "gallery.pdf"
OUT_HTML = ROOT / "_build" / "gallery.html"

COVER = cover(
    "CLAUDGL ENGINE · PART 0 · 0-0",
    Raw('M<span class="ac">Input</span>Manager'),
    "부품 견본",
    "과별 강의 자료에 쓰는 부품을 한곳에 모은 견본이다",
    [
        ("목표 결과물", "이 과가 끝나면 화면이나 로그에 보여야 하는 것 한 줄"),
        ("핵심 개념", "개념 A · 개념 B · 개념 C"),
        ("선수 지식", "앞 과에서 만든 것, 알고 있어야 할 C++ 기능"),
        ("예상 시간", "읽기 30분 + 구현 2〜3시간"),
        ("건드릴 파일", "`Engine/Manager/InputManager.h`, `Engine/Manager/InputManager.cpp`"),
    ],
    note=("읽는 법",
          "개념 장을 먼저 읽고, 설계 장에서 결정할 것을 적은 뒤, 미션을 순서대로 구현한다. 힌트는 막혔을 때 "
          "한 단계씩만 연다. 코드 블록은 완성본이 아니라 모양을 보여 주는 스케치다."),
    toc=["코드 블록", "그림", "상자와 비교", "미션과 완료 기준", "질문과 해설", "용어집"],
)

ch1 = chapter(1, "코드 블록", [
    h3("1.1", "현재 코드 — 지금 저장소에 있는 것"),
    code("""
class MInputManager
{
public:
    bool IsKeyPressed( EKey key );
    bool IsKeyHeld( EKey key );
    bool IsKeyReleased( EKey key );

private:
    std::array<bool, kKeyRangeMax> _current_keys;   // no initializer
    std::array<bool, kKeyRangeMax> _previous_keys;  // no initializer
};
""", title="Engine/Manager/InputManager.h", tag="now", hl=[9, 10]),

    h3("1.2", "선언 스케치 — 모양만, 본문 없음"),
    code("""
class MExample
{
public:
    void Init();                       // what must be ready after this call?
    void Shutdown();                   // who calls this, and when?
    bool IsReady() const;

private:
    // which members does Init() need to fill in?
};
""", title="Engine/Manager/Example.h", tag="sketch"),

    h3("1.3", "문법과 안티패턴"),
    code("""
auto manager = std::make_unique<MInputManager>();   // value-initialized
MInputManager on_stack;                             // default-initialized
""", tag="syntax"),
    code("""
if ( keys[code] ) { /* reads an indeterminate value */ }
""", title="reading before writing", tag="bad"),

    h3("1.4", "출력과 파일 배치"),
    console(Raw(
        '<span class="dim">[12:00:01.204]</span> <span class="ok">[Info ]</span> [Core] Engine initialized\n'
        '<span class="dim">[12:00:01.377]</span> <span class="warn">[Warn ]</span> [Input] Unknown key code: 512\n'
        '<span class="dim">[12:00:02.010]</span> <span class="err">[Error]</span> [Render] Shader compile failed'
    ), title="기대하는 출력"),
    tree("""
Engine/
├── Core/
│   ├── EngineCore.h
│   └── Logger.h
└── Manager/
    ├── InputManager.h
    └── Example.h +  #this lesson adds it
"""),

    h3("1.5", "함수 설명 — 남이 만든 함수의 사용법"),
    fn("glfwWindowHint", "void glfwWindowHint( int hint, int value );",
       "다음에 만들 창과 컨텍스트의 조건을 예약한다. 창을 만들 때 한꺼번에 적용된다.",
       params=[("`hint`", "무엇을 정할지. `GLFW_CONTEXT_VERSION_MAJOR` 같은 상수"),
               ("`value`", "그 항목의 값")],
       returns="없다",
       fails="모르는 `hint`를 주면 `GLFW_INVALID_ENUM` 오류가 난다. 값이 맞는지는 창을 만들 때 검사된다",
       notes=[("부르는 순서", "`glfwInit()` 뒤, `glfwCreateWindow()` 앞")],
       lib="GLFW 3.4"),
], lead="코드 블록은 네 가지 꼬리표로 쓰임을 밝힌다. 주석은 영어로 쓰고, 함수 본문 완성본은 싣지 않는다. "
        "라이브러리 함수는 함수 설명 카드로 인자와 반환값까지 적는다.")

ch2 = chapter(2, "그림", [
    h3("2.1", "흐름"),
    flow([("GLFW 콜백", "키 이벤트"), ("_current_keys", "이번 프레임", "accent"),
          ("Update()", "프레임 끝"), ("_previous_keys", "지난 프레임")],
         "화살표는 데이터가 흐르는 방향이다."),
    h3("2.2", "층"),
    layers([
        ("CLIENT", [("cbUpdate", "키 상태를 묻는다")]),
        ("ENGINE", [("MInputManager", "상태를 들고 있다", "accent"), ("GEngine", "소유한다")]),
        ("PLATFORM", [("GLFW", "이벤트를 준다", "dark"), ("Win32", "나중에", "ghost")]),
    ], "위층은 아래층의 인터페이스만 안다."),
    h3("2.3", "클래스 카드"),
    grid([
        iface("MInputManager", ["IsKeyPressed(EKey) : bool", "IsKeyHeld(EKey) : bool", "Update() : void"],
              stereotype="class", note="GEngine이 unique_ptr로 소유"),
        iface("IWindow", ["PollEvents() : void", "ShouldClose() : bool"],
              note="3-2강에서 Claud가 정한다. 여기는 이름만"),
    ]),
    h3("2.4", "그린 그림"),
    Fig(140)
    .box(20, 24, 150, 50, "스택", "지역 변수")
    .box(255, 24, 150, 50, "정적 저장 영역", "static 객체", kind="accent")
    .box(490, 24, 150, 50, "힙", "new, malloc", kind="dark")
    .arrow((170, 49), (255, 49), kind="accent")
    .arrow((405, 49), (490, 49), kind="muted dash")
    .text(212, 41, "참조", kind="s", size=9.5)
    .text(447, 41, "포인터", kind="s", size=9.5)
    .text(330, 112, "상자, 화살표, 글자를 좌표로 놓는다", kind="s")
    .render("HTML 부품으로 만들 수 없는 그림은 `Fig`로 그린다. 메모리 배치, 좌표계, 벡터가 여기에 든다."),
], lead="그림은 HTML 부품으로 만들고, 그것으로 안 되는 것만 `Fig`로 그린다. 한 그림에는 한 가지 관계만 담는다.",
    pb=True)

ch3 = chapter(3, "상자와 비교", [
    box("point", None, "이 절에서 하나만 기억한다면 이것이다. 한두 문장으로 쓴다."),
    box("ue", None, "언리얼에서 같은 자리에 있는 것. 예: `APlayerController`의 입력 처리와 `FKey`."),
    box("cs", None, "전공서의 어느 주제와 닿는가. 예: 값 초기화와 기본 초기화의 차이."),
    box("api", None, "DX11·DX12·Vulkan에서 달라지는 점. 추상화할 때 다시 본다."),
    box("warn", None, "증상부터 쓴다. “처음 몇 프레임 동안 누르지 않은 키가 눌린 것으로 나온다.”"),
    box("decide", None, "정답이 없는 지점. 선택지와 장단점을 표로 보여 주고 고르는 것은 Claud에게 남긴다."),
    box("ex", "예시: 힌트 세 줄", [
        p("개념을 구체적인 숫자나 호출 하나로 보여 준다. 미션의 답이 아니라 다른 상황의 예를 든다."),
        code("""
glfwWindowHint( GLFW_CONTEXT_VERSION_MAJOR, 3 );   // ask for OpenGL 3.3 ...
glfwWindowHint( GLFW_CONTEXT_VERSION_MINOR, 3 );
""", tag="usage"),
    ]),
    ox(("배열을 선언과 동시에 0으로 채운다", "생성 방식이 바뀌어도 안전하다"),
       ("`make_unique`의 값 초기화에 기댄다", "스택에 만들면 쓰레기 값")),
    cards([
        ("Pressed", "이번 프레임에 눌림", "현재 `true`, 직전 `false`", "한 프레임만 참"),
        ("Held", "계속 누르고 있음", "현재 `true`, 직전 `true`", "누르는 동안 참"),
    ]),
    table([24, 38, 38], ["선택지", "장점", "단점"], [
        ["폴링", "단순하다. 프레임마다 상태를 묻는다", "프레임 사이의 짧은 입력을 놓칠 수 있다"],
        ["이벤트 큐", "입력을 순서대로 빠짐없이 받는다", "큐와 소비 시점을 관리해야 한다"],
    ], cell_cls=["lab", "", ""]),
], lead="상자는 여섯 가지다. 한 쪽에 셋을 넘기지 않는다.", pb=True)

ch4 = chapter(4, "미션과 완료 기준", [
    steps([
        ("무엇을 만들지 한 줄로", "이 단계가 끝나면 무엇이 달라지는지 쓴다. 코드는 Claud가 쓴다.",
         ["가벼운 힌트: 어느 파일의 어느 함수를 보면 되는지.",
          "구체적인 힌트: 어떤 C++ 기능이나 API가 필요한지. 완성 코드는 주지 않는다."]),
        ("다음 단계", "앞 단계의 결과 위에 쌓는다.", ["힌트는 없어도 된다."]),
        ("검증 단계", "눈으로 확인할 수 있는 결과를 만든다."),
    ]),
    h3("4.1", "완료 기준"),
    checklist([
        "화면이나 로그에서 확인할 수 있는 결과 한 줄.",
        "검색으로 확인할 수 있는 조건. 예: `std::cout`이 `Engine/` 안에서 검색되지 않는다.",
        "커밋 하나로 묶였다.",
    ]),
], lead="미션은 순서가 있는 단계다. 오른쪽 네모는 끝낸 단계에 표시하는 칸이다.", pb=True)

ch5 = chapter(5, "질문과 해설", [
    exgroup("A", "코드를 쓰지 않고 답하시오", "근거를 한두 문장으로"),
    qlist([
        "`IsKeyPressed`가 한 프레임만 참이 되려면 `Update()`는 프레임의 어디에서 불려야 하는가?",
        "키 배열을 `std::array<bool, N>` 대신 `std::bitset<N>`으로 바꾸면 무엇이 달라지는가?",
    ]),
    answers("질문 A", [
        ("게임 로직의 `Update` 뒤, 다음 프레임의 이벤트 처리 전.",
         "먼저 불리면 현재와 직전이 같아져서 Pressed가 한 번도 참이 되지 않는다."),
        ("메모리가 8분의 1로 줄고, 통째 복사가 빨라진다.",
         "대신 원소 하나의 주소를 얻을 수 없다. 지금 크기에서는 체감 차이가 없다."),
    ]),
], lead="질문은 이해를 확인하는 용도다. 해설에는 답과 근거를 쓰고, 미션의 완성 코드는 싣지 않는다.", pb=True)

ch6 = glossary_chapter(6, [
    ("값 초기화", "value-initialization", "`T()`처럼 빈 괄호로 만드는 초기화. 조건에 따라 0으로 채운다"),
    ("기본 초기화", "default-initialization", "`T t;`처럼 초기값 없이 만드는 초기화"),
    ("콜백", "callback", "나중에 불러 달라고 넘겨 두는 함수"),
], pb=False)

if __name__ == "__main__":
    info = build(
        {"title": "ClaudGL Engine 부품 견본", "footer": "ClaudGL Engine · 부품 견본"},
        COVER, [ch1, ch2, ch3, ch4, ch5, ch6], OUT_HTML,
    )
    pages = render(OUT_HTML, OUT_PDF)
    print(f"pdf: {OUT_PDF} ({pages} pages)")
    print(f"tables: {info['tables']}  diagrams: {info['diagrams']}  code blocks: {info['code_blocks']}")
    print(f"issues: {info['issues']}")
