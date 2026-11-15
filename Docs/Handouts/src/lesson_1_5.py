"""Lesson 1-5 -- Logger (a skeleton already exists in the repository; this handout finishes it).

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

# The engine code has not changed since CODE_COMMIT; it was read again on this day.
READ_DATE = "2026-11-15"

COVER = cover(
    f"CLAUDGL ENGINE · PART {ME['part']} · {ME['id']} · v{ME['ver']}",
    Raw('G<span class="ac">Logger</span>'),
    ME["title"],
    "엔진이 지금 무슨 일을 하고 있는지 스스로 말하게 만든다",
    [
        ("목표 결과물", "콘솔과 파일에 시각·레벨·카테고리가 붙은 로그가 찍히고, `Engine/` 안의 `std::cout`이 사라진다"),
        ("핵심 개념", "로그 레벨과 카테고리 · 매크로와 `std::source_location` · `std::format` · 콘솔 색 · 버퍼와 flush"),
        ("선수 지식", "1-1 〜 1-3강의 코드. 1-4강은 아직 하지 않았어도 된다 (6.4절)"),
        ("예상 시간", f"읽기 40분 + 구현 3시간 남짓 (계획서 기준 {ME['hours']}시간)"),
        ("건드릴 파일", "`Engine/Core/Logger.h`·`.cpp`, `Engine/Core/EngineCore.cpp`, "
                   "`Engine/Manager/InputManager.cpp`, `Client/main.cpp`"),
        ("코드 기준", f"커밋 `{CODE_COMMIT}`의 엔진 코드 — {READ_DATE}에 읽음"),
    ],
    note=("읽는 법",
          "뼈대는 이미 있다. 1장에서 무엇이 있고 무엇이 비었는지 확인하고, 2 〜 5장의 개념을 읽은 뒤, 6장에서 "
          "결정할 것을 적고 7장의 미션을 순서대로 구현한다. 코드 블록은 완성본이 아니다."),
    toc=["왜 필요한가", "로그 한 줄의 구성", "호출한 자리를 어떻게 아는가", "메시지 조립: std::format",
         "어디에 쓰는가: 콘솔과 파일", "설계", "구현 미션", "흔한 함정", "완료 기준", "생각해 볼 질문", "해설", "용어집"],
)

# --------------------------------------------------------------------------

ch1 = chapter(1, "왜 필요한가", [
    h3("1.1", "지금 엔진이 말하는 방식"),
    code(r"""
    if ( !_on_update )
    {
        std::cout << "GEngine::Update() is null.\n";
    }
""", title="Engine/Core/EngineCore.cpp", tag="now", start=64, hl=[66]),
    table([38, 23, 39], ["위치", "지금 하는 일", "빠진 것"], [
        ["`Engine/Core/EngineCore.cpp:66`", "`std::cout`으로 한 줄을 찍는다",
         "언제 났는지, 얼마나 심각한지, 어느 시스템인지가 없다. 끄거나 파일로 남길 방법도 없다."],
        ["`Engine/Core/EngineCore.cpp:30` 〜 `:33`", "GLAD 로드에 실패하면 `Fail`을 돌려준다",
         "이유를 남기지 않는다. `Client/main.cpp:13` 〜 `:14`도 말없이 끝낸다."],
        ["`Engine/Manager/InputManager.cpp:35`, `:42`, `:49`", "`// need log` 주석 셋",
         "잘못된 키가 들어와도 조용히 `false`를 돌려준다."],
    ]),
    p("엔진이 커질수록 “화면이 검은데 왜인지 모르겠다”는 상황이 늘어난다. 2-1강부터는 GL이 내는 오류와 경고를 받아 적을 "
      "곳이 필요하고, 셰이더 컴파일 오류(2-4강)도 같은 통로로 나온다. 그 통로를 여기서 만든다."),

    h3("1.2", "이미 있는 뼈대"),
    code(r"""
class GLogger
{
public:
    static GLogger& Get();

    void Init( const char* file_name );
    void Shutdown();
""", title="Engine/Core/Logger.h", tag="now", start=6),
    p("`Engine/Core/Logger.h:14`의 `Log()`는 매개변수가 다섯이다. 한 줄이 길어 표로 옮긴다."),
    keep(table([32, 68], ["매개변수", "뜻"], [
        ["`ELogLevel log_level`", "얼마나 심각한가 (2.1절)"],
        ["`std::string_view category`", "어느 시스템의 로그인가 (2.3절)"],
        ["`const char* file`, `int line`", "로그를 부른 자리. 누가 채워 넣는지가 3장의 주제다"],
        ["`const std::string& message`", "이미 완성된 문자열. 값을 끼워 넣는 조립은 `Log()` 밖에서 끝난다는 뜻이다 (4장)"],
    ], cell_cls=["lab", ""])),
    code(r"""
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
""", title="Engine/Core/Logger.cpp", tag="now", start=12),
    table([30, 14, 56], ["부품", "상태", "근거"], [
        ["싱글턴 접근 `Get()`", "있다", "`Engine/Core/Logger.cpp:6` 〜 `:10`. `GEngine`과 같은 방식이다 (1-1강)"],
        ["로그 파일 열기·닫기", "있다", "14행, 23행. 열기에 실패했는지는 확인하지 않는다"],
        ["콘솔 색 준비", "있다", "15 〜 18행. 두 함수의 반환값은 확인하지 않는다 (5.1절)"],
        ["`Log()` 본문", "==비었다==", "`Engine/Core/Logger.cpp:26` 〜 `:28`"],
        ["최소 레벨 `_min_level`", "반쯤", "`Engine/Core/Logger.h:25`에 멤버만 있다. 바꾸는 함수도, 읽는 곳도 없다"],
        ["호출 매크로", "없다", "`file`과 `line`을 호출부가 손으로 적어야 하는 상태다"],
        ["`Init`·`Shutdown`을 부르는 곳", "없다", "`GLogger`는 `Logger.h`·`.cpp` 밖에서 한 번도 쓰이지 않는다"],
    ], cell_cls=["lab", "c", ""], compact=True),
    p("눈에 띄는 것이 둘 더 있다. `LogLevel.h`가 프로젝트 파일에 헤더(`ClInclude`)가 아니라 `Content`로 들어가 "
      "있다(`Engine/Engine.vcxproj:350`). 빌드에는 영향이 없다. 그리고 `Logger.h`는 `std::string`과 "
      "`std::string_view`를 쓰면서 `<fstream>`만 포함한다(2행). `pch.h`가 `<string>`을 먼저 넣어 주어서 지금은 통한다."),
], lead="지금 엔진은 문제가 생겨도 거의 말이 없다. 말하는 곳은 한 군데이고, 말해야 할 자리 세 곳에는 주석만 있다.")

ch2 = chapter(2, "로그 한 줄의 구성", [
    console(Raw(
        '<span class="dim">[14:02:07.318]</span> <span class="warn">[Warn ]</span> [Input] '
        'Invalid key: 512  <span class="dim">(InputManager.cpp:35)</span>'
    ), title="로그 한 줄 (형식은 예시)"),
    keep(table([18, 26, 56], ["조각", "답하는 질문", "메모"], [
        ["시각", "언제 일어났나", "두 줄 사이에 얼마나 걸렸는지도 여기서 읽는다"],
        ["레벨", "얼마나 심각한가", "걸러 내는 기준이자 색을 정하는 기준"],
        ["카테고리", "어느 시스템인가", "`Core`, `Input`, `Render`. 검색할 때 쓰는 손잡이"],
        ["메시지", "무슨 일인가", "값이 들어간 문장. “실패했다”보다 “무엇이 왜 실패했다”"],
        ["위치", "코드의 어디인가", "파일과 줄 번호. 메시지만으로 찾기 어려울 때 쓴다"],
    ], cell_cls=["lab", "", ""])),

    h3("2.1", "레벨"),
    code(r"""
enum class ELogLevel : int
{
    Trace,
    Debug,
    Info,
    Warning,
    Error,
    Fatal
};
""", title="Engine/Enum/LogLevel.h", tag="now", start=3),
    table([14, 44, 42], ["레벨", "언제 쓰는가", "예"], [
        ["`Trace`", "흐름을 따라갈 때만 켜는 아주 잦은 기록", "프레임마다 찍는 값, 함수 진입"],
        ["`Debug`", "개발 중에만 궁금한 값", "창 크기, 읽어 들인 파일 수"],
        ["`Info`", "정상적으로 일어난 큰 일", "엔진 초기화 완료"],
        ["`Warning`", "이상하지만 계속 갈 수 있다", "잘못된 키 코드, 콜백이 비어 있음"],
        ["`Error`", "요청받은 일이 실패했다", "파일을 열지 못함"],
        ["`Fatal`", "더 진행할 수 없다", "GL 함수 로드 실패"],
    ], cell_cls=["lab", "", ""]),
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

    h3("2.3", "카테고리"),
    p("레벨이 세로축이라면 카테고리는 가로축이다. 로그가 수천 줄이 되면 “입력 쪽 경고만” 보고 싶어진다. 지금 뼈대는 "
      "카테고리를 `std::string_view`로 받는다(`Engine/Core/Logger.h:14`). 문자열이면 새 카테고리를 만드는 데 아무 "
      "준비가 필요 없고, 대신 오타(`\"Inptu\"`)를 컴파일러가 잡아 주지 못한다."),
    box("ue", None,
        "`UE_LOG( LogTemp, Warning, TEXT( \"...\" ) )`의 세 인자가 카테고리, 레벨(Verbosity), 메시지다. 레벨은 `Fatal`, "
        "`Error`, `Warning`, `Display`, `Log`, `Verbose`, `VeryVerbose` 일곱 단계이고 `Fatal`은 찍은 뒤 프로그램을 "
        "멈춘다. 카테고리는 문자열이 아니라 `DECLARE_LOG_CATEGORY_EXTERN`으로 선언하는 객체라서, 카테고리마다 "
        "레벨을 따로 조절할 수 있다 (콘솔 명령 `Log LogTemp Verbose`)."),
], lead="로그 한 줄은 다섯 조각으로 이루어진다. 조각마다 나중에 로그를 읽는 사람의 질문 하나에 답한다.")

ch3 = chapter(3, "호출한 자리를 어떻게 아는가", [
    p("위치 정보는 `Log()`를 **부른 쪽**의 파일과 줄이어야 쓸모가 있다. 그런데 함수는 자기를 누가 불렀는지 모른다."),
    code(r"""
void GLogger::Log( /* ... */ )
{
    // __FILE__ and __LINE__ are replaced right here, inside Logger.cpp
    std::cout << __FILE__ << ":" << __LINE__;   // always "Logger.cpp:<this line>"
}
""", title="every log line points at the logger itself", tag="bad"),

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
    p("`__FILE__`에 무엇이 들어가는지는 컴파일러에 넘어간 경로에 달렸다. MSVC는 `/FC` 옵션이 켜져 있으면 전체 "
      "경로(`D:\\…\\EngineCore.cpp`)를 넣는다. 로그 한 줄이 길어지는 것이 싫으면 파일 이름만 남기는 처리가 필요하다."),

    h3("3.2", "방법 둘: std::source_location (C++20)"),
    code(r"""
#include <source_location>

void Where( std::source_location loc = std::source_location::current() );
// loc.file_name()  loc.line()  loc.function_name()
""", tag="syntax"),
    p("기본 인자는 함수를 **부르는 자리**에서 계산된다. 그래서 `current()`를 기본 인자로 두면 호출한 쪽의 위치가 "
      "들어온다. 매크로 없이 같은 일을 하는 표준 방법이다."),
    table([28, 36, 36], ["", "매크로 + `__FILE__`·`__LINE__`", "`std::source_location`"], [
        ["호출부의 모양", "매크로 이름으로 부른다", "평범한 함수 호출"],
        ["함수 이름", "`__FUNCTION__`을 따로 넘긴다 (MSVC 확장)", "`function_name()`으로 함께 온다"],
        ["형식 인자와 함께 쓰기", "`...`으로 그대로 넘긴다", "기본 인자를 매개변수 팩 뒤에 둘 수 없어 우회가 필요하다"],
        ["릴리스에서 호출을 지우기", "매크로를 비우면 된다", "호출은 남는다"],
        ["디버거에서 따라 들어가기", "펼쳐진 코드라 한 줄로 보인다", "함수라서 그대로 들어간다"],
    ], cell_cls=["lab", "", ""]),
    box("point", None,
        "지금 `Log()`는 `const char* file, int line`을 받는다(`Engine/Core/Logger.h:14`). 호출부가 이 둘을 손으로 적지 "
        "않게 하려면 매크로가 한 겹 필요하다는 뜻이다. `std::source_location`으로 가면 이 두 매개변수는 하나로 바뀐다. "
        "어느 쪽으로 갈지는 6.2절에서 정한다."),
    box("cs", None,
        "전처리는 컴파일보다 앞 단계다. 전처리기는 타입도 범위도 모르고 토큰만 바꿔 끼운다. 매크로의 장점(호출 자리에서 "
        "펼쳐진다, 지울 수 있다)과 단점(범위가 없다, 타입 검사가 없다)이 모두 여기서 나온다. 전공서의 번역 단계"
        "(translation phases) 항목과 닿는다."),
], lead="로그에 파일과 줄 번호를 넣으려면 풀어야 하는 문제가 하나 있다. 방법은 둘이고 성격이 다르다.")

ch4 = chapter(4, "메시지 조립: std::format", [
    h3("4.1", "형식 문자열"),
    code(r"""
#include <format>

std::string a = std::format( "{} x {} = {}", 3, 4, 12 );     // "3 x 4 = 12"
std::string b = std::format( "{:>8.3f} ms", 16.6667 );       // "  16.667 ms"
""", tag="syntax"),
    table([20, 42, 38], ["표기", "뜻", "예 → 결과"], [
        ["`{}`", "다음 인자를 기본 모양으로", "`{}` , 42 → `42`"],
        ["`{:6}`", "폭 6. 숫자는 오른쪽, 문자열은 왼쪽 정렬", "`{:6}` , \"ab\" → `ab    `"],
        ["`{:<6}` `{:>6}` `{:^6}`", "왼쪽, 오른쪽, 가운데 정렬", "`{:>6}` , \"ab\" → `    ab`"],
        ["`{:05}`", "빈자리를 0으로 채운다", "`{:05}` , 42 → `00042`"],
        ["`{:.2f}`", "소수점 아래 2자리", "`{:.2f}` , 3.14159 → `3.14`"],
        ["`{:x}`", "16진수", "`{:x}` , 255 → `ff`"],
        ["`{0}` `{1}`", "인자를 번호로 가리킨다", "`{1}-{0}` , 1, 2 → `2-1`"],
    ], cell_cls=["lab", "", ""], compact=True),
    table([22, 26, 26, 26], ["", "`printf`", "`<<`", "`std::format`"], [
        ["형식과 값이 한눈에", "보인다", "값 사이에 흩어진다", "보인다"],
        ["형식과 인자가 어긋나면", "실행 중에 깨진다", "어긋날 일이 없다", "컴파일 오류"],
        ["내가 만든 타입", "넣을 수 없다", "`operator<<`", "`std::formatter` 특수화"],
        ["결과", "화면이나 `char` 버퍼", "스트림", "`std::string`"],
    ], cell_cls=["lab", "", "", ""], compact=True),
    p("`std::format`은 형식 문자열을 컴파일할 때 검사한다. `{}`가 둘인데 인자가 하나면 빌드가 실패한다. 그 대가로 "
      "형식 문자열은 컴파일 시점에 알려진 상수여야 한다. 실행 중에 만들어진 문자열을 형식으로 쓰려면 `std::vformat`과 "
      "`std::make_format_args`를 쓴다."),
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
    table([30, 35, 35], ["", "`std::chrono` + `std::format`", "`localtime_s` + `std::strftime`"], [
        ["지금 시각을 얻는 곳", "`std::chrono::system_clock::now()`", "`std::time( nullptr )`"],
        ["형식", "`{:%H:%M:%S}`", "`\"%H:%M:%S\"`"],
        ["그대로 쓰면", "UTC로 나오고, MSVC에서는 초 아래 7자리까지 나온다", "지역 시각, 초 단위까지"],
        ["손볼 것", "지역 시각으로 바꾸기, 밀리초로 자르기", "밀리초를 따로 구해 붙이기"],
    ], cell_cls=["lab", "", ""]),
    p("`system_clock`의 시각은 UTC다. 한국에서는 9시간 이른 숫자가 찍힌다. 지역 시각으로 바꾸는 도구는 "
      "`std::chrono::current_zone()`과 `zoned_time`이고(MSVC에서는 Windows 10 1903 이상이 필요하다), 자릿수는 "
      "`std::chrono::floor<std::chrono::milliseconds>`로 자른다. 프레임 시간을 재는 `glfwGetTime()`(1-2강)은 "
      "프로그램이 시작한 뒤 흐른 초라서 벽시계 시각이 아니다. 로그에는 벽시계 시각이 맞다."),
    box("cs", None,
        "`printf`의 `...`은 타입 정보 없이 값만 스택에 쌓아 넘기는 C의 가변 인자다. 형식 문자열의 `%d`를 믿고 꺼내므로 "
        "어긋나면 엉뚱한 메모리를 읽는다. `std::format`은 가변 인자 템플릿이라 컴파일러가 인자마다 타입을 안다. "
        "“컴파일 시점에 아는 것이 많을수록 실행 중 사고가 준다”는 C++의 방향을 보여 주는 예다."),
], lead="값을 문장에 끼워 넣는 일이다. C++20의 `<format>`을 쓴다. 프로젝트는 이미 C++20이다(`Engine/Engine.vcxproj:113`).")

ch5 = chapter(5, "어디에 쓰는가: 콘솔과 파일", [
    h3("5.1", "콘솔에 색 입히기"),
    code(r"""
std::cout << "\x1b[31m" << "red" << "\x1b[0m" << " normal\n";   // 31 = red, 0 = reset
""", tag="syntax"),
    p(r"`\x1b`는 ESC 문자(27)다. ESC, `[`, 숫자, `m`으로 이어지는 글자열을 콘솔은 화면에 찍지 않고 명령으로 "
      "받아들인다. ANSI 이스케이프 시퀀스라고 부른다. 한 번 바꾼 색은 되돌릴 때까지 이어지므로 끝에 0번(reset)을 "
      "보내야 한다."),
    table([16, 20, 16, 20, 28], ["코드", "색", "코드", "색", "비고"], [
        ["`30` 〜 `37`", "기본 8색", "`90` 〜 `97`", "밝은 8색", "글자색"],
        ["`31`", "빨강", "`33`", "노랑", "오류, 경고에 흔히 쓴다"],
        ["`32`", "초록", "`36`", "청록", "정보, 디버그에 흔히 쓴다"],
        ["`90`", "회색", "`41`", "빨강 배경", "`40` 〜 `47`이 배경색"],
        ["`0`", "전부 되돌림", "`1`", "굵게", "`;`로 이어 쓴다: `1;31`"],
    ], cell_cls=["lab", "", "lab", "", ""], compact=True),
    p("Windows 콘솔은 이 글자열을 해석하는 기능(가상 터미널 처리)이 기본으로 꺼져 있다. 켜는 코드가 뼈대의 `Init`에 "
      "이미 있다(`Engine/Core/Logger.cpp:15` 〜 `:18`). `GetConsoleMode`로 현재 모드를 읽고, "
      "`ENABLE_VIRTUAL_TERMINAL_PROCESSING` 비트를 더해 `SetConsoleMode`로 다시 넣는다. 켜지 않은 채로 색 코드를 "
      "보내면 `←[31m` 같은 글자가 그대로 보인다."),
    p("두 함수는 실패할 수 있다. 출력이 콘솔이 아닐 때다. `Client.exe > out.txt`처럼 출력을 파일로 돌리면 "
      "`GetConsoleMode`가 실패하고, 색 코드는 그 파일에 글자로 남는다. 지금 코드는 반환값을 보지 않는다."),

    h3("5.2", "버퍼와 flush"),
    flow([
        ("쓰기", "스트림에 넣는다"),
        ("스트림 버퍼", "프로세스 안", "accent"),
        ("운영체제", "flush 때 넘어간다"),
        ("파일", "디스크", "dark"),
    ], "`<<`로 쓴 글자는 먼저 프로세스 안의 버퍼에 모인다. 버퍼가 차거나 flush할 때 운영체제로 넘어간다."),
    p(r"파일에 쓸 때마다 운영체제를 부르면 느리므로 스트림은 모았다가 한꺼번에 넘긴다. 문제는 프로그램이 "
      "비정상으로 죽을 때다. 버퍼에 남아 있던 글자는 프로세스와 함께 사라진다. 로그가 가장 필요한 순간이 바로 그때다. "
      r"`std::endl`은 `'\n'`을 쓰고 flush까지 한다. `'\n'`만 쓰면 flush하지 않는다. `close()`와 스트림의 소멸자는 "
      "flush한다."),
    table([24, 38, 38], ["flush 시점", "얻는 것", "내주는 것"], [
        ["줄마다", "죽기 직전 줄까지 파일에 남는다", "로그가 많을 때 느려진다"],
        ["`Warning` 이상일 때만", "중요한 줄은 남고 평소에는 빠르다", "죽기 직전의 `Info`·`Debug`는 잃을 수 있다"],
        ["`Shutdown()`에서만", "가장 빠르다", "비정상 종료 때 마지막 부분이 통째로 없다"],
    ], cell_cls=["lab", "", ""]),

    h3("5.3", "로그 파일"),
    ul([
        "`_log_file.open( file_name )`(`Engine/Core/Logger.cpp:14`)은 모드를 주지 않았으므로 파일을 비우고 새로 쓴다. "
        "실행할 때마다 지난 로그가 사라진다. 이어 붙이려면 `std::ios::app`이다.",
        "상대 경로는 작업 디렉터리 기준이다. Visual Studio에서 실행하면 기본 작업 디렉터리는 프로젝트 폴더라서 "
        "`Client/` 아래에 생긴다. 경로를 제대로 다루는 일은 1-7강이다.",
        "열기에 실패해도 예외가 나지 않는다. 그 뒤의 쓰기가 조용히 무시될 뿐이다. `is_open()`으로 확인한다.",
        "파일에는 색 코드를 넣지 않는다. 메모장으로 열었을 때 `[31m`이 섞여 보인다.",
        "`.gitignore`에 이미 `*.log`가 있다(96행). 확장자를 `.log`로 하면 저장소에 올라가지 않는다.",
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
├── Core/
│   ├── EngineCore.cpp  #std::cout and silent failures -> log calls
│   ├── Logger.h  #new declarations; do the macros live here too?
│   └── Logger.cpp  #Log() body and its helpers
└── Manager/
    └── InputManager.cpp  #three "// need log" comments -> log calls
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
        ["호출 위치를 얻는 방법", "매크로와 `__FILE__`·`__LINE__` (지금 시그니처) / `std::source_location`",
         "3.2절의 표. 형식 인자를 어떻게 넘길지와 함께 정해야 한다"],
        ["레벨 검사의 위치", "`Log()` 안 / 매크로 안 / 둘 다",
         "매크로에서 검사하면 버려질 로그의 조립을 건너뛴다. 대신 매크로가 최소 레벨을 읽을 수 있어야 한다"],
        ["flush 시점", "줄마다 / `Warning` 이상 / `Shutdown()`에서만", "5.2절의 표. 콘솔과 파일을 다르게 둘 수도 있다"],
        ["카테고리의 표현", "문자열 (지금) / 열거형 / 카테고리 객체",
         "오타를 컴파일러가 잡는가, 새 카테고리를 만드는 수고, 카테고리별 레벨이 필요한가"],
        ["`message`의 타입", "`const std::string&` (지금) / `std::string_view`",
         "문자열 리터럴만 넘길 때 임시 `std::string`이 만들어지는가"],
        ["`Init`·`Shutdown`을 부르는 곳", "`Client/main.cpp` / `GEngine::Init` 안",
         "엔진보다 먼저 준비되어야 엔진의 초기화 실패를 적을 수 있다. 로그 파일 이름은 누가 정하는가"],
        ["릴리스 빌드의 `Trace`·`Debug`", "남긴다 / 컴파일에서 뺀다",
         "뺀다면 매크로를 `_DEBUG`에 따라 다르게 정의한다. 뺀 매크로의 인자는 계산되지 않는다"],
    ], cell_cls=["lab", "", ""], compact=True)),
    box("decide", None,
        "위 일곱 가지에 정답은 없다. 미션에 들어가기 전에 행마다 하나를 고르고 이유를 한 줄씩 적어 둔다. 지금 뼈대는 "
        "첫째·넷째·다섯째에서 이미 한쪽을 골라 두었다. 그대로 가도 되고 바꿔도 된다."),

    h3("6.3", "선언 스케치"),
    p("결정을 마친 뒤 `Logger.h`에 더할 선언의 모양이다. 주석은 답이 아니라 스스로에게 던질 질문이다."),
    code(r"""
class GLogger
{
public:
    void      SetMinLevel( ELogLevel level );
    ELogLevel GetMinLevel() const;      // who reads this: Log() only, or the macro too?

    // Log( level, category, file, line, message ) already exists.
    // Where does the level check live: here, in the macro, or both?

private:
    // Which helpers does Log() need?
    //   - level -> text  ("Info ", "Warn ", ...)
    //   - level -> console color
    //   - text for "now"
    // Free functions inside Logger.cpp, or private members here?
    // Which choice keeps Logger.h small for everyone who includes it?
};
""", title="Engine/Core/Logger.h", tag="sketch"),

    h3("6.4", "이 강에서 하지 않는 것"),
    table([30, 70], ["미루는 것", "이유"], [
        ["`Fatal`에서 멈추기", "이 강에서는 찍기만 한다. 조건이 깨진 자리에서 멈추는 일은 1-6강(Assert)이다"],
        ["제대로 된 종료 순서", "1-4강을 건너뛰었으므로 엔진에는 종료 경로가 없다. `Run()`이 끝나면 `main`이 끝난다"
                         "(`Client/main.cpp:19` 〜 `:20`). `Shutdown()`을 부르는 자리는 임시로 두고 1-4강에서 옮긴다"],
        ["초기화 실패 처리 전반", "`glfwInit()`과 창 생성의 실패 확인은 1-4강이다. 여기서는 이미 있는 실패 분기"
                           "(`Engine/Core/EngineCore.cpp:30` 〜 `:33`)에 로그만 넣는다"],
        ["스레드 안전", "지금은 스레드가 하나다. 잠금은 스레드가 생길 때 넣는다"],
        ["싱크 인터페이스", "출력 대상이 둘뿐이다. 셋째가 필요해질 때 추상화해도 늦지 않다"],
    ], cell_cls=["lab", ""]),
], lead="뼈대가 방향의 절반을 정해 두었다. 남은 것을 정한 뒤에 구현한다.")

ch7 = chapter(7, "구현 미션", [
    steps([
        ("`Log()`가 콘솔에 한 줄을 찍는다",
         "레벨 이름, 카테고리, 메시지를 2장의 예시처럼 찍는다. 시각과 색은 아직 없다. `main`에서 직접 불러 본다.",
         ["`enum class`는 저절로 글자가 되지 않는다. 레벨을 글자로 바꾸는 작은 함수가 먼저 필요하다.",
          "`switch`로 레벨마다 문자열 리터럴을 돌려준다. 이름의 폭을 맞추면 줄이 세로로 정렬된다 (4.1절)."]),
        ("최소 레벨보다 낮은 로그를 버린다",
         "`_min_level`을 바꾸는 함수를 만들고, 낮은 레벨이 실제로 찍히지 않는지 확인한다.",
         ["비교는 한 줄이다. `LogLevel.h`의 값 순서가 이미 맞춰져 있다 (2.1절)."]),
        ("시각을 붙인다",
         "줄 맨 앞에 `시:분:초.밀리초`를 붙인다.",
         ["찍힌 시각을 벽시계와 비교한다. 9시간 차이가 나면 UTC다. 초 아래 자릿수도 확인한다 (4.3절)."]),
        ("레벨마다 색을 입힌다",
         "콘솔 출력에만 색을 넣는다. 이 단계에서 `GLogger::Init`을 부르는 곳이 생겨야 한다.",
         ["색을 켜는 코드와 되돌리는 코드 사이에 무엇을 넣을지 정한다. 레벨 이름만인가, 줄 전체인가.",
          "`←[31m`이 그대로 보이면 `Init`이 불리지 않았거나 `SetConsoleMode`가 실패한 것이다."]),
        ("파일에도 쓴다",
         "같은 줄을 색 코드 없이 로그 파일에 쓴다. 6.2절에서 고른 flush 시점을 적용한다.",
         ["콘솔용과 파일용 문자열이 어디서 갈라지는지 생각한다. 공통 부분을 먼저 만들고 색만 덧붙이는 순서가 있다.",
          "`Init`에서 파일 열기에 실패했을 때 무엇을 할지 정한다. 콘솔은 살아 있다.",
          "실행한 뒤 파일이 어디에 생겼는지 직접 찾아본다 (5.3절)."]),
        ("매크로로 감싼다",
         "호출부가 파일과 줄을 적지 않고, 형식 문자열과 값을 그대로 넘길 수 있게 한다. 6.1절의 사용 예처럼 보이면 된다.",
         ["`__FILE__`과 `__LINE__`은 매크로 본문 안에 적어야 호출한 자리의 값이 된다 (3.1절).",
          "형식 문자열까지 `...`에 포함시키면 값이 하나도 없는 호출을 따로 다루지 않아도 된다.",
          "`if` 뒤에 중괄호 없이 써도 깨지지 않는지 확인한다 (10장의 4번).",
          "`std::source_location`을 골랐다면 3.2절 표의 “형식 인자와 함께 쓰기” 칸이 여기서 풀 문제다."]),
        ("기존 코드를 바꾼다",
         "1.1절 표의 세 곳을 로그 호출로 바꾼다 (레벨은 직접 고른다). `EngineCore.cpp:6`의 `<iostream>`도 없앤다.",
         ["`IsKeyPressed`는 프레임마다 불린다. 같은 경고가 초당 수백 줄 찍힐 수 있다. 그대로 둘지 정한다.",
          "초기화가 끝났다는 `Info` 한 줄을 넣어 두면 그 뒤의 모든 로그에 기준점이 생긴다."]),
        ("검증하고 치운다",
         "여섯 레벨을 한 번씩 찍어 색을 보고, 최소 레벨을 `Warning`으로 바꿔 세 줄만 나오는지 본다. 로그 파일에 "
         "색 코드가 없는지 메모장으로 확인한 뒤 임시 호출을 지운다."),
    ]),
], lead="한 단계가 끝날 때마다 빌드해서 눈으로 확인한다. 힌트는 막혔을 때 위에서부터 하나씩만 본다.", pb=True)

ch8 = chapter(8, "흔한 함정", [
    table([30, 38, 32], ["증상", "원인", "확인 방법"], [
        ["콘솔에 `←[32m` 같은 글자가 그대로 보인다", "가상 터미널 처리가 켜지지 않았다. `Init`을 부르지 않았거나 "
                                          "`SetConsoleMode`가 실패했다", "두 함수의 반환값을 찍어 본다"],
        ["로그 파일이 비어 있거나 끝부분이 없다", "flush 전에 프로그램이 끝났다. `Shutdown()`이 불리지 않았다",
         "`Shutdown()`에 중단점을 걸어 본다"],
        ["로그 파일이 보이지 않는다", "상대 경로가 작업 디렉터리 기준이다", "프로젝트 속성 → 디버깅 → 작업 디렉터리"],
        ["파일에 `[32m`이 섞여 있다", "콘솔용 문자열을 파일에도 그대로 썼다", "파일을 메모장으로 연다"],
        ["형식 문자열이 상수가 아니라는 컴파일 오류", "변수에 담긴 문자열을 형식으로 넘겼다", "4.1절의 `std::vformat`"],
        ["`<format>`을 찾지 못한다", "`/std:c++20`에서 `<format>`이 들어온 것은 VS 2022 17.2부터로 알고 있다",
         "도움말 → Visual Studio 정보에서 버전 확인"],
        ["`APIENTRY` 매크로 재정의 경고 (C4005)", "`Logger.cpp`는 `pch.h`(glad) 뒤에 `Windows.h`를 넣는다"
                                         "(4행). `include/glad/glad.h:32`가 먼저 정의해 둔다", "빌드 출력 창. 경고가 "
                                                                                    "실제로 나는지 빌드해서 확인하지는 않았다"],
    ], compact=True),
], lead="증상에서 거꾸로 찾는 표다.")

ch9 = chapter(9, "완료 기준", [
    checklist([
        "실행하면 콘솔에 시각, 레벨, 카테고리, 메시지가 붙은 줄이 나오고 레벨마다 색이 다르다.",
        "같은 내용이 로그 파일에 색 코드 없이 남는다.",
        "최소 레벨을 `Warning`으로 바꾸면 `Trace`·`Debug`·`Info`가 콘솔과 파일 양쪽에서 사라진다.",
        "호출부 어디에도 파일 이름이나 줄 번호를 손으로 적은 곳이 없다.",
        "`Engine/` 안에서 `std::cout`이 검색되지 않는다. `need log`도 검색되지 않는다.",
        "6.2절의 일곱 가지에 대해 고른 것과 이유가 적혀 있다.",
        "커밋 하나로 묶였다.",
    ]),
    console(Raw(
        '<span class="dim">[14:02:07.101]</span> <span class="ok">[Info ]</span> [Core ] Logger initialized: ClaudGL.log\n'
        '<span class="dim">[14:02:07.318]</span> <span class="ok">[Info ]</span> [Core ] Engine initialized: 1600x1600\n'
        '<span class="dim">[14:02:07.320]</span> <span class="warn">[Warn ]</span> [Core ] Update callback is not set\n'
        '<span class="dim">[14:02:09.774]</span> <span class="warn">[Warn ]</span> [Input] Invalid key: -1'
    ), title="기대하는 출력 (형식과 문구는 예시)"),
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
         "실행 파일이 있는 폴더(`Client/Client.vcxproj:74`의 `OutDir`)를 작업 디렉터리로 준다. (5.3절)"),
        ("두 객체가 파괴되는 순서를 확인해야 한다.",
         "함수 안의 `static` 객체는 생성이 끝난 순서의 반대로 파괴된다. `GEngine::Get()`이 먼저 불리고"
         "(`Client/main.cpp:10`) `GLogger::Get()`이 그 뒤에 처음 불렸다면 Logger가 먼저 사라지고, `~GEngine()`은 "
         "이미 파괴된 객체에 로그를 쓰게 된다. 1-4강에서 종료 순서를 다룰 때 다시 나온다. (6.4절)"),
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
    ("flush", "flush", "버퍼에 모인 글자를 운영체제로 내보내는 일"),
    ("ANSI 이스케이프 시퀀스", "ANSI escape sequence", "ESC로 시작해 콘솔에 색·커서 이동을 지시하는 글자열"),
    ("가상 터미널 처리", "ENABLE_VIRTUAL_TERMINAL_PROCESSING", "Windows 콘솔이 이스케이프 시퀀스를 해석하게 하는 모드"),
    ("작업 디렉터리", "working directory", "상대 경로의 기준이 되는 폴더. 실행하는 방법에 따라 달라진다"),
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
