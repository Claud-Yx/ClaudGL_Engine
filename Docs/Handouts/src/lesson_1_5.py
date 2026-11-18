"""Lesson 1-5 -- Logger, built from scratch.

Version 2: the engine code was removed on 2026-11-16 (first pass kept at tag
first-pass-2026-04), so the logger skeleton that version 1 quoted is no longer
in the repository. This version gives the same declarations as sketches, adds
function cards, worked examples and drawn figures, and refers to engine code by
function name only. Chapter and section numbers are unchanged because other
handouts point at them (3.1, 5.2, 5.3, 6.2, 6.4, mission steps 6 and 7).

Version 4 (2026-11-19): the reader found the missions vague and scattered
(same change as lesson 1-4 v4). Each mission step now states what must be done
as plain statements and ends with a "통과" (pass) condition, and a new last
chapter 13 "할 일 목록" spells every mission out as a task list with a way to
check each task, plus a default choice for each decision of 6.2 for when the
reader is stuck. Chapters 1 to 12 keep their numbers; the eight mission steps
keep their numbers and meaning.

Run:  python -I src/lesson_1_5.py      (from Docs/Handouts, with the handout venv)
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

ME = lesson("1-5")
OUT_PDF = ROOT / handout_name(ME["id"])
OUT_HTML = ROOT / "_build" / "lesson_1_5.html"

# Project files (.vcxproj, .gitignore, framework.h, glad.h) were read on this day.
READ_DATE = "2026-11-16"

# HTML collapses runs of ordinary spaces, so padding shown inside an inline code
# chip is written with no-break spaces.
SP = " "

COVER = cover(
    f"CLAUDGL ENGINE · PART {ME['part']} · {ME['id']} · v{ME['ver']}",
    Raw('G<span class="ac">Logger</span>'),
    ME["title"],
    "엔진이 지금 무슨 일을 하고 있는지 스스로 말하게 만든다",
    [
        ("목표 결과물", "콘솔과 파일에 시각·레벨·카테고리가 붙은 로그가 찍히고, `std::cout`은 로거 안에만 남는다"),
        ("핵심 개념", "로그 레벨과 카테고리 · 매크로와 `std::source_location` · `std::format` · 콘솔 색 · 버퍼와 flush"),
        ("선수 지식", "1-1 〜 1-3강을 끝낸 코드. 1-4강은 먼저 끝냈어도, 아직이어도 된다 (6.4절)"),
        ("예상 시간", f"읽기 1시간 + 구현 3시간 남짓 (계획서 기준 {ME['hours']}시간)"),
        ("건드릴 파일", "`Engine/Enum/LogLevel.h`, `Engine/Core/Logger.h`·`.cpp` (새 파일), `Engine/Core/EngineCore.cpp`, "
                   "`Engine/Manager/InputManager.cpp`, `Client/main.cpp`"),
        ("코드 기준", f"엔진 코드는 함수 이름으로 가리킨다. 프로젝트 설정과 헤더의 줄 번호는 {READ_DATE}의 파일 기준이다"),
    ],
    note=("읽는 법",
          "Logger는 이 강에서 처음부터 만든다. 1.2절의 선언이 뼈대이고 본체는 전부 직접 쓴다. 2 〜 5장의 개념과 함수 설명을 "
          "읽은 뒤, 6장에서 결정할 것을 적고 7장의 미션을 순서대로 구현한다. 미션이 무엇을 하라는 것인지 분명하지 "
          "않으면 13장의 할 일 목록을 본다. 코드 블록은 완성본이 아니다."),
    toc=["왜 필요한가", "로그 한 줄의 구성", "호출한 자리를 어떻게 아는가", "메시지 조립: std::format",
         "어디에 쓰는가: 콘솔과 파일", "설계", "구현 미션", "흔한 함정", "완료 기준", "생각해 볼 질문", "해설", "용어집",
         "할 일 목록"],
)

# --------------------------------------------------------------------------

ch1 = chapter(1, "왜 필요한가", [
    h3("1.1", "지금 엔진이 말하는 방식"),
    p("1-1 〜 1-3강에서 쓴 코드에는 “문제가 생긴 자리”가 적어도 세 곳 있다. 그 자리에서 엔진이 무엇을 하는지는 "
      "직접 쓴 코드에 달려 있으므로, 미션에 들어가기 전에 아래 표의 자리를 열어 지금 무슨 일이 일어나는지 적어 둔다."),
    table([28, 30, 42], ["확인할 것", "볼 자리", "왜 문제인가"], [
        ["Update 콜백 없이 `Run()`을 불렀을 때", "`GEngine::Run`",
         "말이 없으면 “창은 뜨는데 아무 일도 없다”의 이유를 알 수 없다. `std::cout`으로 한 줄 찍고 있다면 그 줄에는 "
         "시각도 심각도도 없고, 끌 방법도 없다"],
        ["GLAD가 함수 주소를 얻지 못했을 때", "`GEngine::Init`의 실패 분기",
         "`Fail`만 돌려주면 이유가 남지 않는다. 1-4강을 먼저 했다면 `std::cerr`로 찍고 있을 것이다. 그 줄도 여기서 바꾼다"],
        ["잘못된 키로 상태를 물었을 때", "`MInputManager`의 조회 함수 셋 (`IsKeyPressed` 등)",
         "값 하나만 돌려주고 지나가면 잘못 부른 쪽은 틀린 줄 모른다"],
        ["그 밖에 화면에 글자를 찍는 곳", "`Engine/`에서 `std::cout`, `std::cerr`, `printf` 검색",
         "찍는 방식이 자리마다 다르면 한꺼번에 끄거나 파일로 남길 수 없다"],
    ], cell_cls=["lab", "", ""]),
    p("엔진이 커질수록 “화면이 검은데 왜인지 모르겠다”는 상황이 늘어난다. 2-1강부터는 GL이 내는 오류와 경고를 받아 적을 "
      "곳이 필요하고, 셰이더 컴파일 오류(2-4강)도 같은 통로로 나온다. 그 통로를 여기서 만든다."),
    box("ex", "예시: 같은 일을 알리는 두 줄", [
        console(Raw(
            'Shader compile failed\n'
            '<span class="dim">[14:02:07.320]</span> <span class="err">[Error]</span> [Render] '
            'Shader compile failed: basic.frag <span class="dim">(Shader.cpp:57)</span>'
        ), title="위: std::cout으로 찍은 줄 · 아래: 로거를 거친 줄 (형식과 숫자는 예시)"),
        p("아래 줄은 같은 소식에 네 가지를 더 달고 있다. 언제 일어났는지, 얼마나 심각한지, 어느 시스템의 일인지, 코드의 "
          "어디에서 났는지다. 무엇이 실패했는지도 메시지에 값으로 들어 있다. 2장에서 조각마다 살펴본다."),
    ]),

    h3("1.2", "만들 뼈대"),
    p("Logger는 엔진처럼 프로그램에 하나만 있는 객체로 만든다. 클래스의 모양은 아래와 같이 정해 두고 시작한다. "
      "본체는 한 줄도 없다."),
    code(r"""
#pragma once
// Which standard headers does this file use directly? (std::ofstream, std::string, std::string_view)

#include "Enum/LogLevel.h"

class GLogger
{
public:
    static GLogger& Get();                    // same idea as GEngine::Get() (lesson 1-1, chapter 7)

    void Init( const char* file_name );       // what must be ready when this returns?
    void Shutdown();                          // what is lost if nobody calls this?

    void Log( ELogLevel log_level, std::string_view category, const char* file, int line,
              const std::string& message );

private:
    // Which special member functions keep this a singleton?

    std::ofstream _log_file{};
    ELogLevel     _min_level{ ELogLevel::Trace };
};
""", title="Engine/Core/Logger.h", tag="sketch"),
    keep(table([32, 68], ["`Log()`의 매개변수", "뜻"], [
        ["`ELogLevel log_level`", "얼마나 심각한가 (2.1절)"],
        ["`std::string_view category`", "어느 시스템의 로그인가 (2.3절)"],
        ["`const char* file`, `int line`", "로그를 부른 자리. 누가 채워 넣는지가 3장의 주제다"],
        ["`const std::string& message`", "이미 완성된 문자열. 값을 끼워 넣는 조립은 `Log()` 밖에서 끝난다는 뜻이다 (4장)"],
    ], cell_cls=["lab", ""])),
    table([30, 44, 26], ["부품", "해야 하는 일", "다루는 곳"], [
        ["싱글턴 접근 `Get()`", "어디서 불러도 같은 객체를 돌려준다", "1-1강 7장"],
        ["`Init`", "로그 파일을 열고, 콘솔이 색 코드를 알아듣게 준비한다", "5.1절, 5.3절"],
        ["`Shutdown`", "남은 글자를 내보내고 파일을 닫는다", "5.2절"],
        ["`Log()` 본문", "거르고, 한 줄로 조립하고, 콘솔과 파일에 내보낸다", "2장, 4장, 5장"],
        ["최소 레벨 `_min_level`", "바꾸는 함수와 읽는 곳이 있어야 한다", "2.2절, 6.3절"],
        ["호출 매크로", "호출부가 파일과 줄을 손으로 적지 않게 한다", "3장"],
        ["`Init`·`Shutdown`을 부르는 곳", "엔진보다 먼저 켜지고 나중에 꺼져야 한다", "6.2절"],
    ], cell_cls=["lab", "", ""], compact=True),
], lead="1-3강까지의 엔진은 문제가 생겨도 거의 말이 없다. 말하는 방식도 자리마다 다르다. 먼저 지금 상태를 확인하고, "
        "만들 것의 모양을 본다.")

ch2 = chapter(2, "로그 한 줄의 구성", [
    Fig(104)
    .box(14, 10, 120, 30, kind="soft", r=4)
    .text(74, 30, "[14:02:07.318]", kind="mono", size=10.5)
    .box(150, 10, 70, 30, kind="accent", r=4)
    .text(185, 30, "[Warn ]", kind="mono", size=10.5)
    .box(240, 10, 70, 30, kind="soft", r=4)
    .text(275, 30, "[Input]", kind="mono", size=10.5)
    .box(330, 10, 140, 30, kind="soft", r=4)
    .text(400, 30, "Invalid key: 512", kind="mono", size=10.5)
    .box(484, 10, 162, 30, kind="soft", r=4)
    .text(565, 30, "(InputManager.cpp:41)", kind="mono", size=10.5)
    .line((74, 40), (74, 58), kind="muted")
    .line((185, 40), (185, 58), kind="muted")
    .line((275, 40), (275, 58), kind="muted")
    .line((400, 40), (400, 58), kind="muted")
    .line((565, 40), (565, 58), kind="muted")
    .text(74, 76, "시각", kind="t").text(74, 93, "언제 일어났나", kind="s", size=9.5)
    .text(185, 76, "레벨", kind="t").text(185, 93, "얼마나 심각한가", kind="s", size=9.5)
    .text(275, 76, "카테고리", kind="t").text(275, 93, "어느 시스템인가", kind="s", size=9.5)
    .text(400, 76, "메시지", kind="t").text(400, 93, "무슨 일인가", kind="s", size=9.5)
    .text(565, 76, "위치", kind="t").text(565, 93, "코드의 어디인가", kind="s", size=9.5)
    .render("로그 한 줄의 다섯 조각 (형식은 예시). 조각마다 나중에 로그를 읽는 사람의 질문 하나에 답한다."),
    keep(table([18, 82], ["조각", "메모"], [
        ["시각", "두 줄 사이에 얼마나 걸렸는지도 여기서 읽는다"],
        ["레벨", "걸러 내는 기준이자 색을 정하는 기준"],
        ["카테고리", "`Core`, `Input`, `Render`. 검색할 때 쓰는 손잡이"],
        ["메시지", "값이 들어간 문장. “실패했다”보다 “무엇이 왜 실패했다”"],
        ["위치", "파일과 줄 번호. 메시지만으로 찾기 어려울 때 쓴다"],
    ], cell_cls=["lab", ""], compact=True)),

    h3("2.1", "레벨"),
    code(r"""
#pragma once

enum class ELogLevel : int
{
    Trace,      // no values are written: which number does each name get?
    Debug,
    Info,
    Warning,
    Error,
    Fatal
};
""", title="Engine/Enum/LogLevel.h", tag="sketch"),
    table([14, 44, 42], ["레벨", "언제 쓰는가", "예"], [
        ["`Trace`", "흐름을 따라갈 때만 켜는 아주 잦은 기록", "프레임마다 찍는 값, 함수 진입"],
        ["`Debug`", "개발 중에만 궁금한 값", "창 크기, 읽어 들인 파일 수"],
        ["`Info`", "정상적으로 일어난 큰 일", "엔진 초기화 완료"],
        ["`Warning`", "이상하지만 계속 갈 수 있다", "잘못된 키 코드, 콜백이 비어 있음"],
        ["`Error`", "요청받은 일이 실패했다", "파일을 열지 못함"],
        ["`Fatal`", "더 진행할 수 없다", "GL 함수 로드 실패"],
    ], cell_cls=["lab", "", ""], compact=True),
    p("값을 적지 않았으므로 `Trace`가 0이고 아래로 갈수록 1씩 커진다. 심각할수록 큰 숫자다. 이 순서가 걸러 내기의 "
      "근거가 된다. `enum class`는 정수로 저절로 바뀌지 않지만, 같은 타입끼리는 `<`와 `>=`로 바로 비교된다."),

    h3("2.2", "최소 레벨로 걸러 낸다"),
    flow([
        ("호출", "레벨 + 메시지"),
        ("비교", "최소 레벨 이상인가", "accent"),
        ("조립", "시각·레벨·위치"),
        ("출력", "콘솔 · 파일", "dark"),
    ], "최소 레벨보다 낮으면 비교에서 끝난다. 비교가 조립보다 앞에 있어야 버려질 로그에 비용을 쓰지 않는다 (4.2절)."),
    p("최소 레벨이 `Warning`이면 `Trace`·`Debug`·`Info`는 찍히지 않는다. 평소에는 `Info`로 두고, 문제를 쫓을 때만 "
      "`Trace`까지 여는 식으로 쓴다. 그래서 레벨을 고를 때의 기준은 “이 줄을 평소에도 보고 싶은가”다."),
    box("ex", "예시: 같은 세 줄, 다른 최소 레벨", [
        code(r"""
LOG_DEBUG( "Core", "frame {}", frame );
LOG_INFO( "Core", "window resized to {}x{}", w, h );
LOG_WARN( "Audio", "device {} is missing", id );
""", title="three calls (the macro names are the examples of 6.1)", tag="usage"),
        Fig(104)
        .text(14, 33, "최소 레벨 Info", kind="t", anchor="start", size=10.5)
        .box(132, 14, 80, 30, "Trace", kind="ghost", r=4)
        .box(218, 14, 80, 30, "Debug", kind="ghost", r=4)
        .box(304, 14, 80, 30, "Info", kind="accent", r=4)
        .box(390, 14, 80, 30, "Warning", kind="accent", r=4)
        .box(476, 14, 80, 30, "Error", kind="accent", r=4)
        .box(562, 14, 80, 30, "Fatal", kind="accent", r=4)
        .text(14, 81, "최소 레벨 Warning", kind="t", anchor="start", size=10.5)
        .box(132, 62, 80, 30, "Trace", kind="ghost", r=4)
        .box(218, 62, 80, 30, "Debug", kind="ghost", r=4)
        .box(304, 62, 80, 30, "Info", kind="ghost", r=4)
        .box(390, 62, 80, 30, "Warning", kind="accent", r=4)
        .box(476, 62, 80, 30, "Error", kind="accent", r=4)
        .box(562, 62, 80, 30, "Fatal", kind="accent", r=4)
        .render("색이 든 칸은 찍히고 점선 칸은 버려진다. 위에서는 둘째와 셋째 호출이, 아래에서는 셋째 호출만 찍힌다."),
    ]),

    h3("2.3", "카테고리"),
    p("레벨이 세로축이라면 카테고리는 가로축이다. 로그가 수천 줄이 되면 “입력 쪽 경고만” 보고 싶어진다. 1.2절의 선언은 "
      "카테고리를 `std::string_view`로 받는다. 문자열이면 새 카테고리를 만드는 데 아무 준비가 필요 없고, 대신 "
      "오타(`\"Inptu\"`)를 컴파일러가 잡아 주지 못한다."),
    box("ue", None,
        "`UE_LOG( LogTemp, Warning, TEXT( \"...\" ) )`의 세 인자가 카테고리, 레벨(Verbosity), 메시지다. 레벨은 `Fatal`, "
        "`Error`, `Warning`, `Display`, `Log`, `Verbose`, `VeryVerbose` 일곱 단계이고 `Fatal`은 찍은 뒤 프로그램을 "
        "멈춘다. 카테고리는 문자열이 아니라 `DECLARE_LOG_CATEGORY_EXTERN`으로 선언하는 객체라서, 카테고리마다 "
        "레벨을 따로 조절할 수 있다 (콘솔 명령 `Log LogTemp Verbose`)."),
], lead="로그 한 줄은 다섯 조각으로 이루어진다.")

ch3 = chapter(3, "호출한 자리를 어떻게 아는가", [
    p("위치 정보는 `Log()`를 **부른 쪽**의 파일과 줄이어야 쓸모가 있다. 그런데 함수는 자기를 누가 불렀는지 모른다."),
    code(r"""
void GLogger::Log( /* ... */ )
{
    // __FILE__ and __LINE__ are replaced right here, inside Logger.cpp
    std::cout << __FILE__ << ":" << __LINE__;   // always "Logger.cpp:<this line>"
}
""", title="every log line points at the logger itself", tag="bad"),
    Fig(132)
    .text(170, 16, "함수 본문에 적으면", kind="t")
    .box(30, 28, 126, 46, "main.cpp 12행", "Log( … ) 호출")
    .arrow((156, 51), (184, 51))
    .box(184, 28, 126, 46, "Logger.cpp 40행", "__LINE__", kind="accent")
    .text(170, 98, "찍히는 값: 40", kind="accent", size=11)
    .text(170, 116, "어디서 불러도 같다", kind="s", size=9.5)
    .line((330, 8), (330, 124), kind="muted dash")
    .text(490, 16, "매크로 본문에 적으면", kind="t")
    .box(350, 28, 126, 46, "main.cpp 12행", "LOG( … ) 호출")
    .arrow((476, 51), (504, 51))
    .box(504, 28, 126, 46, "main.cpp 12행", "… __LINE__ …", kind="accent")
    .text(490, 98, "찍히는 값: 12", kind="accent", size=11)
    .text(490, 116, "매크로가 그 자리에 펼쳐진다", kind="s", size=9.5)
    .render("`__LINE__`은 그 글자가 놓인 줄의 번호가 된다. 함수 본문은 한 곳에 있고, 매크로 본문은 쓰는 자리마다 복사된다. "
            "(줄 번호는 예시)"),

    h3("3.1", "방법 하나: 매크로"),
    p("`__FILE__`과 `__LINE__`은 전처리기가 **그 글자가 적힌 자리**의 파일 이름과 줄 번호로 바꿔 넣는 매크로다. "
      "매크로 호출은 함수 호출과 달리 본문이 호출한 자리에 그대로 펼쳐진다. 그래서 매크로 본문 안에 적은 `__LINE__`은 "
      "매크로를 쓴 줄의 번호가 된다."),
    code(r"""
#define LINE_HERE() ( __LINE__ )

int a = LINE_HERE();   // the number of THIS line, not the line of the #define
""", tag="syntax"),
    keep(table([30, 70], ["매크로의 성질", "로그 매크로에서 조심할 것"], [
        ["글자 치환이다", "여러 문장으로 된 매크로는 `if`·`else` 사이에서 깨진다. `do { … } while ( 0 )`으로 감싸는 "
                    "관용구가 여기서 나온다"],
        ["범위가 없다", "`namespace`나 클래스 안에 가둘 수 없다. 이름이 전역으로 퍼지므로 접두사로 구분한다"],
        ["인자가 여러 번 펼쳐질 수 있다", "본문에 인자를 두 번 적으면 `i++` 같은 인자가 두 번 실행된다"],
        ["사라지게 만들 수 있다", "릴리스 빌드에서 빈 내용으로 정의하면 호출과 인자 계산이 통째로 없어진다. "
                           "함수로는 할 수 없는 일이다"],
    ], cell_cls=["lab", ""])),
    box("ex", "예시: 인자가 두 번 펼쳐지는 매크로", [
        code(r"""
#define SQUARE( x ) ( ( x ) * ( x ) )

int i = 3;
int n = SQUARE( i++ );    // expands to ( ( i++ ) * ( i++ ) ): i is changed twice
""", tag="bad"),
        p("함수였다면 `i++`는 한 번만 계산되어 넘어온다. 매크로는 글자를 그대로 붙여 넣으므로 인자가 본문에 적힌 횟수만큼 "
          "실행된다. 로그 매크로의 본문에 인자를 한 번씩만 쓰는 이유다."),
    ]),
    p("`__FILE__`에 무엇이 들어가는지는 컴파일러에 넘어간 경로에 달렸다. MSVC는 `/FC` 옵션이 켜져 있으면 드라이브 "
      "문자부터 시작하는 전체 경로를 넣는다. 로그 한 줄이 길어지는 것이 싫으면 파일 이름만 남기는 처리가 필요하다."),

    h3("3.2", "방법 둘: std::source_location (C++20)"),
    fn("std::source_location::current", "static consteval std::source_location current() noexcept;",
       "이 식이 계산되는 자리의 파일 이름, 줄, 함수 이름을 담은 객체를 만든다. 컴파일할 때 값이 정해진다.",
       returns="`std::source_location`. `file_name()`, `line()`, `column()`, `function_name()`으로 꺼낸다",
       notes=[("계산되는 자리", "함수 본문 안에서 부르면 그 줄이다. 매개변수의 기본 인자로 쓰면 그 함수를 **부른 줄**이 된다"),
              ("헤더", "`<source_location>`")],
       lib="C++20"),
    code(r"""
#include <source_location>

void Where( std::source_location loc = std::source_location::current() );

Where();    // loc describes THIS line: the default argument is evaluated at the call site
""", tag="syntax"),
    p("기본 인자는 함수를 **부르는 자리**에서 계산된다. 그래서 `current()`를 기본 인자로 두면 호출한 쪽의 위치가 "
      "들어온다. 매크로 없이 같은 일을 하는 표준 방법이다."),
    keep(table([28, 36, 36], ["", "매크로 + `__FILE__`·`__LINE__`", "`std::source_location`"], [
        ["호출부의 모양", "매크로 이름으로 부른다", "평범한 함수 호출"],
        ["함수 이름", "`__FUNCTION__`을 따로 넘긴다 (MSVC 확장)", "`function_name()`으로 함께 온다"],
        ["형식 인자와 함께 쓰기", "`...`으로 그대로 넘긴다", "기본 인자를 매개변수 팩 뒤에 둘 수 없어 우회가 필요하다"],
        ["릴리스에서 호출을 지우기", "매크로를 비우면 된다", "호출은 남는다"],
        ["디버거에서 따라 들어가기", "펼쳐진 코드라 한 줄로 보인다", "함수라서 그대로 들어간다"],
    ], cell_cls=["lab", "", ""], compact=True)),
    box("point", None,
        "1.2절의 `Log()`는 `const char* file, int line`을 받는다. 호출부가 이 둘을 손으로 적지 않게 하려면 매크로가 "
        "한 겹 필요하다는 뜻이다. `std::source_location`으로 가면 이 두 매개변수는 하나로 바뀐다. 어느 쪽으로 갈지는 "
        "6.2절에서 정한다."),
    box("cs", None,
        "전처리는 컴파일보다 앞 단계다. 전처리기는 타입도 범위도 모르고 토큰만 바꿔 끼운다. 매크로의 장점과 단점이 모두 "
        "여기서 나온다. 전공서의 번역 단계(translation phases) 항목과 닿는다."),
], lead="로그에 파일과 줄 번호를 넣으려면 풀어야 하는 문제가 하나 있다. 방법은 둘이고 성격이 다르다.", pb=True)

ch4 = chapter(4, "메시지 조립: std::format", [
    h3("4.1", "형식 문자열"),
    fn("std::format",
       "template<class... Args>\n"
       "std::string format(std::format_string<Args...> fmt, Args&&... args);",
       "형식 문자열의 `{}` 자리에 인자를 차례로 끼워 넣은 새 문자열을 만든다.",
       params=[("`fmt`", "형식 문자열. 컴파일할 때 내용이 정해진 상수여야 한다. 문자열 리터럴이면 된다"),
               ("`args`", "끼워 넣을 값들. 개수와 타입이 `fmt`와 맞는지 컴파일러가 검사한다")],
       returns="완성된 `std::string`. 호출할 때마다 새로 만들어진다",
       fails="`{}`의 개수나 형식 지정이 인자와 맞지 않으면 컴파일 오류가 난다",
       notes=[("헤더", "`<format>`. C++20이 필요하다 (프로젝트 설정은 `Engine/Engine.vcxproj:149`)")],
       lib="C++20"),
    keep(table([20, 42, 38], ["표기", "뜻", "예 → 결과"], [
        ["`{}`", "다음 인자를 기본 모양으로", "`{}` , 42 → `42`"],
        ["`{:6}`", "폭 6. 숫자는 오른쪽, 문자열은 왼쪽 정렬", f"`{{:6}}` , \"ab\" → `ab{SP * 4}`"],
        ["`{:<6}` `{:>6}` `{:^6}`", "왼쪽, 오른쪽, 가운데 정렬", f"`{{:>6}}` , \"ab\" → `{SP * 4}ab`"],
        ["`{:05}`", "빈자리를 0으로 채운다", "`{:05}` , 42 → `00042`"],
        ["`{:.2f}`", "소수점 아래 2자리", "`{:.2f}` , 3.14159 → `3.14`"],
        ["`{:x}`", "16진수", "`{:x}` , 255 → `ff`"],
        ["`{0}` `{1}`", "인자를 번호로 가리킨다", "`{1}-{0}` , 1, 2 → `2-1`"],
    ], cell_cls=["lab", "", ""], compact=True)),
    box("ex", "예시: 호출 한 줄과 그 결과", [
        table([58, 42], ["호출", "돌려주는 문자열"], [
            ["`std::format( \"{} / {}\", 3, 4.5 )`", "`3 / 4.5`"],
            ["`std::format( \"[{:>6}]\", 42 )`", f"`[{SP * 4}42]`"],
            ["`std::format( \"[{:<8}]\", \"ab\" )`", f"`[ab{SP * 6}]`"],
            ["`std::format( \"{:06.2f}\", 3.14159 )`", "`003.14`"],
            ["`std::format( \"{:#x}\", 255 )`", "`0xff`"],
            ["`std::format( \"{0}{0}{1}\", \"na\", \"!\" )`", "`nana!`"],
        ], cell_cls=["lab", ""], compact=True),
        p("폭은 “적어도 이만큼”이다. 넷째 줄은 폭 6을 0으로 채우고 소수점 아래를 2자리로 자른 것이다. 로그의 레벨 이름을 "
          "같은 폭으로 맞출 때 둘째, 셋째 줄의 방법을 쓴다."),
    ]),
    table([22, 26, 26, 26], ["", "`printf`", "`<<`", "`std::format`"], [
        ["형식과 값이 한눈에", "보인다", "값 사이에 흩어진다", "보인다"],
        ["형식과 인자가 어긋나면", "실행 중에 깨진다", "어긋날 일이 없다", "컴파일 오류"],
        ["내가 만든 타입", "넣을 수 없다", "`operator<<`", "`std::formatter` 특수화"],
        ["결과", "화면이나 `char` 버퍼", "스트림", "`std::string`"],
    ], cell_cls=["lab", "", "", ""], compact=True),
    fn("std::vformat", "std::string vformat(std::string_view fmt, std::format_args args);",
       "`std::format`과 같은 일을 하되, 형식 문자열을 실행 중에 해석한다. 컴파일할 때의 검사가 없다.",
       params=[("`fmt`", "형식 문자열. 변수에 담긴 것이어도 된다"),
               ("`args`", "`std::make_format_args( a, b )`로 묶은 인자들. 최근 컴파일러에서는 변수만 받고 임시 값은 받지 않는다")],
       returns="완성된 `std::string`",
       fails="형식이 틀렸거나 인자와 맞지 않으면 `std::format_error` 예외를 던진다",
       notes=[("헤더", "`<format>` (C++20)")],
       lib="C++20"),
    p("결과는 `std::string`이다. 로그 한 줄마다 문자열 하나가 만들어지고 버려진다. 지금 규모에서는 문제가 되지 않는다. "
      "나중에 측정해서 문제가 되면 `std::format_to`로 미리 잡아 둔 버퍼에 쓰는 길이 있다."),

    h3("4.2", "형식 인자가 지나는 길"),
    flow([
        ("호출부", "형식 + 값들"),
        ("매크로", "가변 인자로 받는다", "accent"),
        ("std::format", "문자열 하나로"),
        ("Log()", "완성된 문자열", "dark"),
    ], "`Log()`가 완성된 문자열을 받으므로(1.2절), 값이 몇 개든 그 앞에서 하나로 합쳐져야 한다."),
    code(r"""
#define PRINT_ALL( ... ) std::printf( __VA_ARGS__ )

PRINT_ALL( "%d %d\n", 1, 2 );   // __VA_ARGS__ becomes: "%d %d\n", 1, 2
""", tag="syntax"),
    p("`...`으로 받은 인자 묶음은 `__VA_ARGS__` 자리에 쉼표째 그대로 들어간다. 여기서 순서 문제가 하나 생긴다. "
      "함수의 인자는 함수가 불리기 **전에** 계산된다. 조립한 문자열을 `Log()`에 넘기고 `Log()` 안에서 레벨을 "
      "검사하면, 버려질 로그도 조립 비용은 이미 치른 뒤다. 검사를 어디에 둘지가 6.2절의 결정 하나다."),

    h3("4.3", "시각"),
    fn("std::chrono::system_clock::now",
       "static std::chrono::time_point<std::chrono::system_clock> now() noexcept;",
       "지금의 벽시계 시각을 돌려준다. 기준은 UTC다.",
       returns="시각을 나타내는 `time_point`. `std::format`의 `{:%H:%M:%S}` 같은 표기로 글자가 된다",
       notes=[("자릿수", "MSVC의 `system_clock`은 100나노초 단위로 센다. 그대로 찍으면 초 아래가 7자리까지 나온다"),
              ("자르기", "`std::chrono::floor<단위>( 시각 )`이 그 단위 아래를 버린 시각을 돌려준다"),
              ("헤더", "`<chrono>`")],
       lib="C++20"),
    box("ex", "예시: 날짜와 시각을 초 단위까지", [
        code(r"""
auto now = std::chrono::system_clock::now();
auto sec = std::chrono::floor<std::chrono::seconds>( now );   // drop everything below one second
std::string text = std::format( "{:%F %T}", sec );           // "2026-11-16 05:02:07" (UTC)
""", tag="usage"),
        p("`%F`는 `연-월-일`, `%T`는 `시:분:초`다. 한국의 오후 2시 2분에 실행하면 `05:02`가 찍힌다. 한국 시각이 UTC보다 "
          "9시간 앞서기 때문이다. 로그에 쓸 것은 날짜 없이 밀리초까지이므로 단위와 형식이 이 예와 다르다."),
    ]),
    table([30, 35, 35], ["", "`std::chrono` + `std::format`", "`localtime_s` + `std::strftime`"], [
        ["지금 시각을 얻는 곳", "`std::chrono::system_clock::now()`", "`std::time( nullptr )`"],
        ["형식", "`{:%H:%M:%S}`", "`\"%H:%M:%S\"`"],
        ["그대로 쓰면", "UTC로 나오고, MSVC에서는 초 아래 7자리까지 나온다", "지역 시각, 초 단위까지"],
        ["손볼 것", "지역 시각으로 바꾸기, 밀리초로 자르기", "밀리초를 따로 구해 붙이기"],
    ], cell_cls=["lab", "", ""]),
    p("지역 시각으로 바꾸는 도구는 `std::chrono::current_zone()`과 `zoned_time`이다 (MSVC에서는 Windows 10 1903 이상이 "
      "필요하다). 프레임 시간을 재는 `glfwGetTime()`(1-2강)은 프로그램이 시작한 뒤 흐른 초라서 벽시계 시각이 아니다. "
      "로그에는 벽시계 시각이 맞다."),
    box("cs", None,
        "`printf`의 `...`은 타입 정보 없이 값만 스택에 쌓아 넘기는 C의 가변 인자다. 형식 문자열의 `%d`를 믿고 꺼내므로 "
        "어긋나면 엉뚱한 메모리를 읽는다. `std::format`은 가변 인자 템플릿이라 컴파일러가 인자마다 타입을 안다. "
        "“컴파일 시점에 아는 것이 많을수록 실행 중 사고가 준다”는 C++의 방향을 보여 주는 예다."),
], lead="값을 문장에 끼워 넣는 일이다. C++20의 `<format>`을 쓴다.")

ch5 = chapter(5, "어디에 쓰는가: 콘솔과 파일", [
    h3("5.1", "콘솔에 색 입히기"),
    code(r"""
std::cout << "\x1b[31m" << "red" << "\x1b[0m" << " normal\n";   // 31 = red, 0 = reset
""", tag="syntax"),
    p(r"`\x1b`는 ESC 문자(27)다. ESC, `[`, 숫자, `m`으로 이어지는 글자열을 콘솔은 화면에 찍지 않고 명령으로 "
      "받아들인다. ANSI 이스케이프 시퀀스라고 부른다. 한 번 바꾼 색은 되돌릴 때까지 이어지므로 끝에 0번(reset)을 "
      "보내야 한다."),
    box("ex", r"예시: \x1b[33m을 한 바이트씩", [
        table([18, 16, 66], ["바이트", "글자", "콘솔이 읽는 뜻"], [
            ["`0x1B`", "ESC", "여기서부터는 찍을 글자가 아니라 명령이다"],
            ["`0x5B`", "`[`", "인자가 붙는 명령이 이어진다"],
            ["`0x33` `0x33`", "`33`", "인자. 33번은 글자색 노랑이다"],
            ["`0x6D`", "`m`", "명령의 끝. `m`은 색과 글자 모양을 바꾸는 명령이다"],
        ], cell_cls=["lab", "c", ""], compact=True),
        p("다섯 바이트가 한 묶음이고 화면에는 아무것도 찍히지 않는다. 이 뒤에 오는 글자가 노랑으로 나온다."),
    ]),
    table([16, 20, 16, 20, 28], ["코드", "색", "코드", "색", "비고"], [
        ["`30` 〜 `37`", "기본 8색", "`90` 〜 `97`", "밝은 8색", "글자색"],
        ["`31`", "빨강", "`33`", "노랑", "오류, 경고에 흔히 쓴다"],
        ["`32`", "초록", "`36`", "청록", "정보, 디버그에 흔히 쓴다"],
        ["`90`", "회색", "`41`", "빨강 배경", "`40` 〜 `47`이 배경색"],
        ["`0`", "전부 되돌림", "`1`", "굵게", "`;`로 이어 쓴다: `1;31`"],
    ], cell_cls=["lab", "", "lab", "", ""], compact=True),
    p("Windows의 예전 콘솔 창은 이 글자열을 해석하는 기능(가상 터미널 처리)을 꺼 둔 채로 시작하고, Windows Terminal은 "
      "켜 둔 채로 시작한다. 어느 쪽에서 실행될지 모르므로 프로그램이 직접 켜 달라고 요청한다. 켜지 않은 채로 색 코드를 "
      "보내면 `←[31m` 같은 글자가 그대로 보인다. 요청에는 아래 세 함수를 쓴다."),
    fn("GetStdHandle", "HANDLE GetStdHandle(DWORD nStdHandle);",
       "이 프로세스의 표준 입력·출력·오류 가운데 하나를 가리키는 핸들을 돌려준다.",
       params=[("`nStdHandle`", "`STD_OUTPUT_HANDLE`, `STD_ERROR_HANDLE`, `STD_INPUT_HANDLE` 중 하나")],
       returns="핸들. `std::cout`이 쓰는 곳은 `STD_OUTPUT_HANDLE`이다",
       fails="`INVALID_HANDLE_VALUE`. 콘솔이 아예 없는 프로그램에서는 `NULL`이 올 수 있다. Client는 콘솔 프로그램이다"
             "(`Client/Client.vcxproj:142`)",
       notes=[("헤더", "`<Windows.h>`")],
       lib="Win32"),
    fn("GetConsoleMode", "BOOL GetConsoleMode(HANDLE hConsoleHandle, LPDWORD lpMode);",
       "그 콘솔의 현재 모드(켜져 있는 기능들의 비트 묶음)를 읽는다.",
       params=[("`hConsoleHandle`", "콘솔의 입력 또는 출력 핸들"),
               ("`lpMode`", "읽은 값을 받을 `DWORD` 변수의 주소")],
       returns="성공하면 0이 아닌 값",
       fails="0. 핸들이 콘솔이 아닐 때 실패한다. `Client.exe > out.txt`처럼 출력을 파일로 돌리면 그렇게 된다",
       notes=[("헤더", "`<Windows.h>`")],
       lib="Win32"),
    fn("SetConsoleMode", "BOOL SetConsoleMode(HANDLE hConsoleHandle, DWORD dwMode);",
       "그 콘솔의 모드를 통째로 `dwMode`로 바꾼다.",
       params=[("`hConsoleHandle`", "콘솔의 입력 또는 출력 핸들"),
               ("`dwMode`", "새 모드. 출력 핸들에 `ENABLE_VIRTUAL_TERMINAL_PROCESSING` 비트가 들어 있으면 색 코드를 해석한다")],
       returns="성공하면 0이 아닌 값",
       fails="0. 콘솔이 아닌 핸들이거나, 그 기능을 모르는 오래된 Windows일 때",
       notes=[("부르는 순서", "모드는 통째로 바뀐다. 이미 켜져 있던 기능을 잃지 않으려면 먼저 읽은 값에 비트를 더해서 넘긴다"),
              ("헤더", "`<Windows.h>`")],
       lib="Win32"),
    p("세 함수 모두 실패할 수 있고, 실패는 반환값으로만 알려 준다. 출력이 콘솔이 아닐 때가 그렇다. 그때 색 코드를 "
      "그대로 보내면 그 글자들이 파일에 남는다. 반환값을 보고 무엇을 할지는 직접 정한다."),

    h3("5.2", "버퍼와 flush"),
    Fig(138)
    .box(14, 24, 128, 50, "쓰기", "stream << text")
    .arrow((142, 49), (186, 49))
    .box(186, 24, 150, 50, "스트림 버퍼", "프로세스 안의 메모리", kind="accent")
    .arrow((336, 49), (398, 49), kind="accent")
    .text(367, 41, "flush", kind="accent", size=10)
    .box(398, 24, 132, 50, "운영체제", "파일 캐시")
    .arrow((530, 49), (566, 49))
    .box(566, 24, 80, 50, "디스크", "파일", kind="dark")
    .line((261, 74), (261, 90), kind="muted")
    .text(261, 106, "프로세스가 죽으면", kind="s", size=9.5)
    .text(261, 122, "여기 남은 글자는 사라진다", kind="s", size=9.5)
    .line((464, 74), (464, 90), kind="muted")
    .text(464, 106, "여기까지 오면", kind="s", size=9.5)
    .text(464, 122, "프로세스가 죽어도 남는다", kind="s", size=9.5)
    .render("`<<`로 쓴 글자는 먼저 프로세스 안의 버퍼에 모인다. 버퍼가 가득 차거나 flush할 때 운영체제로 넘어간다."),
    p(r"파일에 쓸 때마다 운영체제를 부르면 느리므로 스트림은 모았다가 한꺼번에 넘긴다. 문제는 프로그램이 "
      "비정상으로 죽을 때다. 버퍼에 남아 있던 글자는 프로세스와 함께 사라진다. 로그가 가장 필요한 순간이 바로 그때다."),
    fn("std::ofstream::flush", "std::ostream& flush();",
       "스트림 버퍼에 모여 있는 글자를 지금 운영체제로 내보낸다.",
       returns="스트림 자신. `file << text << std::flush;`처럼 이어 쓸 수도 있다",
       notes=[("flush가 일어나는 다른 때", r"`std::endl`은 `'\n'`을 쓰고 flush까지 한다. `'\n'`만 쓰면 flush하지 않는다. "
                                   "`close()`와 스트림의 소멸자도 flush한다"),
              ("비용", "부를 때마다 운영체제를 한 번 부른다. 줄마다 하면 로그가 많을 때 느려진다"),
              ("헤더", "`<ostream>`. `<fstream>`을 포함하면 따라온다")],
       lib="C++"),
    table([24, 38, 38], ["flush 시점", "얻는 것", "내주는 것"], [
        ["줄마다", "죽기 직전 줄까지 파일에 남는다", "로그가 많을 때 느려진다"],
        ["`Warning` 이상일 때만", "중요한 줄은 남고 평소에는 빠르다", "죽기 직전의 `Info`·`Debug`는 잃을 수 있다"],
        ["`Shutdown()`에서만", "가장 빠르다", "비정상 종료 때 마지막 부분이 통째로 없다"],
    ], cell_cls=["lab", "", ""]),

    h3("5.3", "로그 파일"),
    fn("std::ofstream::open",
       "void open(const char* filename, std::ios_base::openmode mode = std::ios_base::out);",
       "파일을 열어 이 스트림에 연결한다.",
       params=[("`filename`", "파일 경로. 상대 경로는 작업 디렉터리 기준이다"),
               ("`mode`", "여는 방식. 기본값 `out`은 파일이 있으면 내용을 비우고 새로 쓴다. `std::ios::app`을 주면 끝에 이어 붙인다")],
       returns="없다",
       fails="예외를 던지지 않는다. 스트림이 실패 상태가 되고, 그 뒤의 쓰기는 조용히 무시된다",
       notes=[("헤더", "`<fstream>`"),
              ("짝이 되는 함수", "`close()`. 남은 글자를 flush하고 파일을 닫는다")],
       lib="C++"),
    fn("std::ofstream::is_open", "bool is_open() const;",
       "이 스트림에 지금 열린 파일이 연결되어 있는지 알려 준다.",
       returns="열려 있으면 `true`",
       notes=[("쓰는 때", "`open()` 바로 뒤. 열기에 실패했는지 알 수 있는 가장 간단한 방법이다"),
              ("헤더", "`<fstream>`")],
       lib="C++"),
    ul([
        "**실행할 때마다 지난 로그가 사라진다.** `open()`에 모드를 주지 않으면 파일을 비우고 새로 쓴다. 이어 붙일지는 "
        "직접 정한다.",
        "**파일이 생기는 곳은 실행하는 방법에 달렸다.** 상대 경로는 작업 디렉터리 기준이다. Visual Studio에서 실행하면 "
        "기본 작업 디렉터리는 프로젝트 폴더라서 `Client/` 아래에 생긴다. 경로를 제대로 다루는 일은 1-7강이다.",
        "**파일에는 색 코드를 넣지 않는다.** 메모장으로 열었을 때 `[31m`이 섞여 보인다.",
        f"**확장자를 `.log`로 하면 저장소에 올라가지 않는다.** `.gitignore`에 이미 `*.log`가 있다 (96행, {READ_DATE} 확인).",
    ]),
    layers([
        ("CALL SITE", [("Engine 코드", "`EngineCore.cpp`, `InputManager.cpp`"), ("Client 코드", "`main.cpp`")]),
        ("LOGGER", [("GLogger::Log", "거르고, 조립하고, 내보낸다", "accent")]),
        ("SINK", [("콘솔", "색 있음", "dark"), ("파일", "색 없음", "dark"), ("VS 출력 창", "나중에", "ghost")]),
    ], "로그가 나가는 곳을 싱크(sink)라고 부른다. 지금은 둘이고, `Log()` 안에서 직접 쓴다."),
    box("api", None,
        "Logger가 Core에 있는 이유는 어느 그래픽 API에도 기대지 않기 때문이다. API마다 진단 메시지를 내는 통로는 "
        "다르지만(OpenGL의 디버그 콜백, DX11·DX12의 InfoQueue, Vulkan의 검증 레이어) 받아 적는 곳은 이 Logger 하나다. "
        "OpenGL 쪽을 잇는 일이 2-1강이다."),
    box("ue", None,
        "UE의 `GLog`에는 출력 장치(`FOutputDevice`)가 여럿 붙어 있다. 같은 로그가 `Saved/Logs/`의 파일, 에디터의 "
        "Output Log 창, 콘솔로 동시에 나간다. 여기서 싱크라고 부른 것이다."),
], lead="조립한 한 줄을 두 곳에 내보낸다. 콘솔은 지금 보려고, 파일은 나중에 보려고 쓴다.")

ch6 = chapter(6, "설계", [
    h3("6.1", "파일 배치와 완성된 뒤의 모습"),
    tree("""
Engine/
├── Enum/
│   └── LogLevel.h +  #enum class ELogLevel (2.1)
├── Core/
│   ├── EngineCore.cpp  #silent failures and std::cout -> log calls
│   ├── Logger.h +  #class GLogger (1.2); do the macros live here too?
│   └── Logger.cpp +  #Get, Init, Shutdown, Log and its helpers
└── Manager/
    └── InputManager.cpp  #invalid key -> log call
Client/
└── main.cpp  #temporary test calls, then removed
"""),
    code(r"""
LOG_INFO( "Core", "Engine initialized: {}x{}", width, height );
LOG_WARN( "Input", "Invalid key: {}", static_cast<int>( key ) );
LOG_ERROR( "Core", "Failed to load GL functions" );
""", title="the call site when this lesson is done (names and argument order are examples)", tag="usage"),
    keep(h3("6.2", "결정할 것"),
    table([22, 36, 42], ["결정", "선택지", "따져 볼 것"], [
        ["호출 위치를 얻는 방법", "매크로와 `__FILE__`·`__LINE__` (1.2절의 선언) / `std::source_location`",
         "3.2절의 표. 형식 인자를 어떻게 넘길지와 함께 정해야 한다"],
        ["레벨 검사의 위치", "`Log()` 안 / 매크로 안 / 둘 다",
         "매크로에서 검사하면 버려질 로그의 조립을 건너뛴다. 대신 매크로가 최소 레벨을 읽을 수 있어야 한다"],
        ["flush 시점", "줄마다 / `Warning` 이상 / `Shutdown()`에서만", "5.2절의 표. 콘솔과 파일을 다르게 둘 수도 있다"],
        ["카테고리의 표현", "문자열 (1.2절의 선언) / 열거형 / 카테고리 객체",
         "오타를 컴파일러가 잡는가, 새 카테고리를 만드는 수고, 카테고리별 레벨이 필요한가"],
        ["`message`의 타입", "`const std::string&` (1.2절의 선언) / `std::string_view`",
         "문자열 리터럴만 넘길 때 임시 `std::string`이 만들어지는가"],
        ["`Init`·`Shutdown`을 부르는 곳", "`Client/main.cpp` / `GEngine::Init` 안",
         "엔진보다 먼저 준비되어야 엔진의 초기화 실패를 적을 수 있다. 로그 파일 이름은 누가 정하는가"],
        ["릴리스 빌드의 `Trace`·`Debug`", "남긴다 / 컴파일에서 뺀다",
         "뺀다면 매크로를 `_DEBUG`에 따라 다르게 정의한다. 뺀 매크로의 인자는 계산되지 않는다"],
    ], cell_cls=["lab", "", ""], compact=True)),
    Fig(140)
    .text(330, 13, "여섯째 · Init과 Shutdown을 부르는 곳: 이 길은 둘 사이에서만 열려 있다", kind="accent", size=9.5)
    .line((14, 30), (14, 22), (646, 22), (646, 30), kind="muted")
    .box(14, 38, 100, 46, "호출부", "형식 + 값들")
    .arrow((114, 61), (140, 61))
    .box(140, 38, 104, 46, "매크로", "위치를 붙인다", kind="accent")
    .arrow((244, 61), (270, 61))
    .box(270, 38, 104, 46, "std::format", "문자열 하나로")
    .arrow((374, 61), (400, 61))
    .box(400, 38, 104, 46, "Log()", "거르고 조립한다", kind="dark")
    .arrow((504, 54), (546, 46))
    .arrow((504, 68), (546, 76))
    .box(546, 32, 100, 26, "콘솔", r=4)
    .box(546, 64, 100, 26, "파일", r=4)
    .text(64, 103, "넷째 · 카테고리", kind="accent", size=9.5)
    .text(192, 103, "첫째 · 호출 위치", kind="accent", size=9.5)
    .text(192, 118, "둘째 · 레벨 검사", kind="accent", size=9.5)
    .text(192, 133, "일곱째 · 릴리스에서 지우기", kind="accent", size=9.5)
    .text(322, 103, "다섯째 · message 타입", kind="accent", size=9.5)
    .text(452, 103, "둘째 · 레벨 검사", kind="accent", size=9.5)
    .text(596, 108, "셋째 · flush 시점", kind="accent", size=9.5)
    .render("로그 호출 하나가 지나는 길과, 위 표의 결정이 걸리는 자리 (순서는 표의 행 순서). 둘째는 두 자리 가운데 "
            "어디에 둘지가 선택이다."),
    box("decide", None,
        "위 일곱 가지에 정답은 없다. 미션에 들어가기 전에 행마다 하나를 고르고 이유를 한 줄씩 적어 둔다. 1.2절의 선언은 "
        "첫째·넷째·다섯째에서 이미 한쪽을 골라 두었다. 그대로 가도 되고 바꿔도 된다."),

    pagebreak(),
    keep(h3("6.3", "선언 스케치"),
    p("결정을 마친 뒤 1.2절의 선언에 더할 것의 모양이다. 주석은 답이 아니라 스스로에게 던질 질문이다."),
    code(r"""
class GLogger
{
public:
    void      SetMinLevel( ELogLevel level );
    ELogLevel GetMinLevel() const;      // who reads this: Log() only, or the macro too?

    // Log( level, category, file, line, message ) is declared in 1.2.
    // Where does the level check live: here, in the macro, or both?

private:
    // Which helpers does Log() need?
    //   - level -> text  ("Info ", "Warn ", ...)
    //   - level -> console color
    //   - text for "now"
    // Free functions inside Logger.cpp, or private members here?
    // Which choice keeps Logger.h small for everyone who includes it?
};
""", title="Engine/Core/Logger.h", tag="sketch")),

    h3("6.4", "이 강에서 하지 않는 것"),
    table([30, 70], ["미루는 것", "이유"], [
        ["`Fatal`에서 멈추기", "이 강에서는 찍기만 한다. 조건이 깨진 자리에서 멈추는 일은 1-6강(Assert)이다"],
        ["제대로 된 종료 순서", "1-4강을 아직 하지 않았다면 엔진에는 종료 경로가 없다. `Run()`이 끝나면 `main`이 끝난다. "
                         "그때는 `Shutdown()`을 부르는 자리를 임시로 두고 1-4강에서 옮긴다. 1-4강을 먼저 했다면 그 강의 "
                         "6.2절에서 정한 종료 순서에 끼워 넣는다"],
        ["초기화 실패 처리 전반", "`glfwInit()`과 창 생성의 실패 확인은 1-4강이다. 여기서는 이미 있는 실패 분기에 "
                           "로그만 넣는다"],
        ["스레드 안전", "지금은 스레드가 하나다. 잠금은 스레드가 생길 때 넣는다"],
        ["싱크 인터페이스", "출력 대상이 둘뿐이다. 셋째가 필요해질 때 추상화해도 늦지 않다"],
    ], cell_cls=["lab", ""]),
], lead="1.2절의 선언이 방향의 절반을 정해 두었다. 남은 것을 정한 뒤에 구현한다.")

ch7 = chapter(7, "구현 미션", [
    steps([
        ("파일을 만들고 `Log()`가 콘솔에 한 줄을 찍는다",
         "`LogLevel.h`, `Logger.h`, `Logger.cpp`가 Engine 프로젝트에 들어 있고 2.1절과 1.2절의 선언이 옮겨져 있다. "
         "`GLogger::Get()`은 어디서 불러도 같은 객체를 돌려준다. `Log()`는 받은 레벨의 이름, 카테고리, 메시지를 2장의 "
         "그림과 같은 모양의 한 줄로 콘솔에 찍는다. 시각과 색은 아직 없다. 6.2절의 첫째·넷째·다섯째 결정에서 다른 쪽을 "
         "골랐다면 선언의 그 매개변수만 달라진다. **통과:** `main`에서 `Log()`를 직접 한 번 부르면 레벨 이름, 카테고리, "
         "메시지가 든 줄이 콘솔에 하나 찍힌다.",
         ["`Get()`은 1-1강 7장과 같은 방식이다. 새 `.cpp`의 첫 줄은 1-1강 2.4절에 있다.",
          "`enum class`는 저절로 글자가 되지 않는다. `switch`로 레벨마다 문자열을 돌려주는 작은 함수가 먼저 필요하다."]),
        ("최소 레벨보다 낮은 로그를 버린다",
         "최소 레벨을 바꾸는 함수가 있다 (6.3절의 `SetMinLevel`). 최소 레벨보다 낮은 레벨로 부른 로그는 찍히지 않고, "
         "같거나 높은 레벨은 그대로 찍힌다. 검사를 두는 자리는 6.2절의 둘째 결정이다. 매크로는 미션 6에서 생기므로 "
         "매크로 쪽을 골랐다면 지금은 `Log()`에 두고 그때 옮긴다. **통과:** 최소 레벨을 `Error`로 올리고 `Warning`과 "
         "`Error`로 한 번씩 부르면 `Error` 줄만 찍힌다.",
         ["비교는 한 줄이다. `LogLevel.h`의 값 순서가 이미 맞춰져 있다 (2.1절)."]),
        ("시각을 붙인다",
         "줄 맨 앞에 그 로그를 찍는 순간의 시각이 `시:분:초.밀리초`로 붙는다. 날짜는 넣지 않는다. 지역 시각이고 초 "
         "아래는 세 자리다. 얻는 방법은 4.3절 표의 둘 가운데 고른다. **통과:** 찍힌 시와 분이 컴퓨터의 시계와 같고 "
         "초 아래가 세 자리다.",
         ["9시간 차이가 나면 UTC이고, 초 아래가 일곱 자리면 자르지 않은 것이다 (4.3절 표의 마지막 줄)."]),
        ("레벨마다 색을 입힌다",
         "`GLogger::Init`이 콘솔에 색 코드를 해석해 달라고 요청하고, `Log()`는 레벨마다 다른 색으로 찍는다. 색 코드는 "
         "콘솔로 가는 글자에만 넣는다. 어느 레벨에 어느 색을 줄지, 요청이 실패하면 무엇을 할지는 직접 정한다 (5.1절). "
         "`Init`은 엔진이 첫 로그를 찍기 전에 불린다. 부르는 곳은 6.2절의 여섯째 결정이다. **통과:** 레벨이 다른 두 "
         "줄의 색이 다르고, `←[32m` 같은 글자가 화면에 그대로 보이지 않는다.",
         ["5.1절 함수 설명의 인자와 “부르는 순서” 칸을 이으면 `Init`에 쓸 순서가 나온다. 반환값을 본다."]),
        ("파일에도 쓴다",
         "`Init`이 받은 이름으로 로그 파일을 열고, `Shutdown`이 남은 글자를 내보낸 뒤 파일을 닫는다. `Log()`는 콘솔에 "
         "찍은 것과 같은 줄을 색 코드 없이 파일에도 쓴다. flush 시점은 6.2절의 셋째 결정을, `Shutdown`을 부르는 곳은 "
         "여섯째 결정을 따른다. 지난 로그에 이어 붙일지, 파일을 열지 못하면 무엇을 할지는 직접 정한다 (5.3절). "
         "**통과:** 프로그램을 끝낸 뒤 로그 파일을 메모장으로 열면 콘솔에 찍힌 줄이 모두 있고 `[31m` 같은 글자가 없다.",
         ["콘솔용과 파일용 문자열이 어디서 갈라지는지 생각한다. 공통 부분을 먼저 만들고 색만 덧붙이는 순서가 있다.",
          "파일이 보이지 않으면 상대 경로의 기준이 되는 폴더를 본다. 열렸는지 묻는 함수도 5.3절에 있다."]),
        ("매크로로 감싼다",
         "호출부는 레벨, 카테고리, 형식 문자열, 값만 적는다. 파일 이름과 줄 번호는 적지 않아도 호출한 자리의 것이 줄 "
         "끝에 찍힌다. 값이 없는 호출도, 중괄호 없는 `if`와 `else` 사이의 호출도 컴파일된다. 방법은 6.2절의 첫째 "
         "결정이고, 둘째와 일곱째 결정도 여기서 반영한다. 이름과 인자 순서는 6.1절의 예와 달라도 된다. **통과:** "
         "6.1절의 세 줄과 같은 모양의 호출이 컴파일되고, 찍힌 위치가 그 호출을 적은 파일과 줄 번호다.",
         ["`__FILE__`과 `__LINE__`은 매크로 본문 안에 적어야 호출한 자리의 값이 된다 (3.1절).",
          "형식 문자열까지 `...`에 포함시키면 값이 하나도 없는 호출을 따로 다루지 않아도 된다.",
          "`if`와 `else` 사이에서 깨지면 3.1절 표의 첫 줄을 본다 (10장의 4번).",
          "`std::source_location`을 골랐다면 3.2절 표의 “형식 인자와 함께 쓰기” 칸이 여기서 풀 문제다."]),
        ("기존 코드를 바꾼다",
         "1.1절 표에서 찾은 자리가 로그 호출로 그 일을 알린다. Update 콜백 없이 불린 `Run`, `Init`의 GLAD 실패 분기, "
         "잘못된 키를 받은 조회 함수 셋이다. 레벨은 직접 고른다. `Engine/`에 남은 `std::cout`과 `std::cerr`도 로그 "
         "호출로 바꾸거나 지우고, 필요 없어진 `<iostream>` 포함을 없앤다. **통과:** `Engine/`에서 `std::cout`과 "
         "`std::cerr`를 검색하면 로거가 콘솔에 쓰는 줄 말고는 나오지 않는다.",
         ["키 상태를 묻는 함수는 프레임마다 불린다. 같은 경고가 초당 수백 줄 찍힐 수 있다. 그대로 둘지 정한다.",
          "초기화가 끝났다는 `Info` 한 줄을 넣어 두면 그 뒤의 모든 로그에 기준점이 생긴다."]),
        ("검증하고 치운다",
         "여섯 레벨을 한 번씩 찍어 줄마다 색을 본다. 최소 레벨을 `Warning`으로 올리면 그 가운데 세 줄만 콘솔과 파일 "
         "양쪽에 남는다. 확인이 끝나면 시험하려고 넣은 호출을 지운다. **통과:** 임시 호출이 남아 있지 않고, 9장의 "
         "일곱 줄을 확인한 뒤 커밋 하나로 묶었다."),
    ]),
], lead="한 단계가 끝날 때마다 빌드해서 눈으로 확인한다. 단계마다 “통과”에 적힌 것이 보이면 다음으로 간다. 힌트는 "
        "막혔을 때 위에서부터 하나씩만 본다. 무엇을 하라는 것인지 그래도 분명하지 않으면 맨 뒤 13장에 단계별로 "
        "풀어 적은 목록이 있다.", pb=True)

ch8 = chapter(8, "흔한 함정", [
    table([25, 47, 28], ["증상", "원인", "확인 방법"], [
        ["콘솔에 `←[32m` 같은 글자가 그대로 보인다", "가상 터미널 처리가 켜지지 않았다. `Init`을 부르지 않았거나 "
                                          "모드를 바꾸는 호출이 실패했다", "5.1절 세 함수의 반환값을 찍어 본다"],
        ["로그 파일이 비어 있거나 끝부분이 없다", "flush 전에 프로그램이 끝났다. `Shutdown()`이 불리지 않았다",
         "`Shutdown()`에 중단점을 걸어 본다"],
        ["로그 파일이 보이지 않는다", "상대 경로가 작업 디렉터리 기준이다", "프로젝트 속성 → 디버깅 → 작업 디렉터리"],
        ["형식 문자열이 상수가 아니라는 컴파일 오류", "변수에 담긴 문자열을 형식으로 넘겼다", "4.1절의 `std::vformat`"],
        ["`APIENTRY` 매크로 재정의 경고 (C4005)", "pch가 glad를 먼저 넣는다 (`Engine/framework.h:5`). "
                                         "`include/glad/glad.h:31` 〜 `:33`이 `APIENTRY`를 정의해 두고, 뒤에 "
                                         "포함한 `Windows.h`가 다시 정의한다",
         "빌드 출력 창. 실제로 나는지 빌드해서 확인하지는 않았다"],
        ["`std::min`, `std::max`에서 엉뚱한 구문 오류", "`Windows.h`가 `min`, `max`를 매크로로 정의한다",
         "`Windows.h`를 포함하기 전에 `NOMINMAX`를 정의하거나, 포함을 `Logger.cpp` 안에만 둔다"],
        ["새 파일의 함수에서 `LNK2019`", "새 `.cpp`가 Engine 프로젝트에 들어가지 않았거나 Engine을 다시 빌드하지 않았다",
         "솔루션 전체를 빌드한다 (1-1강 10장)"],
    ], compact=True),
], lead="증상에서 거꾸로 찾는 표다.")

ch9 = chapter(9, "완료 기준", [
    checklist([
        "실행하면 콘솔에 시각, 레벨, 카테고리, 메시지, 위치가 붙은 줄이 나오고 레벨마다 색이 다르다.",
        "같은 내용이 로그 파일에 색 코드 없이 남는다.",
        "최소 레벨을 `Warning`으로 바꾸면 `Trace`·`Debug`·`Info`가 콘솔과 파일 양쪽에서 사라진다.",
        "호출부 어디에도 파일 이름이나 줄 번호를 손으로 적은 곳이 없다.",
        "`Engine/` 안에서 `std::cout`과 `std::cerr`는 로거가 콘솔에 쓰는 줄에서만 검색된다.",
        "6.2절의 일곱 가지에 대해 고른 것과 이유가 적혀 있다.",
        "커밋 하나로 묶였다.",
    ]),
    console(Raw(
        '<span class="dim">[14:02:07.101]</span> <span class="ok">[Info ]</span> [Core ] Logger initialized: ClaudGL.log '
        '<span class="dim">(Logger.cpp:33)</span>\n'
        '<span class="dim">[14:02:07.318]</span> <span class="ok">[Info ]</span> [Core ] Engine initialized: 1600x1600 '
        '<span class="dim">(EngineCore.cpp:52)</span>\n'
        '<span class="dim">[14:02:07.320]</span> <span class="warn">[Warn ]</span> [Core ] Update callback is not set '
        '<span class="dim">(EngineCore.cpp:71)</span>\n'
        '<span class="dim">[14:02:09.774]</span> <span class="warn">[Warn ]</span> [Input] Invalid key: -1 '
        '<span class="dim">(InputManager.cpp:41)</span>'
    ), title="기대하는 출력 (형식, 문구, 줄 번호는 예시)"),
], lead="전부 눈이나 검색으로 확인할 수 있는 조건이다.")

ch10 = chapter(10, "생각해 볼 질문", [
    exgroup("A", "코드를 쓰지 않고 답하시오", "한두 문장으로, 이유까지"),
    qlist([
        "`GLogger::Log()`의 본문 안에 `__LINE__`을 적으면 로그에는 어떤 줄 번호가 찍히는가?",
        "최소 레벨이 `Warning`일 때 `LOG_DEBUG( \"Core\", \"{}\", BuildBigReport() )`를 부르면 `BuildBigReport()`는 "
        "실행되는가? 무엇에 따라 달라지는가?",
        "`Error` 로그를 찍은 바로 다음 줄에서 널 포인터를 건드려 프로그램이 죽었다. 콘솔에는 그 줄이 보였는데 "
        "파일에는 없다. 무슨 일이 있었는가?",
        "로그 매크로를 `{ … }`로만 감쌌다. `if ( x ) LOG_INFO( … ); else Foo();`는 왜 컴파일되지 않는가?",
        "로그 파일 이름을 `\"ClaudGL.log\"`로 주었다. Visual Studio에서 실행할 때와 탐색기에서 `Client.exe`를 "
        "더블클릭할 때 파일은 각각 어디에 생기는가?",
        "`GEngine`과 `GLogger`는 둘 다 함수 안의 `static` 지역 변수다. 나중에 `~GEngine()`에서 로그를 찍게 된다면 "
        "무엇을 확인해야 하는가?",
    ], lines=3),
], lead="답을 보기 전에 소리 내어 설명해 본다. 막히는 문항이 다시 읽을 장이다.", pb=True)

ch11 = chapter(11, "해설", [
    answers("질문 A", [
        ("`Logger.cpp` 안의 그 줄 번호가 찍힌다. 어디서 불러도 같다.",
         "`__LINE__`은 적힌 자리에서 치환된다. 호출부의 번호를 얻으려면 호출부에서 펼쳐지는 매크로 안에 적거나, "
         "호출부에서 계산되는 기본 인자를 써야 한다. (3장)"),
        ("레벨 검사가 어디에 있느냐에 달렸다.",
         "검사가 `Log()` 안에만 있으면 실행된다. 함수 인자는 호출 전에 계산되기 때문이다. 매크로가 먼저 검사하고 "
         "통과할 때만 조립하면 실행되지 않는다. 릴리스에서 매크로를 비웠다면 그때도 실행되지 않는다. (4.2절, 6.2절)"),
        ("파일로 갈 글자가 스트림 버퍼에 남은 채 프로세스가 죽었다.",
         "비정상 종료에서는 소멸자도 `Shutdown()`도 불리지 않아 flush될 기회가 없다. 콘솔과 파일의 flush 시점이 "
         "달랐던 것이다. (5.2절)"),
        ("`}` 뒤의 `;`가 `if` 문을 끝내 버려서 `else`가 짝을 잃는다.",
         "`do { … } while ( 0 )`은 끝에 `;`가 붙어야 비로소 한 문장이 되므로, 호출부의 `;`를 자연스럽게 받아 준다. (3.1절)"),
        ("Visual Studio에서는 `Client/` 폴더, 더블클릭하면 `Client.exe`가 있는 폴더.",
         "상대 경로는 작업 디렉터리 기준이다. Visual Studio의 기본 작업 디렉터리는 프로젝트 폴더이고, 탐색기는 "
         "실행 파일이 있는 폴더(`Client/Client.vcxproj:86`의 `OutDir`)를 작업 디렉터리로 준다. (5.3절)"),
        ("두 객체가 파괴되는 순서를 확인해야 한다.",
         "함수 안의 `static` 객체는 생성이 끝난 순서의 반대로 파괴된다. `main`에서 `GEngine::Get()`이 먼저 불리고 "
         "`GLogger::Get()`이 그 뒤에 처음 불렸다면 Logger가 먼저 사라지고, `~GEngine()`은 이미 파괴된 객체에 로그를 "
         "쓰게 된다. 1-4강에서 종료 순서를 다룰 때 다시 나온다. (6.4절)"),
    ]),
])

ch12 = glossary_chapter(12, [
    ("로그 레벨", "log level, verbosity", "로그의 심각도. 걸러 내는 기준이 된다"),
    ("카테고리", "category", "로그를 낸 시스템의 이름. `Core`, `Input`"),
    ("싱크", "sink", "로그가 나가는 곳. 콘솔, 파일"),
    ("전처리기 매크로", "preprocessor macro", "컴파일 전에 글자 치환으로 펼쳐지는 이름"),
    ("가변 인자 매크로", "variadic macro, __VA_ARGS__", "`...`으로 인자를 개수 제한 없이 받는 매크로"),
    ("소스 위치", "std::source_location", "파일·줄·함수 이름을 담는 C++20 타입"),
    ("형식 문자열", "format string", "`{}` 자리에 값을 끼워 넣는 틀이 되는 문자열"),
    ("벽시계 시각", "wall-clock time, system_clock", "달력과 시계가 가리키는 시각. 프로그램이 켜진 뒤 흐른 시간과 다르다"),
    ("스트림 버퍼", "stream buffer", "쓴 글자를 운영체제로 넘기기 전에 프로세스 안에 모아 두는 곳"),
    ("flush", "flush", "버퍼에 모인 글자를 운영체제로 내보내는 일"),
    ("ANSI 이스케이프 시퀀스", "ANSI escape sequence", "ESC로 시작해 콘솔에 색·커서 이동을 지시하는 글자열"),
    ("가상 터미널 처리", "ENABLE_VIRTUAL_TERMINAL_PROCESSING", "Windows 콘솔이 이스케이프 시퀀스를 해석하게 하는 모드"),
    ("핸들", "HANDLE", "운영체제가 관리하는 대상을 가리키는 값. 표준 출력, 파일, 창"),
    ("작업 디렉터리", "working directory", "상대 경로의 기준이 되는 폴더. 실행하는 방법에 따라 달라진다"),
], pb=False)


def todo(mission: str, rows: list) -> Raw:
    """One mission of the task list: a heading and a small table kept on one page."""
    return keep(h4(mission),
                table([6, 54, 40], ["", "할 일", "됐는지 보는 법"], rows, cell_cls=["num", "", ""], compact=True))


ch13 = chapter(13, "할 일 목록", [
    keep(h3("13.1", "결정이 막히면"),
    p("6.2절의 일곱 가지를 고르지 못해 미션이 멈출 때 쓰는 기본 선택이다. 정답이 아니라 1.2절의 선언을 가장 덜 고치고 "
      "나중에 바꾸기 쉬운 쪽이다. 다른 선택을 해도 미션의 “통과”만 맞으면 된다."),
    table([32, 68], ["결정", "막혔을 때의 기본 선택"], [
        ["호출 위치를 얻는 방법", "매크로와 `__FILE__`·`__LINE__`. 1.2절의 선언 그대로다"],
        ["레벨 검사의 위치", "`Log()` 안 한 곳"],
        ["flush 시점", "줄마다"],
        ["카테고리의 표현", "문자열. 1.2절의 선언 그대로다"],
        ["`message`의 타입", "`const std::string&`. 1.2절의 선언 그대로다"],
        ["`Init`·`Shutdown`을 부르는 곳", "`Client/main.cpp`. 엔진의 `Init`보다 먼저 켜고, 엔진의 일이 끝난 뒤에 끈다"],
        ["릴리스 빌드의 `Trace`·`Debug`", "남긴다"],
    ], cell_cls=["lab", ""], compact=True)),

    h3("13.2", "미션별 할 일"),
    todo("미션 1 — 파일을 만들고 Log()가 콘솔에 한 줄을 찍는다", [
        ["1", "`Engine/Enum/LogLevel.h`, `Engine/Core/Logger.h`, `Engine/Core/Logger.cpp`를 만들어 Engine 프로젝트에 더한다",
         "`Engine/Engine.vcxproj`에 세 파일의 항목이 생겼다"],
        ["2", "2.1절과 1.2절의 선언을 옮긴다. 1.2절 주석의 질문 둘(직접 쓰는 표준 헤더, 싱글턴을 지키는 특수 멤버 함수)에 "
              "답해 채운다", "`Logger.cpp`가 `Logger.h`를 포함한 채로 컴파일된다"],
        ["3", "`GLogger::Get()`이 늘 같은 객체를 돌려준다 (1-1강 7장)", "두 곳에서 본 `&GLogger::Get()`의 주소가 같다"],
        ["4", "`Log()`가 받은 레벨의 이름, 카테고리, 메시지를 한 줄로 콘솔에 찍는다. 시각과 색은 아직 넣지 않는다",
         "레벨 자리에 숫자가 아니라 이름이 찍힌다"],
        ["5", "`main`에서 `Log()`를 직접 한 번 부른다. 파일과 줄 자리는 손으로 채운다. 미션 6에서 없앨 임시 호출이다",
         "콘솔에 그 한 줄이 찍힌다"],
    ]),
    todo("미션 2 — 최소 레벨보다 낮은 로그를 버린다", [
        ["1", "`_min_level`을 바꾸는 함수를 만든다 (6.3절의 `SetMinLevel`)", "선언과 본체가 있고 빌드된다"],
        ["2", "호출의 레벨이 최소 레벨보다 낮으면 그 로그는 찍히지 않는다. 같거나 높으면 찍힌다",
         "최소 레벨을 `Error`로 올리면 `Warning` 호출은 안 찍히고 `Error` 호출은 찍힌다"],
        ["3", "검사를 두는 자리는 6.2절의 둘째 결정이다. 매크로 쪽을 골랐어도 매크로는 미션 6에서 생기므로 지금은 "
              "`Log()`에 두고 그때 옮긴다", "지금은 `Log()` 안에 비교하는 줄이 보인다"],
        ["4", "최소 레벨을 읽는 함수(6.3절의 `GetMinLevel`)를 둘지 정한다. 누가 읽는가는 6.3절 스케치의 질문이다",
         "두기로 했다면 선언과 본체가 있다"],
    ]),
    todo("미션 3 — 시각을 붙인다", [
        ["1", "줄 맨 앞에 그 로그를 찍는 순간의 시각을 `시:분:초.밀리초`로 붙인다. 날짜는 넣지 않는다. 시각을 얻는 방법은 "
              "4.3절 표의 두 가지 가운데 고른다", "모든 줄이 시각으로 시작한다"],
        ["2", "지역 시각으로 찍는다", "찍힌 시와 분이 컴퓨터의 시계와 같다. 9시간 차이가 나면 UTC다"],
        ["3", "초 아래는 세 자리로 찍는다", "초 아래 숫자가 셋이다. 일곱이면 자르지 않은 것이다"],
    ]),
    todo("미션 4 — 레벨마다 색을 입힌다", [
        ["1", "`GLogger::Init`이 콘솔에 색 코드를 해석해 달라고 요청한다. 쓸 함수는 5.1절의 셋이고, 부르는 순서는 카드의 "
              "“부르는 순서” 칸에서 찾는다", "색 코드를 보내도 `←[32m` 같은 글자가 화면에 보이지 않는다"],
        ["2", "요청이 실패했을 때 무엇을 할지 정한다. 출력이 콘솔이 아니면 실패한다 (5.1절 끝)",
         "세 함수의 반환값을 받아 보는 줄이 있다"],
        ["3", "레벨마다 다른 색을 정하고 (5.1절의 색 표), `Log()`가 콘솔로 가는 글자에만 그 색 코드를 넣는다",
         "레벨이 다른 두 줄의 색이 다르다"],
        ["4", "엔진이 첫 로그를 찍기 전에 `GLogger::Init`을 부른다. 부르는 곳은 6.2절의 여섯째 결정이다",
         "첫 줄부터 색이 입혀져 나온다"],
    ]),
    todo("미션 5 — 파일에도 쓴다", [
        ["1", "`Init`이 받은 이름으로 로그 파일을 연다. 지난 로그를 비울지 이어 붙일지는 직접 정한다 (5.3절)",
         "실행하면 그 이름의 파일이 생긴다. 안 보이면 작업 디렉터리를 찾는다"],
        ["2", "파일을 열지 못했을 때 무엇을 할지 정한다. 열렸는지 아는 방법은 5.3절의 카드에 있다",
         "연 다음에 결과를 확인하는 줄이 있다"],
        ["3", "`Log()`가 콘솔에 찍은 것과 같은 줄을 파일에도 쓴다. 색 코드는 넣지 않는다",
         "메모장으로 열면 콘솔과 같은 줄이 있고 `[31m` 같은 글자가 없다"],
        ["4", "6.2절의 셋째 결정에서 고른 시점에 flush한다",
         "실행 중에 파일을 열어 보면 고른 대로다. 줄마다라면 방금 찍힌 줄까지 있다"],
        ["5", "`Shutdown`이 남은 글자를 내보내고 파일을 닫는다", "끝낸 뒤 파일에 마지막 줄까지 있다"],
        ["6", "`Shutdown`을 부른다. 부르는 곳은 6.2절의 여섯째 결정이다. 엔진에 종료 경로가 아직 없으면 임시 자리에 두고 "
              "1-4강에서 옮긴다 (6.4절)", "창을 닫으면 `Shutdown()`의 중단점에 한 번 걸린다"],
    ]),
    todo("미션 6 — 매크로로 감싼다", [
        ["1", "호출부가 레벨, 카테고리, 형식 문자열, 값만 적으면 되는 호출 방법을 만든다. 방법은 6.2절의 첫째 결정이다. "
              "이름과 인자 순서는 6.1절의 예와 달라도 된다",
         "6.1절의 세 줄과 같은 모양의 호출이 컴파일된다. 값이 둘, 하나, 없는 호출이다"],
        ["2", "형식 문자열과 값이 `Log()`에 닿기 전에 문자열 하나로 합쳐진다 (4.2절)", "`{}` 자리에 값이 들어간 메시지가 찍힌다"],
        ["3", "파일 이름과 줄 번호는 호출한 자리의 것이 저절로 들어가 줄 끝에 찍힌다",
         "찍힌 위치가 그 호출을 적은 파일과 줄이다. `Logger.cpp`로 나오면 3장을 다시 본다"],
        ["4", "중괄호 없는 `if`와 `else` 사이에 써도 컴파일된다", "10장 4번의 줄을 그대로 적으면 컴파일된다"],
        ["5", "6.2절의 둘째 결정(레벨 검사의 위치)을 반영한다",
         "매크로 쪽을 골랐다면 낮은 레벨의 호출이 `Log()`의 중단점에 걸리지 않는다"],
        ["6", "6.2절의 일곱째 결정(릴리스 빌드의 `Trace`·`Debug`)을 반영한다",
         "빼기로 했다면 `_DEBUG`가 없을 때 두 매크로의 정의가 비어 있다"],
        ["7", "미션 1에서 `main`에 적은 직접 호출을 새 방법으로 바꾼다", "호출부에 파일 이름이나 줄 번호를 손으로 적은 곳이 없다"],
    ]),
    todo("미션 7 — 기존 코드를 바꾼다", [
        ["1", "`GEngine::Run`이 Update 콜백 없이 불리면 로그 호출로 알린다", "Update 콜백을 달지 않고 실행하면 그 줄이 찍힌다"],
        ["2", "`GEngine::Init`의 GLAD 실패 분기가 로그 호출로 이유를 남긴다. 1-4강에서 `std::cerr`로 찍어 둔 줄이 있으면 "
              "그것도 바꾼다", "그 분기 안에 로그 호출이 보인다"],
        ["3", "`MInputManager`의 조회 함수 셋이 잘못된 키를 받으면 로그 호출로 알린다. 프레임마다 불리는 함수라 같은 줄이 "
              "이어질 수 있다. 그대로 둘지는 직접 정한다", "잘못된 키로 조회 함수를 한 번 부르면 그 줄이 찍힌다"],
        ["4", "세 자리의 레벨을 직접 고른다 (2.1절의 표)", "자리마다 그 레벨을 고른 이유를 한 줄로 말할 수 있다"],
        ["5", "`Engine/`에 남은 `std::cout`, `std::cerr`, `printf` 줄을 로그 호출로 바꾸거나 지운다",
         "`Engine/`을 검색하면 로거가 콘솔에 쓰는 줄에서만 나온다"],
        ["6", "더는 쓰지 않는 `<iostream>` 포함을 지운다", "`<iostream>`이 남은 파일에는 그것을 실제로 쓰는 줄이 있다"],
    ]),
    todo("미션 8 — 검증하고 치운다", [
        ["1", "`main`에서 여섯 레벨을 한 번씩 찍는다", "여섯 줄이 나오고 레벨마다 색이 다르다"],
        ["2", "최소 레벨을 `Warning`으로 올리고 다시 실행한다", "콘솔과 로그 파일 양쪽에 `Warning`·`Error`·`Fatal` 세 줄만 남는다"],
        ["3", "시험하려고 넣은 호출을 지운다", "`Client/main.cpp`에 시험용 호출이 남아 있지 않다"],
        ["4", "6.2절의 일곱 가지마다 고른 것과 이유를 한 줄씩 적어 두었는지 본다", "일곱 줄이 채워져 있다"],
        ["5", "9장의 일곱 줄을 확인하고 커밋 하나로 묶는다", "9장의 일곱 줄이 모두 맞다"],
    ]),
], lead="미션의 문장만으로 무엇을 하라는 것인지 분명하지 않을 때 보는 목록이다. 미션마다 할 일을 한 줄씩 풀고, 됐는지 "
        "보는 법을 옆에 적었다. 어떻게 하는지는 적지 않았다. 그것은 2 〜 5장과 미션의 힌트에 있다.", pb=True)

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
