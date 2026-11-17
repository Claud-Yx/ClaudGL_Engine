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

private:
    GEngine() = default;

    // Which special member functions must be private or deleted? (chapter 7)
    GLFWwindow* _main_window{}; // what does this hold before Init() runs?
};
