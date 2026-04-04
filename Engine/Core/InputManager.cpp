#include "pch.h"
#include "InputManager.h"

#include "EngineCore.h"

bool MInputManager::IsValidKey( EKey key )
{
    int code = static_cast<int>(key);
    return code >= 0 && code < kKeyRangeMax;
}

void MInputManager::cbSetKey( GLFWwindow* window, int key, int scancode, int action, int mods )
{
    if ( key == GLFW_KEY_UNKNOWN ) return;

    auto engine  = static_cast<GEngine*>(glfwGetWindowUserPointer( window ));

    if ( action == GLFW_PRESS )
    {
        engine->GetInputManager()->_current_keys[key] = true;
    }
    else if ( action == GLFW_RELEASE )
    {
        engine->GetInputManager()->_current_keys[key] = false;
    }
}

void MInputManager::Update()
{
    _previous_keys = _current_keys;
}

bool MInputManager::IsKeyPressed( EKey key )
{
    if ( !IsValidKey( key ) ) return false; // need log
    int code = static_cast<int>(key);
    return _current_keys[code] && !_previous_keys[code];
}

bool MInputManager::IsKeyHeld( EKey key )
{
    if ( !IsValidKey( key ) ) return false; // need log
    int code = static_cast<int>(key);
    return _current_keys[code] && _previous_keys[code];
}

bool MInputManager::IsKeyReleased( EKey key )
{
    if ( !IsValidKey( key ) ) return false; // need log
    int code = static_cast<int>(key);
    return !_current_keys[code] && _previous_keys[code];
}
