#include "pch.h"
#include "EngineCore.h"

std::shared_ptr<GEngine> engine;

void cbFramebufferSize( GLFWwindow* window, int width, int height );

int main( void )
{
	engine = GEngine::Generate();
	engine->SetMainWindow( engine->CreateWindow( 800, 600, "Hello OpenGL", nullptr, nullptr ) );
	
	engine->cbSetFramebufferSize( engine->kMainWindow, cbFramebufferSize );

	engine->kMainWindow
}

void cbFramebufferSize( GLFWwindow* window, int width, int height )
{

	glViewport( 0, 0, width, height);
}
