#include "pch.h"

#include "Core/EngineCore.h"

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

    double Time{};
    while ( not glfwWindowShouldClose( engine.GetWindow() ) )
    {
        Time   = glfwGetTime();
        auto r = static_cast<float>((glm::sin( Time ) + 1.0) * 0.5);
        auto g = static_cast<float>((glm::sin( Time * 0.8 ) + 1.0) * 0.5);
        auto b = static_cast<float>((glm::sin( Time * 0.5 ) + 1.0) * 0.5);
        glfwPollEvents();
        glClearColor( r, g, b, 0.0f );
        glClear( GL_COLOR_BUFFER_BIT );
        glfwSwapBuffers( engine.GetWindow() );
    }

    return static_cast<int>(result);
}
