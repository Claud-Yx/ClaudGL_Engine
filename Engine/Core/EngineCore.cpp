#include "pch.h"
#include "EngineCore.h"

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
    
    return InitErrorCode::Success;
}
