"""Lesson 1-1 -- project layout and window creation (handout written after the code; it quotes the repository).

Run:  python -I src/lesson_1_1.py      (from Docs/Handouts, with the handout venv)
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

ME = lesson("1-1")
OUT_PDF = ROOT / handout_name(ME["id"])
OUT_HTML = ROOT / "_build" / "lesson_1_1.html"

COVER = cover(
    f"CLAUDGL ENGINE · PART {ME['part']} · {ME['id']} · v{ME['ver']}",
    Raw('GEngine::<span class="ac">Init</span>'),
    ME["title"],
    "프로젝트 두 개가 어떻게 묶이고, 창 하나가 뜨기까지 무슨 일이 일어나는가",
    [
        ("다루는 범위", "솔루션 구성, 외부 라이브러리 셋, 미리 컴파일된 헤더, 창 생성, `GEngine` 싱글턴"),
        ("핵심 개념", "정적 라이브러리와 링크 · pch · OpenGL 컨텍스트 · 함수 로더 · 싱글턴"),
        ("관련 파일", "`Engine/Engine.vcxproj`, `Client/Client.vcxproj`, `Engine/framework.h`, "
                  "`Engine/Core/EngineCore.h`·`.cpp`, `Client/main.cpp`"),
        ("읽는 시간", "약 40분"),
        ("코드 기준", f"커밋 `{CODE_COMMIT}` — {CODE_READ_DATE}에 읽음"),
    ],
    note=("읽는 법",
          "이미 Claud가 쓴 코드를 다시 읽는 자료다. 코드 블록 왼쪽 숫자는 실제 파일의 줄 번호이니 IDE에서 같은 줄을 "
          "열어 놓고 보면 좋다. 7장은 다시 보니 걸리는 곳을 모았고, 고치는 일은 1-4강에서 한다. 8장 질문은 답을 "
          "가리고 먼저 말로 설명해 본다."),
    toc=["한 장으로 보기", "솔루션: 프로젝트 두 개", "외부 라이브러리 셋", "pch: 미리 컴파일된 헤더",
         "창이 뜨기까지", "GEngine 싱글턴", "다시 보면 걸리는 곳", "스스로 설명해 보기", "해설", "용어집"],
)

# --------------------------------------------------------------------------

ch1 = chapter(1, "한 장으로 보기", [
    layers([
        ("실행 파일", [("Client.exe", "`main()` · 게임 코드", "accent")]),
        ("정적 라이브러리", [("ClaudGL.lib", "Engine 프로젝트 + `glad.c`"), ("glfw3.lib", "미리 빌드된 GLFW")]),
        ("운영체제", [("opengl32.lib", "Windows의 OpenGL 입구"), ("Win32", "창 · 입력 · 시간")]),
        ("하드웨어 쪽", [("그래픽 드라이버", "OpenGL 4.6의 실제 구현", "dark")]),
    ], "위의 둘은 링크할 때 `Client.exe` 안으로 복사된다. 실행할 때 따로 필요한 `.lib` 파일은 없다."),
    flow([
        ("main()", "Client"),
        ("GEngine::Get()", "인스턴스 생성"),
        ("Init()", "창 + 컨텍스트", "accent"),
        ("콜백 등록", "크기 · Update"),
        ("Run()", "1-2강"),
    ], "`Client/main.cpp:10` 〜 `:19`의 순서다. 이 자료는 가운데 `Init()`까지를 다룬다."),
], lead="지금 저장소는 프로젝트 두 개와 외부 라이브러리 세 개로 이루어져 있다. 먼저 무엇이 무엇 위에 얹혀 있는지 본다.")

ch2 = chapter(2, "솔루션: 프로젝트 두 개", [
    table([14, 24, 22, 40], ["프로젝트", "종류", "결과물", "설정된 곳"], [
        ["Engine", "정적 라이브러리", "`ClaudGL.lib`", "`Engine/Engine.vcxproj:43` (종류), `:90` (출력 `lib/Debug/x64/`), `:95` (이름)"],
        ["Client", "실행 파일 (콘솔)", "`Client.exe`", "`Client/Client.vcxproj:43` (종류), `:86` (출력 `Debug/x64/`)"],
    ], cell_cls=["lab", "", "", ""]),

    h3("2.1", "정적 라이브러리"),
    p("정적 라이브러리(`.lib`)는 컴파일이 끝난 목적 파일(`.obj`)을 한 파일로 묶은 것이다. 스스로 실행되지 않고, "
      "실행 파일을 링크할 때 필요한 부분이 그 안으로 복사된다. 그래서 `Client.exe`만 있으면 실행된다."),
    cards([
        ("정적 .lib", "링크할 때 exe에 복사", "배포가 단순하다. 엔진을 고치면 Client를 다시 링크해야 한다.", "지금 방식"),
        ("동적 .dll", "실행할 때 불러옴", "exe와 따로 교체할 수 있다. 대신 내보낼 심볼을 표시해야 하고 dll 파일이 옆에 있어야 한다.",
         "UE 에디터 빌드의 모듈"),
    ]),

    h3("2.2", "Client가 Engine을 찾는 세 가지 설정"),
    table([22, 44, 34], ["무엇을", "어디에 적혀 있나", "빠지면 나오는 오류"], [
        ["헤더가 있는 폴더", "`Client/Client.vcxproj:87` — `include\\`와 `Engine\\`", "컴파일 단계 `C1083` (헤더를 열 수 없음)"],
        ["`.lib`가 있는 폴더", "`Client/Client.vcxproj:88` — `lib\\Debug\\x64\\`", "링크 단계 `LNK1104` (파일을 열 수 없음)"],
        ["링크할 `.lib` 이름", "`Client/Client.vcxproj:144` — `ClaudGL.lib;glfw3.lib;opengl32.lib`",
         "링크 단계 `LNK2019` (확인할 수 없는 외부 기호)"],
    ], cell_cls=["lab", "", ""]),
    code(r"""
#pragma once

#pragma comment(lib, "ClaudGL.lib")

#include "framework.h"
""", title="Client/pch.h", tag="now", start=1, hl=[3]),
    p("`#pragma comment(lib, …)`는 “이 파일을 컴파일한 결과물에 이 라이브러리를 링크하라는 메모를 남겨라”는 MSVC 전용 지시다. "
      "`ClaudGL.lib`는 프로젝트 설정(144행)과 이 줄, 두 군데에서 지정되어 있다. 하나만 있어도 된다."),
    box("cs", None,
        "헤더와 `.lib`는 서로 다른 단계에서 쓰인다. 컴파일러는 헤더의 선언만 보고 “이런 함수가 있다고 치고” 호출 코드를 "
        "만든다. 그 함수의 본체가 실제로 어디 있는지는 링커가 `.lib`에서 찾아 이어 붙인다. 오류 번호가 `C`로 시작하면 "
        "컴파일러, `LNK`로 시작하면 링커가 낸 것이다."),
    box("ue", None,
        "언리얼에서는 모듈의 `Build.cs`에 `PublicDependencyModuleNames.Add(\"Engine\")` 한 줄을 적으면 헤더 경로와 "
        "링크 설정이 함께 잡힌다. 위 표의 세 줄을 UnrealBuildTool이 대신 해 주는 것이다."),
], lead="Engine은 정적 라이브러리로, Client는 그것을 링크하는 실행 파일로 만든다. 엔진과 게임 코드를 처음부터 "
        "갈라 둔 구성이다.")

ch3 = chapter(3, "외부 라이브러리 셋", [
    table([15, 45, 40], ["이름", "하는 일", "들어오는 형태"], [
        ["GLFW", "창을 만들고, OpenGL 컨텍스트를 만들고, 키 입력과 시간을 알려 준다", "헤더 + 미리 빌드된 `glfw3.lib`"],
        ["GLAD", "OpenGL 함수의 주소를 실행 중에 찾아 채워 넣는다", "헤더 + `glad.c` (Engine에 같이 컴파일, `Engine/Engine.vcxproj:178`)"],
        ["GLM", "벡터와 행렬 수학", "헤더만 (링크할 것이 없다)"],
    ], cell_cls=["lab", "", ""]),

    h3("3.1", "왜 GLAD가 필요한가"),
    p("Windows가 기본으로 주는 `opengl32.lib`에는 OpenGL 1.1 시절의 함수만 들어 있다. 그 뒤에 나온 함수는 그래픽 드라이버 "
      "안에 있고, 프로그램이 실행된 뒤에 “이 이름의 함수 주소를 달라”고 물어서 받아야 한다. GLAD는 `glCreateShader` 같은 "
      "이름을 전부 함수 포인터로 선언해 두고, `gladLoadGLLoader`가 불릴 때 한꺼번에 주소를 채운다."),
    code(r"""
    if ( !gladLoadGLLoader( (GLADloadproc)glfwGetProcAddress ) )
    {
        return InitErrorCode::Fail;
    }
""", title="Engine/Core/EngineCore.cpp", tag="now", start=30),
    p("`glfwGetProcAddress`가 “이름을 주면 주소를 돌려주는 함수”이고, GLAD는 그것을 받아 수백 번 호출한다."),
    box("warn", None,
        "증상: 첫 `gl*` 호출에서 주소 0을 실행하려다 접근 위반으로 죽는다. 원인은 로드 전의 함수 포인터가 전부 "
        "`nullptr`이기 때문이다. 로드는 컨텍스트가 현재 스레드에 연결된 뒤에만 성공하므로, 28행 "
        "`glfwMakeContextCurrent`와 30행 `gladLoadGLLoader`의 순서는 바꿀 수 없다."),
    box("api", None,
        "DX11에는 이런 로더가 없다. `d3d11.lib`를 링크하고 `D3D11CreateDevice`로 장치 객체를 받은 뒤 그 객체의 멤버 "
        "함수를 부른다. Vulkan은 `vulkan-1.dll`이 로더 역할을 하고, 함수 주소를 직접 받아 쓰는 방식도 지원한다."),
], lead="엔진이 직접 하지 않고 빌려 쓰는 일이 셋 있다. 창, OpenGL 함수 찾기, 수학이다.")

ch4 = chapter(4, "pch: 미리 컴파일된 헤더", [
    p("`glm`이나 표준 라이브러리 헤더는 크다. `.cpp` 파일마다 이것들을 처음부터 다시 읽으면 빌드가 느려진다. pch는 "
      "자주 쓰는 헤더를 한 번만 컴파일해 결과를 저장해 두고, 다른 파일이 그 결과를 불러다 쓰게 하는 장치다."),
    table([26, 40, 34], ["역할", "파일", "설정"], [
        ["만든다 (Create)", "`Engine/pch.cpp`", "`Engine/Engine.vcxproj:334` 〜 `:339`"],
        ["쓴다 (Use)", "나머지 `.cpp` 전부", "`Engine/Engine.vcxproj:147` 〜 `:148`"],
        ["쓰지 않는다", "`include/glad/glad.c`", "`Engine/Engine.vcxproj:178` 〜 `:180`"],
    ], cell_cls=["lab", "", ""]),
    p("pch를 쓰는 `.cpp`는 첫 줄이 반드시 `#include \"pch.h\"`여야 한다. 컴파일러가 그 줄까지를 저장해 둔 결과로 "
      "바꿔치기하기 때문에, 그 앞에 적은 것은 무시된다."),
    code(r"""
#pragma once

#define WIN32_LEAN_AND_MEAN             // Exclude rarely-used stuff from Windows headers

#include "glad/glad.h"
#include "GLFW/glfw3.h"
#include "glm/glm.hpp"
#include "glm/ext.hpp"
#include "glm/gtc/matrix_transform.hpp"

#include <memory>
#include <string>
#include <functional>

#include "Enum/InputKeys.h"

using int8   = __int8;
using int16  = __int16;
using int32  = __int32;
using int64  = __int64;
using uint8  = unsigned __int8;
using uint16 = unsigned __int16;
using uint32 = unsigned __int32;
using uint64 = unsigned __int64;
using byte   = unsigned __int8;
""", title="Engine/framework.h", tag="now", start=1, hl=[5, 6]),
    p("`pch.h`는 이 파일 하나를 포함할 뿐이다(`Engine/pch.h:3`). 5행과 6행의 순서에도 이유가 있다. `glad.h`는 OpenGL "
      "선언을 자기가 맡으려 하므로, 다른 OpenGL 헤더보다 먼저 포함되어야 한다."),
    box("point", None,
        "Client의 `pch.h`도 `framework.h`를 포함한다(`Client/pch.h:5`). Client 폴더에는 그런 파일이 없으므로, 포함 "
        "경로에 들어 있는 `Engine\\` 폴더의 것이 잡힌다. 그래서 Client의 모든 파일이 glad와 GLFW를 볼 수 있고, "
        "`Client/main.cpp:24`에서 `glViewport`를 바로 부를 수 있다. 편하지만, Part 3에서 끊어야 할 연결이다."),
    box("cs", None,
        "17〜25행의 `__int8` 같은 이름은 MSVC에만 있다. 표준은 `<cstdint>`의 `std::int8_t`, `std::uint32_t`다. 지금은 "
        "문제가 없고, 다른 컴파일러로 빌드할 일이 생기면 이 아홉 줄에서 멈춘다."),
], lead="두 프로젝트 모두 pch를 쓴다. 무엇을 미리 컴파일하는지는 `framework.h` 한 파일에 모여 있다.")

ch5 = chapter(5, "창이 뜨기까지", [
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

    glClearColor( 0.5f, 0.0f, 0.0f, 1.0f );
    glfwSetWindowUserPointer( _main_window, this );

    // init manager
    _input_manager = std::make_unique<MInputManager>();
    glfwSetKeyCallback( _main_window, MInputManager::cbSetKey );

    return InitErrorCode::Success;
""", title="Engine/Core/EngineCore.cpp — GEngine::Init 본문", tag="now", start=21),
    table([11, 33, 56], ["줄", "하는 일", "왜 이 자리인가"], [
        ["21", "GLFW를 초기화한다", "다른 GLFW 함수보다 먼저 불려야 한다. 시간 측정(`glfwGetTime`)도 여기서 0초가 된다."],
        ["22〜24", "컨텍스트 조건을 예약한다", "힌트는 이후에 만드는 창에 적용된다. 4.6 버전, core 프로필을 요청한다."],
        ["27", "창과 컨텍스트를 만든다", "OpenGL에서는 창을 만들 때 컨텍스트가 함께 만들어진다."],
        ["28", "컨텍스트를 현재 스레드에 연결한다", "`gl*` 호출은 대상을 인자로 받지 않는다. 현재 연결된 컨텍스트로 간다."],
        ["30〜33", "OpenGL 함수 주소를 채운다", "연결된 컨텍스트가 있어야 드라이버에 물어볼 수 있다 (3.1절)."],
        ["35", "배경색을 정한다", "첫 `gl*` 호출이다. 로드가 끝났으니 부를 수 있다."],
        ["36", "창에 `this`를 달아 둔다", "콜백 안에서 엔진을 찾기 위한 준비다 (1-3강)."],
        ["39〜40", "입력 관리자를 만들고 키 콜백을 건다", "36행보다 뒤다. 콜백이 불릴 때는 이미 포인터가 달려 있다."],
    ], cell_cls=["num", "lab", ""]),

    h3("5.1", "컨텍스트"),
    p("OpenGL 컨텍스트는 OpenGL의 모든 상태(배경색, 바인딩된 버퍼 등)와 객체가 들어 있는 곳이다. 한 스레드에는 한 번에 "
      "하나의 컨텍스트만 연결되고, `gl*` 함수는 전부 그 연결된 컨텍스트에 대고 일한다. `glClearColor`가 "
      "“어느 창의” 배경색인지 묻지 않는 이유다."),
    h3("5.2", "호출하는 쪽"),
    code(r"""
    GEngine& engine    = GEngine::Get();
    auto     ErrorCode = engine.Init( 4, 6, 1600, 1600, "Claud GL Engine", nullptr, nullptr );

    if ( ErrorCode != GEngine::InitErrorCode::Success )
        return static_cast<int>(ErrorCode);
""", title="Client/main.cpp", tag="now", start=10),
    p("앞의 `4, 6`이 OpenGL 버전이다. 여섯째 인자 `nullptr`은 전체 화면으로 쓸 모니터가 없다는 뜻(창 모드)이고, "
      "일곱째 `nullptr`은 자원을 공유할 다른 창이 없다는 뜻이다. 실패하면 `-1`이 프로세스 종료 코드가 된다."),
    box("api", None,
        "DX11에서는 창(HWND), 장치(Device), 스왑 체인이 서로 다른 객체다. 창은 Win32나 GLFW로 만들고 그래픽 쪽은 따로 "
        "만든 뒤 둘을 잇는다. OpenGL은 창과 컨텍스트가 붙어 있어서 `Init` 하나에 다 들어갔다. 3-2강에서 Window와 "
        "RenderDevice를 가르는 이유가 여기 있다."),
], lead="`GEngine::Init`은 스물두 줄이다. 줄마다 순서에 이유가 있다.")

ch6 = chapter(6, "GEngine 싱글턴", [
    code(r"""
GEngine& GEngine::Get()
{
    static GEngine instance; // C++11 guarantees thread-safe initialization
    return instance;
}
""", title="Engine/Core/EngineCore.cpp", tag="now", start=8),
    code(r"""
    GEngine()                            = default;
    ~GEngine()                           = default;
    GEngine( const GEngine& )            = delete;
    GEngine& operator=( const GEngine& ) = delete;
""", title="Engine/Core/EngineCore.h — private 구역", tag="now", start=13),
    table([34, 66], ["장치", "막는 것"], [
        ["함수 안의 `static` 지역 변수", "인스턴스가 둘 생기는 일. 처음 `Get()`이 불릴 때 한 번만 만들어진다."],
        ["`private` 생성자", "밖에서 `GEngine e;`로 따로 만드는 일."],
        ["복사 생성자·대입 `= delete`", "`GEngine copy = GEngine::Get();`처럼 복사본이 생기는 일."],
    ], cell_cls=["lab", ""]),
    ox(("`GEngine& engine = GEngine::Get();`", "참조로 받는다. `Client/main.cpp:10`"),
       ("`GEngine engine = GEngine::Get();`", "복사가 필요해서 컴파일 오류")),
    p("만들어지는 때는 분명하다. 사라지는 때는 `main`이 끝난 뒤, 정적 객체들이 정리될 때다. 그 시점에는 창이 이미 "
      "닫혔을 수도 있으므로, 소멸자에서 GLFW나 OpenGL을 부르는 설계는 위험하다. 정리할 것이 있으면 `main`이 끝나기 "
      "전에 명시적으로 부르는 함수가 필요하다 (1-4강)."),
    box("cs", None,
        "전역 변수 대신 함수 안의 `static`을 쓰는 이유가 하나 더 있다. 서로 다른 `.cpp`에 있는 전역 객체들은 초기화 "
        "순서가 정해져 있지 않아서, 한 전역 객체의 생성자가 아직 만들어지지 않은 다른 전역 객체를 쓸 수 있다. "
        "함수 안의 `static`은 “처음 쓰일 때” 만들어지므로 이 문제가 없다."),
    box("ue", None,
        "언리얼에도 같은 이름의 `GEngine`이 있다. 그쪽은 `UEngine*` 타입의 전역 포인터이고, 엔진이 시작할 때 "
        "채워진다. 어디서든 닿는다는 편리함과, 누가 엔진에 기대고 있는지 코드에서 드러나지 않는다는 단점이 똑같이 있다."),
], lead="엔진 객체는 프로그램에 하나만 있고 어디서든 `GEngine::Get()`으로 닿는다. 세 가지 장치가 이를 보장한다.")

ch7 = chapter(7, "다시 보면 걸리는 곳", [
    table([38, 50, 12], ["위치", "관찰", "이어지는 강"], [
        ["`Engine/Core/EngineCore.cpp:21`, `:27`",
         "`glfwInit()`의 반환값과 `glfwCreateWindow()`가 돌려준 포인터를 확인하지 않는다. 드라이버가 4.6을 지원하지 "
         "않으면 27행이 `nullptr`을 돌려주고, 그대로 진행한다.", "1-4강"],
        ["`Engine/Core/EngineCore.cpp:30` 〜 `:33`",
         "GLAD 로드가 실패하면 `Fail`을 돌려주지만, 이미 만든 창과 GLFW는 정리하지 않고 나간다.", "1-4강"],
        ["`Client/Client.vcxproj:144`",
         "링크할 라이브러리 목록이 Debug|x64 구성에만 있다. Release 구성에는 `glfw3.lib`와 `opengl32.lib`가 없어 "
         "링크가 실패할 것으로 보인다 (빌드해서 확인하지는 않았다).", "1-4강"],
        ["`Engine/Engine.vcxproj:181` 〜 `:256`, `:258` 〜 `:333`",
         "`EngineCore.cpp`와 `InputManager.cpp`에만 파일 단위 설정이 70여 줄씩 붙어 있다. 구성 조건이 없어서 "
         "Release에서도 최적화가 꺼지고(`:184`) 디버그 런타임이 쓰이며(`:182`), `D:\\YunProject\\…` 절대 경로가 "
         "들어 있다(`:187`). `Logger.cpp`(`:257`)에는 없다.", "1-4강"],
        ["`ClaudGL_Engine.sln`, `Client/Client.vcxproj`",
         "Client가 Engine에 의존한다는 선언(프로젝트 참조)이 없다. Engine을 고친 뒤 Client만 빌드하면 예전 "
         "`ClaudGL.lib`가 링크될 수 있다.", "1-4강"],
        ["`Engine/framework.h:17` 〜 `:25`", "MSVC 전용 정수형으로 별칭을 만든다 (4장 CS 메모).", "—"],
        ["`Engine/Core/EngineCore.h:48`",
         "`Init`의 매개변수에 `GLint`, `GLFWmonitor*`, `GLFWwindow*`가 드러난다. Engine의 공개 헤더가 GLFW·OpenGL "
         "타입에 묶여 있다.", "3-2강"],
    ]),
    box("point", "이 표를 읽는 법",
        "넷째 줄의 파일 단위 설정은 Claud가 직접 쓴 것이 아니라 IDE가 넣었을 가능성이 높다. 손으로 고치기 전에 "
        "Visual Studio의 파일 속성 창에서 “부모 또는 프로젝트 기본값에서 상속”으로 되돌릴 수 있는지 먼저 본다."),
], lead=f"{CODE_READ_DATE}에 다시 읽으며 적었다. 지금 Debug|x64로 빌드하고 실행하는 데는 지장이 없는 것들이다. "
        "고치는 방법은 여기 적지 않는다.", pb=True)

ch8 = chapter(8, "스스로 설명해 보기", [
    exgroup("A", "코드를 보지 않고 답하시오", "한두 문장으로, 이유까지"),
    qlist([
        "`Client.exe`를 다른 PC로 옮길 때 `ClaudGL.lib`도 함께 옮겨야 하는가?",
        "`Client/Client.vcxproj:144`에서 `ClaudGL.lib`를 지워도 링크가 되는 이유는 무엇인가?",
        "`gladLoadGLLoader`를 `glfwMakeContextCurrent`보다 먼저 부르면 `Init`은 어떻게 끝나는가?",
        "두 스레드가 동시에 처음으로 `GEngine::Get()`을 부르면 인스턴스가 둘 생길 수 있는가?",
        "`glad.c`만 pch를 쓰지 않게 설정한 이유는 무엇인가?",
        "`glClearColor`는 왜 창이나 컨텍스트를 인자로 받지 않는가?",
    ]),
], lead="답을 보기 전에 소리 내어 설명해 본다. 막히는 문항이 다시 읽을 장이다.", pb=True)

ch9 = chapter(9, "해설", [
    answers("질문 A", [
        ("옮기지 않아도 된다.", "정적 라이브러리의 내용은 링크할 때 `Client.exe` 안으로 복사되었다. `glfw3.lib`도 마찬가지다. (2.1절)"),
        ("`Client/pch.h:3`의 `#pragma comment(lib, \"ClaudGL.lib\")`가 같은 지정을 한 번 더 하고 있기 때문이다.",
         "라이브러리 폴더 경로(`:88`)는 여전히 필요하다. (2.2절)"),
        ("로드가 실패해 `InitErrorCode::Fail`을 돌려준다.",
         "연결된 컨텍스트가 없으면 함수 주소를 받을 수 없다. `main`은 `-1`로 끝난다. (3.1절, 5장)"),
        ("생기지 않는다.",
         "C++11부터 함수 안 `static` 변수의 초기화는 한 스레드만 수행하고 나머지는 기다리도록 보장된다. (6장)"),
        ("`glad.c`는 C 파일이고 첫 줄에 `#include \"pch.h\"`가 없다.",
         "C++로 만든 pch를 C 파일에 쓸 수 없다. 남이 만든 파일을 고치지 않으려는 뜻도 있다. (4장)"),
        ("현재 스레드에 연결된 컨텍스트가 대상이기 때문이다.",
         "OpenGL은 “지금 연결된 것”에 대고 일하는 상태 기계다. 2-1강에서 이 성질을 정면으로 다룬다. (5.1절)"),
    ]),
])

ch10 = glossary_chapter(10, [
    ("정적 라이브러리", "static library (.lib)", "목적 파일 묶음. 링크할 때 실행 파일 안으로 복사된다"),
    ("링커", "linker", "목적 파일과 라이브러리를 이어 붙여 실행 파일을 만드는 도구"),
    ("미리 컴파일된 헤더", "precompiled header (pch)", "자주 쓰는 헤더를 한 번 컴파일해 저장해 둔 것"),
    ("컨텍스트", "OpenGL context", "OpenGL의 상태와 객체가 들어 있는 곳. 스레드에 연결해서 쓴다"),
    ("core 프로필", "core profile", "오래된 기능을 뺀 OpenGL. `GLFW_OPENGL_CORE_PROFILE`"),
    ("함수 로더", "loader (GLAD)", "드라이버에서 OpenGL 함수 주소를 받아 함수 포인터에 채우는 코드"),
    ("싱글턴", "singleton", "인스턴스가 하나만 있도록 강제한 클래스"),
    ("창 힌트", "window hint", "다음에 만들 창과 컨텍스트의 조건. `glfwWindowHint`"),
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
