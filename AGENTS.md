# ClaudGL Engine - Project Memory

## Important: Interaction Rules
- **DO NOT provide complete code solutions**
- **Act as a professor/mentor** - guide direction, not answers
- User writes ALL code themselves
- Provide hints, concepts, architecture direction only
- Only show code when explicitly requested

## Working Agreements (decided 2026-11-17)
Assistant memory is stored per PC and is not shared between the home and office PCs, so agreements that
must hold on both are written here.
- **Hints only**: when Claud says "힌트만", find the real cause first (read files, check evidence), then
  give labelled hints from weak to strong and offer a way to ask for the answer. When Claud names the
  cause, confirm it with the evidence and then explain fully.
- **Commits**: commit straight to `main`, no feature branch. The code of one lesson is one commit with an
  annotated tag `lesson-<part>-<order>` (for example `lesson-1-2`); docs changes are separate `Docs:`
  commits; messages are Korean in the `Type: 설명` style. Push only when asked.
- **C++ level**: C++20 features are welcome in the engine code when the current lesson has a natural use
  for one (`std::numbers`, designated initializers, `std::format`, `std::source_location`, `using enum`,
  `std::span`, concepts). Suggest at most one per lesson. No modules, coroutines or a switch to
  `/std:c++latest` unless Claud brings it up.
- **Handouts are not personalized**: they must stay usable by anyone. No analogies or examples drawn from
  Claud's personal background, and Claud's own deviations (renames, extra experiments, skipped missions)
  are recorded in this file, not in the handouts. Such analogies are for chat only, when Claud asks
  directly. Fixes that help any reader (wrong line numbers, a missing pitfall row, an unclear sentence)
  are still made. The lesson-builder skill has the details.
- **When a change seems to have no effect**, or Engine breakpoints do not bind: compare the timestamps of
  `lib/Debug/x64/ClaudGL.lib` and `Debug/x64/Client.exe` with the source before reading code. Rider's
  incremental build can skip a project.
- **Codex mirrors**: `AGENTS.md` is an exact copy of this file. `.agents/skills/claudgl-lesson-builder/SKILL.md`
  is a copy of `.claude/skills/claudgl-lesson-builder/SKILL.md` with `CLAUDE.md` written as `AGENTS.md`
  and "Claude Docs" written as "Codex Docs". When an original changes, update its mirror in the same commit.
- **Pending handout fix**: chapter 10 of the 1-1 handout lists the stale `ClaudGL.lib` only under
  `LNK2019`. At the next 1-1 revision, add it under "crashes at the first `gl*` call although the loader
  line is there", together with the project-reference fix.

## Project Goal
Build one small game engine on OpenGL, start to finish: a lit, shadowed, post-processed scene you can
fly through, with every `gl*` call kept inside the renderer layer.
Other graphics APIs (DirectX 11, DirectX 12, Vulkan) are separate follow-up courses. A cross-API
interface is built only after each API has been used on its own, so do not add a backend-swapping
interface (virtual renderer interfaces, backend selection) in this course.

## Tech Stack
- **Language**: C++20
- **Build**: Visual Studio 2022 (MSVC v143)
- **Libraries**: GLFW, GLAD, GLM
- **Math**: GLM (API-agnostic, use #define for DX/Vulkan differences)

## Architecture Plan

Lesson numbers are `Part-order` (1-5 = fifth lesson of Part 1). The single source is
`Docs/Handouts/src/curriculum.py`; the full plan is `Docs/Handouts/ClaudGL_00_Plan_v<N>.pdf`
(the one in `Docs/Handouts/` is current; older ones are in `Legacy/`). If the lesson list changes, update curriculum.py first, then this section.

### Part 1: Core (API-agnostic)
- [x] 1-1 Project setup and window (GLFW + GLAD + GLM, GEngine singleton)
- [x] 1-2 Game Loop + Delta Time (Run, Update callback)
- [ ] 1-3 Input System (MInputManager, EKey enum, GLFW callback pattern)
- [ ] 1-4 Init failure and shutdown handling
- [ ] 1-5 Logger (Debug logging)
- [ ] 1-6 Assert and error handling policy
- [ ] 1-7 Files and paths

### Part 2: Raw OpenGL (written directly, not wrapped yet)
- [ ] 2-1 OpenGL as a state machine (context, bind model, debug callback)
- [ ] 2-2 First triangle (VBO, VAO, shader compile/link)
- [ ] 2-3 Index buffer and quad
- [ ] 2-4 Shaders (GLSL, uniforms, loading from file)
- [ ] 2-5 Textures
- [ ] 2-6 Transforms and coordinate spaces (MVP, depth test)

### Part 3: Renderer Layer (concrete GL wrapper classes, no backend interface)
- [ ] 3-1 Renderer design (no code)
- [ ] 3-2 Window / RenderDevice split
- [ ] 3-3 Buffer and VertexLayout
- [ ] 3-4 Shader and Texture classes
- [ ] 3-5 Resource Manager (file loading + caching, wired to Shader/Texture)
- [ ] 3-6 Renderer wrap-up and validation (no `gl*` outside the renderer)
- [ ] 3-7 Render state

### Part 4: Scene
- [ ] 4-1 Transform / Hierarchy
- [ ] 4-2 Camera
- [ ] 4-3 Mesh
- [ ] 4-4 Material
- [ ] 4-5 Lighting (Phong/Blinn-Phong)
- [ ] 4-6 Renderer cleanup (submit / sort / draw)

### Part 5: Advanced
- [ ] 5-1 Framebuffer / Post-processing
- [ ] 5-2 Shadow mapping
- [ ] 5-3 (Optional) ImGui integration
- [ ] 5-4 Retrospective

### After this course (separate courses, not Parts)
- This course ends at 5-4. Each follow-up is planned when it starts; the plan lists them in chapter 9.
- Intended order: Animation, Sound, Physics (order among these three not decided), then DX11, DX12,
  Vulkan (each written raw first, with its own renderer), and last a unified engine with a cross-API interface.

## Current Status
Restarted on 2026-11-16 from a libraries-only baseline: project settings, `include/`, pch files and
`Engine/Enum/InputKeys.h` are kept; `Client/main.cpp` is an empty `main`. The first pass (1-1 to 1-3
plus a Logger skeleton, written 2026-04) is kept at tag `first-pass-2026-04` as an answer key:
`git diff first-pass-2026-04 -- <file>`.

Handouts for 1-1 to 1-6 were all rewritten on 2026-11-16 in one format: from scratch with missions,
function reference cards, worked examples and figures, and no quotes of the first-pass code.
`Docs/Handouts/` holds only the newest version of each PDF; older versions are in `Docs/Handouts/Legacy/`.

- [x] 1-1 Project setup, window creation, GEngine singleton (handout v4; code at tag `lesson-1-1`,
  2026-11-17. Mission 7 "break it on purpose" and the first-pass comparison were not done)
- [x] 1-2 Game Loop + Delta Time (handout v5; code at tag `lesson-1-2`, 2026-11-17. The 2-second
  color cycle was skipped on purpose: `cbUpdate` takes absolute time from `GEngine::GetElapsedTime()`
  instead of accumulating dt)
- [ ] 1-3 Input System (handout v5; the EKey list in `InputKeys.h` is kept, not retyped)
- [ ] 1-4 Init failure and shutdown handling (handout v3)
- [ ] 1-5 Logger (handout v3; the logger is built from nothing, no skeleton is left in the repo)
- [ ] 1-6 Assert and error policy (handout v3)
- [ ] **Next**: 1-3 with handout v5. Write the bodies yourself. Variable and function names may differ
  from the handouts and the first pass on purpose (renaming is a way to avoid just typing out the
  handout), so do not flag such differences; map the names when reading a later handout. So far:
  `GetMainWindow()` is `GetWindow()`, `SetUpdateCallback` is `SetCallback_Update`,
  `SetFramebufferSizeCallback` is `SetCallback_FramebufferSize`, `_on_update` is `_on_Update`. The code
  also has `GetDeltaTime()` and a static `GetElapsedTime()` that the handouts do not have. The old
  code-reading handouts in `Legacy/` (1-1 v2, 1-2 v2, 1-3 v3) are the commentary to read after each
  lesson's missions.
- Deferred on purpose: drawing while the window is being resized. The loop stalls inside
  `glfwPollEvents()` during a resize drag; the fix is a window refresh callback plus a separate
  "one frame" function. No handout covers it. Revisit at 3-2, when window code is split from `GEngine`.
- `Client/Client.vcxproj` references the Engine project, so building Client rebuilds `ClaudGL.lib`
  first. Before that reference existed, running Client linked a stale library.

## Notes
- GLM works with all APIs (OpenGL, DX, Vulkan) - just change #defines
- Vulkan: GLM_FORCE_DEPTH_ZERO_TO_ONE
- DirectX: GLM_FORCE_LEFT_HANDED, GLM_FORCE_DEPTH_ZERO_TO_ONE
- glfwGetTime() returns double, cast to float for game logic (GPU is float-optimized)

## Project Structure
```
ClaudGL_Engine/
├── Engine/          # Static library (.lib)
│   ├── Core/
│   │   ├── EngineCore.h/cpp
│   │   ├── InputManager.h/cpp
│   │   └── Keys.h
│   └── pch.h/cpp (framework.h)
├── Client/          # Executable (.exe)
│   └── main.cpp
├── include/         # External headers (GLAD, GLFW, GLM)
└── lib/             # External libraries
```
