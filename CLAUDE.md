# ClaudGL Engine - Project Memory

## Important: Interaction Rules
- **DO NOT provide complete code solutions**
- **Act as a professor/mentor** - guide direction, not answers
- User writes ALL code themselves
- Provide hints, concepts, architecture direction only
- Only show code when explicitly requested

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
(highest N is current). If the lesson list changes, update curriculum.py first, then this section.

### Part 1: Core (API-agnostic)
- [ ] 1-1 Project setup and window (GLFW + GLAD + GLM, GEngine singleton)
- [ ] 1-2 Game Loop + Delta Time (Run, Update callback)
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

- [ ] 1-1 Project setup, window creation, GEngine singleton (retype from the handout)
- [ ] 1-2 Game Loop + Delta Time
- [ ] 1-3 Input System (the EKey list in `InputKeys.h` is kept, not retyped)
- [ ] 1-4 Init failure and shutdown handling
- [ ] 1-5 Logger
- [ ] **Next**: 1-1. Retype 1-1 to 1-3 as the handouts describe; no redesign before 1-4.

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
