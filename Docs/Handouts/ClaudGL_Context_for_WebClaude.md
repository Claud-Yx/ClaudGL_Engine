# ClaudGL Engine — 웹 Claude용 맥락 문서

작성일 2026-11-15, 2026-11-16에 1-4강 자료를 반영해 갱신. 코드 기준은 커밋 `7aa55c4`의 엔진 코드다 (그 뒤 커밋은 문서만 바꿨다).

이 문서는 Claude Code에서 진행하던 스터디를 웹 Claude(claude.ai)에서 이어 가기 위한 인수인계 문서다.
웹 Claude는 저장소를 볼 수 없으므로, 필요한 규칙과 현재 코드 상태를 여기에 옮겨 적었다.
함께 올린 PDF가 있으면 그것이 강의 내용의 원본이고, 이 문서는 그 바깥의 맥락을 채운다.

## 1. 무엇을 하는 프로젝트인가

- 학습용 크로스 API 게임 엔진을 직접 만든다. OpenGL로 시작해 DirectX 11, DirectX 12, Vulkan 순서로 넓힌다.
- 렌더러 백엔드만 갈아 끼울 수 있도록 추상화 계층을 제대로 세우는 것이 목표다.
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

## 3. 커리큘럼과 번호

- 강 번호는 `Part-순서`다. `1-5`는 Part 1의 다섯 번째 강이고, 본문에서는 "1-5강"이라고 쓴다.
- 자료 안의 장·절은 점으로 쓴다 ("3장", "6.2절").
- 전체 30강, 계획 기준 124시간. 원본은 저장소의 `Docs/Handouts/src/curriculum.py`다.

Part 1 Core:
1-1 프로젝트 구성과 창 / 1-2 Game Loop와 Delta Time / 1-3 Input System / 1-4 초기화 실패와 종료 처리 /
1-5 Logger / 1-6 Assert와 오류 처리 정책 / 1-7 파일과 경로 / 1-8 Resource Manager

Part 2 날것의 OpenGL (일부러 추상화하지 않는 구간):
2-1 OpenGL이라는 상태 기계 / 2-2 첫 삼각형 / 2-3 인덱스 버퍼와 사각형 / 2-4 셰이더 다루기 / 2-5 텍스처 /
2-6 변환과 좌표 공간

Part 3 Renderer 추상화:
3-1 추상화 설계 / 3-2 Window와 RenderDevice 분리 / 3-3 Buffer와 VertexLayout / 3-4 Shader와 Texture /
3-5 OpenGL 백엔드 마무리와 검증 / 3-6 렌더 상태

Part 4 Scene:
4-1 Transform과 계층 / 4-2 Camera / 4-3 Mesh / 4-4 Material / 4-5 Lighting / 4-6 Renderer 정리

Part 5 Advanced:
5-1 Framebuffer와 후처리 / 5-2 Shadow Mapping / 5-3 ImGui 통합 (선택) / 5-4 회고와 DX11 준비

Part 6〜8 (DX11, DX12, Vulkan)은 5-4강 뒤에 상세화한다.

## 4. 지금 어디까지 왔는가

- 1-1, 1-2, 1-3강: 코드 완료. 창이 뜨고, 루프가 돌고, A·S·D 키로 배경색이 바뀐다.
- 1-4강 (초기화 실패와 종료 처리): 코드는 시작하지 않았다. 강의 자료는 2026-11-16에 나왔다.
- 1-5강 (Logger): 진행 중. 뼈대만 있고 `Log()` 본문이 비어 있다. 강의 자료가 나와 있다.
- 1-4강과 1-5강 중 어느 것을 먼저 할지는 Claud가 정한다. 두 자료 모두 어느 순서로 해도 되게 썼다.
  1-4강 자료는 Logger가 아직 없으면 `std::cerr`로 실패 이유를 찍게 하고, 1-5강 자료는 엔진에 종료 경로가
  없다는 전제로 `GLogger::Shutdown()`을 부르는 자리를 임시로 둔다.

## 5. 강의 자료

파일 이름은 `ClaudGL_<강 번호>_<주제>_v<버전>.pdf`다. 한 번 나간 PDF를 고치면 버전을 올린다.

- `ClaudGL_00_Plan_v4.pdf` — 전체 강의 계획서. 스터디를 시작할 때 보는 지침서라서 진행 상황은 들어 있지 않다.
- `ClaudGL_1-1_ProjectAndWindow_v2.pdf`, `ClaudGL_1-2_GameLoop_v2.pdf`, `ClaudGL_1-3_Input_v2.pdf`
  — 이미 쓴 코드를 인용해서 다시 읽는 자료. 미션이 없다.
- `ClaudGL_1-4_InitAndShutdown_v1.pdf`, `ClaudGL_1-5_Logger_v1.pdf` — 개념, 설계, 구현 미션이 있는 자료.
  완성 코드는 없다.

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

## 6. 1-5강과 관련된 현재 코드

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

- 저장소를 직접 읽지 못한다. 6절의 코드는 2026-11-15 기준이다. Claud가 코드를 고친 뒤에는 바뀐 코드를
  붙여 넣어 달라고 한다. 줄 번호도 그때의 코드 기준으로 다시 센다.
- 강의 자료 PDF를 새로 만들거나 고치는 일은 Claude Code 쪽의 `claudgl-lesson-builder` 스킬이 한다.
  자료에서 틀린 곳이나 바꿀 곳을 찾으면 목록으로 정리해 주면, Claud가 Claude Code에 전달한다.
