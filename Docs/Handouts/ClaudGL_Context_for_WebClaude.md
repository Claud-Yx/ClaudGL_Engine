# ClaudGL Engine — 웹 Claude용 맥락 문서

작성일 2026-11-15. 2026-11-16에 1-4강 자료, 계획서 v5, 코드 재시작을 반영해 갱신.
6절에 옮겨 적은 코드는 커밋 `7aa55c4`(태그 `first-pass-2026-04`)의 1차 작성 코드다. 지금 작업 폴더에는 그 코드가 없다 (4절).

이 문서는 Claude Code에서 진행하던 스터디를 웹 Claude(claude.ai)에서 이어 가기 위한 인수인계 문서다.
웹 Claude는 저장소를 볼 수 없으므로, 필요한 규칙과 현재 코드 상태를 여기에 옮겨 적었다.
함께 올린 PDF가 있으면 그것이 강의 내용의 원본이고, 이 문서는 그 바깥의 맥락을 채운다.

## 1. 무엇을 하는 프로젝트인가

- 학습용 게임 엔진을 OpenGL 하나로 끝까지 직접 만든다. 조명·그림자·후처리가 있는 장면을 돌아다니는 것이 완성 기준이다.
- `gl*` 호출은 렌더러 계층 안에만 둔다. 다만 백엔드를 갈아 끼우는 인터페이스(가상 함수, 백엔드 선택)는 이 강의에서 만들지 않는다.
- DirectX 11, DirectX 12, Vulkan은 각각 독립된 후속 강의다. 여러 API를 덮는 인터페이스는 API를 각각 써 본 뒤 마지막에 만든다 (Claud가 2026-11-16에 정함).
- 언어 C++20, 빌드 Visual Studio 2022 (MSVC v143), 라이브러리 GLFW 3.4 · GLAD · GLM.
- 구성: `Engine/`(정적 라이브러리)과 `Client/`(실행 파일, 콘솔 서브시스템).
- 저장소: https://github.com/Claud-Yx/ClaudGL_Engine

## 2. 지켜 줄 규칙

멘토 규칙 (프로젝트 `CLAUDE.md`):

- 완성된 코드 해답을 주지 않는다. 교수·멘토처럼 방향을 안내한다.
- 엔진 코드는 전부 Claud가 직접 쓴다.
- 힌트, 개념, 설계 방향만 준다. 코드는 Claud가 명시적으로 요청할 때만 보여 준다.
- 막혔다고 하면 힌트를 가벼운 것부터 한 단계씩 준다.

대화 규칙 (Claud의 선호):

- 한국어로 답한다.
- 칭찬으로 채우지 않는다. 냉정하고 객관적으로 판단한다.
- 코드 리뷰에서는 어느 파일의 몇 번째 줄인지 밝힌다.
- 코드 안의 주석은 영어로 쓴다.
- 표에는 한글을 넣지 않는다. 표는 영문으로만 만들고 설명은 아래에 한글로 쓴다.
- 리눅스 명령어가 나오면 반드시 해설을 붙인다.
- 빌드는 Claud가 직접 한다. 빌드 결과를 확인하지 않은 것은 확인하지 않았다고 말한다.
- Claud는 UE5 경험이 있다. UE5에서 같은 자리에 있는 개념을 곁들이면 이해가 빠르다.
- 설명은 대학 강의처럼 자세히 한다. 라이브러리 함수는 인자, 돌려주는 값, 실패하는 경우까지 설명하고 예시를 든다
  (2026-11-16에 Claud가 정함). 남이 만든 함수의 사용법을 설명하는 것은 멘토 규칙에 어긋나지 않는다.

## 3. 커리큘럼과 번호

- 강 번호는 `Part-순서`다. `1-5`는 Part 1의 다섯 번째 강이고, 본문에서는 "1-5강"이라고 쓴다.
- 자료 안의 장·절은 점으로 쓴다 ("3장", "6.2절").
- 전체 30강, 계획 기준 124시간. 원본은 저장소의 `Docs/Handouts/src/curriculum.py`다.

Part 1 Core:
1-1 프로젝트 구성과 창 / 1-2 Game Loop와 Delta Time / 1-3 Input System / 1-4 초기화 실패와 종료 처리 /
1-5 Logger / 1-6 Assert와 오류 처리 정책 / 1-7 파일과 경로

Part 2 날것의 OpenGL (일부러 클래스로 감싸지 않는 구간):
2-1 OpenGL이라는 상태 기계 / 2-2 첫 삼각형 / 2-3 인덱스 버퍼와 사각형 / 2-4 셰이더 다루기 / 2-5 텍스처 /
2-6 변환과 좌표 공간

Part 3 Renderer 계층 (GL 객체를 쥐는 구체 클래스. 가상 함수 인터페이스는 만들지 않는다):
3-1 Renderer 설계 / 3-2 Window와 RenderDevice 분리 / 3-3 Buffer와 VertexLayout / 3-4 Shader와 Texture /
3-5 Resource Manager / 3-6 Renderer 마무리와 검증 / 3-7 렌더 상태

Part 4 Scene:
4-1 Transform과 계층 / 4-2 Camera / 4-3 Mesh / 4-4 Material / 4-5 Lighting / 4-6 Renderer 정리

Part 5 Advanced:
5-1 Framebuffer와 후처리 / 5-2 Shadow Mapping / 5-3 ImGui 통합 (선택) / 5-4 회고

이 강의는 5-4강에서 끝난다. 그 뒤는 독립된 강의로, 생각하는 순서는 애니메이션·사운드·물리(셋 사이의 순서는 미정)
→ DX11 → DX12 → Vulkan → 통합 엔진이다. 강 구성은 그 강의를 시작할 때 따로 계획한다.

## 4. 지금 어디까지 왔는가

- 2026-11-16에 처음부터 다시 시작했다. 1차로 쓴 코드(1-1 〜 1-3강 완료, Logger 뼈대)는 7개월 전 것이라 Claud가
  다시 쳐 보기로 했다. 작업 폴더에는 프로젝트 설정, `include/`, pch 파일, `Engine/Enum/InputKeys.h`만 남아 있고
  `Client/main.cpp`는 빈 `main`이다.
- 1차 코드는 태그 `first-pass-2026-04`에 그대로 있다. 다시 친 코드와 비교하는 답안지로 쓴다.
- 지금 할 강은 1-1강이다 (자료 v3). 클래스와 함수의 이름·선언은 1차 코드와 같게 두고, 본체는 Claud가 직접 쓴다.
  1차 코드를 보여 주며 따라 치게 하지 않는다.
- 1-4강 (초기화 실패와 종료 처리), 1-5강 (Logger)은 자료가 나와 있고 코드는 아직이다.
- 1-4강과 1-5강 중 어느 것을 먼저 할지는 Claud가 정한다. 두 자료 모두 어느 순서로 해도 되게 썼다.
  1-4강 자료는 Logger가 아직 없으면 `std::cerr`로 실패 이유를 찍게 하고, 1-5강 자료는 엔진에 종료 경로가
  없다는 전제로 `GLogger::Shutdown()`을 부르는 자리를 임시로 둔다.

## 5. 강의 자료

파일 이름은 `ClaudGL_<강 번호>_<주제>_v<버전>.pdf`다. 한 번 나간 PDF를 고치면 버전을 올린다.

- `ClaudGL_00_Plan_v5.pdf` — 전체 강의 계획서. 스터디를 시작할 때 보는 지침서라서 진행 상황은 들어 있지 않다.
- `ClaudGL_1-1_ProjectAndWindow_v3.pdf`, `ClaudGL_1-2_GameLoop_v4.pdf`, `ClaudGL_1-3_Input_v4.pdf`,
  `ClaudGL_1-4_InitAndShutdown_v2.pdf`, `ClaudGL_1-5_Logger_v2.pdf`, `ClaudGL_1-6_Assert_v2.pdf`
  — 여섯 강 모두 2026-11-16에 같은 양식으로 다시 썼다. 처음부터 직접 쓰는 자료이고 함수 설명, 예시, 그림,
  구현 미션이 있다. 완성 코드는 없다. 1차 코드는 인용하지 않고, 엔진 코드는 함수 이름으로 가리킨다.
  1-2강은 2026-11-17에 2.2절의 표와 문장 하나를 고쳐 v4가 됐다.
- 예전 판은 `Legacy/` 폴더에 있다. 그 가운데 `Legacy/ClaudGL_1-1_ProjectAndWindow_v2.pdf`,
  `Legacy/ClaudGL_1-2_GameLoop_v2.pdf`, `Legacy/ClaudGL_1-3_Input_v3.pdf`는 1차 코드를 줄 단위로 읽는 자료다.
  미션이 없고, 각 강의 미션을 끝낸 뒤에 읽는 해설로 쓴다.

1-4강 자료의 구성: 왜 필요한가 → 초기화는 실패할 수 있다 → 반쯤 된 초기화 되돌리기 → 종료 경로
→ 자원의 주인과 값 초기화 → 설계 → 구현 미션(8단계) → 흔한 함정 → 완료 기준 → 생각해 볼 질문 → 해설 → 용어집.
1-1 〜 1-3강 자료가 "1-4강에서 고친다"고 미뤄 둔 13건을 여기서 받는다. 넷은 이 강의 주제이고, 나머지 아홉
(첫 프레임 dt, dt 상한, 수직 동기, 입력 쪽 셋, 프로젝트 설정 셋)은 6.4절의 표에 모여 있다.

1-4강에서 Claud가 정할 것 (6.2절): `Init`이 실패를 알리는 방식 / 이유를 찍는 곳 / 찍는 수단 /
반쯤 된 초기화를 되돌리는 방법 / 정리를 부르는 주체 / 창 핸들을 드는 방법 / 루프를 끝내는 스위치.

1-5강 자료의 구성: 왜 필요한가 → 로그 한 줄의 구성 → 호출한 자리를 어떻게 아는가 → 메시지 조립(std::format)
→ 콘솔과 파일 → 설계 → 구현 미션(8단계) → 흔한 함정 → 완료 기준 → 생각해 볼 질문 → 해설 → 용어집.

웹 Claude에게: 강의 자료의 미션에 대한 완성 코드를 먼저 내놓지 않는다. 자료의 장·절 번호("5.2절")를
그대로 가리키며 설명하면 Claud가 찾아보기 쉽다.

## 6. 1-5강과 관련된 1차 코드

아래는 태그 `first-pass-2026-04`의 코드다. 1-4강과 1-5강 자료가 가리키는 파일과 줄 번호도 이 코드 기준이다.
Claud가 다시 친 코드는 줄 번호가 조금 다를 수 있으니, 줄 번호를 말할 때는 지금 코드를 붙여 달라고 한다.

`Engine/Enum/LogLevel.h`

```cpp
#pragma once

enum class ELogLevel : int
{
    Trace,
    Debug,
    Info,
    Warning,
    Error,
    Fatal
};
```

`Engine/Core/Logger.h`

```cpp
#pragma once
#include <fstream>

#include "Enum/LogLevel.h"

class GLogger
{
public:
    static GLogger& Get();

    void Init( const char* file_name );
    void Shutdown();

    void Log( ELogLevel log_level, std::string_view category, const char* file, int line, const std::string& message );

private:
    GLogger()                            = default;
    ~GLogger()                           = default;
    GLogger( const GLogger& )            = delete;
    GLogger& operator=( const GLogger& ) = delete;

    // property

    std::ofstream _log_file{};
    ELogLevel     _min_level{ELogLevel::Trace};
};
```

`Engine/Core/Logger.cpp`

```cpp
#include "pch.h"
#include "Logger.h"

#include <Windows.h>

GLogger& GLogger::Get()
{
    static GLogger instance; // C++11 guarantees thread-safe initialization
    return instance;
}

void GLogger::Init( const char* file_name )
{
    _log_file.open( file_name );
    HANDLE handle = GetStdHandle( STD_OUTPUT_HANDLE );
    DWORD  mode   = 0;
    GetConsoleMode( handle, &mode );
    SetConsoleMode( handle, mode | ENABLE_VIRTUAL_TERMINAL_PROCESSING );
}

void GLogger::Shutdown()
{
    _log_file.close();
}

void GLogger::Log( ELogLevel log_level, std::string_view category, const char* file, int line, const std::string& message )
{
}
```

로그로 바꿔야 할 자리 (1-5강 미션 7단계):

- `Engine/Core/EngineCore.cpp:66` — `std::cout << "GEngine::Update() is null.\n";` (`Run()` 안, Update 콜백이 비었을 때)
- `Engine/Core/EngineCore.cpp:30` 〜 `:33` — `gladLoadGLLoader`가 실패하면 말없이 `InitErrorCode::Fail`을 돌려준다
- `Engine/Manager/InputManager.cpp:35`, `:42`, `:49` — `if ( !IsValidKey( key ) ) return false; // need log`
- `Engine/Core/EngineCore.cpp:6` — `#include <iostream>` (위의 `std::cout`이 사라지면 필요 없다)

주변 사실:

- `GEngine`도 `GLogger`와 같은 방식의 싱글턴이다 (함수 안 `static` 지역 변수). `Client/main.cpp:10`에서
  `GEngine::Get()`이 가장 먼저 불린다.
- `GEngine`에는 `Shutdown`이 없다. `Run()`이 끝나면 `main`이 끝난다. `glfwTerminate()`도 불리지 않는다 (1-4강 몫).
- `GLogger`는 아직 `Logger.h`·`Logger.cpp` 밖에서 한 번도 쓰이지 않는다. `Init`을 부르는 곳이 없다.
- `pch.h`는 `framework.h`를 포함하고, 거기에 glad, GLFW, GLM, `<memory>`, `<string>`, `<functional>`이 들어 있다.
- `Logger.cpp`는 `pch.h`(glad 포함) 뒤에 `<Windows.h>`를 포함한다. `APIENTRY` 재정의 경고(C4005)가 날 수 있는데
  빌드로 확인하지는 않았다.
- `.gitignore`에 `*.log`가 이미 있다.

## 7. 1-5강에서 Claud가 정해야 하는 것

정답이 없는 지점이다. 대신 골라 주지 말고, 선택지의 장단점을 물으면 답해 준다.

1. 호출 위치를 얻는 방법 — 매크로와 `__FILE__`·`__LINE__` (지금 시그니처가 이쪽이다) / `std::source_location`
2. 레벨 검사의 위치 — `Log()` 안 / 매크로 안 / 둘 다
3. flush 시점 — 줄마다 / `Warning` 이상일 때만 / `Shutdown()`에서만
4. 카테고리의 표현 — 문자열 (지금) / 열거형 / 카테고리 객체
5. `message`의 타입 — `const std::string&` (지금) / `std::string_view`
6. `Init`·`Shutdown`을 부르는 곳 — `Client/main.cpp` / `GEngine::Init` 안
7. 릴리스 빌드에서 `Trace`·`Debug`를 남길지 컴파일에서 뺄지

이 강에서 하지 않기로 한 것: `Fatal`에서 멈추기 (1-6강), 제대로 된 종료 순서와 초기화 실패 처리 전반 (1-4강),
스레드 안전, 싱크 인터페이스 추상화.

## 8. 1-5강의 완료 기준

- 콘솔에 시각, 레벨, 카테고리, 메시지가 붙은 줄이 나오고 레벨마다 색이 다르다.
- 같은 내용이 로그 파일에 색 코드 없이 남는다.
- 최소 레벨을 `Warning`으로 바꾸면 `Trace`·`Debug`·`Info`가 콘솔과 파일 양쪽에서 사라진다.
- 호출부 어디에도 파일 이름이나 줄 번호를 손으로 적은 곳이 없다.
- `Engine/` 안에서 `std::cout`과 `need log`가 검색되지 않는다.
- 위 7가지에 대해 고른 것과 이유가 적혀 있다.

## 9. 웹 Claude가 할 수 없는 것

- 저장소를 직접 읽지 못한다. 6절의 코드는 1차 코드이고 지금 작업 폴더에는 없다. Claud가 다시 친 코드를
  붙여 넣어 달라고 한다. 줄 번호도 그때의 코드 기준으로 다시 센다.
- 강의 자료 PDF를 새로 만들거나 고치는 일은 Claude Code 쪽의 `claudgl-lesson-builder` 스킬이 한다.
  자료에서 틀린 곳이나 바꿀 곳을 찾으면 목록으로 정리해 주면, Claud가 Claude Code에 전달한다.
