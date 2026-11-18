#include "pch.h"
#include "EngineCore.h"
#include "Manager/InputManager.h"

#include <utility>

GEngine::~GEngine()
{
    glfwDestroyWindow( _main_window );
    glfwTerminate();
}

GEngine& GEngine::Get()
{
    static GEngine engine{};
    return engine;
}

GLFWwindow* GEngine::GetWindow() const
{
    return _main_window;
}

MInputManager* GEngine::GetInputManager()
{
    return _input_manager.get();
}

GEngine::InitErrorCode GEngine::Init( GLint version_major, GLint version_minor, int width, int height, const char* title, GLFWmonitor* monitor, GLFWwindow* share )
{
    if ( glfwInit() == GLFW_FALSE ) return InitErrorCode::Fail;

    glfwWindowHint( GLFW_CONTEXT_VERSION_MAJOR, version_major );
    glfwWindowHint( GLFW_CONTEXT_VERSION_MINOR, version_minor );
    glfwWindowHint( GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE );

    _main_window = glfwCreateWindow( width, height, title, monitor, share );
    if ( not _main_window ) return InitErrorCode::Fail;

    glfwMakeContextCurrent( _main_window );
    if ( not gladLoadGLLoader( reinterpret_cast<GLADloadproc>(glfwGetProcAddress) ) )
        return InitErrorCode::Fail;

    // Set engine pointer into window user pointer
    glfwSetWindowUserPointer( _main_window, this );

    // Init managers
    _input_manager = std::make_unique<MInputManager>();
    glfwSetKeyCallback( _main_window, MInputManager::cbSetKey );


    return InitErrorCode::Success;
}

void GEngine::SetCallback_Update( std::function<void( float )> func )
{
    _on_Update = std::move( func );
}

void GEngine::SetCallback_FramebufferSize( GLFWframebuffersizefun func )
{
    glfwSetFramebufferSizeCallback( _main_window, func );
}

void GEngine::Run()
{
    while ( _is_running and not glfwWindowShouldClose( _main_window ) )
    {
        // Get delta time
        auto cur_time    = glfwGetTime();
        _delta_time      = cur_time - _last_frame_time;
        _last_frame_time = cur_time;

        // Polling events
        glfwPollEvents();

        // Clear frame buffer
        glClear( GL_COLOR_BUFFER_BIT );

        // Update client
        Update( static_cast<float>(_delta_time) );

        // Input manager update
        if ( _input_manager ) _input_manager->Update();

        glfwSwapBuffers( _main_window );
    }
}

void GEngine::Stop()
{
    _is_running = false;
}

double GEngine::GetDeltaTime() const
{
    return _delta_time;
}

double GEngine::GetElapsedTime()
{
    return glfwGetTime();
}

void GEngine::Update( float delta_time )
{
    // Client update
    if ( _on_Update ) _on_Update( delta_time );
}
