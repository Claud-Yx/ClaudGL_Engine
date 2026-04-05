#include "pch.h"
#include "Logger.h"

#include <Windows.h>

GLogger& GLogger::Get()
{
    static GLogger instance; // C++11 guarantees thread-safe initialization
    return instance;
}

void GLogger::Init( const char* file_name )
{
    _log_file.open( file_name );
    HANDLE handle = GetStdHandle( STD_OUTPUT_HANDLE );
    DWORD  mode   = 0;
    GetConsoleMode( handle, &mode );
    SetConsoleMode( handle, mode | ENABLE_VIRTUAL_TERMINAL_PROCESSING );
}

void GLogger::Shutdown()
{
    _log_file.close();
}

void GLogger::Log( ELogLevel log_level, std::string_view category, const char* file, int line, const std::string& message )
{
}
