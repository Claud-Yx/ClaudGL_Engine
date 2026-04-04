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

### Phase 1: Core (API-agnostic)
- [x] 1.1 Game Loop + Time (Application class, Delta Time)
- [x] 1.2 Input System (MInputManager, EKey enum, GLFW callback pattern)
- [ ] 1.3 Logger (Debug logging)
- [ ] 1.4 Resource Manager (File loading + caching)

### Phase 2: Renderer Abstraction
- [ ] 2.1 RenderDevice interface
- [ ] 2.2 Buffer, Shader, Texture interfaces
- [ ] 2.3 OpenGL backend implementation
- [ ] 2.4 Basic triangle rendering (validation)

### Phase 3: Scene
- [ ] 3.1 Transform / Hierarchy
- [ ] 3.2 Camera system
- [ ] 3.3 Mesh + Material
- [ ] 3.4 Lighting (Phong/Blinn-Phong)

### Phase 4: Advanced
- [ ] 4.1 Framebuffer / Post-processing
- [ ] 4.2 Shadow mapping
- [ ] 4.3 (Optional) ImGui editor integration

## Current Status
- [x] Project setup (GLFW + GLAD + GLM)
- [x] Window creation
- [x] GEngine singleton (basic structure)
- [x] Game Loop + Delta Time (Run, Update callback, static_cast float)
- [x] Input System (MInputManager, EKey, GLFW callback, IsKeyPressed/Held/Released)
- [ ] **Next**: Phase 1.3 - Logger

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
