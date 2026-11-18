#pragma once

class MInputManager;

class GEngine
{
public:
    enum class InitErrorCode : int8_t
    {
        Success           = 0,
        GLFW_InitFailed   = 1,
        GLFW_WindowFailed = 2,
        GLAD_Failed       = 3
    };

    ~GEngine();
    GEngine( const GEngine& other )            = delete;
    GEngine& operator=( const GEngine& other ) = delete;
    GEngine( GEngine&& other )                 = delete;
    GEngine& operator=( GEngine&& other )      = delete;

    static GEngine& Get();
    GLFWwindow*     GetWindow() const; // why does main need this in lesson 1-1?

    // Manager getter
    MInputManager* GetInputManager();

    [[nodiscard]] InitErrorCode Init( GLint       version_major, GLint version_minor, int   width, int height,
                                      const char* title, GLFWmonitor*  monitor, GLFWwindow* share );

    void        SetCallback_Update( std::function<void( float )> func );
    void        SetCallback_FramebufferSize( GLFWframebuffersizefun func );
    static void SetCallback_SetError( GLFWerrorfun func );

    void Run();
    void Shutdown();
    void RequestQuit();

    double        GetDeltaTime() const;
    static double GetElapsedTime();

private:
    GEngine() = default;

    void                         Update( float delta_time );
    std::function<void( float )> _on_Update;

    // Which special member functions must be private or deleted? (chapter 7)
    GLFWwindow* _main_window{}; // what does this hold before Init() runs?

    // Manager
    std::unique_ptr<MInputManager> _input_manager{};

    bool   _is_running{ true };
    bool   _is_glfw_initialized{ false };
    double _last_frame_time{};
    double _delta_time{};
};
