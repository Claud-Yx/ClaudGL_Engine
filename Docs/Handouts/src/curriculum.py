"""Single source of truth for the ClaudGL Engine curriculum.

plan.py renders this into the plan PDF; lesson files read their own row from
here (id, title, part, file name, version).

Numbering: a lesson id is "<part>-<order in part>" (1-1, 1-2, ... 5-4). The id
is assigned from the order of LESSONS, so inserting a lesson renumbers the ones
after it in the same part -- check prose references ("1-4강") when that happens.

Versions: every PDF name ends in _v<N>. Rebuilding while a version is still
being worked on overwrites the same file. Once a PDF has been handed to Claud,
any later change bumps the number (PLAN_VERSION here, `ver` on the lesson), so
the old file stays and the new one sits beside it.

Lesson fields:
    id       "1-4" (assigned below)
    part     part number (1-5)
    k        order inside the part (assigned below)
    title    lesson title
    concepts key concepts (inline markup allowed)
    result   visible result when the lesson is done
    hours    estimate: reading + implementing + debugging
    slug     English topic for the PDF file name; None until a handout exists
    ver      handout version; 0 until a handout exists
    opt      True for optional lessons
"""
from __future__ import annotations

PROJECT = "ClaudGL Engine"

PLAN_VERSION = 4
PLAN_DATE = "2026-11-14"

PARTS = {
    1: ("Core", "엔진의 뼈대"),
    2: ("날것의 OpenGL", "추상화 전에 직접 써 보기"),
    3: ("Renderer 추상화", "GL을 한 곳에 가두기"),
    4: ("Scene", "장면을 이루는 것들"),
    5: ("Advanced", "프레임버퍼·그림자·도구"),
}

# Later APIs: overview only in the plan, no lessons yet.
LATER_PARTS = {6: "DX11", 7: "DX12", 8: "Vulkan"}


def L(part, title, concepts, result, hours, slug=None, ver=0, opt=False):
    return dict(part=part, title=title, concepts=concepts, result=result, hours=hours,
                slug=slug, ver=ver, opt=opt)


LESSONS = [
    # ---- Part 1: Core ----
    L(1, "프로젝트 구성과 창",
      "정적 라이브러리와 실행 파일, GLFW·GLAD·GLM, pch, GL 컨텍스트, 싱글턴",
      "빈 창이 뜬다",
      3, slug="ProjectAndWindow", ver=2),
    L(1, "Game Loop와 Delta Time",
      "루프 한 바퀴의 순서, 델타 타임, Update 콜백, 더블 버퍼링",
      "창을 닫을 때까지 매 프레임 `Update(dt)`가 불린다",
      2, slug="GameLoop", ver=2),
    L(1, "Input System",
      "`EKey`, 이벤트를 상태로 바꾸기, 키 콜백과 user pointer, Pressed·Held·Released",
      "키를 누르면 배경색이 바뀐다",
      3, slug="Input", ver=2),
    L(1, "초기화 실패와 종료 처리",
      "초기화 실패 처리, 종료 경로, 값 초기화, 자원의 주인",
      "`Init`이 실패하면 원인이 보고되고, 창을 닫으면 GLFW 자원이 해제된다",
      3),
    L(1, "Logger",
      "로그 레벨과 카테고리, 매크로와 `std::source_location`, `std::format`, 콘솔 색, 파일 출력",
      "콘솔과 파일에 레벨별 로그가 찍히고 `std::cout` 직접 호출이 사라진다",
      4),
    L(1, "Assert와 오류 처리 정책",
      "assert 매크로, `__debugbreak`, 오류 코드와 예외 중 하나를 고르는 기준",
      "조건이 깨지면 파일·줄 번호와 함께 그 자리에서 멈춘다",
      3),
    L(1, "파일과 경로",
      "작업 디렉터리, `std::filesystem`, 텍스트·바이너리 읽기",
      "어디서 실행하든 `Assets/` 아래 파일을 찾아 읽는다",
      3),
    L(1, "Resource Manager",
      "핸들과 포인터, 캐시(`unordered_map`), 수명(`shared_ptr`·`weak_ptr`)",
      "같은 경로를 두 번 요청해도 파일은 한 번만 읽는다",
      5),

    # ---- Part 2: raw OpenGL ----
    L(2, "OpenGL이라는 상태 기계",
      "컨텍스트, 객체·핸들·바인드 모델, 디버그 콜백",
      "GL이 내는 오류와 경고가 Logger로 들어온다",
      3),
    L(2, "첫 삼각형",
      "VBO·VAO, 정점 속성, 셰이더 컴파일과 링크, 드로우 콜",
      "화면에 삼각형 하나",
      5),
    L(2, "인덱스 버퍼와 사각형",
      "EBO, 와인딩과 컬링, DSA(OpenGL 4.5)",
      "정점 4개와 인덱스 6개로 사각형",
      3),
    L(2, "셰이더 다루기",
      "GLSL 기초, uniform, 셰이더 파일 로드, 컴파일 오류 로그",
      "파일에서 읽은 셰이더로 색이 시간에 따라 변한다",
      4),
    L(2, "텍스처",
      "이미지 로딩, 필터·밉맵·래핑, UV, 텍스처 유닛",
      "사각형에 이미지가 입혀진다",
      4),
    L(2, "변환과 좌표 공간",
      "MVP 행렬, GLM, 깊이 테스트, 클립 공간 규약",
      "회전하는 큐브",
      5),

    # ---- Part 3: renderer abstraction ----
    L(3, "추상화 설계",
      "Part 2에서 쓴 GL 호출 목록, 감출 것과 드러낼 것, 가상 함수와 컴파일 타임 선택, 핸들",
      "인터페이스 초안 문서 (코드 없음)",
      4),
    L(3, "Window와 RenderDevice 분리",
      "`GEngine`에서 GLFW·GL 떼어 내기, 프레임 시작과 끝, 공개 헤더 정리",
      "Engine 공개 헤더에서 GL·GLFW 타입이 사라진다",
      5),
    L(3, "Buffer와 VertexLayout",
      "버퍼 서술자, 정점 레이아웃 서술, 자원 수명",
      "인터페이스로 만든 버퍼로 삼각형을 그린다",
      5),
    L(3, "Shader와 Texture",
      "셰이더·텍스처 인터페이스, Resource Manager와 연결",
      "텍스처 입힌 사각형이 인터페이스만으로 그려진다",
      5),
    L(3, "OpenGL 백엔드 마무리와 검증",
      "백엔드 폴더 격리, 생성 지점 한 곳, 검색으로 하는 검증",
      "Client와 공개 헤더에 `gl*` 호출이 0개",
      4),
    L(3, "렌더 상태",
      "깊이·블렌드·컬 상태를 값으로 다루기, 파이프라인 상태 묶음",
      "전역 상태를 건드리지 않고 상태를 넘겨서 그린다",
      4),

    # ---- Part 4: scene ----
    L(4, "Transform과 계층",
      "TRS, 쿼터니언, 부모·자식, dirty flag",
      "부모를 돌리면 자식이 따라 돈다",
      5),
    L(4, "Camera",
      "view·projection 행렬, 자유 시점 카메라, 마우스 입력",
      "키보드와 마우스로 장면을 돌아다닌다",
      4),
    L(4, "Mesh",
      "정점 포맷, 기본 도형 생성, OBJ 로딩",
      "파일에서 읽은 모델이 화면에 보인다",
      5),
    L(4, "Material",
      "셰이더·파라미터·텍스처 묶음, uniform 위치 캐시, UBO",
      "같은 메시를 서로 다른 머티리얼로 그린다",
      5),
    L(4, "Lighting",
      "Phong과 Blinn-Phong, 노멀 변환, 광원 종류, 감마",
      "조명이 들어간 장면",
      6),
    L(4, "Renderer 정리",
      "제출·정렬·드로우 분리, 렌더 큐",
      "씬은 그릴 것을 제출만 하고 Renderer가 그린다",
      4),

    # ---- Part 5: advanced ----
    L(5, "Framebuffer와 후처리",
      "오프스크린 렌더링, 렌더 타깃, 풀스크린 패스",
      "화면 전체에 후처리 효과가 걸린다",
      5),
    L(5, "Shadow Mapping",
      "광원 시점 깊이 패스, 깊이 비교, 바이어스, PCF",
      "그림자가 드리운 장면",
      6),
    L(5, "ImGui 통합",
      "immediate mode UI, 백엔드 연결, 디버그 패널",
      "실행 중에 값을 바꾸는 패널",
      4, opt=True),
    L(5, "회고와 DX11 준비",
      "GL에 묶인 곳 점검, 인터페이스 수정 목록",
      "DX11 포팅 전 점검표",
      3),
]

# Assign ids from the list order: "<part>-<order in part>".
_count: dict[int, int] = {}
for _x in LESSONS:
    _count[_x["part"]] = _count.get(_x["part"], 0) + 1
    _x["k"] = _count[_x["part"]]
    _x["id"] = f"{_x['part']}-{_x['k']}"

# Handouts 1-1 to 1-3 were written after the code: they quote the repository
# as it was at this commit, read on this day.
CODE_COMMIT = "7aa55c4"
CODE_READ_DATE = "2026-11-14"


def lesson(lesson_id: str) -> dict:
    return next(x for x in LESSONS if x["id"] == lesson_id)


def lessons_of(part: int) -> list[dict]:
    return [x for x in LESSONS if x["part"] == part]


def hours_of(part: int) -> int:
    return sum(x["hours"] for x in lessons_of(part))


def total_hours() -> int:
    return sum(x["hours"] for x in LESSONS)


def handout_name(lesson_id: str) -> str:
    """PDF file name of a lesson handout, e.g. ClaudGL_1-5_Logger_v1.pdf."""
    x = lesson(lesson_id)
    if not x["slug"] or not x["ver"]:
        raise ValueError(f"lesson {lesson_id} has no slug/ver yet: set them in curriculum.py")
    return f"ClaudGL_{x['id']}_{x['slug']}_v{x['ver']}.pdf"


def plan_name() -> str:
    return f"ClaudGL_00_Plan_v{PLAN_VERSION}.pdf"
