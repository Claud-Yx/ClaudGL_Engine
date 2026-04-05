#pragma once
#include <array>
#include "Enum/InputKeys.h"

class MInputManager
{
public:
    MInputManager()  = default;
    ~MInputManager() = default;

    static bool IsValidKey( EKey key );

    static void cbSetKey( GLFWwindow* window, int key, int scancode, int action, int mods );

    void Update();

    bool IsKeyPressed( EKey key );
    bool IsKeyHeld( EKey key );
    bool IsKeyReleased( EKey key );

private:
    static constexpr int kKeyRangeMax{ static_cast<int>(EKey::RangeMax) };

    std::array<bool, kKeyRangeMax> _current_keys;
    std::array<bool, kKeyRangeMax> _previous_keys;
};
