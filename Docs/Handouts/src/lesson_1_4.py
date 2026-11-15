"""Lesson 1-4 -- init failure and shutdown (not implemented in the repository yet; mission-style handout).

Run:  python -I src/lesson_1_4.py      (from Docs/Handouts, with the handout venv)
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

ME = lesson("1-4")
OUT_PDF = ROOT / handout_name(ME["id"])
OUT_HTML = ROOT / "_build" / "lesson_1_4.html"

# The engine code has not changed since CODE_COMMIT; it was read again on this day.
READ_DATE = "2026-11-16"

COVER = cover(
    f"CLAUDGL ENGINE · PART {ME['part']} · {ME['id']} · v{ME['ver']}",
    Raw('Init · <span class="ac">Shutdown</span>'),
    ME["title"],
    "실패하면 이유를 말하고, 끝날 때는 만든 것을 치운다",
    [
        ("목표 결과물", "`Init`이 실패하면 원인이 보이고 0이 아닌 종료 코드로 끝난다. 창을 닫으면 창과 GLFW가 해제된다"),
        ("핵심 개념", "실패 확인과 보고 · 반쯤 된 초기화 되돌리기 · 종료 경로와 순서 · 자원의 주인 · 값 초기화"),
        ("선수 지식", "1-1 〜 1-3강의 코드. 1-5강(Logger)은 먼저 끝냈어도, 아직이어도 된다 (2.3절)"),
        ("예상 시간", f"읽기 40분 + 구현 2시간 남짓 (계획서 기준 {ME['hours']}시간). 6.4절의 작은 정리는 따로 1 〜 2시간"),
        ("건드릴 파일", "`Engine/Core/EngineCore.h`·`.cpp`, `Engine/Manager/InputManager.h`·`.cpp`, `Client/main.cpp`"),
        ("코드 기준", f"커밋 `{CODE_COMMIT}`의 엔진 코드 — {READ_DATE}에 읽음"),
    ],
    note=("읽는 법",
          "1-1 〜 1-3강 자료의 “다시 보면 걸리는 곳”에서 이 강으로 미뤄 둔 것이 13건이다. 그중 넷이 이 강의 "
          "주제이고(1.3절), 나머지 아홉은 6.4절에 모았다. 코드 블록은 완성본이 아니다."),
    toc=["왜 필요한가", "초기화는 실패할 수 있다", "반쯤 된 초기화 되돌리기", "종료 경로", "자원의 주인과 값 초기화",
         "설계", "구현 미션", "흔한 함정", "완료 기준", "생각해 볼 질문", "해설", "용어집"],
)

# --------------------------------------------------------------------------

ch1 = chapter(1, "왜 필요한가", [
    h3("1.1", "실패해도 계속 간다"),
    code(r"""
    glfwInit();
    glfwWindowHint( GLFW_CONTEXT_VERSION_MAJOR, version_major );
    glfwWindowHint( GLFW_CONTEXT_VERSION_MINOR, version_minor );
    glfwWindowHint( GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE );

    // Create Window
    _main_window = glfwCreateWindow( width, height, title, monitor, share );
    glfwMakeContextCurrent( _main_window );

    if ( !gladLoadGLLoader( (GLADloadproc)glfwGetProcAddress ) )
    {
        return InitErrorCode::Fail;
    }
""", title="Engine/Core/EngineCore.cpp", tag="now", start=21, hl=[21, 27, 32]),
    table([16, 38, 46], ["줄", "지금 하는 일", "빠진 것"], [
        ["21행", "`glfwInit()`의 반환값을 버린다", "GLFW 초기화가 실패해도 다음 줄로 간다"],
        ["27행", "`glfwCreateWindow()`의 결과를 그대로 넣는다",
         "드라이버가 요청한 버전을 지원하지 않으면 `nullptr`이다. 확인하지 않는다"],
        ["30 〜 33행", "GLAD가 실패하면 `Fail`을 돌려준다",
         "이유를 남기지 않는다. 이미 만든 창과 GLFW도 그대로 두고 나간다"],
    ], cell_cls=["lab", "", ""]),

    h3("1.2", "끝나도 치우지 않는다"),
    code(r"""
    GEngine& engine    = GEngine::Get();
    auto     ErrorCode = engine.Init( 4, 6, 1600, 1600, "Claud GL Engine", nullptr, nullptr );

    if ( ErrorCode != GEngine::InitErrorCode::Success )
        return static_cast<int>(ErrorCode);

    engine.SetFramebufferSizeCallback( cbFramebufferSize );
    engine.SetUpdateCallback( cbUpdate );

    engine.Run();
}
""", title="Client/main.cpp", tag="now", start=10, hl=[14, 19]),
    p("`Run()`이 돌아오면(19행) 바로 `main`이 끝난다. `Engine/`과 `Client/` 어디에도 `glfwDestroyWindow`와 "
      "`glfwTerminate` 호출이 없다. 실패했을 때는 14행에서 아무 말 없이 `-1`을 돌려주고 끝난다."),
    p("프로세스가 끝나면 운영체제가 메모리, 창, 핸들을 회수한다. 그래서 지금은 눈에 보이는 문제가 없다. 그래도 "
      "정리 코드를 두는 이유는 셋이다."),
    ul([
        "**운영체제가 대신 해 주지 않는 일이 있다.** 버퍼에 남은 로그를 파일로 내보내는 일(1-5강), 전체 화면에서 바꾼 "
        "해상도와 감마를 되돌리는 일(`glfwTerminate`가 한다), 나중에는 설정과 저장 데이터를 쓰는 일이다.",
        "**순서가 필요한 자원이 곧 생긴다.** Part 2부터 만드는 GL 객체는 컨텍스트가 살아 있을 때 지워야 한다. "
        "순서를 지키는 자리를 지금 만들어 둔다.",
        "**프로세스가 끝나지 않고 엔진만 다시 시작하는 경우가 있다.** 에디터의 Play·Stop, 그래픽 장치를 잃었을 때의 "
        "재생성이 그렇다. 그때는 운영체제가 치워 주지 않는다.",
    ]),

    keep(h3("1.3", "앞 강에서 넘어온 것"),
    table([42, 34, 24], ["관찰", "위치", "이 자료에서"], [
        ["`glfwInit()`과 `glfwCreateWindow()`의 결과를 확인하지 않는다", "`Engine/Core/EngineCore.cpp:21`, `:27`", "2장"],
        ["GLAD가 실패하면 창과 GLFW를 둔 채 나간다", "`Engine/Core/EngineCore.cpp:30` 〜 `:33`", "3장"],
        ["`_is_running`을 끄는 함수도, 루프 뒤의 정리도 없다",
         "`Engine/Core/EngineCore.h:33`, `Engine/Core/EngineCore.cpp:69`", "4장"],
        ["입력 상태 배열 둘에 초기값이 없다", "`Engine/Manager/InputManager.h:24` 〜 `:25`", "5.3절"],
    ], cell_cls=["", "", "c"])),
    p("나머지 아홉 건(첫 프레임 dt, dt 상한, 수직 동기, 입력 쪽 넷, 프로젝트 설정 셋)은 주제가 달라 6.4절에 표로 모았다."),
], lead="지금 `Init`은 실패할 수 있는 호출 셋 중 하나만 확인하고, 엔진에는 끝내는 절차가 없다.")

ch2 = chapter(2, "초기화는 실패할 수 있다", [
    h3("2.1", "세 호출이 실패를 알리는 방법"),
    table([24, 24, 52], ["호출", "실패하면", "언제 실패하는가"], [
        ["`glfwInit()`", "`GLFW_FALSE`를 돌려준다", "창 시스템을 쓸 수 없는 환경. 실패하면 GLFW가 스스로 정리까지 하고 돌아온다"],
        ["`glfwCreateWindow()`", "`nullptr`을 돌려준다",
         "요청한 OpenGL 버전·프로파일을 드라이버가 지원하지 않을 때가 가장 흔하다. 힌트 값이 잘못됐을 때도 그렇다"],
        ["`gladLoadGLLoader()`", "`0`을 돌려준다", "current인 컨텍스트가 없거나, GL 버전 문자열을 읽지 못했을 때"],
    ], cell_cls=["lab", "", ""]),
    p("셋 다 반환값으로 알린다. C API라서 예외는 없다. 확인하지 않으면 실패는 조용히 다음 줄로 넘어간다."),

    h3("2.2", "지금 코드에서 실패가 흘러가는 길"),
    flow([
        ("21행", "초기화 실패"),
        ("27행", "창이 nullptr"),
        ("28행", "컨텍스트 없음"),
        ("30행", "GLAD가 0", "accent"),
        ("32행", "return Fail", "dark"),
    ], "앞에서 실패해도 멈추는 곳이 없어서, 어떤 실패든 30행까지 내려와 같은 `Fail`이 된다."),
    p("21행이 실패하면 그 뒤의 GLFW 호출은 전부 `GLFW_NOT_INITIALIZED` 오류를 내고 아무 일도 하지 않는다. 27행은 "
      "`nullptr`을 돌려주고, 30행의 `glfwGetProcAddress`는 current인 컨텍스트가 없으니 함수 주소 대신 `nullptr`을 준다. "
      "GLAD는 첫 함수(`glGetString`)를 얻지 못하면 바로 `0`을 돌려준다(`include/glad/glad.c:1806` 〜 `:1807`). "
      "27행만 실패해도 같은 길이다."),
    p("결과적으로 서로 다른 세 가지 실패가 `main`에는 똑같은 `-1`로 보인다. 이 흐름은 GLFW 문서와 glad 소스를 따라 읽은 "
      "것이다. 실행해서 확인하지는 않았다. 그리고 `main`이 반환값을 보지 않고 `Run()`을 부르면, 69행이 `nullptr` 창으로 "
      "`glfwWindowShouldClose`를 부른다."),

    h3("2.3", "GLFW가 이유를 알려 주는 통로"),
    code(r"""
void OnGlfwError( int code, const char* description );   // the signature GLFW expects

glfwSetErrorCallback( OnGlfwError );                      // allowed before glfwInit()

const char* description = nullptr;
int         code        = glfwGetError( &description );   // returns and clears the last error
""", tag="syntax"),
    p("GLFW 함수가 실패하면 등록해 둔 오류 콜백이 **그 자리에서** 불린다. 인자는 오류 코드와 사람이 읽을 설명이다. "
      "“왜 `nullptr`인가”의 답이 여기로 온다. 알아 둘 것은 셋이다."),
    ul([
        "`glfwSetErrorCallback`은 `glfwInit()`보다 먼저 불러도 되는 몇 안 되는 함수다. 먼저 달아야 초기화 실패의 "
        "이유를 받는다.",
        "`description`이 가리키는 문자열은 콜백이 돌아갈 때까지만 유효하다. 포인터를 저장해 두고 나중에 읽으면 안 된다.",
        "콜백 대신 `glfwGetError`로 마지막 오류를 직접 물어볼 수도 있다 (GLFW 3.3부터. 이 프로젝트는 3.4다).",
    ]),
    table([36, 20, 44], ["오류 코드", "값", "이 강에서 볼 만한 경우"], [
        ["`GLFW_NOT_INITIALIZED`", "`0x00010001`", "`glfwInit()` 전이나 `glfwTerminate()` 뒤에 GLFW 함수를 불렀다"],
        ["`GLFW_NO_CURRENT_CONTEXT`", "`0x00010002`", "컨텍스트 없이 `glfwGetProcAddress`, `glfwSwapInterval`을 불렀다"],
        ["`GLFW_INVALID_VALUE`", "`0x00010004`", "있을 수 없는 버전(예: 3.9)을 힌트로 주었다"],
        ["`GLFW_VERSION_UNAVAILABLE`", "`0x00010007`", "요청한 버전을 드라이버가 만들지 못한다"],
        ["`GLFW_PLATFORM_ERROR`", "`0x00010008`", "운영체제나 드라이버 쪽에서 난 오류"],
    ], cell_cls=["lab", "c", ""], compact=True),
    p("받은 이유를 어디에 찍는가는 지금 가진 수단에 달렸다. 1-5강을 먼저 끝냈다면 로그 매크로를 쓴다. 아직이면 "
      "`std::cerr`로 찍어 두고 1-5강에서 바꾼다. `std::cerr`는 쓸 때마다 바로 내보내는 스트림이라, 찍은 직후에 "
      "프로그램이 죽어도 글자가 남는다."),

    h3("2.4", "호출한 쪽에 알리기"),
    code(r"""
    enum class InitErrorCode : int8_t
    {
        Fail    = -1,
        Success = 0
    };
""", title="Engine/Core/EngineCore.h", tag="now", start=6),
    table([24, 38, 38], ["방법", "얻는 것", "내주는 것"], [
        ["`bool`", "가장 단순하다", "이유는 다른 통로(로그, 콜백)로만 전해진다"],
        ["원인별 열거형 (지금 모양의 확장)", "호출한 쪽이 원인에 따라 다르게 대응할 수 있다", "실패 종류가 늘 때마다 값을 더한다"],
        ["예외", "반환값을 비워 둘 수 있고, 무시할 수 없다", "엔진 전체의 오류 정책과 얽힌다. 그 결정은 1-6강이다"],
        ["`std::expected` (C++23)", "값과 오류를 한 타입에 담는다", "지금 설정(`stdcpp20`)에서는 쓸 수 없다"],
    ], cell_cls=["lab", "", ""]),
    code(r"""
[[nodiscard]] bool Load();

Load();              // warning C4834: discarding return value of function with 'nodiscard' attribute
""", tag="syntax"),
    p("반환값으로 알리는 방식의 약점은 호출한 쪽이 안 볼 수 있다는 것이다. 21행이 바로 그 예다. `[[nodiscard]]`(C++17)를 "
      "붙인 함수는 반환값을 버리면 컴파일러가 경고한다."),
    p("`main`의 반환값은 프로세스의 종료 코드가 된다. 0은 성공, 0이 아니면 실패라는 약속이고 `<cstdlib>`에 "
      "`EXIT_SUCCESS`와 `EXIT_FAILURE`가 있다. Visual Studio에서는 실행이 끝난 뒤 출력 창 마지막 줄에 코드가 찍힌다."),
    box("api", None,
        "어느 API든 초기화는 실패할 수 있고 알리는 방법만 다르다. DX11·DX12는 `HRESULT`를 돌려주고(`FAILED( hr )`로 "
        "확인), Vulkan은 `VkResult`를 돌려준다. 이유를 자세히 듣는 통로도 따로 있다. DX의 디버그 레이어와 Vulkan의 "
        "검증 레이어가 GLFW의 오류 콜백과 같은 자리다."),
], lead="초기화의 세 호출은 모두 실패할 수 있다. 실패를 알아차리는 일, 이유를 얻는 일, 호출한 쪽에 전하는 일을 차례로 본다.")

ch3 = chapter(3, "반쯤 된 초기화 되돌리기", [
    p("`Init`은 여러 단계를 차례로 밟는다. 셋째 단계에서 실패하면 첫째와 둘째는 이미 끝나 있다. GLAD가 실패한 시점"
      "(`Engine/Core/EngineCore.cpp:30`)에는 GLFW가 초기화되어 있고 창도 떠 있다. 실패를 돌려주기 전에 이것들을 "
      "되돌려야 `Init`이 “전부 됐거나, 아무것도 안 했거나” 둘 중 하나가 된다."),
    code(r"""
if ( !StepA() ) return false;
if ( !StepB() ) { UndoA(); return false; }
if ( !StepC() ) { UndoB(); UndoA(); return false; }
if ( !StepD() ) { UndoC(); UndoB(); UndoA(); return false; }   // grows with every step
""", title="every failure branch repeats the cleanup", tag="bad"),

    h3("3.1", "되돌리는 방법 셋"),
    table([26, 37, 37], ["방법", "얻는 것", "내주는 것"], [
        ["실패 분기마다 직접 되돌린다", "읽는 그대로 실행된다", "단계가 늘수록 위 예처럼 반복이 쌓이고, 하나를 빠뜨리기 쉽다"],
        ["어느 단계에서 불러도 되는 정리 함수 하나", "정리가 한 곳에 모인다. 정상 종료와 실패가 같은 코드를 쓴다",
         "함수가 “만들어진 것만 되돌린다”를 스스로 판단해야 한다. 두 번 불려도 안전해야 한다"],
        ["자원마다 주인 객체를 둔다 (RAII)", "되돌리기가 소멸자에서 저절로 일어난다. 빠뜨릴 수 없다",
         "자원마다 감싸는 타입이 필요하다. 소멸 순서가 선언 순서에 묶인다 (5.1절)"],
    ], cell_cls=["lab", "", ""]),
    p("둘째 방법에서 “두 번 불려도 안전하다”는 성질을 멱등(idempotent)이라고 부른다. 정리 함수가 멱등이면 실패 "
      "경로와 정상 경로 어디서든 걱정 없이 부를 수 있다. 조건은 단순하다. 되돌린 뒤에는 되돌렸다는 사실이 "
      "상태에 남아야 한다."),

    h3("3.2", "생성자가 아니라 Init인 이유"),
    p("`GEngine`은 객체를 만드는 일(생성자)과 쓸 수 있게 준비하는 일(`Init`)이 나뉘어 있다. 2단계 초기화다. "
      "함수 안의 `static`으로 만드는 싱글턴은 생성자에 인자를 넘기기 어렵고, 생성자는 값을 돌려줄 수 없어서 실패를 "
      "알리려면 예외밖에 없다. `Init`으로 빼면 인자와 반환값이 생긴다. 대가는 “만들어졌지만 아직 쓸 수 없는 상태”가 "
      "생긴다는 것이다. `Init` 전과 `Shutdown` 뒤가 그 상태다."),
    box("ue", None,
        "UE도 같은 모양이다. 엔진 루프는 `FEngineLoop::PreInit()` → `Init()` → `Tick()` → `Exit()`으로 나뉘고, 모듈은 "
        "`StartupModule()`과 `ShutdownModule()`을 짝으로 가진다. 액터의 `BeginPlay()`·`EndPlay()`도 생성자·소멸자와 따로 있는 "
        "2단계다. 생성자에서 하면 안 되는 일을 `BeginPlay`로 미루던 이유가 여기 있다."),
    box("cs", None,
        "RAII(자원 획득은 초기화)는 자원의 수명을 객체의 수명에 묶는 C++의 기본 기법이다. 함수가 어떤 길로 빠져나가든 "
        "지역 객체의 소멸자는 불린다는 보장에 기댄다. C에는 소멸자가 없어서 `goto cleanup;`으로 정리 코드를 한곳에 "
        "모은다. 전공서의 생성자·소멸자, 스마트 포인터 장과 닿는다."),
], lead="실패를 알아차린 다음의 문제다. 이미 해 놓은 일을 어떻게 할 것인가.")

ch4 = chapter(4, "종료 경로", [
    h3("4.1", "루프를 끝내는 스위치"),
    p("루프의 조건은 `_is_running && !glfwWindowShouldClose( _main_window )`다(`Engine/Core/EngineCore.cpp:69`). "
      "스위치가 둘인 셈이다. 창의 닫기 단추는 GLFW가 뒤쪽 깃발을 올려 준다. 앞쪽 `_is_running`은 `true`로 시작하고"
      "(`Engine/Core/EngineCore.h:33`) 바꾸는 함수가 없어서 지금은 쓰이지 않는다. 게임 코드가 “끝내자”고 할 방법이 "
      "없다는 뜻이다. `glfwSetWindowShouldClose`로 뒤쪽 깃발을 직접 올리는 길도 있다."),

    h3("4.2", "만든 순서의 반대로"),
    table([8, 34, 30, 28], ["", "`Init`이 만드는 것", "되돌리는 호출", "기대는 것"], [
        ["1", "GLFW 라이브러리 상태", "`glfwTerminate()`", "—"],
        ["2", "창과 GL 컨텍스트", "`glfwDestroyWindow()`", "1"],
        ["3", "GL 함수 포인터 (GLAD)", "없다. 되돌릴 것이 없다", "2"],
        ["4", "`MInputManager`", "`unique_ptr`가 놓을 때", "—"],
        ["5", "창에 건 콜백과 user pointer", "창과 함께 사라진다", "2, 4"],
    ], cell_cls=["num", "lab", "", "c"]),
    p("나중에 만든 것은 먼저 만든 것에 기댄다. 창은 GLFW 없이 존재할 수 없고, 키 콜백은 창과 `MInputManager`가 "
      "둘 다 있어야 돈다. 그래서 정리는 기대는 쪽부터, 곧 만든 순서의 반대로 한다. Part 2부터는 이 표에 GL 객체"
      "(버퍼, 셰이더, 텍스처)가 더해지고, 그것들은 2번이 살아 있을 때 지워야 한다."),
    ul([
        "`glfwTerminate()`는 남아 있는 창을 스스로 파괴한다. 창을 먼저 직접 파괴하면 순서가 코드에 드러난다.",
        "`glfwDestroyWindow()`를 부른 뒤에는 그 창의 콜백이 더는 불리지 않는다. 콜백 안에서 이 함수를 부르면 안 된다.",
        "`glfwTerminate()`는 GLFW가 초기화되지 않은 상태에서 불러도 아무 일도 하지 않는다. 한 번 부른 뒤에 다른 GLFW "
        "함수를 부르면 `GLFW_NOT_INITIALIZED` 오류가 난다.",
    ]),

    h3("4.3", "소멸자에 맡기면"),
    flow([
        ("Init", "만든다"),
        ("Run", "쓴다"),
        ("Shutdown", "되돌린다", "accent"),
        ("main 끝", "지역 객체 소멸"),
        ("정적 소멸", "~GEngine", "dark"),
    ], "`GEngine`은 함수 안의 `static`이라 소멸자가 `main`이 끝난 뒤에 불린다."),
    p("`~GEngine()`에 정리를 넣으면 부르는 것을 잊을 수 없다는 장점이 있다. 문제는 시점이다. 함수 안의 `static` "
      "객체들은 생성이 끝난 순서의 반대로 파괴되는데, 그 순서는 누가 `Get()`을 먼저 불렀느냐로 정해진다. `GLogger`가 "
      "`GEngine`보다 늦게 만들어졌다면 먼저 사라지고, `~GEngine()`은 이미 없는 Logger에 대고 로그를 찍게 된다"
      "(1-5강 질문 6). `main` 안에서 명시적으로 정리를 끝내면 소멸자가 할 일이 없어지고 이 순서 문제도 함께 사라진다."),

    h3("4.4", "프로세스가 끝나는 길"),
    table([34, 22, 22, 22], ["끝나는 길", "`Run()` 뒤의 코드", "지역 객체 소멸자", "정적 객체 소멸자"], [
        ["`main`에서 `return`", "실행된다", "불린다", "불린다"],
        ["`std::exit()`", "실행 안 됨", "안 불린다", "불린다"],
        ["`std::abort()`, 접근 위반, 잡지 않은 예외", "실행 안 됨", "안 불린다", "안 불린다"],
        ["콘솔 창을 닫음, 작업 관리자", "실행 안 됨", "안 불린다", "기대할 수 없다"],
    ], cell_cls=["lab", "c", "c", "c"]),
    p("Client는 콘솔 프로그램이라(`Client/Client.vcxproj:142`) 창이 둘 뜬다. GLFW 창의 닫기 단추는 첫째 길로 가고, "
      "콘솔 창의 닫기 단추는 넷째 길로 간다. 넷째 길에서는 `Shutdown()`이 불리지 않는다. 그래서 정리 코드는 "
      "“불리면 좋은 것”이지 “반드시 불리는 것”이 아니다. 잃으면 안 되는 것(로그의 flush)은 그때그때 해 둔다 (1-5강 5.2절)."),
    box("ue", None,
        "UE에서 `_is_running`에 해당하는 것이 `IsEngineExitRequested()`이고, 끄는 함수가 `RequestEngineExit()`다. "
        "게임 코드는 직접 루프를 깨지 않고 “끝내 달라”고 요청만 한다. 모듈은 로드된 순서의 반대로 `ShutdownModule()`이 "
        "불린다. 4.2절과 같은 규칙이다."),
], lead="루프가 끝난 뒤 무엇을 어떤 순서로 치우는가, 그리고 그 코드가 언제 실행되고 언제 실행되지 않는가.")

ch5 = chapter(5, "자원의 주인과 값 초기화", [
    h3("5.1", "누가 주인인가"),
    code(r"""
    std::unique_ptr<class MInputManager> _input_manager;

    // Property

    GLFWwindow* _main_window = nullptr;
    bool        _is_running  = true;
""", title="Engine/Core/EngineCore.h", tag="now", start=28, hl=[28, 32]),
    keep(table([24, 26, 50], ["자원", "들고 있는 곳", "지금 놓아 주는 곳"], [
        ["`MInputManager`", "`_input_manager` (28행)", "`unique_ptr`가 `~GEngine()`에서 놓는다. `main`이 끝난 뒤다"],
        ["창과 GL 컨텍스트", "`_main_window` (32행)", "없다. 날 포인터라 `GEngine`이 사라져도 창은 남는다"],
        ["GLFW 라이브러리 상태", "아무도 들고 있지 않다", "없다"],
    ], cell_cls=["lab", "", ""])),
    p("주인(owner)은 그 자원을 놓아 줄 책임이 있는 쪽이다. `unique_ptr`는 타입이 주인임을 말해 준다. 날 포인터는 "
      "말해 주지 않는다. `_main_window`는 `GEngine`이 만들었으니 사실상 주인이지만, 코드 어디에도 그렇게 적혀 있지 않다."),
    code(r"""
struct FileCloser
{
    void operator()( std::FILE* f ) const { std::fclose( f ); }
};

// fclose runs when `file` goes out of scope
std::unique_ptr<std::FILE, FileCloser> file( std::fopen( "a.txt", "r" ) );
""", title="unique_ptr with a custom deleter", tag="syntax"),
    p("`delete`가 아닌 함수로 놓아야 하는 자원도 `unique_ptr`에 맡길 수 있다. 둘째 템플릿 인자가 놓는 방법이다. "
      "주의할 것이 하나 있다. 멤버는 선언한 순서로 만들어지고 그 반대로 파괴된다. 주인 객체를 멤버로 두면 정리 순서가 "
      "선언 순서에 묶이고, 정적 객체의 멤버라면 그 시점은 `main`이 끝난 뒤다 (4.3절)."),

    h3("5.2", "빌려 쓰는 포인터"),
    p("`GetMainWindow()`와 `GetInputManager()`는 날 포인터를 돌려준다(`Engine/Core/EngineCore.h:43` 〜 `:44`). "
      "받은 쪽은 주인이 아니라 빌려 쓰는 쪽이다. 주인이 자원을 놓은 뒤에도 그 포인터를 들고 있으면 죽은 메모리를 "
      "가리키는 댕글링 포인터가 된다. 그래서 정리 함수는 놓은 포인터를 `nullptr`로 돌려놓는 일까지 해야 한다. "
      "`nullptr`은 검사할 수 있지만 댕글링 포인터는 검사할 방법이 없다."),

    h3("5.3", "값 초기화"),
    code(r"""
    std::array<bool, kKeyRangeMax> _current_keys;
    std::array<bool, kKeyRangeMax> _previous_keys;
""", title="Engine/Manager/InputManager.h", tag="now", start=24),
    code(r"""
struct S { int n; };
S  a;                  // default-initialization: a.n is indeterminate
S  b{};                // value-initialization:   b.n == 0
S* c = new S;          // default-initialization
S* d = new S();        // value-initialization
""", tag="syntax"),
    keep(table([40, 22, 38], ["만드는 방법", "초기화", "두 배열의 내용"], [
        ["`std::make_unique<MInputManager>()` (지금)", "값 초기화", "전부 `false`"],
        ["지역 변수 `MInputManager m;`", "기본 초기화", "정해지지 않은 값"],
        ["생성자를 `MInputManager() {}`로 바꾼 뒤 `make_unique`", "값 초기화", "정해지지 않은 값"],
    ], cell_cls=["lab", "c", ""])),
    p("지금 배열이 0으로 시작하는 것은 두 가지 우연이 겹친 결과다. `make_unique`가 `new T()`로 값 초기화를 하고"
      "(`Engine/Core/EngineCore.cpp:39`), 생성자가 `= default`라서(`Engine/Manager/InputManager.h:8`) 값 초기화가 "
      "멤버를 먼저 0으로 채운다. 생성자에 본문을 주는 순간(셋째 줄) 0으로 채우는 단계가 사라진다. 초기값이 만드는 "
      "방법에 달려 있으면 안 된다. 같은 프로젝트의 `Engine/Core/EngineCore.h:35` 〜 `:36`은 이미 초기값을 적어 두었다."),
    box("ue", None,
        "UE에서 주인을 정하는 것은 GC다. `UPROPERTY()`가 붙은 `UObject*`(UE5에서는 `TObjectPtr`)는 참조로 세어져 "
        "살아남고, 붙지 않은 날 포인터는 GC가 모르는 빌린 포인터라 대상이 수거되면 댕글링이 된다. `UObject`가 아닌 "
        "것은 `TUniquePtr`·`TSharedPtr`로 주인을 적는다. “이 포인터는 주인인가”를 묻는 습관은 같다."),
], lead="정리하려면 먼저 누가 무엇을 들고 있는지 알아야 한다. 그리고 만들 때의 값이 우연에 기대고 있지 않은지 본다.")

ch6 = chapter(6, "설계", [
    h3("6.1", "파일 배치와 완성된 뒤의 모습"),
    tree("""
Engine/
├── Core/
│   ├── EngineCore.h  #new declarations: shutdown, quit request
│   └── EngineCore.cpp  #checks in Init(), error callback, shutdown body
└── Manager/
    ├── InputManager.h  #initial values
    └── InputManager.cpp
Client/
└── main.cpp  #what happens after Init() fails, and after Run() returns
"""),
    code(r"""
int main( void )
{
    GEngine& engine = GEngine::Get();

    if ( /* Init failed */ )
    {
        // The reason has already been reported. Is anything left to clean up here?
        return EXIT_FAILURE;
    }

    engine.Run();
    engine.Shutdown();      // or does Run() / the destructor do this? (6.2)
}
""", title="main() when this lesson is done (names are examples)", tag="usage"),

    keep(h3("6.2", "결정할 것"),
    table([22, 38, 40], ["결정", "선택지", "따져 볼 것"], [
        ["`Init`이 실패를 알리는 방식", "`bool` / 원인별 `InitErrorCode` / 예외",
         "2.4절의 표. `main`이 원인에 따라 다르게 할 일이 있는가. 엔진 전체의 정책은 1-6강에서 정한다"],
        ["이유를 찍는 곳", "`Init` 안 / 오류 콜백 / `main`", "같은 실패가 두 번 찍히지 않는가. 가장 자세한 정보는 누가 가지고 있는가"],
        ["찍는 수단", "로그 매크로 (1-5강을 끝냈다면) / `std::cerr`", "`std::cerr`로 가면 1-5강의 미션 7에서 함께 바꾼다"],
        ["반쯤 된 초기화 되돌리기", "분기마다 직접 / 정리 함수 하나 / RAII", "3.1절의 표. 단계가 늘어날 것을 생각한다"],
        ["정리를 부르는 주체", "`main`이 명시적으로 / `Run()`의 끝 / `~GEngine()`",
         "4.3절. `Run()` 뒤에 Client가 엔진을 더 쓸 일이 있는가. 잊었을 때 무슨 일이 생기는가"],
        ["창 핸들을 드는 방법", "날 포인터와 수동 해제 (지금) / `unique_ptr`와 삭제자", "5.1절. 순서를 손으로 쥘 것인가, 선언 순서에 맡길 것인가"],
        ["루프를 끝내는 스위치", "`_is_running`을 끄는 함수 / `glfwSetWindowShouldClose` / 둘 다",
         "4.1절. 깃발이 둘이면 “끝났는가”를 묻는 곳도 둘이 된다"],
    ], cell_cls=["lab", "", ""], compact=True)),
    box("decide", None,
        "일곱 가지에 정답은 없다. 미션 전에 행마다 하나를 고르고 이유를 한 줄씩 적어 둔다. 1-5강 6.2절의 여섯째 결정"
        "(`GLogger`의 `Init`·`Shutdown`을 부르는 곳)도 다섯째 행과 같이 정한다. Logger는 엔진보다 먼저 켜지고 "
        "나중에 꺼져야 엔진의 처음과 끝을 적을 수 있다."),

    h3("6.3", "선언 스케치"),
    code(r"""
class GEngine
{
public:
    // What does the caller learn from the result: yes/no only, or the reason too?
    // Should ignoring the result be a compile warning?
    InitErrorCode Init( /* same parameters as now */ );

    void Shutdown();        // Safe to call twice? Safe to call after a failed Init()?
                            // Can Init() be called again afterwards?
    void RequestQuit();     // Name is an example. Who calls this, and from where?

private:
    // Which members does Shutdown() reset, and in which order?
    // What tells Shutdown() how far Init() got?
};
""", title="Engine/Core/EngineCore.h", tag="sketch"),

    pagebreak(),
    keep(h3("6.4", "함께 넘어온 작은 정리"),
    p("1-1 〜 1-3강 자료가 이 강으로 미룬 것 중 주제 밖의 아홉 건이다. 미션 8에서 다룬다. 위치는 파일 이름만 적었다.")),
    table([21, 27, 52], ["항목", "위치", "생각할 것"], [
        Group("루프 (1-2강)"),
        ["첫 프레임의 dt", "`EngineCore.cpp:72`", "첫 dt가 한 프레임 분량이 되려면 루프 직전에 무엇을 해 두는가"],
        ["dt의 상한", "`EngineCore.cpp:78`", "상한은 몇 초인가. 넘으면 자르는가, 그 프레임을 건너뛰는가"],
        ["수직 동기", "호출이 없다", "`glfwSwapInterval`은 컨텍스트가 current여야 통한다. 값은 누가 정하는가"],
        Group("입력 (1-3강)"),
        ["콜백의 범위 검사", "`InputManager.cpp:20`, `:24`", "`key`는 `int`, `IsValidKey`는 `EKey`를 받는다. 검사를 어디에 두는가"],
        ["“지금 눌려 있는가”", "`InputManager.h:17` 〜 `:19`", "함수 이름, 그리고 Pressed·Held와의 관계"],
        ["조회 함수의 `const`", "`InputManager.h:17` 〜 `:19`", "`GetInputManager()`의 반환 타입은 그대로 두어도 되는가"],
        Group("프로젝트 설정 (1-1강)"),
        ["Release의 링크 입력", "`Client.vcxproj:144`", "Debug|x64에만 있다. 모든 구성에 한 번에 적는 방법이 있는가"],
        ["파일 단위 컴파일 설정", "`Engine.vcxproj:181` 〜 `:256`, `:258` 〜 `:333`", "속성 창에서 굵게 보이는 값이 그 파일에만 덮어쓴 값이다"],
        ["프로젝트 참조", "`ClaudGL_Engine.sln`", "Client의 참조에 Engine을 더한다. 직접 적은 `ClaudGL.lib`는 그 뒤에도 필요한가"],
    ], cell_cls=["lab", "", ""], compact=True),

    h3("6.5", "이 강에서 하지 않는 것"),
    table([30, 70], ["미루는 것", "이유"], [
        ["엔진 전체의 오류 정책", "오류 코드와 예외 중 무엇을 규칙으로 삼을지는 1-6강이다. 여기서는 `Init` 하나만 정한다"],
        ["조건이 깨지면 그 자리에서 멈추기", "assert는 1-6강이다. 이 강의 실패는 “일어날 수 있는 일”이고 assert는 “일어나면 안 되는 일”을 다룬다"],
        ["창을 클래스로 떼어 내기", "`GEngine`에서 GLFW를 분리하는 일은 3-2강이다. 지금은 `GEngine`이 창의 주인이다"],
        ["GL 객체의 정리", "아직 GL 객체를 만들지 않는다. 순서를 지킬 자리만 만들어 둔다"],
    ], cell_cls=["lab", ""]),
], lead="만드는 함수는 둘이고(`Shutdown`, 루프를 끝내는 요청), 나머지는 이미 있는 `Init`과 `main`을 고치는 일이다.")

ch7 = chapter(7, "구현 미션", [
    steps([
        ("GLFW 오류 콜백을 단다",
         "실패의 이유를 받는 통로부터 만든다. `Init`에 OpenGL 9.9를 요청해 콜백이 불리는지 확인한다.",
         ["콜백은 `this`가 없는 함수여야 한다. 1-3강의 `cbSetKey`가 같은 종류였다.",
          "콜백이 불리지 않으면 다는 위치를 본다. 무엇보다 먼저여야 하는가 (2.3절)."]),
        ("세 호출의 결과를 확인한다",
         "`glfwInit`, `glfwCreateWindow`, `gladLoadGLLoader`가 실패하면 그 자리에서 멈추고 실패를 돌려준다.",
         ["2.1절 표의 둘째 칸이 확인할 값이다.",
          "창 생성 실패는 9.9 요청으로 만든다. GLAD 실패는 만들기 어려우니 조건을 잠깐 뒤집어 그 분기를 지나가 본다."]),
        ("이유를 호출한 쪽에 전한다",
         "6.2절의 첫째·둘째 결정을 적용한다. `main`은 실패하면 0이 아닌 종료 코드로 끝난다.",
         ["반환값을 버린 호출을 컴파일러가 잡게 할 수 있다 (2.4절).",
          "같은 실패가 두 번 찍히면 콜백과 `Init` 중 누가 무엇을 말할지 나눈다."]),
        ("`Shutdown()`을 만든다",
         "4.2절 표에 되돌리는 순서를 직접 적은 뒤 그 순서대로 구현한다. 두 번 불러도 안전해야 한다.",
         ["되돌린 뒤 멤버에 무엇을 남겨야 다음 호출이 “이미 되돌렸다”를 아는가 (3.1절, 5.2절).",
          "`unique_ptr`를 수명이 끝나기 전에 비우는 멤버 함수가 있다."]),
        ("실패한 `Init`이 뒷정리를 한다",
         "창을 만든 뒤 GLAD에서 실패해도 창과 GLFW가 남지 않게 한다. 6.2절의 넷째 결정을 적용한다.",
         ["미션 2에서 뒤집어 둔 조건을 다시 쓴다. 정리 호출에 중단점을 걸어 실제로 지나가는지 본다."]),
        ("종료 경로를 잇는다",
         "`Run()`이 끝난 뒤 정리가 불리게 하고, 엔진에 루프를 끝내 달라고 요청하는 함수를 만든다. Client에서 "
         "`Esc`로 끝내 본다.",
         ["`EKey::Escape`는 이미 있다(`Engine/Enum/InputKeys.h:61`).",
          "GLFW 창의 닫기 단추와 `Esc`가 같은 정리 코드를 지나가는지 중단점으로 확인한다."]),
        ("초기값을 적는다",
         "`MInputManager`의 두 배열에 초기값을 준다. 다른 클래스에도 초기값 없는 멤버가 있는지 훑어본다.",
         ["같은 프로젝트의 `EngineCore.h:35` 〜 `:36`이 쓰는 표기가 `std::array`에도 통한다."]),
        ("작은 정리를 하고 묶는다",
         "6.4절 표에서 지금 할 것을 골라 처리한다. 9.9와 뒤집은 조건을 되돌린 뒤 커밋한다.",
         ["프로젝트 설정 셋은 코드와 다른 커밋으로 나누면 나중에 되짚기 쉽다."]),
    ]),
], lead="한 단계가 끝날 때마다 빌드해서 눈으로 확인한다. 힌트는 막혔을 때 위에서부터 하나씩만 본다.", pb=True)

ch8 = chapter(8, "흔한 함정", [
    table([30, 40, 30], ["증상", "원인", "확인 방법"], [
        ["오류 콜백이 한 번도 불리지 않는다", "`glfwInit()` 뒤에 달았다. 초기화 실패는 이미 지나간 뒤다. 또는 실패가 실제로 "
                                  "나지 않았다", "9.9를 요청해 본다"],
        ["끝날 때 `GLFW_NOT_INITIALIZED` 오류가 찍힌다", "`glfwTerminate()` 뒤에 GLFW 함수를 불렀다. 순서가 "
                                                       "뒤집혔거나 정리가 두 번 불렸다", "정리 함수에 중단점을 걸고 호출 순서를 본다"],
        ["창을 닫을 때 접근 위반으로 죽는다", "파괴한 창의 포인터를 다시 썼다. 포인터를 `nullptr`로 돌려놓지 않았다",
         "죽은 줄에서 `_main_window`의 값을 본다"],
        ["실패했는데 창이 잠깐 떴다 사라진다", "정상이다. 창이 만들어진 뒤의 단계에서 실패했다", "어느 단계의 실패인지 찍힌 이유를 읽는다"],
        ["콘솔 창을 닫으면 정리 코드가 불리지 않는다", "`main`으로 돌아오지 않는 종료다 (4.4절)", "GLFW 창의 닫기 단추로 닫아 비교한다"],
        ["`main`이 실패를 돌려줬는데 종료 코드가 큰 수로 보인다", "`-1`을 돌려주었다. 종료 코드는 부호 없는 32비트로도 표시된다",
         "출력 창의 `0xffffffff`"],
        ["정리한 뒤의 마지막 로그가 파일에 없다", "Logger를 엔진보다 먼저 닫았다 (1-5강을 끝낸 경우)", "닫는 순서를 본다"],
    ], compact=True),
], lead="증상에서 거꾸로 찾는 표다.")

ch9 = chapter(9, "완료 기준", [
    checklist([
        "OpenGL 9.9를 요청하면 창이 뜨지 않고, GLFW가 준 이유가 보이고, 종료 코드가 0이 아니다.",
        "GLAD 분기를 억지로 지나가게 하면 창과 GLFW가 정리된 뒤에 끝난다.",
        "GLFW 창의 닫기 단추와 `Esc` 어느 쪽으로 끝내도 `glfwDestroyWindow`와 `glfwTerminate`가 한 번씩 불린다.",
        "정리 함수를 연달아 두 번 불러도 오류가 찍히지 않는다.",
        "`Engine/`에서 `glfwTerminate`를 검색하면 정리 코드에서만 나온다. `glfwInit();`처럼 결과를 버리는 줄은 없다.",
        "`Engine/Manager/InputManager.h`의 두 배열에 초기값이 적혀 있다.",
        "6.2절의 일곱 가지에 대해 고른 것과 이유가 적혀 있고, 9.9와 뒤집은 조건을 되돌린 뒤 커밋했다.",
    ]),
    console(Raw(
        '<span class="err">GLFW error 0x00010007</span>: <span class="dim">(GLFW가 주는 설명 문장)</span>\n'
        '<span class="err">Engine init failed</span>: window creation\n'
        '<span class="dim">... Client.exe exited with code 1 (0x1)</span>'
    ), title="9.9를 요청했을 때 기대하는 출력 (형식과 문구는 예시. 오류 코드는 실제로 나온 값을 적어 둔다)"),
], lead="전부 눈이나 검색으로 확인할 수 있는 조건이다.")

ch10 = chapter(10, "생각해 볼 질문", [
    exgroup("A", "코드를 쓰지 않고 답하시오", "한두 문장으로, 이유까지"),
    qlist([
        "지금 코드에서 `glfwInit()`이 실패하면 `Init`은 어느 줄에서 무엇을 돌려주는가? `main`은 그것이 창 생성 실패인지 "
        "GLAD 실패인지 구별할 수 있는가?",
        "`Init`이 창을 만든 뒤 GLAD에서 실패했고 `main`은 바로 끝났다. 창과 GLFW 자원은 결국 어떻게 되는가? 그런데도 "
        "되돌리는 코드를 넣는 이유를 둘 드시오.",
        "정리 함수에서 `glfwTerminate()`를 먼저 부르고 `glfwDestroyWindow( _main_window )`를 나중에 부르면 "
        "무슨 일이 생기는가?",
        "`MInputManager`의 생성자를 `MInputManager() {}`로 바꾸었다. `std::make_unique<MInputManager>()`로 만든 "
        "객체의 `_current_keys`에는 무엇이 들어 있는가? 바꾸기 전에는 왜 `false`였는가?",
        "정리 코드를 `~GEngine()`에 넣었다. 이 코드는 언제 불리는가? 불리지 않는 경우를 둘 드시오.",
        "Client가 `GetMainWindow()`로 받은 포인터를 변수에 넣어 두었다. `Shutdown()` 뒤에 그 변수를 쓰면 어떻게 되는가? "
        "`Shutdown()`이 `_main_window`를 `nullptr`로 돌려놓으면 이 문제가 풀리는가?",
    ], lines=3),
], lead="답을 보기 전에 소리 내어 설명해 본다. 막히는 문항이 다시 읽을 장이다.", pb=True)

ch11 = chapter(11, "해설", [
    answers("질문 A", [
        ("32행에서 `InitErrorCode::Fail`을 돌려준다. `main`은 구별할 수 없다.",
         "실패를 확인하는 곳이 30행 하나뿐이라 앞의 실패도 거기까지 내려와 같은 값이 된다. 구별하려면 단계마다 "
         "확인하고, 값이나 메시지로 원인을 따로 전해야 한다. (2.2절, 2.4절)"),
        ("프로세스가 끝나면서 운영체제가 회수한다.",
         "넣는 이유는 1.2절의 셋 중에서 고른다. 운영체제가 해 주지 않는 일(flush, 화면 설정 복원)이 있고, 순서가 "
         "필요한 자원이 곧 생기고, 프로세스가 끝나지 않은 채 다시 초기화하는 경우가 있다. (1.2절, 3장)"),
        ("창은 `glfwTerminate()`가 이미 파괴했다. 뒤의 호출은 죽은 포인터를 넘기고 `GLFW_NOT_INITIALIZED` 오류를 낸다.",
         "`glfwTerminate()`는 남은 창을 모두 파괴하고, 그 뒤의 GLFW 함수는 초기화되지 않았다는 오류를 낸다. "
         "기대는 쪽(창)을 먼저, 기대어지는 쪽(GLFW)을 나중에 되돌려야 한다. (4.2절)"),
        ("정해지지 않은 값이 들어 있다. 바꾸기 전에는 값 초기화가 멤버를 먼저 0으로 채웠다.",
         "`make_unique`의 값 초기화는 생성자가 `= default`이면 0으로 채운 뒤 생성자를 부르고, 본문을 직접 준 "
         "생성자이면 채우지 않고 생성자만 부른다. 멤버에 초기값을 적으면 어느 쪽이든 같아진다. (5.3절)"),
        ("`main`이 끝난 뒤, 정적 객체가 파괴될 때 불린다.",
         "`std::abort()`나 접근 위반으로 죽을 때, 콘솔 창을 닫아 프로세스가 끝날 때는 불리지 않는다. 불리는 경우에도 "
         "다른 정적 객체(`GLogger`)가 먼저 사라졌을 수 있다. (4.3절, 4.4절)"),
        ("죽은 창을 가리키는 댕글링 포인터를 쓰게 된다. 풀리지 않는다.",
         "`nullptr`로 돌려놓는 것은 `GEngine` 안의 멤버 하나다. Client가 복사해 둔 값은 그대로다. 빌린 포인터는 "
         "오래 들고 있지 않고 필요할 때마다 주인에게 다시 묻는 것이 규칙이다. (5.2절)"),
    ]),
])

ch12 = glossary_chapter(12, [
    ("2단계 초기화", "two-phase initialization", "만드는 일(생성자)과 준비하는 일(`Init`)을 나누는 방식"),
    ("멱등", "idempotent", "여러 번 해도 한 번 한 것과 결과가 같은 성질"),
    ("소유권", "ownership", "자원을 놓아 줄 책임. 그 책임을 진 쪽이 주인이다"),
    ("자원 획득은 초기화", "RAII", "자원의 수명을 객체의 수명에 묶어 소멸자에서 놓게 하는 기법"),
    ("댕글링 포인터", "dangling pointer", "이미 놓인 자원을 가리키는 포인터"),
    ("값 초기화", "value-initialization", "`T()`·`T{}`로 만드는 방식. 직접 쓴 생성자가 없으면 0으로 채운다"),
    ("기본 초기화", "default-initialization", "`T x;`·`new T`로 만드는 방식. 기본 타입 멤버는 값이 없다"),
    ("`[[nodiscard]]`", "nodiscard attribute", "반환값을 버리면 컴파일러가 경고하게 하는 표시 (C++17)"),
], pb=False)

if __name__ == "__main__":
    info = build(
        {"title": f"ClaudGL Engine {ME['id']} {ME['title']} v{ME['ver']}",
         "footer": f"ClaudGL Engine · {ME['id']} {ME['title']} · v{ME['ver']}"},
        COVER, [ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8, ch9, ch10, ch11, ch12], OUT_HTML,
    )
    pages = render(OUT_HTML, OUT_PDF)
    print(f"pdf: {OUT_PDF} ({pages} pages)")
    print(f"tables: {info['tables']}  diagrams: {info['diagrams']}  code blocks: {info['code_blocks']}")
    print(f"issues: {info['issues']}")
