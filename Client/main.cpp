#include "pch.h"
#include "Core/EngineCore.h"
#include "Manager/InputManager.h"

void cbFramebufferSize( GLFWwindow* window, int width, int height );
void cbUpdate( float delta_time );

int main( void )
{
    GEngine& engine    = GEngine::Get();
    auto     ErrorCode = engine.Init( 4, 6, 1600, 1600, "Claud GL Engine", nullptr, nullptr );

    if ( ErrorCode != GEngine::InitErrorCode::Success )
        return static_cast<int>(ErrorCode);

    engine.SetFramebufferSizeCallback( cbFramebufferSize );
    engine.SetUpdateCallback( cbUpdate );

    engine.Run();
}

void cbFramebufferSize( GLFWwindow* window, int width, int height )
{
    glViewport( 0, 0, width, height );
}

void cbUpdate( float delta_time )
{
    if ( GEngine::Get().GetInputManager()->IsKeyPressed( EKey::A ) )
    {
        glClearColor( 0.f, 1.f, 0.f, 1.f );
    }
    else if ( GEngine::Get().GetInputManager()->IsKeyPressed( EKey::S ) )
    {
        glClearColor( 0.f, 0.f, 1.f, 1.f );
    }
    else if ( GEngine::Get().GetInputManager()->IsKeyPressed( EKey::D ) )
    {
        glClearColor( 1.f, 0.f, 0.f, 1.f );
    }
}
