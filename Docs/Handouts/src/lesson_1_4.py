"""Lesson 1-4 -- init failure and shutdown (mission-style handout, lecture format).

The engine code this lesson works on is written by Claud in lessons 1-1 to 1-3,
so the handout points at it by function name, never by line number.

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

# Library headers (include/GLFW, include/glad) and project files were read on this day.
READ_DATE = "2026-11-16"

CHECK_HEADER = ["확인할 것", "볼 자리", "왜 문제인가"]

COVER = cover(
    f"CLAUDGL ENGINE · PART {ME['part']} · {ME['id']} · v{ME['ver']}",
    Raw('Init · <span class="ac">Shutdown</span>'),
    ME["title"],
    "실패하면 이유를 말하고, 끝날 때는 만든 것을 치운다",
    [
        ("목표 결과물", "`Init`이 실패하면 원인이 보이고 0이 아닌 종료 코드로 끝난다. 창을 닫으면 창과 GLFW가 해제된다"),
        ("핵심 개념", "실패 확인과 보고 · 반쯤 된 초기화 되돌리기 · 종료 경로와 순서 · 자원의 주인 · 값 초기화"),
        ("선수 지식", "1-1 〜 1-3강을 끝낸 네 코드. 1-5강(Logger)은 먼저 끝냈어도, 아직이어도 된다 (2.3절)"),
        ("예상 시간", f"읽기 1시간 + 구현 2시간 남짓 (계획서 기준 {ME['hours']}시간). 6.4절의 작은 정리는 따로 1 〜 2시간"),
        ("건드릴 파일", "`Engine/Core/EngineCore.h`·`.cpp`, `Engine/Manager/InputManager.h`·`.cpp`, `Client/main.cpp`"),
        ("코드 기준", f"1-1 〜 1-3강을 끝낸 뒤 네가 가진 코드. 라이브러리 헤더와 프로젝트 설정은 {READ_DATE}에 읽음"),
    ],
    note=("읽는 법",
          "엔진 코드는 네가 직접 쓴 것이라 줄 번호 대신 함수 이름(`Init`, `Run`, `main`)으로 가리킨다. “네 코드에서 확인할 것” "
          "표를 네 코드와 맞춰 보는 일이 첫 미션이다. 2 〜 5장이 개념과 함수 설명이고, 6장에서 모양을 정한 뒤 7장의 "
          "미션을 순서대로 한다. 코드 블록은 완성본이 아니다."),
    toc=["왜 필요한가", "초기화는 실패할 수 있다", "반쯤 된 초기화 되돌리기", "종료 경로", "자원의 주인과 값 초기화",
         "설계", "구현 미션", "흔한 함정", "완료 기준", "생각해 볼 질문", "해설", "용어집"],
)

# --------------------------------------------------------------------------
# figures
# --------------------------------------------------------------------------

FIG_FAIL = (
    Fig(184)
    .box(20, 6, 150, 42, "glfwInit()", "GLFW를 켠다")
    .arrow((170, 27), (215, 27))
    .box(215, 6, 170, 42, "glfwCreateWindow()", "창과 컨텍스트를 만든다")
    .arrow((385, 27), (430, 27))
    .box(430, 6, 170, 42, "gladLoadGLLoader()", "GL 함수 주소를 채운다")
    .arrow((600, 27), (648, 27))
    .text(624, 19, "성공", kind="s", size=9.5)
    .arrow((95, 48), (95, 76), kind="muted")
    .text(103, 66, "실패", kind="s", anchor="start", size=9.5)
    .arrow((300, 48), (300, 76), kind="muted")
    .text(308, 66, "실패", kind="s", anchor="start", size=9.5)
    .arrow((515, 48), (515, 76), kind="accent")
    .text(523, 66, "실패", kind="accent", anchor="start", size=9.5)
    .box(20, 76, 150, 42, "GLFW_FALSE", "반환값을 버린다", kind="ghost")
    .box(215, 76, 170, 42, "nullptr", "검사 없이 _main_window에", kind="ghost")
    .box(430, 76, 170, 42, "0", "하나뿐인 확인", kind="accent")
    .arrow((170, 97), (215, 97), kind="muted dash")
    .arrow((385, 97), (430, 97), kind="muted dash")
    .arrow((515, 118), (515, 142), kind="accent")
    .box(430, 142, 170, 38, "return Fail", "main이 받는 값은 하나", kind="dark")
    .text(20, 156, "앞의 두 실패는 멈추는 곳이 없어 점선을 따라 흘러간다.", kind="s", anchor="start", size=10)
    .text(20, 173, "셋 중 무엇이 실패했든 main에는 같은 Fail이 간다.", kind="s", anchor="start", size=10)
    .render("윗줄이 `Init`이 차례로 부르는 호출이다. 실패할 수 있는 곳은 셋인데 확인하는 곳은 하나다.")
)

FIG_LADDER = (
    Fig(222)
    .text(20, 12, "Init의 단계", kind="s", anchor="start", size=9.5)
    .text(300, 12, "여기서 실패하면 이미 만들어져 있는 것", kind="s", anchor="start", size=9.5)
    .text(500, 12, "되돌리는 순서", kind="s", anchor="start", size=9.5)
    .box(20, 20, 150, 36, "1  GLFW 초기화")
    .arrow((60, 56), (60, 72))
    .box(46, 72, 150, 36, "2  창과 컨텍스트")
    .arrow((86, 108), (86, 124))
    .box(72, 124, 150, 36, "3  GL 함수 주소", kind="accent")
    .arrow((112, 160), (112, 176), kind="muted")
    .box(98, 176, 150, 36, "4  뒤에 더할 단계", kind="ghost")
    .arrow((170, 38), (288, 38), kind="muted dash")
    .text(300, 42, "없다", kind="s", anchor="start", size=10)
    .text(500, 42, "GLFW가 스스로 정리했다", kind="s", anchor="start", size=9.5)
    .arrow((196, 90), (288, 90), kind="muted dash")
    .box(300, 78, 56, 24, "GLFW", kind="soft", r=4)
    .text(500, 94, "glfwTerminate()", kind="mono", anchor="start", size=9.5)
    .arrow((222, 142), (288, 142), kind="accent dash")
    .box(300, 130, 56, 24, "GLFW", kind="soft", r=4)
    .box(362, 130, 56, 24, "창", kind="soft", r=4)
    .text(500, 139, "glfwDestroyWindow()", kind="mono", anchor="start", size=9.5)
    .text(500, 153, "glfwTerminate()", kind="mono", anchor="start", size=9.5)
    .arrow((248, 194), (288, 194), kind="muted dash")
    .box(300, 182, 56, 24, "GLFW", kind="soft", r=4)
    .box(362, 182, 56, 24, "창", kind="soft", r=4)
    .box(424, 182, 62, 24, "GL 주소", kind="plain", r=4)
    .text(500, 191, "glfwDestroyWindow()", kind="mono", anchor="start", size=9.5)
    .text(500, 205, "glfwTerminate()", kind="mono", anchor="start", size=9.5)
    .render("아래 단계에서 실패할수록 이미 만들어진 것이 많다. 되돌리는 순서는 늘 만든 순서의 반대다. "
            "GL 함수 주소는 되돌릴 것이 없어서 넷째 줄의 호출은 셋째 줄과 같다.")
)

FIG_ORDER = (
    Fig(236)
    .text(135, 14, "Init: 위에서 아래로 만든다", kind="t", size=10.5)
    .text(525, 14, "Shutdown: 아래에서 위로 되돌린다", kind="t", size=10.5)
    .box(30, 24, 210, 38, "glfwInit()", "GLFW 라이브러리 상태")
    .box(30, 78, 210, 38, "glfwCreateWindow()", "창과 GL 컨텍스트")
    .box(30, 132, 210, 38, "gladLoadGLLoader()", "GL 함수 포인터")
    .box(30, 186, 210, 38, "그 뒤에 만든 것", "입력 관리자, 콜백, 뒤에는 GL 객체")
    .arrow((135, 62), (135, 78))
    .arrow((135, 116), (135, 132))
    .arrow((135, 170), (135, 186))
    .box(420, 24, 210, 38, "glfwTerminate()", "맨 마지막", kind="dark")
    .box(420, 78, 210, 38, "glfwDestroyWindow()", "컨텍스트도 함께 사라진다")
    .box(420, 132, 210, 38, "되돌릴 것 없음", kind="ghost")
    .box(420, 186, 210, 38, "가장 먼저 되돌린다", "창과 컨텍스트가 살아 있을 때", kind="accent")
    .arrow((525, 186), (525, 170), kind="accent")
    .arrow((525, 132), (525, 116), kind="accent")
    .arrow((525, 78), (525, 62), kind="accent")
    .line((240, 43), (420, 43), kind="muted dash")
    .line((240, 97), (420, 97), kind="muted dash")
    .line((240, 151), (420, 151), kind="muted dash")
    .text(330, 37, "짝", kind="s", size=9.5)
    .text(330, 91, "짝", kind="s", size=9.5)
    .arrow((240, 205), (420, 205), kind="accent")
    .text(330, 197, "Run()이 끝난 뒤", kind="accent", size=9.5)
    .render("같은 높이에 있는 것이 서로 짝이다. 나중에 만든 것이 먼저 만든 것에 기대므로, 기대는 쪽부터 되돌린다.")
)

FIG_OWNER = (
    Fig(172)
    .text(20, 16, "날 포인터", kind="t", anchor="start")
    .box(20, 28, 150, 96, kind="soft")
    .text(95, 48, "GEngine", kind="t")
    .box(32, 62, 126, 44, "_main_window", "GLFWwindow* (주소만)")
    .arrow((158, 84), (212, 84))
    .box(212, 60, 96, 48, "창", "GLFW가 만든 것")
    .text(20, 146, "GEngine이 사라져도 창은 남는다.", kind="s", anchor="start", size=10)
    .text(20, 162, "놓는 호출을 직접 적어야 하고, 순서도 직접 쥔다.", kind="s", anchor="start", size=10)
    .line((330, 8), (330, 166), kind="muted dash")
    .text(350, 16, "unique_ptr와 삭제자", kind="t", anchor="start")
    .box(350, 28, 150, 96, kind="soft")
    .text(425, 48, "GEngine", kind="t")
    .box(362, 62, 126, 44, "unique_ptr", "주소 + 놓는 방법", kind="accent")
    .arrow((488, 84), (542, 84), kind="accent")
    .box(542, 60, 96, 48, "창", "GLFW가 만든 것")
    .text(350, 146, "unique_ptr가 사라지거나 비워질 때 삭제자가 불린다.", kind="s", anchor="start", size=10)
    .text(350, 162, "삭제자가 glfwDestroyWindow를 부른다.", kind="s", anchor="start", size=10)
    .render("왼쪽은 주인이라는 사실이 코드에 적혀 있지 않다. 오른쪽은 타입에 적혀 있다. 6.2절의 여섯째 결정이 이 둘 사이의 선택이다.")
)

# --------------------------------------------------------------------------

ch1 = chapter(1, "왜 필요한가", [
    h3("1.1", "실패해도 계속 간다"),
    p("1-1강에서 쓴 `Init`은 GLFW를 켜고, 창을 만들고, 컨텍스트를 연결하고, GLAD로 함수 주소를 채운다. 이 가운데 "
      "실패할 수 있는 호출이 셋인데 1-1강은 마지막 하나만 확인하게 했다 (1-1강 8.2절). 네 코드가 실제로 어떤지부터 본다."),
    keep(h4("네 코드에서 확인할 것"),
    table([33, 27, 40], CHECK_HEADER, [
        ["`glfwInit()`의 반환값을 받는가", "`GEngine::Init`의 첫 GLFW 호출", "버리고 있다면 GLFW 초기화가 실패해도 다음 줄로 간다"],
        ["`glfwCreateWindow()`의 결과를 검사하는가", "`Init`에서 `_main_window`에 넣는 줄",
         "드라이버가 요청한 버전을 지원하지 않으면 `nullptr`이다. 검사가 없으면 그 값이 다음 호출로 넘어간다"],
        ["GLAD가 실패한 분기에서 무엇을 하는가", "`Init`의 `gladLoadGLLoader` 분기",
         "`Fail`만 돌려준다면 이유가 남지 않는다. 이미 만든 창과 GLFW도 그대로 두고 나간다"],
    ], cell_cls=["lab", "", ""])),

    h3("1.2", "끝나도 치우지 않는다"),
    keep(h4("네 코드에서 확인할 것"),
    table([33, 27, 40], CHECK_HEADER, [
        ["`Run()`이 돌아온 뒤 무엇을 하는가", "`main`의 `engine.Run()` 다음 줄",
         "바로 `main`이 끝난다면 창과 GLFW를 되돌리는 코드가 지나갈 자리가 없다"],
        ["`glfwDestroyWindow`, `glfwTerminate`를 부르는 곳이 있는가", "`Engine/`과 `Client/` 전체 검색",
         "한 곳도 없다면 엔진에 끝내는 절차가 없는 것이다"],
        ["`Init`이 실패했을 때 화면에 무엇이 보이는가", "`main`에서 `Init`의 결과를 보는 분기",
         "0이 아닌 값을 돌려주고 끝날 뿐이라면, 왜 끝났는지는 어디에도 찍히지 않는다"],
    ], cell_cls=["lab", "", ""])),
    p("프로세스가 끝나면 운영체제가 메모리, 창, 핸들을 회수한다. 그래서 지금은 눈에 보이는 문제가 없다. 그래도 "
      "정리 코드를 두는 이유는 셋이다."),
    ul([
        "**운영체제가 대신 해 주지 않는 일이 있다.** 버퍼에 남은 로그를 파일로 내보내는 일(1-5강), 바꿔 둔 감마를 "
        "되돌리는 일(`glfwTerminate`가 한다. 4.2절), 나중에는 설정과 저장 데이터를 쓰는 일이다.",
        "**순서가 필요한 자원이 곧 생긴다.** Part 2부터 만드는 GL 객체는 컨텍스트가 살아 있을 때 지워야 한다. "
        "순서를 지키는 자리를 지금 만들어 둔다.",
        "**프로세스가 끝나지 않고 엔진만 다시 시작하는 경우가 있다.** 에디터의 Play·Stop, 그래픽 장치를 잃었을 때의 "
        "재생성이 그렇다. 그때는 운영체제가 치워 주지 않는다.",
    ]),

    keep(h3("1.3", "앞 강에서 넘어온 것"),
    p("1-1 〜 1-3강은 한 번에 한 주제만 다루려고 몇 가지를 일부러 남겨 두었다. 이 강이 그것을 받는다."),
    table([18, 60, 22], ["어디서", "남겨 둔 것", "이 자료에서"], [
        ["1-1강", "`glfwInit`과 `glfwCreateWindow`의 결과를 확인하지 않는다", "2장"],
        ["1-1강", "GLAD가 실패하면 창과 GLFW를 둔 채 나간다", "3장"],
        ["1-2강", "첫 프레임의 dt, dt의 상한, 수직 동기", "6.4절"],
        ["1-3강", "입력 상태 배열 둘에 초기값이 없다", "5.3절"],
        ["1-3강", "콜백의 범위 검사, “지금 눌려 있는가”, 조회 함수의 `const`", "6.4절"],
        ["프로젝트 설정", "Release의 링크 입력, 프로젝트 참조", "6.4절"],
    ], cell_cls=["lab", "", "c"], compact=True)),
    p("종료 요청과 루프 뒤의 정리(4장)는 이 강에서 처음 만든다. 6.4절로 간 항목은 미션 8에서 다룬다."),
], lead="1-1강의 `Init`은 실패할 수 있는 호출 셋 중 하나만 확인하고, 엔진에는 끝내는 절차가 없다. 일부러 남겨 둔 "
        "자리이고 이 강이 그 자리를 채운다.")

ch2 = chapter(2, "초기화는 실패할 수 있다", [
    h3("2.1", "세 호출이 실패를 알리는 방법"),
    table([24, 24, 52], ["호출", "실패하면", "언제 실패하는가"], [
        ["`glfwInit()`", "`GLFW_FALSE`를 돌려준다", "창 시스템을 쓸 수 없는 환경. 실패하면 GLFW가 스스로 정리까지 하고 돌아온다"],
        ["`glfwCreateWindow()`", "`nullptr`을 돌려준다",
         "요청한 OpenGL 버전·프로필을 드라이버가 지원하지 않을 때가 가장 흔하다. 힌트 값이 잘못됐을 때도 그렇다"],
        ["`gladLoadGLLoader()`", "`0`을 돌려준다", "현재 컨텍스트가 없거나, GL 버전 문자열을 읽지 못했을 때"],
    ], cell_cls=["lab", "", ""]),
    p("셋 다 반환값으로 알린다. C API라서 예외는 없다. 확인하지 않으면 실패는 조용히 다음 줄로 넘어간다. 세 함수의 "
      "설명 카드는 1-1강 4장과 5.2절에 있다."),

    h3("2.2", "확인하지 않은 실패가 흘러가는 길"),
    FIG_FAIL,
    ul([
        "**`glfwInit`이 실패하면** 그 뒤의 GLFW 호출(`glfwWindowHint`, `glfwCreateWindow`, `glfwMakeContextCurrent`, "
        "`glfwGetProcAddress`)은 전부 `GLFW_NOT_INITIALIZED` 오류를 내고 아무 일도 하지 않는다. 창은 `nullptr`이 된다.",
        "**`glfwCreateWindow`만 실패해도** `_main_window`는 `nullptr`이다. 현재 컨텍스트가 없으니 `glfwGetProcAddress`가 "
        "`GLFW_NO_CURRENT_CONTEXT` 오류를 내고 함수 주소 대신 `nullptr`을 돌려준다.",
        "**어느 쪽이든** GLAD는 첫 함수(`glGetString`)의 주소를 얻지 못하면 바로 0을 돌려준다"
        "(`include/glad/glad.c:1806` 〜 `:1807`). 그래서 하나뿐인 확인에 걸려 `Fail`이 나간다.",
    ]),
    p("결과적으로 서로 다른 세 가지 실패가 `main`에는 똑같은 값 하나로 보인다. 이 흐름은 GLFW 헤더의 설명과 glad 소스를 "
      "따라 읽은 것이고 실행해서 확인하지는 않았다. 1-1강에서 9.9를 요청해 보았을 때 본 것과 맞는지 비교해 본다. "
      "`main`이 `Init`의 결과를 보지 않고 `Run()`을 부른다면 더 나쁘다. 루프 조건의 `glfwWindowShouldClose`에 "
      "`nullptr`이 넘어간다."),

    h3("2.3", "GLFW가 이유를 알려 주는 통로"),
    p("반환값은 “실패했다”까지만 말한다. `nullptr`은 왜 `nullptr`인지 말하지 않는다. GLFW는 이유를 알려 주는 통로를 "
      "따로 둘 가지고 있다. 오류가 나는 순간 불러 주는 **오류 콜백**과, 나중에 직접 물어보는 `glfwGetError`다."),
    fn("glfwSetErrorCallback",
       "typedef void (* GLFWerrorfun)(int error_code, const char* description);\n"
       "GLFWerrorfun glfwSetErrorCallback(GLFWerrorfun callback);",
       "오류 콜백을 단다. 그 뒤로 GLFW 함수가 오류를 낼 때마다 이 함수가 오류 코드와 설명 문장을 들고 불린다.",
       params=[("`callback`", "오류가 날 때마다 불릴 함수. 첫 줄의 `GLFWerrorfun` 모양이어야 한다. `nullptr`을 주면 "
                              "달아 둔 콜백을 뗀다"),
               ("콜백의 `error_code`", "오류의 종류를 나타내는 숫자. 아래 표의 상수들이다"),
               ("콜백의 `description`", "사람이 읽을 설명. UTF-8 문자열이고 콜백이 돌아갈 때까지만 유효하다. 나중에 "
                                       "쓰려면 포인터가 아니라 내용을 복사해 둔다")],
       returns="전에 달려 있던 콜백. 없었으면 `nullptr`. 이 함수 자체는 오류를 내지 않는다",
       notes=[("부르는 순서", "`glfwInit()`보다 먼저 불러도 되는 몇 안 되는 함수다. 먼저 달아야 초기화 실패의 이유를 받는다"),
              ("콜백이 불리는 때", "GLFW 함수가 오류를 낸 그 자리에서, 그 함수가 실패를 돌려주기 전에 불린다"),
              ("남는 기간", "한 번 달면 `glfwTerminate()` 뒤에도 달려 있다"),
              ("선언된 곳", "`include/GLFW/glfw3.h:1590` (콜백 타입), `:2503`")],
       lib="GLFW 3.4"),
    fn("glfwGetError", "int glfwGetError(const char** description);",
       "이 스레드에서 마지막으로 난 오류의 코드를 돌려주고, 그 기록을 지운다.",
       params=[("`description`", "설명 문자열의 주소를 받아 갈 변수의 주소. 설명이 필요 없으면 `nullptr`을 준다")],
       returns="마지막 오류 코드. 지난번에 물어본 뒤로 오류가 없었으면 `GLFW_NO_ERROR`(0)이고, 설명 포인터에는 "
               "`nullptr`이 들어간다. 이 함수 자체는 오류를 내지 않는다",
       notes=[("주의", "한 번 읽으면 지워진다. 같은 오류를 두 번 읽을 수 없다. 받은 문자열은 GLFW의 것이라 직접 해제하지 "
                       "않으며, 다음 오류가 나거나 `glfwTerminate()`가 불릴 때까지만 유효하다"),
              ("선언된 곳", "`include/GLFW/glfw3.h:2457`. `glfwInit()` 전에도 부를 수 있다. GLFW 3.3에서 생겼다")],
       lib="GLFW 3.4"),
    keep(table([22, 39, 39], ["", "오류 콜백", "`glfwGetError`"], [
        ["언제 알게 되나", "오류가 난 그 자리에서", "내가 물어볼 때"],
        ["놓치는 경우", "콜백을 달기 전에 난 오류", "묻기 전에 다른 오류가 또 났을 때. 마지막 하나만 남는다"],
        ["어울리는 자리", "모든 GLFW 오류를 한 곳에서 찍기", "방금 실패한 호출의 이유를 값으로 받아 판단하기"],
    ], cell_cls=["lab", "", ""], compact=True)),
    keep(table([36, 20, 44], ["오류 코드", "값", "이 강에서 볼 만한 경우"], [
        ["`GLFW_NOT_INITIALIZED`", "`0x00010001`", "`glfwInit()` 전이나 `glfwTerminate()` 뒤에 GLFW 함수를 불렀다"],
        ["`GLFW_NO_CURRENT_CONTEXT`", "`0x00010002`", "컨텍스트 없이 `glfwGetProcAddress`, `glfwSwapInterval`을 불렀다"],
        ["`GLFW_INVALID_VALUE`", "`0x00010004`", "있을 수 없는 버전(예: 3.9)을 힌트로 주었다"],
        ["`GLFW_VERSION_UNAVAILABLE`", "`0x00010007`", "요청한 버전을 드라이버가 만들지 못한다"],
        ["`GLFW_PLATFORM_ERROR`", "`0x00010008`", "운영체제나 드라이버 쪽에서 난 오류"],
    ], cell_cls=["lab", "c", ""], compact=True),
    p("다섯 상수는 `include/GLFW/glfw3.h:681` 〜 `:762`에 설명과 함께 정의되어 있다.")),
    box("ex", "예시: OpenGL 3.9를 요청했을 때 콜백이 받는 것", [
        p("OpenGL 3.x는 3.3에서 끝났다. 3.9는 있었던 적이 없는 버전이다. 힌트로 3과 9를 주고 `glfwCreateWindow`를 부르면 "
          "GLFW가 드라이버에 묻기 전에 값을 거르고, 콜백을 부른 다음 `nullptr`을 돌려준다. 콜백이 받은 두 인자를 찍으면 이렇다."),
        console(Raw('<span class="err">GLFW error 0x00010004</span>: Invalid OpenGL version 3.9'),
                title="출력 (찍는 형식과 설명 문구는 예시)"),
        p("앞의 숫자가 `error_code`(표의 `GLFW_INVALID_VALUE`)이고 뒤의 문장이 `description`이다. 문장은 GLFW 버전에 따라 "
          "달라질 수 있으므로 코드에서 오류를 가릴 때는 숫자를 쓴다. 미션에서 쓸 9.9는 다르게 온다. 앞으로 나올 버전일 "
          "수도 있어서 GLFW가 거르지 못하고 `GLFW_VERSION_UNAVAILABLE`이 된다 (`include/GLFW/glfw3.h:746` 〜 `:749`)."),
    ]),
    p("받은 이유를 어디에 찍는가는 지금 가진 수단에 달렸다. 1-5강을 먼저 끝냈다면 로그 매크로를 쓴다. 아직이면 "
      "`std::cerr`로 찍어 두고 1-5강에서 바꾼다. `std::cerr`는 쓸 때마다 바로 내보내는 스트림이라, 찍은 직후에 "
      "프로그램이 죽어도 글자가 남는다."),

    h3("2.4", "호출한 쪽에 알리기"),
    p("이유를 찍는 것과 별개로, `Init`을 부른 `main`은 성공인지 실패인지 알아야 다음 행동을 정할 수 있다. 1-1강 "
      "8.3절의 선언은 이 일을 열거형으로 한다."),
    code(r"""
enum class InitErrorCode : int8_t
{
    Fail    = -1,       // Which of the three steps failed? The caller cannot tell.
    Success = 0
};
""", title="Engine/Core/EngineCore.h — the shape from lesson 1-1", tag="sketch"),
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
    p("반환값으로 알리는 방식의 약점은 호출한 쪽이 안 볼 수 있다는 것이다. `glfwInit();`처럼 결과를 버리는 줄이 바로 "
      "그 예다. `[[nodiscard]]`(C++17)를 붙인 함수는 반환값을 버리면 컴파일러가 경고한다. 함수가 아니라 열거형이나 "
      "클래스의 선언에 붙일 수도 있다. 그러면 그 타입을 돌려주는 모든 함수에 적용된다."),
    p("`main`의 반환값은 프로세스의 종료 코드가 된다. 0은 성공, 0이 아니면 실패라는 약속이고 `<cstdlib>`에 "
      "`EXIT_SUCCESS`(0)와 `EXIT_FAILURE`(1)가 있다."),
    box("ex", "예시: 종료 코드를 읽는 법", [
        p("`main`이 3을 돌려주는 `Demo.exe`가 있다고 하자. 그 값은 프로세스가 끝난 뒤에도 운영체제에 남아서, 프로그램을 "
          "실행시킨 쪽이 읽을 수 있다."),
        console(Raw(
            '<span class="dim">Visual Studio의 출력 창, 실행이 끝났을 때</span>\n'
            "The program '[9412] Demo.exe' has exited with code 3 (0x3).\n"
            '<span class="dim">명령 프롬프트에서 직접 실행한 뒤</span>\n'
            "&gt; Demo.exe\n"
            "&gt; echo %ERRORLEVEL%\n"
            "3"
        ), title="종료 코드가 보이는 곳 (형식은 예시)"),
        p("숫자의 뜻은 프로그램이 정한다. 약속은 0과 0 아닌 것의 구분뿐이다. 빌드 스크립트나 배치 파일은 이 값을 보고 "
          "다음 단계로 갈지 멈출지 정한다. `-1`을 돌려주면 같은 줄이 `code -1 (0xffffffff)`로 찍힌다. 종료 코드가 "
          "32비트 값이라 `-1`의 비트가 그대로 보이는 것이다. 헷갈리지 않으려면 작은 양수를 쓴다."),
    ]),
    box("api", None,
        "어느 API든 초기화는 실패할 수 있고 알리는 방법만 다르다. DX11·DX12는 `HRESULT`를 돌려주고(`FAILED( hr )`로 "
        "확인), Vulkan은 `VkResult`를 돌려준다. 이유를 자세히 듣는 통로도 따로 있다. DX의 디버그 레이어와 Vulkan의 "
        "검증 레이어가 GLFW의 오류 콜백과 같은 자리다."),
], lead="초기화의 세 호출은 모두 실패할 수 있다. 실패를 알아차리는 일, 이유를 얻는 일, 호출한 쪽에 전하는 일을 차례로 본다.")

ch3 = chapter(3, "반쯤 된 초기화 되돌리기", [
    p("`Init`은 여러 단계를 차례로 밟는다. 셋째 단계에서 실패하면 첫째와 둘째는 이미 끝나 있다. GLAD가 실패한 순간에는 "
      "GLFW가 초기화되어 있고 창도 떠 있다. 실패를 돌려주기 전에 이것들을 되돌려야 `Init`이 “전부 됐거나, 아무것도 "
      "안 했거나” 둘 중 하나가 된다."),
    FIG_LADDER,
    p("그림의 오른쪽 칸을 실패 분기마다 그대로 옮겨 적으면 아래와 같은 코드가 된다. 단계가 하나 늘 때마다 모든 분기를 "
      "다시 손봐야 한다."),
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
    box("ex", "예시: 두 번 부르면 안 되는 정리", [
        code(r"""
std::FILE* g_save = std::fopen( "save.dat", "rb" );

void CloseSave()
{
    std::fclose( g_save );      // on the 2nd call g_save still holds the address of the closed file
}
""", title="a cleanup that is not idempotent", tag="bad"),
        p("첫 호출 뒤에도 `g_save`에는 닫힌 파일의 주소가 그대로 남아 있다. 둘째 호출은 그 주소로 다시 `fclose`를 "
          "부르고, 그 결과는 정의되어 있지 않다. 함수가 “이미 닫았다”를 알 방법이 없는 것이 원인이다. 닫은 뒤에 그 사실을 "
          "어디에 남기면 둘째 호출이 아무 일도 하지 않게 되는가? 미션 4에서 같은 질문을 창과 GLFW에 대해 답한다."),
    ]),
    box("ex", "예시: 소멸자는 만든 것만, 만든 순서의 반대로 되돌린다", [
        code(r"""
struct Tracer
{
    const char* name;
    explicit Tracer( const char* n ) : name( n ) { std::printf( "+%s ", name ); }
    ~Tracer() { std::printf( "-%s ", name ); }
};

bool Demo( bool fail_at_b )
{
    Tracer a( "A" );
    if ( fail_at_b ) return false;      // B was never made
    Tracer b( "B" );
    return true;
}
""", tag="syntax"),
        console(Raw(
            'Demo( true )    <span class="dim">-&gt;</span>  +A -A\n'
            'Demo( false )   <span class="dim">-&gt;</span>  +A +B -B -A'
        ), title="출력"),
        p("어느 `return`으로 나가든, 그때까지 만들어진 지역 객체만 만든 순서의 반대로 소멸자가 불린다. 안티패턴에서 손으로 "
          "적던 `UndoB(); UndoA();`를 컴파일러가 대신 적어 주는 셈이다. 셋째 방법이 “빠뜨릴 수 없다”는 것은 이 뜻이다."),
    ]),

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
    p("1-2강에서 쓴 `Run()`의 루프 조건을 다시 본다. 조건에 들어 있는 것 하나하나가 루프를 끝내는 스위치다. "
      "1-2강의 선언대로 썼다면 둘이다."),
    table([20, 44, 36], ["스위치", "누가 바꾸는가", "지금 상태"], [
        ["창의 닫기 깃발", "사용자가 닫기 단추를 누르면 GLFW가 올린다. 코드에서는 `glfwSetWindowShouldClose`로 올리거나 내린다",
         "쓰이고 있다. 루프가 `glfwWindowShouldClose`로 읽는다 (1-1강 6장)"],
        ["`_is_running`", "엔진 자신. `true`로 시작한다", "끄는 함수가 없어서 한 번도 바뀌지 않는다"],
    ], cell_cls=["lab", "", ""]),
    p("게임 코드가 “끝내자”고 말할 방법이 지금은 없다. 메뉴의 종료 단추나 `Esc` 키가 그런 요청이다. 길은 둘이다. "
      "`_is_running`을 끄는 함수를 엔진에 만들거나, 창의 닫기 깃발을 코드에서 직접 올린다."),
    fn("glfwSetWindowShouldClose", "void glfwSetWindowShouldClose(GLFWwindow* window, int value);",
       "창의 닫기 깃발(close flag)을 정한다. 창을 닫거나 파괴하지 않는다. 깃발의 값만 바꾼다.",
       params=[("`window`", "깃발을 바꿀 창"),
               ("`value`", "`GLFW_TRUE`면 올리고 `GLFW_FALSE`면 내린다")],
       returns="없다",
       fails="GLFW가 초기화되지 않았으면 `GLFW_NOT_INITIALIZED` 오류가 난다",
       notes=[("깃발을 읽는 쪽", "`glfwWindowShouldClose()`. 루프가 이 값을 보고 스스로 끝나야 한다 (1-1강 6장)"),
              ("쓰임새 둘", "코드에서 “끝내자”고 알릴 때 올린다. 사용자가 누른 닫기를 무르고 싶을 때 내린다"),
              ("선언된 곳", "`include/GLFW/glfw3.h:3306`")],
       lib="GLFW 3.4"),
    box("ex", "예시: 닫기 요청을 무르기", [
        code(r"""
glfwSetWindowShouldClose( window, GLFW_TRUE );    // same effect as clicking the close button
glfwSetWindowShouldClose( window, GLFW_FALSE );   // take the request back, e.g. the user chose "Cancel"
""", tag="usage"),
        p("문서 편집기에서 저장하지 않고 닫기 단추를 누르면 “저장할까요?”가 뜬다. 닫기 단추가 깃발을 올렸고, 프로그램이 "
          "루프 조건을 보기 전에 물어본 것이다. “취소”를 고르면 둘째 줄처럼 깃발을 내리고 루프는 계속 돈다. 깃발은 "
          "명령이 아니라 요청이라서 이런 일이 가능하다."),
    ]),

    h3("4.2", "만든 순서의 반대로"),
    FIG_ORDER,
    table([8, 34, 30, 28], ["", "`Init`이 만드는 것", "되돌리는 호출", "기대는 것"], [
        ["1", "GLFW 라이브러리 상태", "`glfwTerminate()`", "—"],
        ["2", "창과 GL 컨텍스트", "`glfwDestroyWindow()`", "1"],
        ["3", "GL 함수 포인터 (GLAD)", "없다. 되돌릴 것이 없다", "2"],
        ["4", "`MInputManager`", "`unique_ptr`가 놓을 때", "—"],
        ["5", "창에 건 콜백과 user pointer", "창과 함께 사라진다", "2, 4"],
    ], cell_cls=["num", "lab", "", "c"], compact=True),
    p("나중에 만든 것은 먼저 만든 것에 기댄다. 창은 GLFW 없이 존재할 수 없고, 키 콜백은 창과 `MInputManager`가 "
      "둘 다 있어야 돈다. 그래서 정리는 기대는 쪽부터, 곧 만든 순서의 반대로 한다. Part 2부터는 이 표에 GL 객체"
      "(버퍼, 셰이더, 텍스처)가 더해지고, 그것들은 2번이 살아 있을 때 지워야 한다."),
    fn("glfwDestroyWindow", "void glfwDestroyWindow(GLFWwindow* window);",
       "창과 그 창의 OpenGL 컨텍스트를 함께 파괴한다.",
       params=[("`window`", "파괴할 창. 이 호출이 끝나면 그 값은 죽은 주소다")],
       returns="없다",
       fails="GLFW가 초기화되지 않았으면 `GLFW_NOT_INITIALIZED`, 운영체제 쪽 문제면 `GLFW_PLATFORM_ERROR` 오류가 난다",
       notes=[("파괴된 뒤", "그 창의 콜백은 더 불리지 않는다. 그 컨텍스트가 메인 스레드의 현재 컨텍스트였다면 연결을 "
                          "먼저 풀고 파괴한다"),
              ("부르면 안 되는 곳", "콜백 안. 키 콜백에서 곧바로 창을 파괴할 수 없다는 뜻이다. 메인 스레드에서만 부른다"),
              ("짝이 되는 함수", "`glfwCreateWindow()`. `glfwTerminate()`보다 앞에 부른다"),
              ("선언된 곳", "`include/GLFW/glfw3.h:3264`")],
       lib="GLFW 3.4"),
    fn("glfwTerminate", "void glfwTerminate(void);",
       "GLFW 라이브러리를 끝낸다. 남아 있는 창과 커서를 모두 파괴하고, 바꿔 둔 감마 램프를 되돌리고, GLFW가 잡고 있던 "
       "나머지 자원을 놓는다.",
       returns="없다",
       fails="운영체제 쪽 문제면 `GLFW_PLATFORM_ERROR` 오류가 난다",
       notes=[("부르는 순서", "`glfwInit()`이 성공했다면 프로그램이 끝나기 전에 부른다. `glfwInit()`이 실패했을 때는 부를 "
                            "필요가 없다. 실패를 돌려주기 전에 GLFW가 스스로 불렀다"),
              ("부른 뒤", "`glfwInit()`을 다시 성공시키기 전까지 대부분의 GLFW 함수가 `GLFW_NOT_INITIALIZED` 오류를 낸다"),
              ("두 번 부르면", "아무 일도 없다. GLFW가 초기화되지 않은 상태에서는 아무것도 하지 않는다"),
              ("부르면 안 되는 곳", "콜백 안, 그리고 메인 스레드가 아닌 스레드"),
              ("선언된 곳", "`include/GLFW/glfw3.h:2254`")],
       lib="GLFW 3.4"),
    p("`glfwTerminate()`가 남은 창을 스스로 파괴하므로 `glfwDestroyWindow()`를 빼도 창은 사라진다. 그래도 직접 "
      "파괴하면 순서가 코드에 드러나고, Part 2에서 GL 객체를 지울 자리(창을 파괴하기 직전)가 분명해진다. 표의 5번은 "
      "질문으로 남긴다. 키 콜백은 창과 `MInputManager` 둘 다에 기댄다. 둘 중 무엇을 먼저 놓아야 콜백이 죽은 객체를 "
      "건드릴 틈이 없는가? 미션 4에서 순서를 적을 때 답한다."),

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
    p("주인(owner)은 그 자원을 놓아 줄 책임이 있는 쪽이다. `Init`이 만든 것 셋을 누가 들고 있는지, 네 `GEngine`의 "
      "멤버 선언에서 찾아본다."),
    keep(h4("네 코드에서 확인할 것"),
    table([22, 28, 50], ["자원", "볼 자리", "왜 문제인가"], [
        ["`MInputManager`", "`_input_manager`의 타입 (1-3강)",
         "`unique_ptr`라면 타입이 주인임을 말해 준다. 다만 놓이는 때가 `~GEngine()`, 곧 `main`이 끝난 뒤다"],
        ["창과 GL 컨텍스트", "`_main_window`의 타입 (1-1강 8.3절)",
         "날 포인터다. 주인인지 빌린 것인지 타입이 말하지 않는다. `GEngine`이 사라져도 창은 남는다"],
        ["GLFW 라이브러리 상태", "멤버 전체를 훑어본다", "들고 있는 멤버가 없다. 초기화했다는 사실이 어디에도 적혀 있지 않다"],
    ], cell_cls=["lab", "", ""])),
    FIG_OWNER,
    fn("std::unique_ptr<T, Deleter>",
       "template<class T, class Deleter = std::default_delete<T>>\n"
       "class unique_ptr;",
       "자원 하나의 하나뿐인 주인. 자신이 사라질 때 `Deleter`를 불러 들고 있던 것을 놓는다.",
       params=[("`T`", "가리키는 대상의 타입. 안에 `T*` 하나를 든다"),
               ("`Deleter`", "놓는 방법. `T*`를 받는 `operator()`가 있는 타입이다. 적지 않으면 `delete`를 부르는 "
                             "`std::default_delete<T>`가 쓰인다. `delete`가 아닌 함수로 놓아야 하는 자원은 여기에 직접 만든 타입을 준다")],
       notes=[("주요 멤버", "`get()` 들고 있는 주소를 빌려준다 · `reset()` 지금 놓고 비운다 · `release()` 놓지 않고 "
                          "주인 자리만 내놓는다 · `if ( ptr )` 비어 있는지 본다"),
              ("놓는 때", "소멸자, `reset()`, 다른 값을 대입받을 때. 비어 있으면(`nullptr`) 삭제자를 부르지 않는다"),
              ("복사와 이동", "복사할 수 없다. `std::move`로 주인 자리를 넘길 수만 있다"),
              ("선언된 곳", "`<memory>` (C++11)")],
       lib="C++ 표준 라이브러리"),
    box("ex", "예시: `fclose`로 놓아야 하는 `FILE*`", [
        code(r"""
struct FileCloser
{
    void operator()( std::FILE* f ) const { std::fclose( f ); }
};

// fclose runs when `file` goes out of scope
std::unique_ptr<std::FILE, FileCloser> file( std::fopen( "a.txt", "r" ) );
""", title="unique_ptr with a custom deleter", tag="syntax"),
        p("`fopen`으로 연 파일은 `delete`가 아니라 `fclose`로 닫아야 한다. 둘째 템플릿 인자에 “닫는 방법”을 타입으로 "
          "넘기면 `unique_ptr`가 그 방법으로 놓는다. `fopen`이 실패해 `nullptr`이 들어왔다면 삭제자는 불리지 않는다. "
          "창도 `delete`가 아닌 함수로 놓는 자원이라는 점에서 같다."),
    ]),
    p("주의할 것이 하나 있다. 멤버는 선언한 순서로 만들어지고 그 반대로 파괴된다. 주인 객체를 멤버로 두면 정리 순서가 "
      "선언 순서에 묶이고, 정적 객체의 멤버라면 그 시점은 `main`이 끝난 뒤다 (4.3절). 그 전에 놓으려면 `reset()`을 "
      "직접 불러야 한다."),

    h3("5.2", "빌려 쓰는 포인터"),
    p("`GetMainWindow()`와 `GetInputManager()`는 날 포인터를 돌려준다. 받은 쪽은 주인이 아니라 빌려 쓰는 쪽이다. "
      "주인이 자원을 놓은 뒤에도 그 포인터를 들고 있으면 죽은 메모리를 가리키는 댕글링 포인터가 된다. 그래서 정리 "
      "함수는 놓은 포인터를 `nullptr`로 돌려놓는 일까지 해야 한다. `nullptr`은 검사할 수 있지만 댕글링 포인터는 "
      "검사할 방법이 없다."),

    h3("5.3", "값 초기화"),
    p("C++에서 객체를 만드는 표기는 여럿이고, 표기에 따라 기본 타입 멤버가 0으로 시작하기도 하고 정해지지 않은 값으로 "
      "시작하기도 한다."),
    code(r"""
struct S { int n; };
S  a;                  // default-initialization: a.n is indeterminate
S  b{};                // value-initialization:   b.n == 0
S* c = new S;          // default-initialization
S* d = new S();        // value-initialization
""", tag="syntax"),
    box("ex", "예시: 값 초기화가 배열에 하는 일", [
        code(r"""
struct Pad     { std::array<bool, 4> keys; };                 // no constructor written
struct PadCtor { PadCtor() {}  std::array<bool, 4> keys; };   // constructor with an empty body

Pad     a;      // default-initialization:  a.keys = { ?, ?, ?, ? }
Pad     b{};    // value-initialization:    b.keys = { false, false, false, false }
PadCtor c{};    // the written constructor runs, nothing is zeroed:  c.keys = { ?, ?, ?, ? }
""", tag="syntax"),
        p("셋 다 함수 안의 지역 변수라고 하자. `?`는 정해지지 않은 값이다. 읽으면 무엇이 나올지 약속이 없고, 우연히 0일 "
          "수도 있어서 한동안 문제없이 도는 것이 더 위험하다. `a`와 `b`는 중괄호 한 쌍의 차이이고, `b`와 `c`는 생성자를 손으로 적었느냐의 차이다. "
          "`std::array<bool, 4>`는 `bool` 넷을 그대로 담은 구조체라서 스스로 0으로 채워 주는 생성자가 없다. 빈 채로 "
          "시작하는 `std::vector`와 다른 점이다."),
    ]),
    keep(h4("네 코드에서 확인할 것"),
    table([33, 27, 40], CHECK_HEADER, [
        ["두 배열의 선언에 초기값이 있는가", "`MInputManager`의 `_current_keys`, `_previous_keys`",
         "없다면 배열의 처음 내용은 객체를 만드는 표기에 달려 있다"],
        ["`MInputManager`를 어떤 표기로 만드는가", "`Init`에서 `_input_manager`를 채우는 줄",
         "`std::make_unique`는 값 초기화를 한다. 지역 변수로 만들면 기본 초기화다"],
        ["생성자를 어떻게 적었는가", "`MInputManager`의 생성자 선언",
         "적지 않았거나 클래스 안에서 `= default`면 0으로 채워지고, `{}`로 본문을 주면 채워지지 않는다"],
    ], cell_cls=["lab", "", ""])),
    keep(table([46, 18, 36], ["`MInputManager`를 만드는 방법", "초기화", "두 배열의 내용"], [
        ["`std::make_unique<MInputManager>()`, 생성자는 적지 않았거나 `= default`", "값 초기화", "전부 `false`"],
        ["지역 변수 `MInputManager m;`", "기본 초기화", "정해지지 않은 값"],
        ["생성자를 `MInputManager() {}`로 바꾼 뒤 `make_unique`", "값 초기화", "정해지지 않은 값"],
    ], cell_cls=["lab", "c", ""])),
    p("배열에 초기값을 적지 않았는데 0으로 시작하고 있다면 두 가지 우연이 겹친 결과다. `make_unique`가 `new T()`로 값 "
      "초기화를 하고, 생성자가 손으로 쓴 것이 아니라서 값 초기화가 멤버를 먼저 0으로 채운다. 생성자에 본문을 주는 "
      "순간(셋째 줄) 0으로 채우는 단계가 사라진다. 초기값이 만드는 방법에 달려 있으면 안 된다. 멤버 선언에 초기값을 "
      "적어 두면 어떤 표기로 만들어도 같은 값으로 시작한다. 1-1강 8.3절의 `_main_window = nullptr`가 이미 그렇게 하고 있다."),
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
        ["창 핸들을 드는 방법", "날 포인터와 수동 해제 (지금) / `unique_ptr`와 삭제자", "5.1절의 그림. 순서를 손으로 쥘 것인가, 선언 순서에 맡길 것인가"],
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

    keep(h3("6.4", "함께 넘어온 작은 정리"),
    p("앞 강들이 이 강으로 넘긴 것 가운데 주제 밖의 항목이다 (1.3절). 미션 8에서 다룬다. “볼 자리”는 네 코드의 함수 "
      "이름이고, 프로젝트 설정만 파일과 줄 번호다."),
    table([21, 27, 52], ["항목", "볼 자리", "생각할 것"], [
        Group("루프 (1-2강)"),
        ["첫 프레임의 dt", "`Run()`에서 시각을 처음 재는 곳", "첫 dt가 한 프레임 분량이 되려면 루프 직전에 무엇을 해 두는가"],
        ["dt의 상한", "`Run()`에서 dt를 구한 직후", "상한은 몇 초인가. 넘으면 자르는가, 그 프레임을 건너뛰는가"],
        ["수직 동기", "호출이 없다. 넣는다면 `Init`", "`glfwSwapInterval`은 현재 컨텍스트가 있어야 통한다. 값은 누가 정하는가 (표 다음의 카드)"],
        Group("입력 (1-3강)"),
        ["콜백의 범위 검사", "`cbSetKey`의 첫머리", "`key`는 `int`, `IsValidKey`는 `EKey`를 받는다. 검사를 어디에 두는가"],
        ["“지금 눌려 있는가”", "`MInputManager`의 조회 함수 셋", "함수 이름, 그리고 Pressed·Held와의 관계"],
        ["조회 함수의 `const`", "같은 셋, 그리고 `GetInputManager()`", "`GetInputManager()`의 반환 타입은 그대로 두어도 되는가"],
        Group("프로젝트 설정 (1-1강)"),
        ["Release의 링크 입력", "`Client/Client.vcxproj:144`", "Debug|x64에만 있다. 모든 구성에 한 번에 적는 방법이 있는가"],
        ["새로 더한 `.cpp` 항목", "`Engine/Engine.vcxproj`의 `ClCompile` 항목",
         "네가 더한 파일의 항목이 한 줄인가. 여러 줄이면 그 파일에만 덮어쓴 설정이 붙은 것이다 (속성 창에서 굵게 보인다)"],
        ["프로젝트 참조", "`ClaudGL_Engine.sln`", "Client의 참조에 Engine을 더한다. 직접 적은 `ClaudGL.lib`는 그 뒤에도 필요한가"],
    ], cell_cls=["lab", "", ""], compact=True)),
    fn("glfwSwapInterval", "void glfwSwapInterval(int interval);",
       "현재 컨텍스트의 스왑 간격을 정한다. `glfwSwapBuffers`가 버퍼를 바꾸기 전에 화면 갱신을 적어도 몇 번 기다릴지다.",
       params=[("`interval`", "기다릴 화면 갱신의 최소 횟수. 0이면 기다리지 않는다. 1이면 수직 동기다")],
       returns="없다",
       fails="현재 컨텍스트가 없으면 `GLFW_NO_CURRENT_CONTEXT` 오류가 난다. `glfwMakeContextCurrent()` 뒤에 불러야 한다",
       notes=[("부르지 않으면", "GLFW는 컨텍스트를 만들 때 이 값을 건드리지 않는다. 플랫폼과 드라이버의 기본값을 따른다"),
              ("주의", "드라이버가 요청을 따르지 않을 수 있다. 그래픽 제어판에서 수직 동기를 강제로 켜거나 끈 경우가 그렇다"),
              ("선언된 곳", "`include/GLFW/glfw3.h:6210`. 기본 설명은 1-2강에 있다")],
       lib="GLFW 3.4"),
    box("ex", "예시: 60Hz 모니터에서의 스왑 간격", [
        table([14, 38, 22, 26], ["`interval`", "`glfwSwapBuffers`가 하는 일", "프레임 수의 상한", "한 프레임의 dt"], [
            ["0", "기다리지 않고 바로 바꾼다", "없다", "그릴 수 있는 만큼 짧다"],
            ["1", "다음 화면 갱신까지 기다린다", "초당 60", "약 0.0167초"],
            ["2", "화면 갱신을 두 번 기다린다", "초당 30", "약 0.0333초"],
        ], cell_cls=["c", "", "c", "c"], compact=True),
        p("144Hz 모니터라면 같은 1이 초당 144가 된다. 상한이 모니터에 달려 있으므로 값을 엔진이 정해 버릴지, `Init`을 "
          "부르는 쪽이 고르게 할지가 결정할 거리다."),
    ]),

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
        ("네 코드를 읽고 GLFW 오류 콜백을 단다",
         "먼저 네 `Init`, `Run`, `main`을 읽고 1.1절·1.2절·5.1절·5.3절의 표를 채운다. “볼 자리”에 실제 파일과 줄을 적는다. "
         "그다음 실패의 이유를 받는 통로를 만들고, `Init`에 OpenGL 9.9를 요청해 콜백이 불리는지 확인한다.",
         ["콜백은 `this`가 없는 함수여야 한다. 1-3강의 `cbSetKey`가 같은 종류였다.",
          "콜백이 불리지 않으면 다는 위치를 본다. 무엇보다 먼저여야 하는가 (2.3절 카드의 “부르는 순서”)."]),
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
         ["되돌린 뒤 멤버에 무엇을 남겨야 다음 호출이 “이미 되돌렸다”를 아는가 (3.1절의 예시, 5.2절).",
          "`unique_ptr`를 수명이 끝나기 전에 비우는 멤버 함수는 5.1절의 카드에 있다."]),
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
         ["멤버 선언에 초기값을 적는 일은 1-1강 8.3절의 `_main_window`에서 이미 했다. `std::array`에는 5.3절 문법 "
          "블록의 중괄호가 통한다."]),
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
        ["`main`이 실패를 돌려줬는데 종료 코드가 `0xffffffff`로 보인다", "`-1`을 돌려주었다. 종료 코드는 32비트 값으로 "
                                                                "표시된다 (2.4절의 예시)", "출력 창의 마지막 줄"],
        ["`glfwSwapInterval`을 불렀는데 프레임 수가 그대로다", "컨텍스트를 연결하기 전에 불렀다. 또는 드라이버 설정이 요청을 덮어쓴다",
         "오류 콜백에 `GLFW_NO_CURRENT_CONTEXT`가 찍혔는지 본다"],
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
        "세 호출 가운데 GLAD만 확인하는 1-1강의 `Init`에서 `glfwInit()`이 실패했다. `Init`은 어디에서 무엇을 "
        "돌려주는가? `main`은 그것이 창 생성 실패인지 GLAD 실패인지 구별할 수 있는가?",
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
        ("GLAD를 확인하는 분기에서 `InitErrorCode::Fail`을 돌려준다. `main`은 구별할 수 없다.",
         "실패를 확인하는 곳이 그 분기 하나뿐이라 앞의 실패도 거기까지 흘러가 같은 값이 된다. 구별하려면 단계마다 "
         "확인하고, 값이나 메시지로 원인을 따로 전해야 한다. (2.2절, 2.4절)"),
        ("프로세스가 끝나면서 운영체제가 회수한다.",
         "넣는 이유는 1.2절의 셋 중에서 고른다. 운영체제가 해 주지 않는 일(flush, 감마 복원)이 있고, 순서가 "
         "필요한 자원이 곧 생기고, 프로세스가 끝나지 않은 채 다시 초기화하는 경우가 있다. (1.2절, 3장)"),
        ("창은 `glfwTerminate()`가 이미 파괴했다. 뒤의 호출은 죽은 포인터를 넘기고 `GLFW_NOT_INITIALIZED` 오류를 낸다.",
         "`glfwTerminate()`는 남은 창을 모두 파괴하고, 그 뒤의 GLFW 함수는 초기화되지 않았다는 오류를 낸다. "
         "기대는 쪽(창)을 먼저, 기대어지는 쪽(GLFW)을 나중에 되돌려야 한다. (4.2절)"),
        ("정해지지 않은 값이 들어 있다. 바꾸기 전에는 값 초기화가 멤버를 먼저 0으로 채웠다.",
         "`make_unique`의 값 초기화는 생성자가 손으로 쓴 것이 아니면 0으로 채운 뒤 생성자를 부르고, 본문을 직접 준 "
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
    ("오류 콜백", "error callback", "GLFW 함수가 오류를 낼 때 그 자리에서 불리는 함수. 오류 코드와 설명을 받는다"),
    ("종료 코드", "exit code", "`main`이 돌려준 값. 0이면 성공, 0이 아니면 실패로 읽는다"),
    ("삭제자", "deleter", "`unique_ptr`가 자원을 놓을 때 부르는 것. 둘째 템플릿 인자로 정한다"),
    ("닫기 깃발", "close flag", "창마다 하나 있는 “닫아 달라”는 표시. 루프가 읽고 스스로 끝낸다"),
    ("스왑 간격", "swap interval", "버퍼를 바꾸기 전에 기다릴 화면 갱신 횟수. 1이면 수직 동기"),
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
