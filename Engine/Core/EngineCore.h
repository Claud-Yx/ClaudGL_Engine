#pragma once

class GEngine
{
public:
    enum class InitErrorCode : int8_t
    {
        Fail    = -1,
        Success = 0
    };

private:
    GEngine()                            = default;
    ~GEngine()                           = default;
    GEngine( const GEngine& )            = delete;
    GEngine& operator=( const GEngine& ) = delete;

    // Method

    void Update( float delta_time );

    // Callback

    std::function<void( float )> _on_update;

    // Manager

    std::unique_ptr<class MInputManager> _input_manager;

    // Property

    GLFWwindow* _main_window = nullptr;
    bool        _is_running  = true;

    double _last_frame_time{};
    double _delta_time{};

public:
    static GEngine& Get();

    // Accessor 

    GLFWwindow*    GetMainWindow() const { return _main_window; }
    MInputManager* GetInputManager();

    // Method 

    InitErrorCode Init( GLint version_major, GLint version_minor, int width, int height, const char* title, GLFWmonitor* monitor, GLFWwindow* share );

    // Callback
    void SetUpdateCallback( std::function<void( float )> func );
    void SetFramebufferSizeCallback( GLFWframebuffersizefun func );

    void Run();
};
