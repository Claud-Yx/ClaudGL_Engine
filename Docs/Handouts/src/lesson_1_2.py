"""Lesson 1-2 -- game loop and delta time (handout written after the code; it quotes the repository).

Run:  python -I src/lesson_1_2.py      (from Docs/Handouts, with the handout venv)
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

ME = lesson("1-2")
OUT_PDF = ROOT / handout_name(ME["id"])
OUT_HTML = ROOT / "_build" / "lesson_1_2.html"

COVER = cover(
    f"CLAUDGL ENGINE · PART {ME['part']} · {ME['id']} · v{ME['ver']}",
    Raw('GEngine::<span class="ac">Run</span>'),
    ME["title"],
    "창이 닫힐 때까지 도는 한 바퀴 안에서 무슨 일이 어떤 순서로 일어나는가",
    [
        ("다루는 범위", "루프의 조건과 한 바퀴의 순서, 델타 타임, Update 콜백, 버퍼 스왑"),
        ("핵심 개념", "게임 루프 · 가변 타임스텝 · 콜백과 의존 방향 · 더블 버퍼링 · 수직 동기"),
        ("관련 파일", "`Engine/Core/EngineCore.h`·`.cpp`, `Client/main.cpp`"),
        ("읽는 시간", "약 40분"),
        ("코드 기준", f"커밋 `{CODE_COMMIT}` — {CODE_READ_DATE}에 읽음"),
    ],
    note=("읽는 법",
          "1-1강에서 창이 뜨는 데까지 봤다. 이 자료는 그 뒤 `Run()` 한 함수를 다룬다. 코드 블록 왼쪽 숫자는 실제 "
          "줄 번호다. 6장은 다시 보니 걸리는 곳이고, 고치는 일은 1-4강에서 한다."),
    toc=["한 장으로 보기", "루프가 필요한 이유", "Delta Time", "Update 콜백", "한 프레임의 순서",
         "다시 보면 걸리는 곳", "스스로 설명해 보기", "해설", "용어집"],
)

# --------------------------------------------------------------------------

ch1 = chapter(1, "한 장으로 보기", [
    code(r"""
void GEngine::Run()
{
    if ( !_on_update )
    {
        std::cout << "GEngine::Update() is null.\n";
    }

    while ( _is_running && !glfwWindowShouldClose( _main_window ) )
    {
        auto CurTime     = glfwGetTime();
        _delta_time      = CurTime - _last_frame_time;
        _last_frame_time = CurTime;

        glfwPollEvents();
        glClear( GL_COLOR_BUFFER_BIT );

        Update( static_cast<float>(_delta_time) );
        _input_manager->Update();

        glfwSwapBuffers( _main_window );
    }
}
""", title="Engine/Core/EngineCore.cpp", tag="now", start=62),
    flow([
        ("시간 재기", "71〜73행"),
        ("이벤트 처리", "75행"),
        ("화면 지우기", "76행"),
        ("Update(dt)", "78행", "accent"),
        ("입력 넘기기", "79행"),
        ("버퍼 교체", "81행"),
    ], "한 바퀴가 한 프레임이다. 끝나면 69행의 조건을 다시 검사하고 처음으로 돌아간다."),
], lead="게임 루프 전체가 이 스물두 줄이다. 아래 여섯 칸이 한 프레임이고, 이 자료의 나머지는 칸 하나씩을 풀어 본다.")

ch2 = chapter(2, "루프가 필요한 이유", [
    p("보통의 프로그램은 위에서 아래로 한 번 실행하고 끝난다. 게임은 사용자가 끌 때까지 “입력을 받고, 상태를 갱신하고, "
      "그린다”를 되풀이해야 한다. 이 되풀이를 한 곳에서 쥐고 있는 것이 게임 루프이고, 엔진의 나머지 부분은 전부 "
      "이 루프에 불려서 일한다."),
    table([32, 68], ["69행의 조건", "뜻"], [
        ["`_is_running`", "엔진이 스스로 멈추려 할 때 쓰는 깃발. `Engine/Core/EngineCore.h:33`에서 `true`로 시작한다."],
        ["`!glfwWindowShouldClose(…)`", "사용자가 창의 닫기 버튼을 눌렀는지. GLFW가 창마다 들고 있는 깃발을 읽는다."],
    ], cell_cls=["lab", ""]),
    p("닫기 버튼을 누른다고 창이 바로 사라지지는 않는다. GLFW는 깃발만 세우고, 루프가 그 깃발을 보고 스스로 빠져나온다. "
      "저장 확인 창 같은 것을 띄울 틈이 여기서 생긴다."),
    box("point", None,
        "프레임은 메트로놈처럼 일정한 간격으로 오지 않는다. 어떤 박은 길고 어떤 박은 짧다. 그래서 게임 로직은 "
        "“한 박에 얼마”가 아니라 “1초에 얼마”로 적어야 한다. 다음 장의 델타 타임이 그 환산에 쓰인다."),
], lead="루프는 프로그램을 살려 두는 장치다. 조건이 거짓이 되는 순간이 프로그램이 끝나는 순간이다.")

ch3 = chapter(3, "Delta Time", [
    code(r"""
        auto CurTime     = glfwGetTime();
        _delta_time      = CurTime - _last_frame_time;
        _last_frame_time = CurTime;
""", title="Engine/Core/EngineCore.cpp", tag="now", start=71),
    p("`glfwGetTime()`은 `glfwInit()`이 불린 뒤로 흐른 시간을 초 단위 `double`로 돌려준다. 이번 값에서 지난 프레임의 "
      "값을 빼면 지난 한 바퀴에 걸린 시간, 곧 델타 타임(dt)이 나온다."),

    h3("3.1", "왜 필요한가"),
    p("`position += 5.0f;`처럼 프레임마다 고정된 양을 더하면 프레임이 많이 나오는 PC에서 더 빨리 움직인다. "
      "`position += speed * dt;`로 쓰면 프레임 수와 상관없이 1초에 `speed`만큼 움직인다."),
    table([16, 20, 32, 32], ["FPS", "dt", "프레임당 이동 (speed 100)", "1초 동안 이동"], [
        ["60", "약 0.0167초", "약 1.67", "100"],
        ["144", "약 0.0069초", "약 0.69", "100"],
        ["30", "약 0.0333초", "약 3.33", "100"],
    ], cell_cls=["lab", "", "", ""]),

    h3("3.2", "double로 재고 float로 넘긴다"),
    p("시각을 담는 두 멤버는 `double`이고(`Engine/Core/EngineCore.h:35` 〜 `:36`), 게임 쪽에 넘길 때만 `float`로 "
      "바꾼다(`Engine/Core/EngineCore.cpp:78`). 둘의 쓰임이 다르기 때문이다."),
    cards([
        ("double", "누적 시각 — 계속 커지는 값",
         "한 시간 뒤면 3600, 하루 뒤면 86400이다. 큰 값에서 작은 차이를 빼내려면 유효 숫자가 넉넉해야 한다.",
         "`_last_frame_time`, `CurTime`"),
        ("float", "차이 — 늘 작은 값",
         "0.007 근처의 작은 수 하나다. `float`의 정밀도로 충분하고, 이후 벡터·행렬 계산이 전부 `float`다.",
         "`Update( float delta_time )`"),
    ]),
    box("cs", None,
        "`float`는 유효 숫자가 약 7자리다. 값이 8192를 넘으면 이웃한 두 `float` 사이의 간격이 약 0.001이 된다. "
        "누적 시각을 `float`로 들고 있으면 실행 후 두 시간 남짓부터 시각이 1밀리초 눈금으로만 변하고, 144FPS의 "
        "프레임 시간(약 6.9밀리초)도 그 눈금으로밖에 재지 못한다. `double`은 같은 조건에서 간격이 "
        "1000억분의 1초보다 작다."),

    h3("3.3", "dt가 튀는 순간"),
    table([34, 66], ["언제", "무슨 일이 생기나"], [
        ["첫 프레임", "`_last_frame_time`이 0에서 시작하므로(`Engine/Core/EngineCore.h:35`), 첫 dt는 `glfwInit()`부터 "
                  "첫 바퀴까지 걸린 시간 전체다. 창 생성과 GLAD 로드 시간이 들어가 보통의 프레임보다 훨씬 크다."],
        ["창을 잡고 끌 때", "Windows에서는 창을 옮기거나 크기를 바꾸는 동안 `glfwPollEvents()`가 돌아오지 않는다. "
                     "놓는 순간의 dt에 그동안의 시간이 통째로 들어간다."],
        ["디버거 중단점", "멈춰 있던 시간이 다음 dt가 된다."],
    ], cell_cls=["lab", ""]),
    box("ue", None,
        "`AActor::Tick(float DeltaSeconds)`의 인자가 이것이다. 언리얼도 기본은 프레임마다 dt가 달라지는 방식이고, "
        "프로젝트 설정의 고정 프레임 레이트 옵션으로 dt를 일정하게 만들 수 있다."),
], lead="프레임 사이의 시간은 PC마다, 순간마다 다르다. 그 차이를 게임 로직이 느끼지 않게 해 주는 숫자가 델타 타임이다.")

ch4 = chapter(4, "Update 콜백", [
    code(r"""
void GEngine::Update( float delta_time )
{
    if ( !_on_update ) return;

    _on_update( delta_time );
}

void GEngine::SetUpdateCallback( std::function<void( float )> func )
{
    _on_update = func;
}
""", title="Engine/Core/EngineCore.cpp", tag="now", start=45),
    p("`_on_update`는 `std::function<void( float )>` 타입의 멤버다(`Engine/Core/EngineCore.h:24`). "
      "“`float` 하나를 받고 아무것도 돌려주지 않는, 부를 수 있는 무언가”를 담는 그릇이다."),

    h3("4.1", "왜 콜백인가"),
    layers([
        ("CLIENT", [("main.cpp", "`cbUpdate`를 정의하고 넘긴다", "accent")]),
        ("ENGINE", [("GEngine", "받아서 보관하고, 프레임마다 부른다")]),
    ], "포함과 링크의 방향은 Client → Engine 한쪽뿐이다. 호출은 프레임마다 거꾸로 Engine → Client로 일어난다."),
    p("Engine은 정적 라이브러리이고 Client를 모른다. `main.cpp`를 포함하지도, 그 안의 함수 이름을 알지도 못한다. "
      "그런데 프레임마다 게임 코드를 불러야 한다. 방법은 하나다. Client가 “이 함수를 불러 달라”고 주소를 넘겨 주고, "
      "Engine은 무엇인지 모른 채 받아 두었다가 부른다."),
    code(r"""
    engine.SetFramebufferSizeCallback( cbFramebufferSize );
    engine.SetUpdateCallback( cbUpdate );

    engine.Run();
""", title="Client/main.cpp", tag="now", start=16, hl=[17]),

    h3("4.2", "같은 일을 하는 다른 방법"),
    table([24, 38, 38], ["방법", "좋은 점", "아쉬운 점"], [
        ["`std::function` (지금)", "함수, 람다, 캡처한 람다를 가리지 않고 받는다", "호출이 한 단계 거쳐 간다. 무엇이 들어 있는지 타입에 드러나지 않는다"],
        ["함수 포인터", "가장 가볍다. C 라이브러리와 그대로 통한다", "캡처한 람다를 받지 못한다. 상태를 따로 넘겨야 한다"],
        ["가상 함수 (상속)", "Update 외에 Init, Shutdown 같은 짝을 한 클래스에 모을 수 있다", "Client가 엔진의 클래스를 상속해야 한다"],
    ], cell_cls=["lab", "", ""]),
    p("16행의 `SetFramebufferSizeCallback`은 둘째 방법이다. GLFW의 함수 포인터 타입을 그대로 받아 GLFW에 "
      "넘긴다(`Engine/Core/EngineCore.cpp:57` 〜 `:60`). 한 클래스 안에 두 방식이 같이 있다."),
    box("ue", None,
        "언리얼의 델리게이트가 같은 자리에 있다. `OnClicked.AddDynamic(this, &UMyWidget::HandleClick)`은 "
        "“나중에 이 함수를 불러 달라”고 맡기는 일이고, 버튼은 누가 맡겼는지 모른 채 부른다."),
], lead="엔진은 프레임마다 게임 코드를 불러야 하는데, 게임 코드가 무엇인지는 모른다. 콜백이 그 사이를 잇는다.")

ch5 = chapter(5, "한 프레임의 순서", [
    table([9, 26, 65], ["줄", "하는 일", "이 순서인 이유"], [
        ["71〜73", "dt를 잰다", "이번 프레임의 모든 로직이 같은 dt를 쓰도록 맨 앞에서 한 번만 잰다."],
        ["75", "`glfwPollEvents()`", "운영체제가 쌓아 둔 이벤트를 처리한다. 키 콜백이 바로 이 호출 안에서 불린다. "
                               "Update보다 앞이어야 이번 프레임의 입력이 이번 프레임의 로직에 닿는다."],
        ["76", "`glClear(…)`", "지난 프레임의 그림을 지운다. 그리기 전이어야 한다."],
        ["78", "`Update(dt)`", "게임 코드가 돈다. 지금은 그리는 단계가 따로 없어서 그리기도 여기서 해야 한다."],
        ["79", "`_input_manager->Update()`", "이번 프레임의 키 상태를 “직전 상태”로 넘긴다. Update보다 뒤여야 한다 (1-3강)."],
        ["81", "`glfwSwapBuffers(…)`", "다 그린 그림을 화면에 내보낸다. 맨 끝이어야 한다."],
    ], cell_cls=["num", "lab", ""]),

    h3("5.1", "더블 버퍼링"),
    flow([
        ("back buffer", "여기에 그린다", "accent"),
        ("glfwSwapBuffers", "둘을 맞바꾼다"),
        ("front buffer", "화면에 보인다", "dark"),
    ], "76행의 `glClear`와 모든 그리기는 back buffer에 대고 일어난다."),
    p("그리는 도중의 화면을 보여 주면 반쯤 지워진 그림이 깜빡인다. 그래서 보이지 않는 버퍼에 다 그린 뒤 한 번에 "
      "바꿔 낸다. `glClearColor`로 정한 색이 화면에 나오는 것도 지우기(76행)와 교체(81행)를 거쳐서다."),

    h3("5.2", "수직 동기"),
    p("버퍼를 바꾸는 시점을 모니터의 화면 갱신에 맞출지 말지를 정하는 값이 스왑 간격이다. GLFW에서는 "
      "`glfwSwapInterval`로 정하는데, 지금 코드에는 이 호출이 없다. 그러면 그래픽 드라이버의 기본값을 따른다. "
      "PC와 드라이버 설정에 따라 60FPS로 묶일 수도, 수천 FPS로 돌 수도 있다."),
    box("api", None,
        "DX11에서는 `IDXGISwapChain::Present(1, 0)`의 첫 인자가 스왑 간격이다. 버퍼 교체와 수직 동기가 한 호출에 "
        "들어 있다. 나중에 RenderDevice 인터페이스에 “프레임 끝” 함수를 둘 때 이 두 가지를 함께 넘기게 된다."),

    h3("5.3", "지금 없는 것"),
    table([30, 70], ["없는 것", "언제 필요해지나"], [
        ["Update와 Render의 분리", "그릴 것이 생기는 Part 2부터 불편해지고, 4-6강에서 가른다."],
        ["고정 타임스텝", "물리처럼 일정한 간격으로 계산해야 하는 것이 생길 때. 이 강의의 범위에는 없다."],
        ["dt 상한", "3.3절의 튀는 dt를 로직이 그대로 받는다. 움직이는 것이 생기면 바로 드러난다."],
    ], cell_cls=["lab", ""]),
], lead="여섯 단계의 순서는 대부분 바꿀 수 없다. 하나를 옮기면 무엇이 깨지는지로 이유를 확인한다.")

ch6 = chapter(6, "다시 보면 걸리는 곳", [
    table([38, 50, 12], ["위치", "관찰", "이어지는 강"], [
        ["`Engine/Core/EngineCore.h:35`, `Engine/Core/EngineCore.cpp:72`",
         "첫 프레임의 dt가 초기화에 걸린 시간 전체다. `Run()`에 들어설 때 시각을 한 번 맞춰 두지 않는다.", "1-4강"],
        ["`Engine/Core/EngineCore.cpp:78`",
         "dt에 상한이 없다. 창을 끌거나 중단점에서 멈춘 뒤 수 초짜리 dt가 그대로 게임 코드에 넘어간다.", "1-4강"],
        ["`Engine/Core/EngineCore.h:33`, `Engine/Core/EngineCore.cpp:69`",
         "`_is_running`을 `false`로 바꾸는 함수가 없다. 엔진 쪽에서 루프를 끝낼 방법이 없고, 루프가 끝난 뒤 "
         "`glfwDestroyWindow`와 `glfwTerminate`를 부르는 곳도 없다.", "1-4강"],
        ["`Engine/`, `Client/` 전체",
         "`glfwSwapInterval` 호출이 없다. 프레임 속도가 드라이버 설정에 달려 있다 (5.2절).", "1-4강"],
        ["`Engine/Core/EngineCore.cpp:64` 〜 `:67`",
         "콜백이 비어 있으면 경고만 찍고 루프를 계속 돈다. 메시지는 `GEngine::Update() is null`이지만 실제로 비어 "
         "있는 것은 콜백이다. `std::cout`을 직접 쓴다.", "1-5강"],
        ["`Engine/Core/EngineCore.cpp:52` 〜 `:55`",
         "`std::function`을 값으로 받아 다시 복사한다. 한 번만 불리는 함수라 영향은 없다.", "—"],
        ["`Engine/Core/EngineCore.cpp:76`", "Core가 `glClear`를 직접 부른다.", "3-2강"],
        ["`Engine/Core/EngineCore.h:52`",
         "`SetFramebufferSizeCallback`이 GLFW의 타입 `GLFWframebuffersizefun`을 공개 헤더에 드러낸다.", "3-2강"],
    ]),
], lead=f"{CODE_READ_DATE}에 다시 읽으며 적었다. 지금 화면에 배경색만 나오는 상태에서는 드러나지 않는 것들이다. "
        "고치는 방법은 여기 적지 않는다.", pb=True)

ch7 = chapter(7, "스스로 설명해 보기", [
    exgroup("A", "코드를 보지 않고 답하시오", "한두 문장으로, 이유까지"),
    qlist([
        "`position += 5.0f;`를 프레임마다 실행하면 60FPS인 PC와 144FPS인 PC에서 1초 뒤 위치는 각각 얼마인가?",
        "`_last_frame_time`을 `float`로 바꾸면 언제부터 어떤 문제가 생기는가?",
        "79행 `_input_manager->Update()`를 78행 `Update(dt)` 바로 앞으로 옮기면 `IsKeyPressed`는 어떻게 되는가?",
        "Engine이 `cbUpdate`를 직접 부르지 않고 콜백으로 받는 이유를 프로젝트 구성으로 설명하시오.",
        "창의 제목 표시줄을 3초 동안 잡고 있다가 놓으면 다음 `cbUpdate`가 받는 `delta_time`은 얼마쯤인가?",
        "81행 `glfwSwapBuffers`를 지우면 화면은 어떻게 보이는가?",
    ]),
], lead="답을 보기 전에 소리 내어 설명해 본다. 막히는 문항이 다시 읽을 장이다.", pb=True)

ch8 = chapter(8, "해설", [
    answers("질문 A", [
        ("300과 720.", "프레임 수만큼 더해지기 때문이다. `speed * dt`로 쓰면 둘 다 같은 값이 된다. (3.1절)"),
        ("실행 후 두 시간 남짓부터 dt가 1밀리초 단위로만 재진다.",
         "큰 `float` 값에서는 이웃한 값 사이의 간격이 넓어진다. 움직임이 미세하게 끊겨 보인다. (3.2절)"),
        ("항상 `false`가 된다.",
         "게임 코드가 돌기 전에 현재 상태가 직전 상태로 복사되어, 둘이 늘 같아진다. (5장, 1-3강)"),
        ("Engine은 Client보다 먼저 만들어지는 정적 라이브러리라서 Client의 함수를 알 수 없다.",
         "의존은 Client → Engine 한 방향이다. 거꾸로 부르려면 Client가 주소를 넘겨 줘야 한다. (4.1절)"),
        ("약 3초.", "끄는 동안 `glfwPollEvents()`가 돌아오지 않아 한 바퀴가 3초짜리가 된다. "
                 "`speed * dt`로 움직이는 물체는 그 한 프레임에 3초 치를 건너뛴다. (3.3절)"),
        ("창의 내용이 갱신되지 않는다.",
         "모든 그리기가 back buffer에만 쌓이고 화면에 보이는 front buffer는 바뀌지 않는다. (5.1절)"),
    ]),
])

ch9 = glossary_chapter(9, [
    ("게임 루프", "game loop", "입력 · 갱신 · 그리기를 프로그램이 끝날 때까지 되풀이하는 반복문"),
    ("델타 타임", "delta time (dt)", "직전 프레임 한 바퀴에 걸린 시간, 초 단위"),
    ("가변 타임스텝", "variable timestep", "프레임마다 실제 걸린 시간을 dt로 쓰는 방식. 지금 코드"),
    ("고정 타임스텝", "fixed timestep", "로직을 일정한 간격으로만 돌리는 방식"),
    ("콜백", "callback", "나중에 불러 달라고 넘겨 두는 함수"),
    ("더블 버퍼링", "double buffering", "보이지 않는 버퍼에 그린 뒤 보이는 버퍼와 맞바꾸는 방식"),
    ("수직 동기", "vsync", "버퍼 교체를 모니터의 화면 갱신 시점에 맞추는 것"),
    ("스왑 간격", "swap interval", "버퍼 교체 사이에 기다릴 화면 갱신 횟수. `glfwSwapInterval`"),
], pb=False)

if __name__ == "__main__":
    info = build(
        {"title": f"ClaudGL Engine {ME['id']} {ME['title']} v{ME['ver']}",
         "footer": f"ClaudGL Engine · {ME['id']} {ME['title']} · v{ME['ver']}"},
        COVER, [ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8, ch9], OUT_HTML,
    )
    pages = render(OUT_HTML, OUT_PDF)
    print(f"pdf: {OUT_PDF} ({pages} pages)")
    print(f"tables: {info['tables']}  diagrams: {info['diagrams']}  code blocks: {info['code_blocks']}")
    print(f"issues: {info['issues']}")
