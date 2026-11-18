#pragma once

#include <array>
#include "Enum/InputKeys.h"

class MInputManager
{
public:
    MInputManager()  = default;
    ~MInputManager() = default;

    static bool IsValidKey( EKey key ); // which values must never become an index? (6.2)

    // GLFW fixes this signature (chapter 3). Why static, and how does it find the arrays? (chapter 4)
    static void cbSetKey( GLFWwindow* window, int key, int scancode, int action, int mods );

    void Update(); // once per frame: where in the frame, and why there? (5.2)

    bool IsKeyPressed( EKey key ); // one row each of the table in chapter 5
    bool IsKeyHeld( EKey key );
    bool IsKeyReleased( EKey key );

private:
    static constexpr int kKeyRangeMax{ static_cast<int>(EKey::RangeMax) };

    std::array<bool, kKeyRangeMax> _cur_keys{};
    std::array<bool, kKeyRangeMax> _prev_keys{};
};
