"""Lesson 1-1 -- project layout and the first window, written from scratch.

Version 3 replaces the earlier "re-read your own code" handout: the engine code
was removed on 2026-11-16 (first pass kept at tag first-pass-2026-04), so this
lesson starts from the libraries-only baseline and has missions.

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

# Project files (.vcxproj, pch, framework.h, library headers) were read on this day.
READ_DATE = "2026-11-16"
BASE_COMMIT = "04083b0"       # the libraries-only baseline this lesson starts from

COVER = cover(
    f"CLAUDGL ENGINE · PART {ME['part']} · {ME['id']} · v{ME['ver']}",
    Raw('GEngine::<span class="ac">Init</span>'),
    ME["title"],
    "빈 프로젝트에서 창 하나가 뜨기까지",
    [
        ("목표 결과물", "`Client.exe`를 실행하면 배경색으로 채워진 빈 창이 뜨고, 창을 닫으면 프로그램이 끝난다"),
        ("핵심 개념", "컴파일과 링크 · 정적 라이브러리 · pch · OpenGL 컨텍스트 · 함수 로더 · 싱글턴"),
        ("선수 지식", "C++의 클래스, `static`, 포인터와 참조. Visual Studio에서 빌드하고 실행하는 법"),
        ("예상 시간", f"읽기 1시간 + 구현 2시간 (계획서 기준 {ME['hours']}시간)"),
        ("건드릴 파일", "`Engine/Core/EngineCore.h`·`.cpp`(새 파일), `Client/main.cpp`"),
        ("시작 상태", f"커밋 `{BASE_COMMIT}`: 프로젝트 설정과 외부 라이브러리만 있고 `main`은 비어 있다 ({READ_DATE}에 읽음)"),
    ],
    note=("읽는 법",
          "처음부터 직접 쓰는 자료다. 2 〜 3장은 이미 되어 있는 프로젝트 구성을 읽고 이해하는 장이고, 4 〜 7장이 이 강에서 "
          "쓸 함수와 개념이다. 8장의 모양을 확인한 뒤 9장의 미션을 순서대로 구현한다. 코드 블록은 완성본이 아니다."),
    toc=["한 장으로 보기", "프로젝트 두 개와 빌드의 흐름", "외부 라이브러리 셋", "GLFW로 창 만들기",
         "OpenGL 컨텍스트와 함수 로더", "창을 살려 두는 가장 작은 루프", "GEngine 싱글턴", "설계", "구현 미션",
         "흔한 함정", "완료 기준", "생각해 볼 질문", "해설", "용어집"],
)

# --------------------------------------------------------------------------

ch1 = chapter(1, "한 장으로 보기", [
    layers([
        ("실행 파일", [("Client.exe", "`main()` · 게임 코드", "accent")]),
        ("정적 라이브러리", [("ClaudGL.lib", "Engine 프로젝트 + `glad.c`"), ("glfw3.lib", "미리 빌드된 GLFW")]),
        ("운영체제", [("opengl32.lib", "Windows의 OpenGL 입구"), ("Win32", "창 · 입력 · 시간")]),
        ("하드웨어 쪽", [("그래픽 드라이버", "OpenGL 4.6의 실제 구현", "dark")]),
    ], "위의 둘은 링크할 때 `Client.exe` 안으로 복사된다. 실행할 때 따로 필요한 `.lib` 파일은 없다."),
    table([24, 76], ["", "무엇이 있는가"], [
        ["이미 있는 것", "솔루션과 프로젝트 두 개의 설정, `include/`의 외부 라이브러리 헤더, pch 파일들, `Engine/framework.h`, "
                    "`Engine/Enum/InputKeys.h`(1-3강에서 쓴다), 빈 `main`이 든 `Client/main.cpp`"],
        ["저장소 밖에 있는 것", "`lib/Debug/x64/glfw3.lib`. 빌드 결과물 폴더라 저장소에 올라가지 않는다. 이 파일이 그 자리에 "
                        "있어야 링크가 된다 (10장)"],
        ["이 강에서 만드는 것", "`Engine/Core/EngineCore.h`와 `.cpp`의 `GEngine` 클래스, 그리고 `Client/main.cpp`의 내용"],
    ], cell_cls=["lab", ""]),
    flow([
        ("기준 빌드", "빈 main"),
        ("GEngine", "하나뿐인 객체"),
        ("Init: 창", "GLFW"),
        ("Init: GL", "컨텍스트 · GLAD", "accent"),
        ("임시 루프", "창을 살려 둔다"),
        ("빈 창", "배경색", "dark"),
    ], "9장의 미션이 지나가는 길이다. 왼쪽에서 오른쪽으로 한 칸씩 빌드하며 간다."),
], lead="이 강이 끝나면 창 하나가 뜬다. 화면에 보이는 것은 그것뿐이지만, 그 뒤에서 프로젝트 두 개와 외부 라이브러리 "
        "세 개가 묶인다. 먼저 무엇이 무엇 위에 얹혀 있는지 본다.")

ch2 = chapter(2, "프로젝트 두 개와 빌드의 흐름", [
    table([14, 22, 20, 44], ["프로젝트", "종류", "결과물", "설정된 곳"], [
        ["Engine", "정적 라이브러리", "`ClaudGL.lib`",
         "`Engine/Engine.vcxproj:43` (종류), `:90` (출력 폴더 `lib/Debug/x64/`), `:95` (이름)"],
        ["Client", "실행 파일 (콘솔)", "`Client.exe`",
         "`Client/Client.vcxproj:43` (종류), `:86` (출력 폴더 `Debug/x64/`), `:142` (콘솔)"],
    ], cell_cls=["lab", "", "", ""]),

    h3("2.1", "소스가 실행 파일이 되기까지"),
    Fig(236)
    .text(20, 15, "Engine 프로젝트", kind="s", anchor="start", size=10)
    .box(20, 24, 180, 50, "소스 파일", "pch.cpp · glad.c · EngineCore.cpp")
    .arrow((200, 49), (250, 49))
    .text(225, 41, "컴파일", kind="s", size=9.5)
    .box(250, 24, 90, 50, ".obj", "목적 파일")
    .arrow((340, 49), (390, 49))
    .text(365, 41, "묶기", kind="s", size=9.5)
    .box(390, 24, 130, 50, "ClaudGL.lib", "정적 라이브러리", kind="accent")
    .text(20, 141, "Client 프로젝트", kind="s", anchor="start", size=10)
    .box(20, 150, 180, 50, "소스 파일", "pch.cpp · main.cpp")
    .arrow((200, 175), (250, 175))
    .text(225, 167, "컴파일", kind="s", size=9.5)
    .box(250, 150, 90, 50, ".obj", "목적 파일")
    .arrow((340, 175), (390, 175), kind="accent")
    .text(365, 167, "링크", kind="accent", size=9.5)
    .box(390, 150, 130, 50, "Client.exe", "실행 파일", kind="dark")
    .arrow((440, 74), (440, 150), kind="accent")
    .box(548, 86, 100, 42, "glfw3.lib", "미리 빌드된 GLFW", kind="soft")
    .box(548, 154, 100, 42, "opengl32.lib", "Windows SDK", kind="soft")
    .arrow((548, 107), (495, 107), (495, 150), kind="accent")
    .arrow((548, 175), (520, 175), kind="accent")
    .text(225, 222, "헤더 폴더 설정이 쓰이는 곳", kind="s", size=9.5)
    .text(455, 222, "lib 폴더와 lib 이름 설정이 쓰이는 곳", kind="s", size=9.5)
    .render("빌드는 두 단계다. 컴파일은 `.cpp` 하나를 `.obj` 하나로 바꾸고, 링크는 `.obj`와 `.lib`를 모아 실행 파일 하나로 만든다."),
    p("**컴파일**은 소스 파일을 하나씩 따로 기계어로 바꾸는 일이다. 컴파일러는 한 번에 `.cpp` 하나만 본다. 그 파일이 "
      "`glfwInit()`을 부르면, 컴파일러는 헤더에 적힌 선언만 보고 “이런 함수가 어딘가에 있다”고 믿고 호출 코드를 만든다. "
      "함수의 본체가 어디 있는지는 아직 모른다. 결과물이 목적 파일(`.obj`)이다."),
    p("**링크**는 그 빈칸을 채우는 일이다. 링커는 `.obj`들과 `.lib`들을 모아, “어딘가에 있다”고 적어 둔 이름마다 실제 "
      "본체를 찾아 주소를 이어 붙인다. 끝까지 못 찾은 이름이 하나라도 있으면 실행 파일은 만들어지지 않는다."),
    p("Engine 프로젝트는 링크하지 않는다. 컴파일한 `.obj`들을 한 파일로 **묶기만** 한다. 그것이 정적 라이브러리다. "
      "그래서 본체가 없는 함수를 불러도 Engine 빌드는 성공하고, 오류는 Client를 링크할 때 나온다."),

    h3("2.2", "정적 라이브러리"),
    cards([
        ("정적 .lib", "링크할 때 exe에 복사", "배포가 단순하다. 엔진을 고치면 Client를 다시 링크해야 한다.", "지금 방식"),
        ("동적 .dll", "실행할 때 불러옴", "exe와 따로 교체할 수 있다. 대신 내보낼 심볼을 표시해야 하고 dll 파일이 옆에 있어야 한다.",
         "UE 에디터 빌드의 모듈"),
    ]),

    h3("2.3", "Client가 Engine을 찾는 세 가지 설정"),
    table([22, 44, 34], ["무엇을", "어디에 적혀 있나", "빠지면 나오는 오류"], [
        ["헤더가 있는 폴더", "`Client/Client.vcxproj:87` — `include\\`와 `Engine\\`", "컴파일 단계 `C1083` (헤더를 열 수 없음)"],
        ["`.lib`가 있는 폴더", "`Client/Client.vcxproj:88` — `lib\\Debug\\x64\\`", "링크 단계 `LNK1104` (파일을 열 수 없음)"],
        ["링크할 `.lib` 이름", "`Client/Client.vcxproj:144` — `ClaudGL.lib;glfw3.lib;opengl32.lib`",
         "링크 단계 `LNK2019` (확인할 수 없는 외부 기호)"],
    ], cell_cls=["lab", "", ""]),
    box("ex", "예시: 오류 번호로 단계를 가린다", [
        p("오류 번호가 `C`로 시작하면 컴파일러가, `LNK`로 시작하면 링커가 낸 것이다. 번호만 봐도 위 그림의 어느 화살표에서 "
          "멈췄는지 알 수 있다. 아래 세 줄은 위 표의 세 설정이 하나씩 빠졌을 때의 모습이다."),
        console(Raw(
            '<span class="err">main.cpp(2,10): fatal error C1083:</span> Cannot open include file: '
            "'Core/EngineCore.h': No such file or directory\n"
            '<span class="err">LINK : fatal error LNK1104:</span> cannot open file \'glfw3.lib\'\n'
            '<span class="err">ClaudGL.lib(EngineCore.obj) : error LNK2019:</span> unresolved external symbol glfwInit\n'
            '    referenced in function "public: ... GEngine::Init(...)"'
        ), title="빌드 출력 (형식은 예시)"),
        p("셋째 줄을 읽는 법: `ClaudGL.lib` 안의 `EngineCore.obj`가 `glfwInit`을 부르는데, 링커가 그 본체를 어느 `.lib`에서도 "
          "찾지 못했다는 뜻이다. `glfw3.lib`가 링크 목록에 없을 때 나온다."),
    ]),
    code(r"""
#pragma once

#pragma comment(lib, "ClaudGL.lib")

#include "framework.h"
""", title="Client/pch.h", tag="now", start=1, hl=[3]),
    p("`#pragma comment(lib, …)`는 “이 파일을 컴파일한 결과물에 이 라이브러리를 링크하라는 메모를 남겨라”는 MSVC 전용 "
      "지시다. `ClaudGL.lib`는 프로젝트 설정(144행)과 이 줄, 두 군데에서 지정되어 있다. 하나만 있어도 된다."),

    h3("2.4", "pch: 미리 컴파일된 헤더"),
    p("`glm`이나 표준 라이브러리 헤더는 크다. `.cpp` 파일마다 이것들을 처음부터 다시 읽으면 빌드가 느려진다. pch는 "
      "자주 쓰는 헤더를 한 번만 컴파일해 결과를 저장해 두고, 다른 파일이 그 결과를 불러다 쓰게 하는 장치다."),
    table([24, 38, 38], ["역할", "파일", "설정"], [
        ["만든다 (Create)", "`Engine/pch.cpp`", "`Engine/Engine.vcxproj:181` 〜 `:186`"],
        ["쓴다 (Use)", "나머지 `.cpp` 전부", "`Engine/Engine.vcxproj:147` 〜 `:148`"],
        ["쓰지 않는다", "`include/glad/glad.c`", "`Engine/Engine.vcxproj:178` 〜 `:180`"],
    ], cell_cls=["lab", "", ""]),
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
""", title="Engine/framework.h", tag="now", start=1, hl=[5, 6]),
    p("`Engine/pch.h`는 이 파일 하나를 포함할 뿐이다. 그래서 pch를 쓰는 모든 `.cpp`는 glad, GLFW, GLM과 `<memory>`, "
      "`<string>`, `<functional>`을 이미 본 상태에서 시작한다. 알아 둘 규칙이 둘 있다."),
    ul([
        "**새로 만드는 `.cpp`의 첫 줄은 `#include \"pch.h\"`다.** 컴파일러는 그 줄까지를 저장해 둔 결과로 바꿔치기한다. "
        "그 줄이 없으면 `C1010` 오류가 나고, 그 줄보다 앞에 적은 것은 무시된다.",
        "**5행이 6행보다 먼저다.** `glad.h`는 OpenGL 선언을 자기가 맡으려 하므로 다른 OpenGL 헤더(GLFW가 끌어오는 것)보다 "
        "먼저 포함되어야 한다. 순서를 바꾸면 `glad.h`가 오류를 낸다.",
    ]),
    box("point", None,
        "Client의 `pch.h`도 `framework.h`를 포함한다(`Client/pch.h:5`). Client 폴더에는 그런 파일이 없으므로, 포함 "
        "경로에 들어 있는 `Engine\\` 폴더의 것이 잡힌다. 그래서 Client의 모든 파일이 glad와 GLFW를 볼 수 있다. 6장의 임시 "
        "루프를 `main`에 쓸 수 있는 이유다. 편하지만, Part 3에서 끊어야 할 연결이다."),
    box("ue", None,
        "언리얼에서는 모듈의 `Build.cs`에 `PublicDependencyModuleNames.Add(\"Engine\")` 한 줄을 적으면 헤더 경로와 "
        "링크 설정이 함께 잡힌다. 2.3절 표의 세 줄을 UnrealBuildTool이 대신 해 주는 것이다."),
    box("cs", None,
        "컴파일러가 한 번에 보는 단위를 번역 단위(translation unit)라고 한다. `.cpp` 하나와 그것이 포함한 헤더 전부다. "
        "“선언은 여러 번, 정의는 한 번”이라는 규칙(ODR)과 헤더 가드가 필요한 이유가 여기서 나온다. 전공서의 "
        "컴파일·링크 단계, 심볼 테이블 항목과 닿는다."),
], lead="Engine은 정적 라이브러리로, Client는 그것을 링크하는 실행 파일로 만든다. 이 구성은 이미 되어 있다. "
        "여기서는 그 설정이 무슨 일을 하는지 읽는다.")

ch3 = chapter(3, "외부 라이브러리 셋", [
    table([13, 37, 28, 22], ["이름", "하는 일", "들어오는 형태", "버전"], [
        ["GLFW", "창을 만들고, OpenGL 컨텍스트를 만들고, 키 입력과 시간을 알려 준다", "헤더 + 미리 빌드된 `glfw3.lib`",
         "3.4"],
        ["GLAD", "OpenGL 함수의 주소를 실행 중에 찾아 채워 넣는다", "헤더 + `glad.c` (Engine에 같이 컴파일)",
         "0.1.36으로 만든 OpenGL 4.6 core 로더"],
        ["GLM", "벡터와 행렬 수학", "헤더만 (링크할 것이 없다)", "1.0.2"],
    ], cell_cls=["lab", "", "", ""]),

    h3("3.1", "왜 GLAD가 필요한가"),
    p("Windows가 기본으로 주는 `opengl32.lib`에는 OpenGL 1.1 시절의 함수만 들어 있다. 그 뒤에 나온 함수는 그래픽 드라이버 "
      "안에 있다. 드라이버는 그래픽 카드 제조사가 만들고 PC마다 다르므로, 빌드할 때는 그 함수들이 어디 있는지 알 수 없다. "
      "프로그램이 실행된 뒤에 “이 이름의 함수 주소를 달라”고 물어서 받아야 한다."),
    code(r"""
typedef void (APIENTRYP PFNGLCLEARPROC)(GLbitfield mask);
GLAPI PFNGLCLEARPROC glad_glClear;
#define glClear glad_glClear
""", title="include/glad/glad.h", tag="now", start=1561),
    p("위 세 줄이 GLAD가 하는 일의 전부를 보여 준다. 1561행은 “`GLbitfield` 하나를 받고 아무것도 돌려주지 않는 함수를 "
      "가리키는 포인터” 타입을 만든다. 1562행은 그 타입의 전역 변수 `glad_glClear`를 선언한다. 1563행은 `glClear`라고 "
      "쓰면 그 변수로 바뀌게 한다. 즉 우리가 부르는 `glClear( … )`는 진짜 함수가 아니라 ==함수 포인터 변수를 통한 호출==이다."),
    p("프로그램이 시작할 때 이 포인터들은 전부 `nullptr`이다. `gladLoadGLLoader`가 불리면 GLAD는 이름마다 주소를 물어 "
      "포인터 수백 개를 한꺼번에 채운다 (5장). 그 전에 `gl*` 함수를 부르면 주소 0을 실행하려다 프로그램이 죽는다."),
    box("api", None,
        "DX11에는 이런 로더가 없다. `d3d11.lib`를 링크하고 `D3D11CreateDevice`로 장치 객체를 받은 뒤 그 객체의 멤버 "
        "함수를 부른다. Vulkan은 `vulkan-1.dll`이 로더 역할을 하고, 함수 주소를 직접 받아 쓰는 방식도 지원한다."),
    box("cs", None,
        "함수 포인터를 채워 넣고 그것을 통해 부르는 방식은 운영체제가 DLL의 함수를 연결할 때(import table)나 C++의 "
        "가상 함수 표(vtable)와 같은 생각이다. 호출할 대상을 빌드할 때가 아니라 실행 중에 정한다. 대학 때 직접 설계한 "
        "CPU로 치면 “점프할 주소를 메모리에서 읽어 오는” 간접 점프다."),
], lead="엔진이 직접 하지 않고 빌려 쓰는 일이 셋 있다. 창, OpenGL 함수 찾기, 수학이다. 셋 다 `include/` 폴더에 "
        "헤더가 들어 있다.")

ch4 = chapter(4, "GLFW로 창 만들기", [
    p("창을 만드는 일은 운영체제마다 방법이 다르다. Windows에서는 창 클래스를 등록하고, `CreateWindowEx`를 부르고, "
      "픽셀 형식을 고르고, WGL로 OpenGL 컨텍스트를 만드는 수십 줄이 필요하다. GLFW는 그 일을 함수 서너 개로 줄여 준다. "
      "이 장의 세 함수가 그것이다."),
    fn("glfwInit", "int glfwInit(void);",
       "GLFW 라이브러리를 초기화한다. 창 시스템과 연결하고, 연결된 모니터를 조사하고, 타이머를 0초로 맞춘다.",
       returns="성공하면 `GLFW_TRUE`(1), 실패하면 `GLFW_FALSE`(0)",
       fails="창 시스템을 쓸 수 없는 환경에서 실패한다. 실패하면 GLFW가 스스로 정리까지 하고 돌아온다",
       notes=[("부르는 순서", "거의 모든 GLFW 함수보다 먼저다. 성공한 뒤 다시 부르면 아무 일 없이 `GLFW_TRUE`를 돌려준다"),
              ("짝이 되는 함수", "`glfwTerminate()`. 프로그램을 끝낼 때 한 번 부른다 (1-4강)"),
              ("선언된 곳", "`include/GLFW/glfw3.h:2220`")],
       lib="GLFW 3.4"),
    fn("glfwWindowHint", "void glfwWindowHint(int hint, int value);",
       "다음에 만들 창과 컨텍스트의 조건을 예약한다. 이 함수는 적어 두기만 하고, 실제 적용은 창을 만들 때 일어난다.",
       params=[("`hint`", "무엇을 정할지 고르는 상수. 아래 표의 이름들"),
               ("`value`", "그 항목에 줄 값")],
       returns="없다",
       fails="모르는 `hint`를 주면 `GLFW_INVALID_ENUM` 오류가 난다. 값이 맞는지는 창을 만들 때 검사된다",
       notes=[("부르는 순서", "`glfwInit()` 뒤, `glfwCreateWindow()` 앞"),
              ("기억되는 기간", "한 번 정한 힌트는 `glfwDefaultWindowHints()`나 `glfwTerminate()` 전까지 남는다"),
              ("선언된 곳", "`include/GLFW/glfw3.h:3053`")],
       lib="GLFW 3.4"),
    keep(table([36, 26, 38], ["이 강에서 쓰는 힌트", "기본값", "뜻"], [
        ["`GLFW_CONTEXT_VERSION_MAJOR`", "1", "요청할 OpenGL 버전의 앞자리. 4.6이면 4"],
        ["`GLFW_CONTEXT_VERSION_MINOR`", "0", "뒷자리. 4.6이면 6"],
        ["`GLFW_OPENGL_PROFILE`", "`GLFW_OPENGL_ANY_PROFILE`",
         "`GLFW_OPENGL_CORE_PROFILE` 또는 `GLFW_OPENGL_COMPAT_PROFILE`. 3.2 이상을 요청할 때만 고를 수 있다"],
    ], cell_cls=["lab", "", ""])),
    p("**버전**은 “적어도 이만큼”이라는 요청이다. 드라이버가 그 버전을 지원하지 않으면 창 만들기가 실패하고, 지원하면 "
      "그보다 높은 버전의 컨텍스트가 만들어질 수도 있다. **프로필**은 OpenGL 3.2에서 생긴 구분이다. core는 `glBegin`처럼 "
      "오래된 고정 기능을 뺀 것이고 compat는 남겨 둔 것이다. 이 프로젝트의 GLAD는 4.6 core용으로 만들어져 있으므로"
      "(`include/glad/glad.h:7` 〜 `:8`) 같은 것을 요청해야 짝이 맞는다."),
    box("ex", "예시: OpenGL 3.3 core를 요청한다면", [
        code(r"""
glfwWindowHint( GLFW_CONTEXT_VERSION_MAJOR, 3 );
glfwWindowHint( GLFW_CONTEXT_VERSION_MINOR, 3 );
glfwWindowHint( GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE );
""", tag="usage"),
        p("세 줄은 서로 순서를 가리지 않는다. 셋 다 “다음 창”에 대한 메모일 뿐이다. 이 프로젝트가 요청할 버전은 4.6이다."),
    ]),
    fn("glfwCreateWindow",
       "GLFWwindow* glfwCreateWindow(int width, int height, const char* title,\n"
       "                             GLFWmonitor* monitor, GLFWwindow* share);",
       "창 하나와 그 창의 OpenGL 컨텍스트를 함께 만든다. 예약해 둔 힌트가 이때 적용된다.",
       params=[("`width`, `height`", "창 안쪽(그림이 그려지는 영역)의 크기. 화면 좌표 단위이고 0보다 커야 한다"),
               ("`title`", "제목 표시줄에 나올 글자. UTF-8 문자열"),
               ("`monitor`", "전체 화면으로 쓸 모니터. `nullptr`이면 창 모드다"),
               ("`share`", "버퍼나 텍스처 같은 객체를 함께 쓸 다른 창. `nullptr`이면 공유하지 않는다")],
       returns="만든 창을 가리키는 `GLFWwindow*`. 이후 그 창에 관한 모든 GLFW 함수에 이 값을 넘긴다",
       fails="`nullptr`을 돌려준다. 요청한 OpenGL 버전이나 프로필을 드라이버가 만들지 못할 때가 가장 흔하다",
       notes=[("주의", "만든 컨텍스트는 아직 어느 스레드에도 연결되어 있지 않다. 연결은 따로 한다 (5장)"),
              ("짝이 되는 함수", "`glfwDestroyWindow()` (1-4강)"),
              ("선언된 곳", "`include/GLFW/glfw3.h:3235`")],
       lib="GLFW 3.4"),
    box("ex", "예시: 창 모드와 전체 화면", [
        code(r"""
GLFWwindow* a = glfwCreateWindow( 800, 600, "Windowed", nullptr, nullptr );
GLFWwindow* b = glfwCreateWindow( 1920, 1080, "Fullscreen", glfwGetPrimaryMonitor(), nullptr );
""", tag="usage"),
        p("넷째 인자 하나로 갈린다. `glfwGetPrimaryMonitor()`는 주 모니터를 가리키는 값을 돌려준다. 이 강에서는 창 모드만 쓴다."),
    ]),
    p("`GLFWwindow*`는 **핸들**이다. `GLFWwindow`가 어떤 구조체인지는 헤더에 나와 있지 않고, 우리는 그 주소만 받아 들고 "
      "다니다가 GLFW 함수에 다시 넘긴다. 안을 들여다볼 수 없으므로 GLFW는 내부 구조를 마음대로 바꿀 수 있다."),
    box("cs", None,
        "내용을 감춘 포인터를 불투명 포인터(opaque pointer)라고 한다. Windows의 `HWND`, C 표준 라이브러리의 `FILE*`가 "
        "같은 방식이다. 자료구조 책의 추상 자료형(ADT)을 C에서 구현하는 방법이다."),
    box("ue", None,
        "언리얼에서 이 자리는 플랫폼 계층이 맡는다. `FWindowsApplication::MakeWindow`가 운영체제의 창을 만들어 "
        "`FGenericWindow`로 돌려주고, 그 위에 Slate의 `SWindow`가 얹힌다. 게임 코드가 Win32 함수를 직접 부르지 않는 "
        "것은 GLFW를 쓰는 이유와 같다."),
], lead="창을 띄우는 데 쓰는 GLFW 함수는 셋이다. 초기화하고, 조건을 예약하고, 만든다. 함수마다 무엇을 받고 무엇을 "
        "돌려주는지 적었다.")

ch5 = chapter(5, "OpenGL 컨텍스트와 함수 로더", [
    h3("5.1", "컨텍스트"),
    p("OpenGL 컨텍스트는 OpenGL의 모든 상태(배경색, 지금 쓰는 버퍼 등)와 객체가 들어 있는 곳이다. `gl*` 함수에는 "
      "“어느 창에 대고 하는 일인가”를 받는 인자가 없다. 대신 **그 함수를 부른 스레드에 지금 연결되어 있는 컨텍스트**가 "
      "대상이 된다. 그 연결을 “현재 컨텍스트(current context)”라고 부른다."),
    Fig(170)
    .box(20, 16, 130, 50, "스레드", "gl* 함수를 부른다")
    .box(20, 100, 130, 50, "함수 포인터들", "GLAD가 채운 주소")
    .arrow((150, 41), (240, 41), kind="accent")
    .text(195, 33, "현재 컨텍스트", kind="accent", size=9.5)
    .arrow((150, 125), (240, 125))
    .text(195, 117, "호출", kind="s", size=9.5)
    .box(240, 8, 205, 152, kind="soft")
    .text(342, 29, "OpenGL 컨텍스트", kind="t")
    .box(255, 40, 82, 44, "상태", "배경색 · 바인딩")
    .box(347, 40, 82, 44, "객체", "버퍼 · 텍스처")
    .text(342, 112, "드라이버가 구현한", kind="s", size=9.5)
    .text(342, 128, "OpenGL 함수들", kind="s", size=9.5)
    .arrow((445, 84), (520, 84))
    .text(482, 76, "그린다", kind="s", size=9.5)
    .box(520, 8, 122, 152, kind="plain")
    .text(581, 29, "창", kind="t")
    .box(535, 40, 92, 44, "back buffer", "그리는 곳", kind="accent")
    .box(535, 98, 92, 44, "front buffer", "보이는 곳", kind="dark")
    .render("스레드는 컨텍스트 하나에 연결되고, 컨텍스트는 창의 버퍼에 그린다. 컨텍스트 하나는 한 번에 한 스레드에만, "
            "스레드 하나에는 한 번에 한 컨텍스트만 연결된다."),
    fn("glfwMakeContextCurrent", "void glfwMakeContextCurrent(GLFWwindow* window);",
       "그 창의 OpenGL 컨텍스트를, 이 함수를 부른 스레드의 현재 컨텍스트로 만든다.",
       params=[("`window`", "컨텍스트를 연결할 창. `nullptr`을 주면 연결을 푼다")],
       returns="없다",
       fails="컨텍스트 없이 만든 창을 주면 `GLFW_NO_WINDOW_CONTEXT` 오류가 난다",
       notes=[("부르는 순서", "`glfwCreateWindow()` 뒤. 이 호출 전에는 어떤 `gl*` 함수도 대상이 없다"),
              ("선언된 곳", "`include/GLFW/glfw3.h:6109`")],
       lib="GLFW 3.4"),

    h3("5.2", "함수 주소 채우기"),
    fn("gladLoadGLLoader",
       "typedef void* (* GLADloadproc)(const char *name);\n"
       "int gladLoadGLLoader(GLADloadproc load);",
       "OpenGL 함수 수백 개의 주소를 `load`에게 하나씩 물어서 함수 포인터에 채운다 (3.1절).",
       params=[("`load`", "“함수 이름을 주면 그 주소를 돌려주는 함수”. GLFW를 쓸 때는 `glfwGetProcAddress`를 넘긴다. "
                         "타입이 조금 달라서 `(GLADloadproc)`로 형 변환한다")],
       returns="성공하면 0이 아닌 값, 실패하면 0",
       fails="현재 컨텍스트가 없으면 첫 함수의 주소부터 얻지 못해 0을 돌려준다 (`include/glad/glad.c:1807`)",
       notes=[("부르는 순서", "`glfwMakeContextCurrent()` 뒤, 첫 `gl*` 호출 앞"),
              ("끝난 뒤", "`GLVersion.major`와 `GLVersion.minor`에 실제로 얻은 OpenGL 버전이 들어 있다"),
              ("선언된 곳", "`include/glad/glad.h:55`, `:87`")],
       lib="GLAD"),
    fn("glfwGetProcAddress", "GLFWglproc glfwGetProcAddress(const char* procname);",
       "현재 컨텍스트에서 그 이름의 OpenGL 함수가 있는 주소를 돌려준다. 직접 부를 일은 없고 GLAD에게 넘겨준다.",
       params=[("`procname`", "함수 이름. 예: `\"glClear\"`")],
       returns="함수의 주소. 그런 함수가 없으면 `nullptr`",
       fails="현재 컨텍스트가 없으면 `GLFW_NO_CURRENT_CONTEXT` 오류를 내고 `nullptr`을 돌려준다",
       notes=[("선언된 곳", "`include/GLFW/glfw3.h:6290`")],
       lib="GLFW 3.4"),
    box("ex", "예시: 함수 이름을 인자로 넘긴다는 것", [
        code(r"""
void* Lookup( const char* name );      // some function that maps a name to an address

int ok = gladLoadGLLoader( Lookup );   // no parentheses after Lookup: pass the function, do not call it
""", tag="syntax"),
        p("`Lookup` 뒤에 괄호가 없다. 함수를 부른 결과가 아니라 ==함수 자체의 주소==를 넘기는 것이다. GLAD는 받은 주소로 "
          "`Lookup( \"glClear\" )`, `Lookup( \"glViewport\" )` … 를 수백 번 부른다. 이렇게 넘겨주는 함수를 콜백이라고 한다."),
    ]),

    h3("5.3", "첫 gl 호출: 배경색"),
    fn("glClearColor", "void glClearColor(GLfloat red, GLfloat green, GLfloat blue, GLfloat alpha);",
       "화면을 지울 때 칠할 색을 컨텍스트의 상태로 저장한다. 이 호출만으로는 화면이 바뀌지 않는다.",
       params=[("`red`, `green`, `blue`", "색의 세 성분. 0.0(없음)부터 1.0(가득)까지"),
               ("`alpha`", "불투명도. 지금은 1.0을 준다")],
       returns="없다",
       notes=[("값의 범위", "0.0 〜 1.0 밖의 값은 이 범위로 잘린다. 처음 값은 (0, 0, 0, 0)이다"),
              ("쓰이는 때", "나중에 `glClear( GL_COLOR_BUFFER_BIT )`가 불릴 때 (6장)"),
              ("부르는 순서", "`gladLoadGLLoader()`가 성공한 뒤")],
       lib="OpenGL"),
    box("ex", "예시: 색을 숫자로 읽기", [
        table([48, 20, 32], ["호출", "색", "읽는 법"], [
            ["`glClearColor( 0.f, 0.f, 0.f, 1.f )`", "검정", "세 성분이 모두 없다"],
            ["`glClearColor( 1.f, 1.f, 1.f, 1.f )`", "흰색", "세 성분이 모두 가득하다"],
            ["`glClearColor( 0.5f, 0.f, 0.f, 1.f )`", "어두운 빨강", "빨강만 절반"],
            ["`glClearColor( 0.1f, 0.1f, 0.1f, 1.f )`", "아주 어두운 회색", "셋이 같으면 회색이다"],
        ], cell_cls=["lab", "", ""], compact=True),
        p("0 〜 255로 쓰던 색은 255로 나누면 된다. (51, 102, 153)은 (0.2, 0.4, 0.6)이다."),
    ]),
    box("warn", "순서가 정해져 있다",
        "증상: 첫 `gl*` 호출에서 주소 0을 실행하려다 접근 위반으로 죽는다. 함수 포인터가 아직 `nullptr`이기 때문이다. "
        "이 장의 함수 셋은 각자 “부르는 순서” 칸에 앞서야 할 것을 적어 두었다. 그 칸들을 이으면 순서는 하나로 정해진다."),
    box("api", None,
        "DX11에서는 창(HWND), 장치(Device), 스왑 체인이 서로 다른 객체다. 창은 Win32나 GLFW로 만들고 그래픽 쪽은 따로 "
        "만든 뒤 둘을 잇는다. 대상도 인자가 아니라 객체로 정한다(`context->ClearRenderTargetView( … )`). OpenGL의 "
        "“현재 컨텍스트”는 이 API만의 특징이고, 2-1강에서 다시 정면으로 다룬다."),
], lead="창을 만들었다고 바로 그릴 수 있는 것은 아니다. 컨텍스트를 스레드에 연결하고, 함수 주소를 채우는 두 단계가 "
        "더 있다.")

ch6 = chapter(6, "창을 살려 두는 가장 작은 루프", [
    p("`main`이 끝나면 프로세스가 끝나고 창도 사라진다. 창이 화면에 남아 있으려면 프로그램이 끝나지 않고 돌고 있어야 한다. "
      "그리고 돌면서 해야 할 일이 있다. 운영체제는 키 입력, 마우스, 닫기 버튼 같은 일을 프로그램에 **이벤트**로 보내는데, "
      "프로그램이 이것을 받아 가지 않으면 창을 “응답 없음”으로 표시한다."),
    flow([
        ("닫을 때인가", "깃발을 읽는다"),
        ("이벤트 처리", "쌓인 것을 받는다", "accent"),
        ("지우기", "배경색으로"),
        ("내보내기", "화면에", "dark"),
    ], "한 바퀴가 한 프레임이다. 첫 칸에서 “닫을 때”라고 나오면 루프를 빠져나간다."),
    fn("glfwWindowShouldClose", "int glfwWindowShouldClose(GLFWwindow* window);",
       "그 창의 “닫아 달라” 깃발을 읽는다.",
       params=[("`window`", "물어볼 창")],
       returns="깃발이 서 있으면 `GLFW_TRUE`, 아니면 `GLFW_FALSE`",
       notes=[("깃발이 서는 때", "사용자가 닫기 버튼이나 Alt+F4를 눌렀을 때. 그 사실은 이벤트를 처리해야 전달된다"),
              ("주의", "깃발이 서도 창이 저절로 닫히지는 않는다. 닫을지 말지는 프로그램이 정한다"),
              ("선언된 곳", "`include/GLFW/glfw3.h:3284`")],
       lib="GLFW 3.4"),
    fn("glfwPollEvents", "void glfwPollEvents(void);",
       "운영체제가 쌓아 둔 이벤트를 지금 전부 처리하고 바로 돌아온다. 쌓인 것이 없으면 기다리지 않는다.",
       returns="없다",
       notes=[("부르지 않으면", "닫기 깃발이 서지 않고, 운영체제가 창을 “응답 없음”으로 표시한다"),
              ("콜백", "등록해 둔 콜백 함수는 이 호출 안에서 불린다 (1-3강)"),
              ("스레드", "메인 스레드에서만 부른다"),
              ("선언된 곳", "`include/GLFW/glfw3.h:4534`")],
       lib="GLFW 3.4"),
    fn("glClear", "void glClear(GLbitfield mask);",
       "고른 버퍼 전체를 미리 정해 둔 값으로 채운다.",
       params=[("`mask`", "지울 버퍼를 비트로 고른다. `GL_COLOR_BUFFER_BIT`, `GL_DEPTH_BUFFER_BIT`, "
                         "`GL_STENCIL_BUFFER_BIT`를 `|`로 묶을 수 있다")],
       returns="없다",
       notes=[("채우는 값", "색 버퍼는 `glClearColor()`로 정해 둔 색"),
              ("대상", "지금 그리는 쪽 버퍼(back buffer). 화면에 보이는 것은 아직 그대로다")],
       lib="OpenGL"),
    fn("glfwSwapBuffers", "void glfwSwapBuffers(GLFWwindow* window);",
       "그 창의 back buffer와 front buffer를 맞바꾼다. 그려 둔 그림이 이때 화면에 나온다.",
       params=[("`window`", "버퍼를 바꿀 창")],
       returns="없다",
       notes=[("부르지 않으면", "아무리 그려도 화면에 나오지 않는다"),
              ("선언된 곳", "`include/GLFW/glfw3.h:6164`")],
       lib="GLFW 3.4"),
    box("point", "이 루프는 임시다",
        "여기서는 네 함수를 `main` 안에 직접 쓴다. 1-2강에서 이 루프를 엔진 안의 `Run()`으로 옮기고, 프레임 사이의 "
        "시간을 재고, 게임 코드가 끼어들 자리를 만든다. 버퍼가 왜 둘인지(더블 버퍼링)도 그때 자세히 본다."),
], lead="창을 만들고 `Init`이 돌아온 뒤에 할 일이다. 네 함수로 된 짧은 루프가 창을 살려 둔다.")

ch7 = chapter(7, "GEngine 싱글턴", [
    p("엔진 객체는 프로그램에 하나만 있어야 한다. 창도 하나, OpenGL 컨텍스트도 하나이기 때문이다. 그리고 어디서든 닿을 수 "
      "있어야 한다. 이 두 가지를 보장하는 흔한 방법이 싱글턴이고, C++에서는 함수 안의 `static` 지역 변수로 만든다."),
    code(r"""
Counter& TheCounter()
{
    static Counter instance;   // created the first time this line runs, and only once
    return instance;           // every caller gets the same object
}
""", title="a function-local static (the type is an example)", tag="syntax"),
    Fig(232)
    .box(20, 14, 150, 44, "스택", "함수의 지역 변수", kind="soft")
    .box(20, 68, 150, 44, "힙", "실행 중에 받는 메모리", kind="soft")
    .box(20, 122, 150, 44, "정적 저장 영역", "프로그램 내내 산다", kind="accent")
    .box(20, 176, 150, 44, "코드", "함수의 기계어", kind="soft")
    .box(230, 18, 210, 36, "engine", "main의 참조 변수")
    .box(230, 72, 210, 36, "GLFWwindow", "glfwCreateWindow가 만든 것")
    .box(230, 126, 210, 36, "instance", "Get() 안의 static GEngine", kind="accent")
    .box(230, 180, 210, 36, "GEngine::Get · Init", "멤버 함수의 본체")
    .line((170, 36), (230, 36), kind="muted dash")
    .line((170, 90), (230, 90), kind="muted dash")
    .line((170, 144), (230, 144), kind="muted dash")
    .line((170, 198), (230, 198), kind="muted dash")
    .arrow((440, 36), (480, 36), (480, 144), (440, 144), kind="accent")
    .text(490, 94, "가리킨다 (참조)", kind="s", anchor="start", size=9.5)
    .arrow((300, 126), (300, 108))
    .text(308, 121, "_main_window", kind="mono", anchor="start", size=9)
    .render("왼쪽은 프로세스의 메모리 구역이고 오른쪽은 이 강에서 거기 놓이는 것들이다. `static` 지역 변수는 정적 저장 "
            "영역에 하나만 있고, `Get()`은 그 객체의 참조를 돌려준다. 창은 GLFW가 힙에 만들고 엔진은 그 주소만 든다."),
    table([34, 66], ["장치", "막는 것"], [
        ["함수 안의 `static` 지역 변수", "인스턴스가 둘 생기는 일. 처음 `Get()`이 불릴 때 한 번만 만들어진다"],
        ["`private` 생성자", "밖에서 `GEngine e;`로 따로 만드는 일"],
        ["복사 생성자와 대입의 `= delete`", "`GEngine copy = GEngine::Get();`처럼 복사본이 생기는 일"],
    ], cell_cls=["lab", ""]),
    ox(("`GEngine& engine = GEngine::Get();`", "참조로 받는다. 같은 객체에 이름을 하나 더 붙일 뿐이다"),
       ("`GEngine engine = GEngine::Get();`", "복사가 필요해서 컴파일 오류가 나야 한다")),
    p("만들어지는 때는 분명하다. 처음 `Get()`이 불릴 때다. 사라지는 때는 `main`이 끝난 뒤, 정적 객체들이 정리될 때다. "
      "그 시점에는 창이 이미 닫혔을 수도 있으므로 소멸자에서 GLFW나 OpenGL을 부르는 설계는 위험하다. 정리할 것이 "
      "있으면 `main`이 끝나기 전에 명시적으로 부르는 함수가 필요하다. 그 일은 1-4강이다."),
    box("cs", None,
        "전역 변수 대신 함수 안의 `static`을 쓰는 이유가 하나 더 있다. 서로 다른 `.cpp`에 있는 전역 객체들은 초기화 "
        "순서가 정해져 있지 않아서, 한 전역 객체의 생성자가 아직 만들어지지 않은 다른 전역 객체를 쓸 수 있다. "
        "함수 안의 `static`은 “처음 쓰일 때” 만들어지므로 이 문제가 없다. C++11부터는 두 스레드가 동시에 처음 불러도 "
        "한 번만 만들어지도록 보장된다."),
    box("ue", None,
        "언리얼에도 같은 이름의 `GEngine`이 있다. 그쪽은 `UEngine*` 타입의 전역 포인터이고, 엔진이 시작할 때 "
        "채워진다. 어디서든 닿는다는 편리함과, 누가 엔진에 기대고 있는지 코드에서 드러나지 않는다는 단점이 똑같이 있다."),
], lead="엔진 객체는 프로그램에 하나만 있고 어디서든 `GEngine::Get()`으로 닿는다. 세 가지 장치가 이를 보장한다.")

ch8 = chapter(8, "설계", [
    h3("8.1", "파일 배치"),
    tree("""
Engine/
├── Core/
│   ├── EngineCore.h +  #class GEngine
│   └── EngineCore.cpp +  #Get() and Init()
├── framework.h
└── pch.h, pch.cpp
Client/
└── main.cpp  #Get, Init, the temporary loop
"""),
    p("Engine 프로젝트는 자기 폴더를 포함 경로에 넣어 두었다(`Engine/Engine.vcxproj:91`). 그래서 엔진 안에서도, "
      "Client에서도 `#include \"Core/EngineCore.h\"`라고 쓴다."),

    keep(h3("8.2", "이 강에서 하지 않는 것"),
    table([28, 72], ["미루는 것", "이유"], [
        ["실패 확인과 정리", "`glfwInit`, `glfwCreateWindow`의 실패를 다루고 `glfwTerminate`로 끝내는 일은 1-4강이다. "
                      "여기서는 GLAD가 실패했을 때 `Fail`을 돌려주는 것까지만 한다"],
        ["루프, 시간, Update", "6장의 루프는 임시다. 1-2강에서 엔진 안으로 옮긴다"],
        ["키 입력", "1-3강이다. `framework.h`가 포함하는 `InputKeys.h`는 그때 쓴다"],
        ["창 크기가 바뀔 때", "그릴 것이 생기는 2-2강에서 뷰포트와 함께 다룬다. 지금은 지우기만 해서 차이가 보이지 않는다"],
    ], cell_cls=["lab", ""], compact=True)),

    h3("8.3", "선언 스케치"),
    code(r"""
#pragma once

class GEngine
{
public:
    enum class InitErrorCode : int8_t
    {
        Fail    = -1,
        Success = 0
    };

    static GEngine& Get();
    GLFWwindow*     GetMainWindow() const;      // why does main need this in lesson 1-1?

    InitErrorCode Init( GLint version_major, GLint version_minor, int width, int height,
                        const char* title, GLFWmonitor* monitor, GLFWwindow* share );

private:
    // Which special member functions must be private or deleted? (chapter 7)
    GLFWwindow* _main_window = nullptr;         // what does this hold before Init() runs?
};
""", title="Engine/Core/EngineCore.h", tag="sketch"),
    code(r"""
GEngine& engine = GEngine::Get();
auto     result = engine.Init( 4, 6, 1600, 1600, "Claud GL Engine", nullptr, nullptr );

// What should main return when result is not Success?
// Then: the temporary loop of chapter 6, using engine.GetMainWindow()
""", title="Client/main.cpp when this lesson is done", tag="usage"),
    box("point", "이 강에서는 이 모양을 그대로 쓴다",
        "1-2강부터의 자료는 위 선언을 기준으로 쓰여 있다. 이름과 인자를 바꾸면 뒤 자료의 설명과 어긋난다. 바꾸고 싶은 "
        "점은 목록에 적어만 둔다. 실패를 알리는 방식은 1-4강과 1-6강에서 다시 정한다."),
], lead="새로 만드는 파일은 둘이다. 클래스의 모양은 정해져 있고, 본체를 채우는 것이 이 강의 일이다.")

ch9 = chapter(9, "구현 미션", [
    steps([
        ("기준 상태를 빌드한다",
         "아무것도 고치지 않고 Debug|x64로 솔루션을 다시 빌드한다. 성공하고, 실행하면 아무것도 뜨지 않고 바로 끝나면 된다.",
         ["`LNK1104`가 `glfw3.lib`를 가리키면 `lib/Debug/x64/` 폴더에 그 파일이 있는지 본다 (10장)."]),
        ("`GEngine` 클래스와 `Get()`을 만든다",
         "`EngineCore.h`와 `.cpp`를 Engine 프로젝트에 더하고, 8.3절의 선언 중 `Get()`까지만 채운다. `main`에서 "
         "`GEngine::Get()`을 불러 빌드되는지 본다.",
         ["새 `.cpp`의 첫 줄에 무엇이 와야 하는지는 2.4절에 있다.",
          "`Engine/Engine.vcxproj`를 열어 `EngineCore.cpp` 항목이 한 줄인지 확인한다 (10장의 마지막 줄)."]),
        ("복사를 막는다",
         "`main`에 `GEngine copy = GEngine::Get();`을 넣어 컴파일 오류가 나게 만든 뒤 그 줄을 지운다.",
         ["7장 표의 둘째, 셋째 줄이다. 오류 메시지에 `deleted function`이 보이면 된다."]),
        ("`Init`: GLFW를 켜고 창을 만든다",
         "4장의 세 함수로 창을 만들어 `_main_window`에 넣고 `main`에서 `Init`을 부른다. 창이 잠깐 보였다 사라지면 맞다.",
         ["`Init`의 인자 가운데 버전 둘은 힌트로, 나머지 다섯은 순서 그대로 `glfwCreateWindow`로 간다. 힌트는 창을 "
          "만들기 전에 적어 둔다."]),
        ("`Init`: 컨텍스트를 연결하고 GLAD를 채운다",
         "5장의 함수들로 `Init`을 끝낸다. GLAD가 실패하면 `Fail`을, 끝까지 가면 `Success`를 돌려준다. 배경색도 여기서 정한다.",
         ["함수 설명의 “부르는 순서” 칸을 이으면 순서가 하나로 정해진다. 코드를 쓰기 전에 종이에 먼저 적어 본다.",
          "`main`은 `Init`의 결과를 보고, `Success`가 아니면 0이 아닌 값을 돌려주며 끝난다."]),
        ("임시 루프를 쓴다",
         "`main`에서 창이 닫힐 때까지 도는 루프를 6장의 네 함수로 쓴다. 창이 계속 떠 있고 안쪽이 배경색으로 채워지면 된다.",
         ["창을 가리키는 값은 엔진이 들고 있다. `main`이 그것을 얻는 길이 8.3절의 선언에 있다."]),
        ("일부러 틀려 본다",
         "하나씩 해 보고 결과를 적은 뒤 되돌린다. (가) GLAD 로드를 컨텍스트 연결보다 앞에 둔다. (나) 버전을 9.9로 "
         "요청한다. (다) 루프에서 `glfwSwapBuffers`를 뺀다.",
         ["(나)에서는 `_main_window`의 값을 디버거로 본다. 그 뒤의 호출들이 어떻게 되는지가 1-4강의 출발점이다."]),
        ("확인하고 커밋한다", "11장의 기준을 하나씩 확인하고 커밋한다. 그 뒤에 4월의 코드와 비교한다 (11.1절)."),
    ]),
], lead="한 단계가 끝날 때마다 빌드해서 눈으로 확인한다. 힌트는 막혔을 때 위에서부터 하나씩만 본다.", pb=True)

ch10 = chapter(10, "흔한 함정", [
    table([32, 38, 30], ["증상", "원인", "확인 방법"], [
        ["`LNK1104: cannot open file 'glfw3.lib'`", "`lib/Debug/x64/`에 `glfw3.lib`가 없다. 저장소에 올라가지 않는 파일이다",
         "탐색기에서 그 폴더를 본다. 구성이 Debug|x64인지도 본다"],
        ["`C1083: Cannot open include file`", "헤더의 위치나 `#include`에 적은 경로가 틀렸다", "`Client/Client.vcxproj:87`의 두 폴더 기준으로 다시 센다"],
        ["`C1010: unexpected end of file while looking for precompiled header`", "새 `.cpp`의 첫 줄에 `#include \"pch.h\"`가 없다", "2.4절"],
        ["`LNK2019`가 `GEngine`의 함수를 가리킨다", "`EngineCore.cpp`가 Engine 프로젝트에 들어가지 않았거나, Engine을 다시 "
                                          "빌드하지 않았다", "솔루션 전체를 빌드한다. Client만 빌드하면 예전 `ClaudGL.lib`가 링크된다"],
        ["실행하자마자 접근 위반으로 죽는다", "GLAD가 채우기 전에 `gl*` 함수를 불렀다", "호출 스택에서 주소 0을 부른 줄을 찾는다 (5장)"],
        ["창이 떴다가 바로 사라진다", "루프 없이 `main`이 끝났다", "6장"],
        ["창이 “응답 없음”이 된다", "루프가 이벤트를 처리하지 않는다", "`glfwPollEvents`"],
        ["창 안이 검거나 이상한 무늬가 보인다", "지우지 않았거나 버퍼를 내보내지 않았다", "`glClear`와 `glfwSwapBuffers`"],
        ["`.vcxproj`에 새 파일 항목이 수십 줄로 들어갔다", "IDE가 그 파일에만 따로 설정을 써 넣었다. 절대 경로가 들어 있으면 "
                                            "다른 PC에서 빌드가 깨진다", "`<ClCompile Include=\"Core\\EngineCore.cpp\" />` 한 줄이어야 한다"],
    ], compact=True),
], lead="증상에서 거꾸로 찾는 표다.")

ch11 = chapter(11, "완료 기준", [
    checklist([
        "실행하면 제목 표시줄이 있는 창이 뜨고, 안쪽이 `glClearColor`로 정한 색으로 채워진다.",
        "창의 닫기 버튼을 누르면 프로그램이 끝난다.",
        "`Client/`에서 `glfwInit`과 `glfwCreateWindow`가 검색되지 않는다. 창을 만드는 일은 엔진이 맡는다.",
        "`GEngine copy = GEngine::Get();`을 넣으면 컴파일되지 않는다.",
        "`Init` 안의 호출 순서를 왜 그렇게 했는지 한 줄씩 말할 수 있다.",
        "`Engine/Engine.vcxproj`에서 `EngineCore.cpp` 항목이 한 줄이다.",
        "커밋 하나로 묶였다.",
    ]),
    Fig(170)
    .box(170, 8, 320, 154, kind="plain", r=5)
    .box(170, 8, 320, 26, kind="dark", r=5)
    .text(184, 25, "Claud GL Engine", kind="light", anchor="start", size=10)
    .text(474, 26, "×", kind="light", size=12)
    .box(171, 34, 318, 127, kind="accent", r=0)
    .text(330, 102, "배경색으로 채워진 영역", kind="s")
    .render("기대하는 화면. 색과 제목은 정한 대로 나온다."),

    h3("11.1", "끝낸 뒤에: 4월의 코드와 비교한다"),
    code(r"""
git diff first-pass-2026-04 -- Engine/Core/EngineCore.cpp Engine/Core/EngineCore.h Client/main.cpp
""", lang="text", title="run in the repository root", tag="usage"),
    p("태그 `first-pass-2026-04`에는 4월에 쓴 1차 코드가 그대로 있다. 기준을 다 채운 뒤에 위 명령으로 지금 코드와 나란히 "
      "본다. 1차 코드에는 1-2강과 1-3강의 내용(루프, 입력)도 들어 있으니 `Init`과 `Get`만 비교한다. 다른 곳이 왜 다른지 "
      "설명할 수 있으면 된다. 1차 코드를 줄 단위로 해설한 자료가 `ClaudGL_1-1_ProjectAndWindow_v2.pdf`다."),
], lead="전부 눈이나 검색으로 확인할 수 있는 조건이다.")

ch12 = chapter(12, "생각해 볼 질문", [
    exgroup("A", "코드를 보지 않고 답하시오", "한두 문장으로, 이유까지"),
    qlist([
        "`Client.exe`를 다른 PC로 옮길 때 `ClaudGL.lib`와 `glfw3.lib`도 함께 옮겨야 하는가?",
        "`Client/Client.vcxproj:144`에서 `ClaudGL.lib`를 지워도 링크가 되는 이유는 무엇인가?",
        "Engine 프로젝트에서 선언만 있고 본체가 없는 함수를 불렀는데 Engine 빌드는 성공했다. 오류는 언제, 어디서 나오는가?",
        "`gladLoadGLLoader`를 `glfwMakeContextCurrent`보다 먼저 부르면 `Init`은 어떻게 끝나는가?",
        "`glClearColor`는 왜 창이나 컨텍스트를 인자로 받지 않는가?",
        "임시 루프에서 `glfwPollEvents()`를 빼면 닫기 버튼을 눌렀을 때 무슨 일이 일어나는가?",
    ], lines=3),
], lead="답을 보기 전에 소리 내어 설명해 본다. 막히는 문항이 다시 읽을 장이다.", pb=True)

ch13 = chapter(13, "해설", [
    answers("질문 A", [
        ("옮기지 않아도 된다.",
         "정적 라이브러리의 내용은 링크할 때 `Client.exe` 안으로 복사되었다. `.lib` 파일은 빌드할 때만 필요하다. (2.1절, 2.2절)"),
        ("`Client/pch.h:3`의 `#pragma comment(lib, \"ClaudGL.lib\")`가 같은 지정을 한 번 더 하고 있기 때문이다.",
         "라이브러리 폴더 경로(`:88`)는 여전히 필요하다. (2.3절)"),
        ("Client를 링크할 때, `LNK2019`로 나온다.",
         "정적 라이브러리는 `.obj`를 묶기만 하고 링크하지 않는다. 이름의 본체를 찾는 일은 실행 파일을 만들 때 "
         "처음 일어난다. (2.1절)"),
        ("GLAD가 0을 돌려주고, `Init`은 `Fail`을 돌려준다.",
         "연결된 컨텍스트가 없으면 `glfwGetProcAddress`가 주소 대신 `nullptr`을 준다. GLAD는 첫 함수부터 얻지 못해 "
         "바로 실패한다. (5.2절)"),
        ("현재 스레드에 연결된 컨텍스트가 대상이기 때문이다.",
         "OpenGL은 “지금 연결된 것”에 대고 일하는 상태 기계다. 2-1강에서 이 성질을 정면으로 다룬다. (5.1절)"),
        ("아무 일도 일어나지 않고, 곧 창이 “응답 없음”이 된다.",
         "닫기 버튼을 눌렀다는 사실은 이벤트로 온다. 이벤트를 처리하지 않으면 닫기 깃발이 서지 않아 "
         "`glfwWindowShouldClose`가 계속 `GLFW_FALSE`를 돌려준다. (6장)"),
    ]),
])

ch14 = glossary_chapter(14, [
    ("번역 단위", "translation unit", "컴파일러가 한 번에 보는 단위. `.cpp` 하나와 그것이 포함한 헤더 전부"),
    ("목적 파일", "object file, .obj", "번역 단위 하나를 컴파일한 결과. 아직 실행할 수 없다"),
    ("링크", "link", "목적 파일과 라이브러리를 모아 이름마다 본체를 이어 붙이는 일"),
    ("정적 라이브러리", "static library, .lib", "목적 파일을 한 파일로 묶은 것. 링크할 때 실행 파일 안으로 복사된다"),
    ("미리 컴파일된 헤더", "precompiled header, pch", "자주 쓰는 헤더를 한 번만 컴파일해 저장해 둔 것"),
    ("핸들", "handle, opaque pointer", "내용은 감추고 가리키는 값만 주고받는 방식. `GLFWwindow*`"),
    ("컨텍스트", "OpenGL context", "OpenGL의 상태와 객체가 들어 있는 곳. 스레드에 연결해서 쓴다"),
    ("현재 컨텍스트", "current context", "지금 이 스레드에 연결되어 있어 `gl*` 호출의 대상이 되는 컨텍스트"),
    ("프로필", "core / compatibility profile", "OpenGL 3.2부터의 구분. core는 오래된 기능을 뺀 것"),
    ("함수 로더", "function loader", "드라이버에 있는 OpenGL 함수의 주소를 실행 중에 찾아 채우는 것. GLAD"),
    ("함수 포인터", "function pointer", "함수의 주소를 담는 변수. 그 주소로 함수를 부를 수 있다"),
    ("콜백", "callback", "다른 코드가 나중에 불러 주도록 넘겨주는 함수"),
    ("이벤트", "event", "키 입력, 닫기 버튼처럼 운영체제가 프로그램에 알려 주는 일"),
    ("싱글턴", "singleton", "프로그램에 인스턴스가 하나뿐이도록 만든 클래스"),
    ("정적 저장 영역", "static storage", "프로그램이 시작할 때부터 끝날 때까지 살아 있는 변수가 놓이는 곳"),
], pb=True)

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
