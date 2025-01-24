#include "glad/glad.h"
#include "GLFW/glfw3.h"
#include <iostream>

#pragma comment(lib, "glfw3.lib")

const unsigned int WIN_W = 300;
const unsigned int WIN_H = 300;

int main( void )
{
	glfwInit();
	glfwWindowHint( GLFW_CONTEXT_VERSION_MAJOR, 4 );
	glfwWindowHint( GLFW_CONTEXT_VERSION_MINOR, 6 );
	glfwWindowHint( GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE );

	if ( !gladLoadGLLoader( (GLADloadproc)glfwGetProcAddress ) )
	{
		std::cout << "Failed to initialize GLAD" << std::endl;
		return -1;
	}

	GLFWwindow* window = glfwCreateWindow( WIN_W, WIN_H, "Hello GLFW", NULL, NULL );

	glfwSetWindowPos( window, 100, 100 );
	glfwMakeContextCurrent( window );
	
	while ( !glfwWindowShouldClose( window ) )
	{
		glfwSwapBuffers( window );
		glfwPollEvents();
	}

	glfwTerminate();

	return 0;
}