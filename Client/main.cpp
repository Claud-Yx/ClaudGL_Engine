#include "pch.h"

#include "Core/EngineCore.h"

void cbFramebufferSize( GLFWwindow* window, int width, int height );
void cbUpdate( float delta_time );

int main( void )
{
    GEngine& engine = GEngine::Get();
    auto     result = engine.Init( 4, 6, 1600, 1600, "Claud GL Engine", nullptr, nullptr );

    // What should main return when result is not Success?
    // Then: the temporary loop of chapter 6, using engine.GetMainWindow()
    switch ( result )
    {
    case GEngine::InitErrorCode::Fail:
        return static_cast<int>(result);
    }

    engine.SetCallback_FramebufferSize( cbFramebufferSize );
    engine.SetCallback_Update( cbUpdate );
    engine.Run();

    return static_cast<int>(result);
}

void cbFramebufferSize( GLFWwindow* window, int width, int height )
{
    glViewport( 0, 0, width, height );
}

void cbUpdate( float delta_time )
{
    auto time = GEngine::GetElapsedTime();
    auto r = static_cast<float>((glm::sin( time ) + 1.0) * 0.5);
    auto g = static_cast<float>((glm::sin( time * 0.8 ) + 1.0) * 0.5);
    auto b = static_cast<float>((glm::sin( time * 0.5 ) + 1.0) * 0.5);
    
    glClearColor( r, g, b, 0.0f );
}
