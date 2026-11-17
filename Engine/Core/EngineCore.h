#pragma once

class GEngine
{
public:
    enum class InitErrorCode : int8_t
    {
        Fail    = -1,
        Success = 0
    };

    ~GEngine();
    GEngine( const GEngine& other )            = delete;
    GEngine& operator=( const GEngine& other ) = delete;
    GEngine( GEngine&& other )                 = delete;
    GEngine& operator=( GEngine&& other )      = delete;

    static GEngine& Get();
    GLFWwindow*     GetWindow() const; // why does main need this in lesson 1-1?

    InitErrorCode Init( GLint       version_major, GLint version_minor, int   width, int height,
                        const char* title, GLFWmonitor*  monitor, GLFWwindow* share );

    void SetCallback_Update( std::function<void( float )> func );
    void SetCallback_FramebufferSize( GLFWframebuffersizefun func );
    void Run();

    double        GetDeltaTime() const;
    static double GetElapsedTime();

private:
    GEngine() = default;

    void                         Update( float delta_time );
    std::function<void( float )> _on_Update;

    // Which special member functions must be private or deleted? (chapter 7)
    GLFWwindow* _main_window{}; // what does this hold before Init() runs?

    bool   _is_running{ true };
    double _last_frame_time{};
    double _delta_time{};
};
