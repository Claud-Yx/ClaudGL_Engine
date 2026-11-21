#pragma once

#include <fstream>

#include "Enum/LogLevel.h"

enum class ELogLevel;

class GLogger
{
public:
    static GLogger& Get();

    void Init( const char* file_name );
    void Shutdown();

    void Log( ELogLevel          log_level, std::string_view category, const char* file, int line,
              const std::string& message );

private:
    std::ofstream _log_file{};
    ELogLevel     _min_level{ ELogLevel::Trace };
};
