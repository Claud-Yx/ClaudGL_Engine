#include "pch.h"
#include "EngineCore.h"

std::shared_ptr<GEngine> GEngine::Generate()
{
	if ( !kInstance )
	{
		kInstance.reset( new GEngine() );
	}

	return kInstance;
}

void GEngine::SetMainWindow( GLFWwindow* window )
{
	kMainWindow = window;
}

GEngine::InitErrorCode GEngine::Init( GLint version_major, GLint version_minor )
{
	glfwInit();
	glfwWindowHint( GLFW_CONTEXT_VERSION_MAJOR, version_major );
	glfwWindowHint( GLFW_CONTEXT_VERSION_MAJOR, version_minor );
	glfwWindowHint( GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE );

	if ( !gladLoadGLLoader( (GLADloadproc)glfwGetProcAddress ) )
	{
		return InitErrorCode::Fail;
	}
	
	return InitErrorCode::Success;
}

GLFWwindow* GEngine::CreateWindow( GLint width, GLint height, const std::string_view& title, GLFWmonitor* monitor, GLFWwindow* share )
{
	return glfwCreateWindow( width, height, title.data(), monitor, share );
}

GLFWframebuffersizefun GEngine::cbSetFramebufferSize( GLFWwindow* window, GLFWframebuffersizefun fn )
{
	return  glfwSetFramebufferSizeCallback( window, fn );
}
