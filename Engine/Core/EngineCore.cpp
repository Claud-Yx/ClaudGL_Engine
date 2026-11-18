#include "pch.h"
#include "EngineCore.h"
#include "Manager/InputManager.h"

#include <utility>

GEngine::~GEngine()
{
    Shutdown();
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
    if ( glfwInit() == GLFW_FALSE ) return InitErrorCode::GLFW_InitFailed;
    _is_glfw_initialized = true;

    glfwWindowHint( GLFW_CONTEXT_VERSION_MAJOR, version_major );
    glfwWindowHint( GLFW_CONTEXT_VERSION_MINOR, version_minor );
    glfwWindowHint( GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE );

    _main_window = glfwCreateWindow( width, height, title, monitor, share );
    if ( not _main_window )
    {
        // Undo what Init() has done so far: GLFW is up, the window is not
        Shutdown();
        return InitErrorCode::GLFW_WindowFailed;
    }

    glfwMakeContextCurrent( _main_window );
    if ( not gladLoadGLLoader( reinterpret_cast<GLADloadproc>(glfwGetProcAddress) ) )
    {
        // Undo what Init() has done so far: GLFW and the window are both up
        Shutdown();
        return InitErrorCode::GLAD_Failed;
    }

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

void GEngine::SetCallback_SetError( GLFWerrorfun func )
{
    glfwSetErrorCallback( func );
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

void GEngine::Shutdown()
{
    _input_manager.reset();

    if ( _main_window ) glfwDestroyWindow( _main_window );
    _main_window = nullptr;

    if ( _is_glfw_initialized )
    {
        glfwTerminate();
        _is_glfw_initialized = false;
    }
}

void GEngine::RequestQuit()
{
    if ( _is_running )
    {
        _is_running = false;
    }
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
