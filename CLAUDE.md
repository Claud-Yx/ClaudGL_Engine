# ClaudGL Engine - Project Memory

## Important: Interaction Rules
- **DO NOT provide complete code solutions**
- **Act as a professor/mentor** - guide direction, not answers
- User writes ALL code themselves
- Provide hints, concepts, architecture direction only
- Only show code when explicitly requested

## Project Goal
Build a cross-API game engine starting with OpenGL, then DirectX 11, DirectX 12, and Vulkan.
Focus on proper architecture with abstraction layers so only the renderer backend needs to change.

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
- [x] 1-1 Project setup and window (GLFW + GLAD + GLM, GEngine singleton)
- [x] 1-2 Game Loop + Delta Time (Run, Update callback)
- [x] 1-3 Input System (MInputManager, EKey enum, GLFW callback pattern)
- [ ] 1-4 Init failure and shutdown handling
- [ ] 1-5 Logger (Debug logging)
- [ ] 1-6 Assert and error handling policy
- [ ] 1-7 Files and paths
- [ ] 1-8 Resource Manager (File loading + caching)

### Part 2: Raw OpenGL (written directly, no abstraction yet)
- [ ] 2-1 OpenGL as a state machine (context, bind model, debug callback)
- [ ] 2-2 First triangle (VBO, VAO, shader compile/link)
- [ ] 2-3 Index buffer and quad
- [ ] 2-4 Shaders (GLSL, uniforms, loading from file)
- [ ] 2-5 Textures
- [ ] 2-6 Transforms and coordinate spaces (MVP, depth test)

### Part 3: Renderer Abstraction
- [ ] 3-1 Abstraction design (no code)
- [ ] 3-2 Window / RenderDevice split
- [ ] 3-3 Buffer and VertexLayout
- [ ] 3-4 Shader and Texture interfaces
- [ ] 3-5 OpenGL backend wrap-up and validation (no `gl*` outside the backend)
- [ ] 3-6 Render state

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
- [ ] 5-4 Retrospective and DX11 prep

### Part 6-8: DX11, DX12, Vulkan
- Overview only. Detailed lessons are planned after 5-4.

## Current Status
- [x] 1-1 Project setup, window creation, GEngine singleton (basic structure)
- [x] 1-2 Game Loop + Delta Time (Run, Update callback, static_cast float)
- [x] 1-3 Input System (MInputManager, EKey, GLFW callback, IsKeyPressed/Held/Released)
- [ ] 1-4 Init failure and shutdown handling (not started)
- [ ] 1-5 Logger (in progress: skeleton exists, `Log()` body is empty)
- [ ] **Next**: 1-4, then finish 1-5 Logger

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
