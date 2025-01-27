#pragma once

//#include "framework.h"

class GEngine
{
public:
	enum class InitErrorCode : int8
	{
		Fail = -1,
		Success = 0
	};

private:
	static std::shared_ptr<GEngine> kInstance;

public:
	static GLFWwindow*  kMainWindow;

private:
	GEngine() = default;

public:
	static std::shared_ptr<GEngine> Generate();

	static void SetMainWindow( GLFWwindow* window );

public:
	InitErrorCode Init(GLint version_major, GLint version_minor);
	GLFWwindow* CreateWindow( GLint width, GLint height, const std::string_view& title, GLFWmonitor* monitor, GLFWwindow* share );

// Callback functions
public:
	GLFWframebuffersizefun cbSetFramebufferSize( GLFWwindow* window, GLFWframebuffersizefun fn );
};

