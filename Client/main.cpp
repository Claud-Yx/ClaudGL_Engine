#include "pch.h"

#include <format>
#include <iostream>

#include "Core/EngineCore.h"
#include "Manager/InputManager.h"

void cbFramebufferSize( GLFWwindow* window, int width, int height );
void cbUpdate( float delta_time );
void cbSetError( int error_code, const char* description );

namespace
{
    float r{}, g{}, b{};
}

int main( void )
{
    GEngine& engine = GEngine::Get();
    GEngine::SetCallback_SetError( cbSetError );
    auto result = engine.Init( 4, 6, 1600, 1600, "Claud GL Engine", nullptr, nullptr );

    // What should main return when result is not Success?
    // Then: the temporary loop of chapter 6, using engine.GetMainWindow()
    switch ( result )
    {
    case GEngine::InitErrorCode::GLFW_InitFailed:
        std::cerr << std::format( "GLFW Init failed" ) << std::endl;
        return static_cast<int>(result);
    case GEngine::InitErrorCode::GLFW_WindowFailed:
        std::cerr << std::format( "Window creation failed" ) << std::endl;
        return static_cast<int>(result);
    case GEngine::InitErrorCode::GLAD_Failed:
        std::cerr << std::format( "GLAD failed" ) << std::endl;
        return static_cast<int>(result);
    }

    engine.SetCallback_FramebufferSize( cbFramebufferSize );
    engine.SetCallback_Update( cbUpdate );

    engine.Run();
    engine.Shutdown();

    return static_cast<int>(result);
}

void cbFramebufferSize( GLFWwindow* window, int width, int height )
{
    glViewport( 0, 0, width, height );
}

void cbUpdate( float delta_time )
{
    // Input
    auto input = GEngine::Get().GetInputManager();
    if ( not input ) return;

    if ( input->IsKeyPressed( EKey::Escape ) ) GEngine::Get().RequestQuit();
    if ( input->IsKeyPressed( EKey::A ) ) r = 1.f;
    if ( input->IsKeyReleased( EKey::A ) ) r = 0.f;
    if ( input->IsKeyPressed( EKey::S ) ) g = 1.f;
    if ( input->IsKeyReleased( EKey::S ) ) g = 0.f;
    if ( input->IsKeyPressed( EKey::D ) ) b = 1.f;
    if ( input->IsKeyReleased( EKey::D ) ) b = 0.f;
    if ( input->IsKeyHeld( EKey::J ) ) r = glm::clamp( r + delta_time * 0.25f, 0.f, 1.f );
    else r                               = glm::clamp( r - delta_time * 0.25f, 0.f, 1.f );
    if ( input->IsKeyHeld( EKey::K ) ) g = glm::clamp( g + delta_time * 0.25f, 0.f, 1.f );
    else g                               = glm::clamp( g - delta_time * 0.25f, 0.f, 1.f );
    if ( input->IsKeyHeld( EKey::L ) ) b = glm::clamp( b + delta_time * 0.25f, 0.f, 1.f );
    else b                               = glm::clamp( b - delta_time * 0.25f, 0.f, 1.f );

    glClearColor( r, g, b, 0.0f );
}

void cbSetError( int error_code, const char* description )
{
    std::cerr << std::format( "Error[{:}]: {}", error_code, description ) << std::endl;
}
