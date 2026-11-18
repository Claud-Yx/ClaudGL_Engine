#include "pch.h"
#include "InputManager.h"

#include "Core/EngineCore.h"

bool MInputManager::IsValidKey( EKey key )
{
    int index = static_cast<int>(key);
    return index > static_cast<int>(EKey::Unknown) && index < static_cast<int>(EKey::RangeMax);
}

void MInputManager::cbSetKey( GLFWwindow* window, int key, int scancode, int action, int mods )
{
    if ( not IsValidKey( static_cast<EKey>(key) ) ) return;

    auto engine = static_cast<GEngine*>(glfwGetWindowUserPointer( window ));
    if ( not engine ) return;

    auto input = engine->GetInputManager();
    if ( not input ) return;

    auto& cur_keys = input->_cur_keys;

    switch ( action )
    {
    case GLFW_PRESS:
    case GLFW_REPEAT:
        cur_keys[key] = true;
        break;
    case GLFW_RELEASE:
        cur_keys[key] = false;
        break;
    default:
        break;
    }
}

void MInputManager::Update()
{
    _prev_keys = _cur_keys;
}

bool MInputManager::IsKeyPressed( EKey key )
{
    if ( not IsValidKey( key ) ) return false;
    int index = static_cast<int>(key);
    return (_cur_keys[index] == true && _prev_keys[index] == false);
}

bool MInputManager::IsKeyHeld( EKey key )
{
    if ( not IsValidKey( key ) ) return false;
    int index = static_cast<int>(key);
    return (_cur_keys[index] == true && _prev_keys[index] == true);
}

bool MInputManager::IsKeyReleased( EKey key )
{
    if ( not IsValidKey( key ) ) return false;
    int index = static_cast<int>(key);
    return (_cur_keys[index] == false && _prev_keys[index] == true);
}
