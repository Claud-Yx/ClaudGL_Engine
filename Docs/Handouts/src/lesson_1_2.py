"""Lesson 1-2 -- game loop and delta time, written from scratch.

Version 3 replaces the earlier "re-read your own code" handout. It starts from
the state at the end of lesson 1-1 (v3): GEngine with Get(), Init(),
GetMainWindow() and a temporary loop in main. It has missions and quotes no
engine code; the first pass (tag first-pass-2026-04) is only the reference
for the declarations.

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

# Library headers and framework.h were read on this day.
READ_DATE = "2026-11-16"

COVER = cover(
    f"CLAUDGL ENGINE · PART {ME['part']} · {ME['id']} · v{ME['ver']}",
    Raw('GEngine::<span class="ac">Run</span>'),
    ME["title"],
    "루프를 엔진 안으로 옮기고, 시간을 재고, 프레임마다 게임 코드를 부른다",
    [
        ("목표 결과물", "창을 닫을 때까지 매 프레임 `Update(dt)`가 불린다. 배경색이 PC의 속도와 상관없이 2초 주기로 변한다"),
        ("핵심 개념", "게임 루프 · 델타 타임 · 콜백과 의존 방향 · 더블 버퍼링 · 뷰포트"),
        ("선수 지식", "1-1강을 끝낸 코드. 함수 포인터와 람다가 무엇인지 들어 본 정도"),
        ("예상 시간", f"읽기 50분 + 구현 1시간 남짓 (계획서 기준 {ME['hours']}시간)"),
        ("건드릴 파일", "`Engine/Core/EngineCore.h`·`.cpp`, `Client/main.cpp`"),
        ("시작 상태", f"1-1강(v3)의 완료 기준을 채운 코드. `main`에 임시 루프가 있다 (헤더는 {READ_DATE}에 읽음)"),
    ],
    note=("읽는 법",
          "처음부터 직접 쓰는 자료다. 2 〜 6장이 이 강에서 쓸 개념과 함수이고, 7장의 모양을 확인한 뒤 8장의 미션을 "
          "순서대로 구현한다. 코드 블록은 완성본이 아니다. 루프에 쓰는 네 함수는 1-1강 6장에서 이미 설명했다."),
    toc=["한 장으로 보기", "게임 루프", "시간 재기: Delta Time", "게임 코드를 부르는 길: 콜백",
         "한 프레임의 순서와 더블 버퍼링", "창 크기가 바뀔 때: 뷰포트", "설계", "구현 미션", "흔한 함정", "완료 기준",
         "생각해 볼 질문", "해설", "용어집"],
)


# --------------------------------------------------------------------------
# figures
# --------------------------------------------------------------------------

def fig_timeline() -> Raw:
    """Frames on a time axis; one frame is longer than the others."""
    f = Fig(150)
    f.text(20, 16, "프레임의 맨 앞에서 glfwGetTime()이 돌려준 값 (초)", kind="s", anchor="start", size=10)
    f.arrow((40, 96), (646, 96))
    f.text(646, 86, "시간", kind="s", anchor="end", size=9.5)
    ticks = [60, 160, 260, 420, 520, 620]
    times = ["2.000", "2.016", "2.033", "2.058", "2.075", "2.091"]
    deltas = ["0.016", "0.017", "0.025", "0.017", "0.016"]
    for x, t in zip(ticks, times):
        f.line((x, 90), (x, 102))
        f.text(x, 116, t, kind="mono", size=9.5)
    for i in range(5):
        left, right = ticks[i], ticks[i + 1]
        long_frame = i == 2
        f.box(left + 3, 40, right - left - 6, 34, f"프레임 {i + 1}", kind="accent" if long_frame else "")
        f.text((left + right) / 2, 138, f"dt = {deltas[i]}", kind="accent" if long_frame else "s", size=9.5)
    return f.render("프레임은 일정한 간격으로 오지 않는다. 이웃한 두 시각의 차이가 그 사이의 프레임에 걸린 시간이다. "
                    "프레임 3에 걸린 0.025초는 프레임 4의 맨 앞에서야 알 수 있고, 프레임 4의 Update가 그 값을 받는다.")


def fig_speed() -> Raw:
    """The same movement at 60 and 30 fps, without and with dt."""
    f = Fig(204)
    x0, x1 = 270.0, 600.0                      # track: position 0 .. 300

    def pos(value: float) -> float:
        return x0 + (x1 - x0) * value / 300.0

    for value in (0, 150, 300):
        f.line((pos(value), 34), (pos(value), 172), kind="muted dash")
        f.text(pos(value), 190, str(value), kind="mono", size=9.5)
    f.text((x0 + x1) / 2, 16, "1초 뒤의 위치", kind="s", size=10)

    f.text(20, 30, "프레임마다 +5", kind="t", anchor="start")
    f.text(20, 108, "프레임마다 +300 × dt", kind="t", anchor="start")
    rows = [
        (52, "60 FPS", "5씩 60번", 300, "accent"),
        (78, "30 FPS", "5씩 30번", 150, "accent"),
        (130, "60 FPS", "5씩 60번", 300, ""),
        (156, "30 FPS", "10씩 30번", 300, ""),
    ]
    for y, fps, step, reach, kind in rows:
        f.text(34, y + 4, fps, anchor="start", size=10.5)
        f.text(110, y + 4, step, kind="s", anchor="start", size=10)
        f.dot(x0, y, r=3, kind=kind)
        f.arrow((x0, y), (pos(reach), y), kind=kind)
        f.text(pos(reach) + 10, y + 4, str(reach), kind="accent" if kind else "t", anchor="start", size=10.5)
    return f.render("위의 둘은 프레임 수에 따라 도착하는 곳이 다르다. 아래의 둘은 한 프레임에 움직이는 양이 dt에 "
                    "비례하므로 같은 곳에 도착한다.")


def fig_buffers() -> Raw:
    """Two buffers keep their place; the swap exchanges their roles."""
    f = Fig(158)
    f.text(150, 16, "교체 전", kind="s", size=10)
    f.text(510, 16, "교체 후", kind="s", size=10)
    f.text(24, 57, "A", kind="t")
    f.text(24, 121, "B", kind="t")
    f.box(40, 28, 220, 50, "back buffer", "프레임 N+1을 그리는 중", kind="accent")
    f.box(40, 92, 220, 50, "front buffer", "프레임 N이 화면에 보인다", kind="dark")
    f.arrow((275, 85), (385, 85), kind="accent")
    f.text(330, 76, "glfwSwapBuffers", kind="mono", size=9.5)
    f.box(400, 28, 220, 50, "front buffer", "프레임 N+1이 화면에 보인다", kind="dark")
    f.box(400, 92, 220, 50, "back buffer", "지우고 프레임 N+2를 그린다", kind="accent")
    return f.render("버퍼 A와 B는 그대로 있고 역할이 바뀐다. 그리는 일은 늘 back buffer에 대고 일어나고, "
                    "화면에 보이는 것은 늘 front buffer다.")


def fig_viewport() -> Raw:
    """Viewport rectangle inside an 800 x 600 framebuffer, origin at the bottom left."""
    f = Fig(268)
    scale = 0.35
    left, bottom = 170.0, 240.0
    f.box(left, bottom - 600 * scale, 800 * scale, 600 * scale, kind="soft", r=0)
    f.arrow((left, bottom), (left + 800 * scale + 40, bottom))
    f.arrow((left, bottom), (left, bottom - 600 * scale - 22))
    f.text(left + 800 * scale + 48, bottom + 4, "x", kind="mono", anchor="start", size=10)
    f.text(left - 10, bottom - 600 * scale - 14, "y", kind="mono", anchor="end", size=10)
    f.text(left - 8, bottom + 15, "(0, 0)", kind="mono", anchor="end", size=9.5)
    f.text(left + 800 * scale + 6, bottom - 600 * scale + 4, "(800, 600)", kind="mono", anchor="start", size=9.5)
    f.text(left + 800 * scale / 2, bottom - 600 * scale + 16, "프레임버퍼 800 × 600 픽셀", kind="s", size=9.5)

    vx, vy, vw, vh = 100, 50, 400, 300
    f.box(left + vx * scale, bottom - (vy + vh) * scale, vw * scale, vh * scale, "뷰포트", "400 × 300", kind="accent", r=0)
    f.line((left + vx * scale, bottom - vy * scale), (left + vx * scale, bottom), kind="muted dash")
    f.line((left, bottom - vy * scale), (left + vx * scale, bottom - vy * scale), kind="muted dash")
    f.text(left + vx * scale, bottom + 15, "100", kind="mono", size=9.5)
    f.text(left - 8, bottom - vy * scale + 3, "50", kind="mono", anchor="end", size=9.5)

    f.text(478, 112, "glViewport( 100, 50, 400, 300 )", kind="mono", anchor="start", size=10)
    f.text(478, 134, "앞의 둘: 왼쪽 아래 모서리", kind="s", anchor="start", size=9.5)
    f.text(478, 150, "뒤의 둘: 너비와 높이", kind="s", anchor="start", size=9.5)
    return f.render("OpenGL은 프레임버퍼의 왼쪽 아래를 (0, 0)으로 보고 y가 위로 커진다. 뷰포트는 그 안의 사각형 하나이고, "
                    "그림은 이 사각형에 맞춰 그려진다.")


# --------------------------------------------------------------------------

ch1 = chapter(1, "한 장으로 보기", [
    table([24, 38, 38], ["", "지금 (1-1강의 끝)", "이 강이 끝나면"], [
        ["루프가 있는 곳", "`main` 안. Client가 `glfw*`, `gl*`을 직접 부른다", "엔진의 `GEngine::Run()` 안"],
        ["시간", "재지 않는다", "프레임마다 dt를 재서 게임 코드에 넘긴다"],
        ["게임 코드가 끼어드는 자리", "없다. 루프 안에 직접 써야 한다", "Client가 넘겨 둔 함수를 엔진이 프레임마다 부른다"],
        ["창 크기가 바뀔 때", "아무 일도 하지 않는다", "넘겨 둔 함수가 불린다 (효과는 2-2강에서 본다)"],
    ], cell_cls=["lab", "", ""]),
    flow([
        ("시간 재기", "dt"),
        ("이벤트 처리", "쌓인 것을 받는다"),
        ("지우기", "배경색으로"),
        ("Update(dt)", "게임 코드", "accent"),
        ("내보내기", "화면에", "dark"),
    ], "이 강에서 만드는 한 프레임이다. 1-1강의 임시 루프에 맨 앞 칸과 넷째 칸이 더해진다."),
    flow([
        ("Run으로 옮기기", "화면은 그대로"),
        ("dt 재기", "glfwGetTime"),
        ("Update 콜백", "std::function", "accent"),
        ("색 바꾸기", "dt로"),
        ("크기 콜백", "통로만"),
        ("실험", "dt가 튀는 때", "dark"),
    ], "8장의 미션이 지나가는 길이다."),
], lead="1-1강에서 창을 띄우고 `main`에 임시 루프를 썼다. 이 강은 그 루프를 엔진 안으로 옮기고, 한 바퀴에 "
        "두 가지를 더한다. 시간을 재는 일과 게임 코드를 부르는 일이다.")

ch2 = chapter(2, "게임 루프", [
    p("보통의 프로그램은 위에서 아래로 한 번 실행하고 끝난다. 게임은 사용자가 끌 때까지 “입력을 받고, 상태를 갱신하고, "
      "그린다”를 되풀이해야 한다. 이 되풀이를 한 곳에서 쥐고 있는 것이 게임 루프이고, 엔진의 나머지 부분은 전부 "
      "이 루프에 불려서 일한다."),

    h3("2.1", "루프가 엔진 안에 있어야 하는 이유"),
    p("1-1강의 임시 루프는 `main` 안에 있다. 그 상태에서는 게임을 하나 더 만들 때마다 같은 루프를 다시 써야 하고, "
      "Client가 `glfwPollEvents` 같은 함수를 직접 알아야 한다. 루프를 엔진으로 옮기면 Client에 남는 일은 "
      "“프레임마다 무엇을 할지”를 엔진에 알려 주는 것뿐이다. 순서와 시간과 창은 엔진이 맡는다."),
    ox(("Client: “프레임마다 이 함수를 불러 달라”", "루프는 엔진에 한 번만 있다. Client는 GLFW를 몰라도 된다"),
       ("Client: 루프를 직접 쓰고 그 안에서 엔진 함수를 부른다", "게임마다 루프를 다시 쓴다. 순서를 틀릴 자리가 늘어난다")),

    h3("2.2", "루프를 끝내는 두 깃발"),
    table([32, 68], ["조건", "뜻"], [
        ["`_is_running`", "엔진이 스스로 멈추려 할 때 쓰는 깃발. `true`로 시작하고, 끄는 함수는 1-4강에서 만든다"],
        ["`glfwWindowShouldClose( … )`가 거짓", "사용자가 창의 닫기 버튼을 아직 누르지 않았다. GLFW가 창마다 들고 있는 깃발을 읽는다"],
    ], cell_cls=["lab", ""]),
    p("둘 다 참인 동안 루프가 돈다. 닫기 버튼을 누른다고 창이 바로 사라지지는 않는다. GLFW는 깃발만 세우고, 루프가 "
      "그 깃발을 보고 스스로 빠져나온다. 저장할지 묻는 창을 띄울 틈이 여기서 생긴다."),

    h3("2.3", "이미 아는 네 함수"),
    table([30, 46, 24], ["함수", "하는 일", "자세한 설명"], [
        ["`glfwWindowShouldClose`", "창의 “닫아 달라” 깃발을 읽는다", "1-1강 6장"],
        ["`glfwPollEvents`", "운영체제가 쌓아 둔 이벤트를 지금 처리한다. 콜백은 이 안에서 불린다", "1-1강 6장"],
        ["`glClear`", "back buffer를 정해 둔 색으로 채운다", "1-1강 6장"],
        ["`glfwSwapBuffers`", "back buffer와 front buffer를 맞바꾼다", "1-1강 6장"],
    ], cell_cls=["lab", "", "c"], compact=True),
    box("point", None,
        "프레임은 메트로놈처럼 일정한 간격으로 오지 않는다. 어떤 박은 길고 어떤 박은 짧다. 그래서 게임 로직은 "
        "“한 박에 얼마”가 아니라 “1초에 얼마”로 적어야 한다. 다음 장의 델타 타임이 그 환산에 쓰인다."),
    box("ue", None,
        "언리얼의 루프는 `FEngineLoop::Tick`이다. 한 번 돌 때마다 `UWorld::Tick`이 불리고, 거기서 액터와 컴포넌트의 "
        "`Tick`이 불린다. 게임 코드를 쓰는 사람이 루프를 직접 쓰지 않고 `Tick( float DeltaSeconds )`만 채우는 것은 "
        "이 강에서 만드는 구조와 같다."),
    box("cs", None,
        "“내가 라이브러리를 부르는” 대신 “틀이 내 코드를 부르는” 구조를 제어의 역전(inversion of control)이라고 한다. "
        "라이브러리와 프레임워크를 가르는 기준이기도 하다. 운영체제가 프로그램에 이벤트를 보내 주는 방식, GUI "
        "프로그램의 메시지 루프가 같은 구조다."),
], lead="루프는 프로그램을 살려 두는 장치다. 조건이 거짓이 되는 순간이 프로그램이 끝나는 순간이다.")

ch3 = chapter(3, "시간 재기: Delta Time", [
    fn("glfwGetTime", "double glfwGetTime(void);",
       "`glfwInit()`이 불린 뒤로 흐른 시간을 초 단위로 돌려준다.",
       returns="초 단위의 `double`. 1.5는 1초 반이다",
       fails="GLFW가 초기화되지 않았으면 `GLFW_NOT_INITIALIZED` 오류를 내고 0을 돌려준다",
       notes=[("무엇의 시각인가", "프로그램이 시작한 뒤의 경과 시간이다. 몇 시 몇 분인지를 알려 주는 벽시계 시각이 아니다"),
              ("얼마나 세밀한가", "시스템에 따라 다르다. 보통 마이크로초(100만분의 1초)에서 나노초 단위다"),
              ("부르는 순서", "`glfwInit()` 뒤. 어느 스레드에서 불러도 된다"),
              ("선언된 곳", "`include/GLFW/glfw3.h:5992`")],
       lib="GLFW 3.4"),
    fig_timeline(),
    p("**델타 타임(dt)**은 직전 한 프레임에 걸린 시간이다. 프레임의 맨 앞에서 시각을 한 번 읽고, 지난 프레임에 읽어 둔 "
      "시각을 빼면 나온다. 그러려면 “지난번에 읽은 시각”을 다음 프레임까지 들고 있어야 한다. 엔진의 멤버 변수가 "
      "그 일을 한다. 이번 프레임이 얼마나 걸릴지는 끝나 봐야 알기 때문에, 바로 앞 프레임의 길이를 대신 쓰는 것이다."),
    box("ex", "예시: 숫자로 따라가기", [
        table([22, 22, 24, 32], ["언제", "이번에 읽은 시각", "지난번에 읽은 시각", "dt = 이번 − 지난번"], [
            ["프레임 4의 맨 앞", "2.058", "2.033", "0.025초 (프레임 3에 걸린 시간)"],
            ["프레임 5의 맨 앞", "2.075", "2.058", "0.017초 (프레임 4에 걸린 시간)"],
        ], cell_cls=["lab", "", "", ""], compact=True),
        p("프레임 4에서 계산을 마친 뒤 “지난번에 읽은 시각”을 2.058로 바꿔 두어야 프레임 5의 계산이 맞는다. 이 갱신을 "
          "잊으면 dt는 프레임마다 계속 커진다. 1초에 몇 프레임인지(FPS)는 1을 dt로 나누면 된다. 0.025초면 40, "
          "0.017초면 약 59다."),
    ]),

    h3("3.1", "왜 필요한가"),
    p("프레임마다 고정된 양을 더하는 코드는 프레임이 많이 나오는 PC에서 더 빨리 움직인다. 1초에 300만큼 움직이고 "
      "싶다면 “프레임마다 5”가 아니라 “1초에 300”이라고 적고, 이번 프레임에 흐른 시간을 곱해야 한다."),
    fig_speed(),
    table([14, 20, 34, 32], ["FPS", "dt", "한 프레임의 이동 (300 × dt)", "1초 동안의 이동"], [
        ["30", "약 0.0333초", "약 10", "300"],
        ["60", "약 0.0167초", "약 5", "300"],
        ["144", "약 0.0069초", "약 2.08", "300"],
    ], cell_cls=["lab", "", "", ""], compact=True),
    p("그래서 `Update`는 dt를 인자로 받는다. 움직임, 회전, 색의 변화처럼 시간에 따라 변하는 것은 전부 "
      "“1초에 얼마”로 정해 두고 dt를 곱한다."),

    h3("3.2", "double로 재고 float로 넘긴다"),
    p("시각은 `double`로 들고, 게임 코드에 넘기는 dt는 `float`다. 둘의 쓰임이 다르기 때문이다."),
    cards([
        ("double", "누적 시각 — 계속 커지는 값",
         "한 시간 뒤면 3600, 하루 뒤면 86400이다. 큰 값에서 작은 차이를 빼내려면 유효 숫자가 넉넉해야 한다.",
         "`glfwGetTime()`의 반환값, 지난번에 읽은 시각"),
        ("float", "차이 — 늘 작은 값",
         "0.007 근처의 작은 수 하나다. `float`의 정밀도로 충분하고, 이후 벡터와 행렬 계산이 전부 `float`다.",
         "`Update( float delta_time )`의 인자"),
    ]),
    box("cs", None,
        "`float`는 유효 숫자가 약 7자리다. 값이 8192를 넘으면 이웃한 두 `float` 사이의 간격이 약 0.001이 된다. "
        "누적 시각을 `float`로 들고 있으면 실행 후 두 시간 남짓부터 시각이 1밀리초 눈금으로만 변하고, 144FPS의 "
        "프레임 시간(약 6.9밀리초)도 그 눈금으로밖에 재지 못한다. `double`은 같은 조건에서 간격이 "
        "1000억분의 1초보다 작다. 컴퓨터구조의 부동소수점 표현(IEEE 754)에서 지수가 커질수록 눈금이 넓어지는 그 성질이다."),

    keep(h3("3.3", "dt가 튀는 순간"),
    table([26, 74], ["언제", "무슨 일이 생기나"], [
        ["첫 프레임", "“지난번에 읽은 시각”이 0에서 시작하면, 첫 dt는 `glfwInit()`부터 첫 바퀴까지 걸린 시간 전체다. "
                  "창을 만들고 GLAD를 채우는 시간이 들어가 보통의 프레임보다 훨씬 크다"],
        ["창을 잡고 끌 때", "Windows에서는 창을 옮기거나 크기를 바꾸는 동안 `glfwPollEvents()`가 돌아오지 않는다. "
                     "놓는 순간의 dt에 그동안의 시간이 통째로 들어간다"],
        ["디버거 중단점", "멈춰 있던 시간이 다음 dt가 된다"],
    ], cell_cls=["lab", ""])),
    p("세 경우 모두 dt를 곱해 움직이는 것은 그 한 프레임에 멀리 건너뛴다. 이 강에서는 일어난다는 것을 눈으로 "
      "확인만 한다(미션 7). 고치는 일은 1-4강이다 (7.3절)."),
    box("ue", None,
        "`AActor::Tick( float DeltaSeconds )`의 인자가 이것이다. 언리얼도 기본은 프레임마다 dt가 달라지는 방식(가변 타임스텝)이고, "
        "프로젝트 설정의 고정 프레임 레이트 옵션으로 dt를 일정하게 만들 수 있다. 엔진 어디서든 "
        "`FApp::GetDeltaTime()`으로 같은 값을 읽는다."),
], lead="프레임 사이의 시간은 PC마다, 순간마다 다르다. 그 차이를 게임 로직이 느끼지 않게 해 주는 숫자가 델타 타임이다.")

ch4 = chapter(4, "게임 코드를 부르는 길: 콜백", [
    h3("4.1", "왜 콜백인가"),
    layers([
        ("CLIENT", [("main.cpp", "`cbUpdate`를 정의하고 넘긴다", "accent")]),
        ("ENGINE", [("GEngine", "받아서 보관하고, 프레임마다 부른다")]),
    ], "포함과 링크의 방향은 Client → Engine 한쪽뿐이다. 호출은 프레임마다 거꾸로 Engine → Client로 일어난다."),
    p("Engine은 정적 라이브러리이고 Client를 모른다 (1-1강 2.1절). `main.cpp`를 포함하지도, 그 안의 함수 이름을 "
      "알지도 못한다. 그런데 프레임마다 게임 코드를 불러야 한다. 방법은 하나다. Client가 “이 함수를 불러 달라”고 "
      "주소를 넘겨 주고, Engine은 무엇인지 모른 채 받아 두었다가 부른다. 그렇게 넘겨주는 함수가 **콜백**이다. "
      "1-1강 5.2절에서 `gladLoadGLLoader`에 `glfwGetProcAddress`를 넘긴 것도 같은 일이었다."),

    h3("4.2", "받아 둘 그릇: std::function"),
    fn("std::function",
       "template< class R, class... Args >\n"
       "class std::function< R( Args... ) >;",
       "“이런 모양으로 부를 수 있는 것”을 무엇이든 하나 담아 두는 그릇이다. 담아 둔 것을 함수처럼 부를 수 있다.",
       params=[("`R( Args... )`", "담을 것의 모양. 돌려주는 타입과 인자 타입들이다. `void( float )`는 "
                                 "“`float` 하나를 받고 아무것도 돌려주지 않는다”는 뜻이다")],
       notes=[("담을 수 있는 것", "보통 함수, 람다, 변수를 캡처한 람다, `operator()`가 있는 객체. 모양만 맞으면 된다"),
              ("부르는 법", "`f( 0.016f )`. 담긴 것이 불린다"),
              ("비어 있을 때", "아무것도 담지 않은 것은 `if ( f )`에서 거짓이다. 빈 것을 부르면 `std::bad_function_call` 예외가 던져진다"),
              ("대가", "무엇이 담겼는지 타입에 드러나지 않고, 호출이 한 단계를 거쳐 간다"),
              ("헤더", "`<functional>`. `Engine/framework.h:13`에서 이미 포함한다")],
       lib="C++ 표준"),
    box("ex", "예시: 담고, 부르고, 비었는지 본다", [
        code(r"""
void PrintHalf( float value );                           // some function with the right shape

std::function<void( float )> f;                          // empty for now
bool has_target = static_cast<bool>( f );                // false

f = PrintHalf;                                           // holds a plain function
f = []( float value ) { /* ... */ };                     // now holds a lambda instead
f( 3.0f );                                               // calls whatever it holds
""", tag="syntax"),
        p("`f`의 타입은 처음부터 끝까지 `std::function<void( float )>` 하나다. 무엇을 담든 부르는 쪽 코드는 바뀌지 않는다. "
          "엔진이 Client의 함수가 무엇인지 몰라도 되는 이유가 여기 있다."),
    ]),

    h3("4.3", "같은 일을 하는 다른 방법"),
    table([24, 38, 38], ["방법", "좋은 점", "아쉬운 점"], [
        ["`std::function`", "함수, 람다, 캡처한 람다를 가리지 않고 받는다", "호출이 한 단계 거쳐 간다. 무엇이 들어 있는지 타입에 드러나지 않는다"],
        ["함수 포인터", "가장 가볍다. C 라이브러리와 그대로 통한다", "캡처한 람다를 받지 못한다. 상태를 따로 넘겨야 한다"],
        ["가상 함수 (상속)", "Update 외에 Init, Shutdown 같은 짝을 한 클래스에 모을 수 있다", "Client가 엔진의 클래스를 상속해야 한다"],
    ], cell_cls=["lab", "", ""]),
    p("이 강에서는 두 가지를 다 써 본다. Update 콜백은 `std::function`으로 받고, 6장의 창 크기 콜백은 GLFW가 "
      "정해 둔 함수 포인터 타입으로 받는다. GLFW는 C 라이브러리라서 `std::function`을 모른다."),
    box("ue", None,
        "언리얼의 델리게이트가 같은 자리에 있다. `OnClicked.AddDynamic( this, &UMyWidget::HandleClick )`은 "
        "“나중에 이 함수를 불러 달라”고 맡기는 일이고, 버튼은 누가 맡겼는지 모른 채 부른다."),
    box("cs", None,
        "`std::function`이 서로 다른 타입을 같은 그릇에 담는 기법을 타입 소거(type erasure)라고 한다. 안에서는 "
        "가상 함수와 비슷한 간접 호출이 일어난다. 함수 포인터는 주소 하나뿐이라 “어떤 변수와 함께 불러야 하는지”를 "
        "담지 못하고, 람다의 캡처가 그 빈자리를 채운다. 프로그래밍 언어론의 클로저(closure)다."),
], lead="엔진은 프레임마다 게임 코드를 불러야 하는데, 게임 코드가 무엇인지는 모른다. 콜백이 그 사이를 잇는다.")

ch5 = chapter(5, "한 프레임의 순서와 더블 버퍼링", [
    table([22, 26, 52], ["단계", "하는 일", "이 순서인 이유"], [
        ["시간 재기", "dt를 계산한다", "이번 프레임의 모든 로직이 같은 dt를 쓰도록 맨 앞에서 한 번만 잰다"],
        ["이벤트 처리", "`glfwPollEvents()`", "입력과 닫기 버튼이 여기서 전달된다. Update보다 앞이어야 이번 프레임의 입력이 "
                                     "이번 프레임의 로직에 닿는다"],
        ["지우기", "`glClear( … )`", "지난 프레임의 그림을 지운다. 그리기보다 앞이어야 한다"],
        ["Update(dt)", "게임 코드가 돈다", "지금은 그리는 단계가 따로 없어서, 그리는 일이 생기면 그것도 여기서 한다"],
        ["내보내기", "`glfwSwapBuffers( … )`", "다 그린 그림을 화면에 내보낸다. 맨 끝이어야 한다"],
    ], cell_cls=["lab", "", ""]),
    p("1-3강에서 Update와 내보내기 사이에 한 줄이 더 들어간다(입력 상태를 다음 프레임으로 넘기는 일). "
      "그 자리가 왜 거기인지는 그때 본다."),

    h3("5.1", "더블 버퍼링"),
    fig_buffers(),
    p("그리는 도중의 화면을 보여 주면 반쯤 지워진 그림이 깜빡인다. 그래서 보이지 않는 버퍼에 다 그린 뒤 한 번에 "
      "바꿔 낸다. `glClearColor`로 정한 색이 화면에 나오는 것도 지우기와 교체를 거쳐서다. 1-1강 5.1절의 그림에서 "
      "창 안에 버퍼가 둘 있던 것이 이것이다."),
    p("교체한 뒤 back buffer에 무엇이 남아 있는지는 정해져 있지 않다. 지난 그림이 그대로일 수도, 아닐 수도 있다. "
      "그래서 매 프레임 지우고 시작한다."),

    h3("5.2", "수직 동기"),
    fn("glfwSwapInterval", "void glfwSwapInterval(int interval);",
       "버퍼를 맞바꾸기 전에 모니터의 화면 갱신을 몇 번 기다릴지 정한다. 1이면 화면 갱신에 맞춰 바꾼다(수직 동기).",
       params=[("`interval`", "기다릴 화면 갱신 횟수. 0이면 기다리지 않고 바로 바꾼다. 1이면 한 번 기다린다")],
       returns="없다",
       fails="현재 컨텍스트가 없으면 `GLFW_NO_CURRENT_CONTEXT` 오류가 난다",
       notes=[("부르는 순서", "`glfwMakeContextCurrent()` 뒤 (1-1강 5.1절)"),
              ("부르지 않으면", "플랫폼과 그래픽 드라이버의 기본값을 따른다. PC에 따라 60FPS로 묶일 수도, 수천 FPS로 돌 수도 있다"),
              ("주의", "그래픽 드라이버의 설정이 프로그램의 요청을 덮어쓸 수 있다. 불렀다고 반드시 그대로 되지는 않는다"),
              ("선언된 곳", "`include/GLFW/glfw3.h:6210`")],
       lib="GLFW 3.4"),
    p("수직 동기를 켜면 `glfwSwapBuffers`가 다음 화면 갱신까지 기다렸다가 돌아온다. 60Hz 모니터라면 한 바퀴가 "
      "약 0.0167초보다 짧아질 수 없고, dt도 그 근처에서 고른 값이 된다. 끄면 그릴 수 있는 만큼 빨리 돈다. "
      "이 강에서는 이 함수를 부르지 않는다. 값을 누가 정할지와 함께 1-4강에서 다룬다 (7.3절)."),
    box("api", None,
        "DX11에서는 `IDXGISwapChain::Present( 1, 0 )`의 첫 인자가 스왑 간격이다. 버퍼 교체와 수직 동기가 한 호출에 "
        "들어 있다. OpenGL에서는 교체(`glfwSwapBuffers`)와 간격(`glfwSwapInterval`)이 따로이고, 간격은 한 번 정해 "
        "두면 계속 쓰인다."),
], lead="다섯 단계의 순서는 대부분 바꿀 수 없다. 하나를 옮기면 무엇이 깨지는지로 이유를 확인한다.")

ch6 = chapter(6, "창 크기가 바뀔 때: 뷰포트", [
    p("사용자가 창의 모서리를 끌어 크기를 바꾸면 그림이 그려지는 영역의 크기도 바뀐다. OpenGL은 그 사실을 스스로 "
      "알아채지 않는다. “이제 이 크기에 맞춰 그려라”를 프로그램이 알려 줘야 하고, 그러려면 크기가 바뀐 순간을 "
      "알아야 한다. 이 장의 두 함수가 그 일을 한다."),
    fn("glfwSetFramebufferSizeCallback",
       "typedef void (* GLFWframebuffersizefun)(GLFWwindow* window, int width, int height);\n"
       "GLFWframebuffersizefun glfwSetFramebufferSizeCallback(GLFWwindow* window,\n"
       "                                                      GLFWframebuffersizefun callback);",
       "그 창의 프레임버퍼 크기가 바뀔 때마다 불러 줄 함수를 등록한다.",
       params=[("`window`", "지켜볼 창"),
               ("`callback`", "등록할 함수. 첫 줄의 `typedef`가 정한 모양이어야 한다. `nullptr`이면 등록을 지운다")],
       returns="전에 등록되어 있던 함수. 없었으면 `nullptr`",
       fails="GLFW가 초기화되지 않았으면 `GLFW_NOT_INITIALIZED` 오류를 내고 `nullptr`을 돌려준다",
       notes=[("콜백이 받는 것", "`window`는 크기가 바뀐 창, `width`와 `height`는 새 크기다. 단위는 픽셀이다"),
              ("불리는 때", "GLFW가 이벤트를 처리하는 동안"),
              ("부르는 순서", "창을 만든 뒤, main 스레드에서. 창 하나에 하나만 등록되고, 다시 등록하면 앞의 것이 밀려난다"),
              ("선언된 곳", "`include/GLFW/glfw3.h:1759`, `:4465`")],
       lib="GLFW 3.4"),
    p("이름이 “창 크기”가 아니라 “프레임버퍼 크기”인 데는 이유가 있다. `glfwCreateWindow`에 준 너비와 높이는 화면 "
      "좌표 단위이고(1-1강 4장), 그림이 그려지는 버퍼는 픽셀 단위다. 화면 배율이 100%가 아닌 모니터에서는 두 숫자가 "
      "다를 수 있다. OpenGL에 넘길 숫자는 늘 픽셀 쪽이다."),
    fn("glViewport", "void glViewport(GLint x, GLint y, GLsizei width, GLsizei height);",
       "프레임버퍼 안에서 그림이 그려질 사각형을 정한다. 컨텍스트의 상태로 저장된다.",
       params=[("`x`, `y`", "사각형의 왼쪽 아래 모서리. 프레임버퍼의 왼쪽 아래가 (0, 0)이다. 단위는 픽셀"),
               ("`width`, `height`", "사각형의 너비와 높이. 단위는 픽셀")],
       returns="없다",
       notes=[("처음 값", "컨텍스트가 처음 창에 연결될 때 그 창 전체로 정해진다"),
              ("바꾸지 않으면", "창이 커져도 그림은 처음 크기의 사각형 안에만 그려진다"),
              ("주의", "`glClear`는 뷰포트와 상관없이 버퍼 전체를 채운다. 지우기만 하는 지금은 차이가 보이지 않는다"),
              ("부르는 순서", "`gladLoadGLLoader()`가 성공한 뒤 (1-1강 5.2절)")],
       lib="OpenGL"),
    fig_viewport(),
    box("ex", "예시: 창을 키웠는데 뷰포트를 그대로 두면", [
        p("800 × 600으로 만든 창을 1200 × 900으로 키웠다고 하자. 뷰포트는 여전히 `( 0, 0, 800, 600 )`이다. "
          "그림은 왼쪽 아래의 800 × 600 사각형 안에만 그려지고, 오른쪽과 위쪽에 늘어난 부분은 배경색만 보인다. "
          "크기 콜백에서 `glViewport( 0, 0, 1200, 900 )`에 해당하는 호출을 하면 그림이 창 전체로 다시 펴진다."),
    ]),
    box("point", "통로는 여기서, 확인은 2-2강에서",
        "1-1강 자료는 창 크기 변화의 처리를 2-2강으로 미뤘다. 지금은 화면에 그리는 것이 없어서 뷰포트를 바꿔도 눈에 "
        "보이는 차이가 없기 때문이다. 다만 “크기가 바뀌면 Client의 함수를 부른다”는 통로는 콜백이 주제인 이 강에서 "
        "만들어 둔다. 삼각형을 그리는 2-2강에서 이 통로가 실제로 일하는 것을 본다."),
], lead="두 번째 콜백이다. Update 콜백은 엔진이 프레임마다 부르고, 이 콜백은 창 크기가 바뀔 때 GLFW가 부른다.")

ch7 = chapter(7, "설계", [
    h3("7.1", "파일 배치"),
    tree("""
Engine/
└── Core/
    ├── EngineCore.h  #new members: Run, Update, two setters, three variables
    └── EngineCore.cpp  #the loop moves in here
Client/
└── main.cpp  #the loop moves out; two callbacks are defined and registered
"""),

    h3("7.2", "선언 스케치"),
    code(r"""
class GEngine
{
public:
    // ... lesson 1-1: InitErrorCode, Get(), GetMainWindow(), Init() ...

    void SetUpdateCallback( std::function<void( float )> func );
    void SetFramebufferSizeCallback( GLFWframebuffersizefun func );   // what does it do with func?
    void Run();                                                       // when does this return?

private:
    void Update( float delta_time );                  // what if nobody set a callback?
    std::function<void( float )> _on_update;

    bool   _is_running = true;                        // nothing sets it to false yet (lesson 1-4)
    double _last_frame_time{};                        // why double here ...
    double _delta_time{};                             // ... and float in Update()?
};
""", title="Engine/Core/EngineCore.h — what this lesson adds", tag="sketch"),
    code(r"""
void cbFramebufferSize( GLFWwindow* window, int width, int height );
void cbUpdate( float delta_time );

// in main, after Init() has succeeded:
engine.SetFramebufferSizeCallback( cbFramebufferSize );
engine.SetUpdateCallback( cbUpdate );
engine.Run();                             // the temporary loop of lesson 1-1 is gone
""", title="Client/main.cpp when this lesson is done", tag="usage"),
    box("decide", "콜백 없이 Run()이 불리면",
        "죽지만 않으면 된다. 셋 중에서 고른다. (가) 아무 말 없이 돈다. 간단하지만 등록을 잊은 것을 알아채기 어렵다. "
        "(나) 한 줄 알리고 돈다. 지금 쓸 수 있는 것은 `std::cout`뿐이고 1-5강에서 Logger로 바꾼다. "
        "(다) 돌지 않고 돌아온다. 실수는 바로 드러나지만 빈 창만 띄워 보는 일도 못 하게 된다."),

    keep(h3("7.3", "1-4강으로 넘기는 것"),
    table([20, 60, 20], ["넘기는 것", "지금 일어나는 일", "어디서 다루나"], [
        ["첫 프레임의 dt", "첫 dt에 초기화에 걸린 시간이 통째로 들어간다 (3.3절)", "1-4강 6.4절"],
        ["dt의 상한", "창을 끌거나 중단점에서 멈춘 뒤의 긴 dt가 그대로 넘어간다 (3.3절)", "1-4강 6.4절"],
        ["수직 동기", "`glfwSwapInterval`을 부르지 않아 드라이버 설정을 따른다 (5.2절)", "1-4강 6.4절"],
    ], cell_cls=["lab", "", "c"])),
    p("이 셋은 미션 7에서 눈으로 확인만 한다. 그 밖에 `_is_running`을 끄는 함수와 루프 뒤의 정리는 1-4강, Update와 "
      "그리기를 가르는 일은 4-6강이다. 고정 타임스텝은 이 강의의 범위 밖이다."),
], lead="새 파일은 없다. 1-1강에서 만든 클래스에 멤버가 더해지고, 루프가 `main`에서 엔진으로 자리를 옮긴다. "
        "이름과 인자는 7.2절의 스케치 그대로 쓴다. 1-3강부터의 자료가 이 선언을 기준으로 쓰여 있다.")

ch8 = chapter(8, "구현 미션", [
    steps([
        ("루프를 `Run()`으로 옮긴다",
         "`main`의 임시 루프를 지우고 같은 일을 `GEngine::Run()` 안에서 한다. `main`은 `engine.Run()`만 부른다. "
         "화면은 임시 루프일 때와 똑같아야 한다.",
         ["`Run()` 안에서는 창을 얻으러 갈 필요가 없다. 루프 조건에는 2.2절의 두 깃발이 다 들어간다."]),
        ("dt를 잰다",
         "프레임의 맨 앞에서 dt를 계산해 멤버에 넣는다. 디버거로 값을 본다. 0.016 근처이거나 그보다 훨씬 작으면 된다.",
         ["한 프레임에 시각을 몇 번 읽어야 하는가. 3장의 예시 표를 손으로 한 줄 더 이어 본다.",
          "dt가 프레임마다 커진다면 갱신 하나를 잊은 것이다."]),
        ("Update 콜백을 만든다",
         "`SetUpdateCallback`과 `Update`를 쓰고, `Run()`이 프레임마다 `Update`에 dt를 넘기게 한다. `main`에 `cbUpdate`를 "
         "정의해 등록하고, 그 안에서 받은 dt를 콘솔에 찍어 불리는지 확인한다.",
         ["콜백을 등록하지 않고 `Run()`을 불러도 죽지 않아야 한다. 4.2절 카드의 “비어 있을 때” 칸을 본다.",
          "`double`을 `float` 인자에 넘기는 자리는 한 곳이다. 변환을 눈에 보이게 적는다."]),
        ("시간으로 색을 바꾼다",
         "`cbUpdate`에서 dt를 써서 배경색이 2초에 한 번씩 밝아졌다 어두워지게 한다. 스톱워치로 주기를 잰다.",
         ["흐른 시간을 더해 갈 변수는 `cbUpdate`가 끝나도 사라지지 않아야 한다.",
          "`glClearColor`는 색을 적어 두기만 한다 (1-1강 5.3절). 실제로 칠하는 호출은 어디에 있는가."]),
        ("순서를 바꿔 본다",
         "5장의 표와 내 `Run()`을 한 줄씩 맞춰 본다. 그다음 지우기를 Update 뒤로, 내보내기를 지우기 앞으로 하나씩 "
         "옮겨 보고 화면이 어떻게 되는지 적은 뒤 되돌린다."),
        ("창 크기 콜백의 통로를 만든다",
         "`SetFramebufferSizeCallback`을 쓰고, `main`에 `cbFramebufferSize`를 정의해 등록한다. 그 안에서 뷰포트를 새 "
         "크기에 맞춘다. 창 크기를 바꿀 때 불리는지 콘솔 출력으로 확인한다.",
         ["등록은 창이 만들어진 뒤여야 한다. 콜백이 받는 인자 셋 중 둘이 `glViewport`로 간다 (6장)."]),
        ("dt가 튀는 순간을 본다",
         "dt를 찍는 줄을 둔 채로 세 가지를 해 보고 숫자를 적는다. (가) 첫 프레임의 dt. (나) 제목 표시줄을 3초 잡고 "
         "있다가 놓은 직후의 dt. (다) 중단점에 멈췄다가 계속했을 때의 dt. 고치지는 않는다 (7.3절)."),
        ("확인하고 커밋한다", "임시로 넣은 콘솔 출력을 지우고 10장의 기준을 확인한 뒤 커밋한다. 그 뒤에 4월의 코드와 "
                     "비교하고, v2 자료를 해설로 읽는다 (10.1절)."),
    ]),
], lead="한 단계가 끝날 때마다 빌드해서 눈으로 확인한다. 힌트는 막혔을 때 위에서부터 하나씩만 본다.", pb=True)

ch9 = chapter(9, "흔한 함정", [
    table([32, 38, 30], ["증상", "원인", "확인 방법"], [
        ["실행하자마자 `std::bad_function_call`로 죽는다", "비어 있는 `std::function`을 불렀다", "4.2절 카드의 “비어 있을 때”"],
        ["dt가 프레임마다 계속 커진다", "“지난번에 읽은 시각”을 갱신하지 않았다", "디버거로 두 멤버의 값을 본다"],
        ["dt가 늘 0이다", "시각을 읽은 직후에 갱신하고 나서 뺐다. 순서가 바뀌었다", "3장의 예시 표와 맞춰 본다"],
        ["색이 변하는 속도가 PC마다 다르다", "dt를 곱하지 않고 프레임마다 고정된 양을 더했다", "3.1절"],
        ["색이 변하지 않는다", "`cbUpdate`를 등록하지 않았거나 `Run()` 뒤에 등록했다", "`Update`에 중단점을 건다"],
        ["시작하자마자 색이 한 번 건너뛴다", "첫 프레임의 dt가 크다", "3.3절. 지금은 정상이다 (7.3절)"],
        ["화면이 깜빡이거나 검게 나온다", "지우기, Update, 내보내기의 순서가 바뀌었다", "5장의 표"],
        ["`cbFramebufferSize`가 불리지 않는다", "`Init`보다 먼저 등록했다. 그때는 창이 아직 없다", "등록하는 줄과 `Init`의 순서"],
        ["콜백을 넘기는 줄에서 변환할 수 없다는 컴파일 오류", "콜백의 인자 모양이 정해진 것과 다르다",
         "`cbUpdate`는 `void( float )`, 크기 콜백은 `include/GLFW/glfw3.h:1759`"],
        ["`LNK2019`가 `cbUpdate`를 가리킨다", "선언만 하고 정의를 쓰지 않았다", "`main.cpp` 아래쪽"],
    ], compact=True),
], lead="증상에서 거꾸로 찾는 표다.")

ch10 = chapter(10, "완료 기준", [
    checklist([
        "배경색이 2초 주기로 밝아졌다 어두워진다. 스톱워치로 잰 주기가 맞다.",
        "창의 닫기 버튼을 누르면 `Run()`이 돌아오고 프로그램이 끝난다.",
        "`Client/`에서 `glfwPollEvents`, `glfwSwapBuffers`, `glfwWindowShouldClose`가 검색되지 않는다. 루프는 엔진이 맡는다.",
        "`SetUpdateCallback`을 부르는 줄을 지우고 실행해도 죽지 않는다.",
        "창 크기를 바꾸면 `cbFramebufferSize`가 불린다 (임시 출력으로 확인하고 지웠다).",
        "미션 5와 7에서 본 것이 적혀 있다.",
        "커밋 하나로 묶였다.",
    ]),
    console(Raw(
        '<span class="dim">dt</span> 0.2314    <span class="dim">first frame: includes the start-up time</span>\n'
        '<span class="dim">dt</span> 0.0167\n'
        '<span class="dim">dt</span> 0.0166\n'
        '<span class="dim">framebuffer</span> 1280 x 720\n'
        '<span class="dim">dt</span> 3.0412    <span class="dim">after holding the title bar for 3 seconds</span>'
    ), title="미션 도중의 임시 출력 (형식과 숫자는 예시)"),

    h3("10.1", "끝낸 뒤에: 4월의 코드와 비교한다"),
    code(r"""
git diff first-pass-2026-04 -- Engine/Core/EngineCore.cpp Engine/Core/EngineCore.h Client/main.cpp
""", lang="text", title="run in the repository root", tag="usage"),
    p("태그 `first-pass-2026-04`에는 4월에 쓴 1차 코드가 그대로 있다. 기준을 다 채운 뒤에 위 명령으로 지금 코드와 나란히 "
      "본다. 1차 코드에는 1-3강의 내용(입력)도 들어 있으니 `Run`, `Update`, 두 콜백만 비교한다. 다른 곳이 왜 다른지 "
      "설명할 수 있으면 된다. 1차 코드를 줄 단위로 해설한 자료가 `Legacy/ClaudGL_1-2_GameLoop_v2.pdf`다."),
], lead="전부 눈이나 검색으로 확인할 수 있는 조건이다.")

ch11 = chapter(11, "생각해 볼 질문", [
    exgroup("A", "코드를 보지 않고 답하시오", "한두 문장으로, 이유까지"),
    qlist([
        "`position += 5.0f;`를 프레임마다 실행하면 60FPS인 PC와 144FPS인 PC에서 1초 뒤 위치는 각각 얼마인가?",
        "“지난번에 읽은 시각”을 `float`로 바꾸면 언제부터 어떤 문제가 생기는가?",
        "Engine이 `cbUpdate`를 직접 부르지 않고 콜백으로 받는 이유를 프로젝트 구성으로 설명하시오.",
        "창의 제목 표시줄을 3초 동안 잡고 있다가 놓으면 다음 `cbUpdate`가 받는 `delta_time`은 얼마쯤인가?",
        "루프에서 `glfwSwapBuffers`를 지우면 화면은 어떻게 보이는가?",
        "크기 콜백에서 `glViewport`를 부르는데도 지금은 창 크기를 바꿔도 달라 보이는 것이 없다. 왜인가?",
    ], lines=3),
], lead="답을 보기 전에 소리 내어 설명해 본다. 막히는 문항이 다시 읽을 장이다.", pb=True)

ch12 = chapter(12, "해설", [
    answers("질문 A", [
        ("300과 720.", "프레임 수만큼 더해지기 때문이다. `speed * dt`로 쓰면 둘 다 같은 값이 된다. (3.1절)"),
        ("실행 후 두 시간 남짓부터 dt가 1밀리초 단위로만 재진다.",
         "큰 `float` 값에서는 이웃한 값 사이의 간격이 넓어진다. 움직임이 미세하게 끊겨 보인다. (3.2절)"),
        ("Engine은 Client보다 먼저 만들어지는 정적 라이브러리라서 Client의 함수를 알 수 없다.",
         "의존은 Client → Engine 한 방향이다. 거꾸로 부르려면 Client가 주소를 넘겨 줘야 한다. (4.1절)"),
        ("약 3초.", "끄는 동안 `glfwPollEvents()`가 돌아오지 않아 한 바퀴가 3초짜리가 된다. (3.3절)"),
        ("창의 내용이 갱신되지 않는다.",
         "모든 그리기가 back buffer에만 쌓이고 화면에 보이는 front buffer는 바뀌지 않는다. (5.1절)"),
        ("`glClear`는 뷰포트와 상관없이 버퍼 전체를 채우기 때문이다.",
         "뷰포트는 “그림을 그릴 사각형”을 정한다. 지금은 지우기만 하고 그리는 것이 없다. 2-2강에서 삼각형을 그리면 "
         "차이가 보인다. (6장)"),
    ]),
])

ch13 = glossary_chapter(13, [
    ("게임 루프", "game loop", "입력 · 갱신 · 그리기를 끝날 때까지 되풀이하는 반복문"),
    ("델타 타임", "delta time (dt)", "직전 프레임 한 바퀴에 걸린 시간, 초 단위"),
    ("가변 타임스텝", "variable timestep", "프레임마다 실제 걸린 시간을 dt로 쓰는 방식. 이 강의 방식"),
    ("고정 타임스텝", "fixed timestep", "로직을 일정한 간격으로만 돌리는 방식"),
    ("콜백", "callback", "나중에 불러 달라고 넘겨 두는 함수"),
    ("제어의 역전", "inversion of control", "내 코드가 틀을 부르는 대신 틀이 내 코드를 부르는 구조"),
    ("타입 소거", "type erasure", "서로 다른 타입을 한 그릇에 담게 해 주는 기법. `std::function`"),
    ("더블 버퍼링", "double buffering", "보이지 않는 버퍼에 그린 뒤 보이는 버퍼와 맞바꾸는 방식"),
    ("수직 동기", "vsync", "버퍼 교체를 모니터의 화면 갱신 시점에 맞추는 것"),
    ("스왑 간격", "swap interval", "버퍼 교체 전에 기다릴 화면 갱신 횟수. `glfwSwapInterval`"),
    ("프레임버퍼", "framebuffer", "그림이 그려지는 픽셀 버퍼. 크기는 픽셀 단위다"),
    ("뷰포트", "viewport", "프레임버퍼 안에서 그림이 그려지는 사각형. `glViewport`"),
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
