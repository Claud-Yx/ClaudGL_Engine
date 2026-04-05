#include "pch.h"
#include "EngineCore.h"

#include "Manager/InputManager.h"

#include <iostream>

GEngine& GEngine::Get()
{
    static GEngine instance; // C++11 guarantees thread-safe initialization
    return instance;
}

MInputManager* GEngine::GetInputManager()
{
    return _input_manager.get();
}

GEngine::InitErrorCode GEngine::Init( GLint version_major, GLint version_minor, int width, int height, const char* title, GLFWmonitor* monitor, GLFWwindow* share )
{
    glfwInit();
    glfwWindowHint( GLFW_CONTEXT_VERSION_MAJOR, version_major );
    glfwWindowHint( GLFW_CONTEXT_VERSION_MINOR, version_minor );
    glfwWindowHint( GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE );

    // Create Window
    _main_window = glfwCreateWindow( width, height, title, monitor, share );
    glfwMakeContextCurrent( _main_window );

    if ( !gladLoadGLLoader( (GLADloadproc)glfwGetProcAddress ) )
    {
        return InitErrorCode::Fail;
    }

    glClearColor( 0.5f, 0.0f, 0.0f, 1.0f );
    glfwSetWindowUserPointer( _main_window, this );

    // init manager
    _input_manager = std::make_unique<MInputManager>();
    glfwSetKeyCallback( _main_window, MInputManager::cbSetKey );

    return InitErrorCode::Success;
}

void GEngine::Update( float delta_time )
{
    if ( !_on_update ) return;

    _on_update( delta_time );
}

void GEngine::SetUpdateCallback( std::function<void( float )> func )
{
    _on_update = func;
}

void GEngine::SetFramebufferSizeCallback( GLFWframebuffersizefun func )
{
    glfwSetFramebufferSizeCallback( _main_window, func );
}

void GEngine::Run()
{
    if ( !_on_update )
    {
        std::cout << "GEngine::Update() is null.\n";
    }

    while ( _is_running && !glfwWindowShouldClose( _main_window ) )
    {
        auto CurTime     = glfwGetTime();
        _delta_time      = CurTime - _last_frame_time;
        _last_frame_time = CurTime;

        glfwPollEvents();
        glClear( GL_COLOR_BUFFER_BIT );

        Update( static_cast<float>(_delta_time) );
        _input_manager->Update();

        glfwSwapBuffers( _main_window );
    }
}
