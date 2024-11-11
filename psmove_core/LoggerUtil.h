#pragma once
#include <string>
#include <fstream>

// 添加 LogLevel 枚举定义
enum class LogLevel {
    DEBUG,
    INFO,
    WARNING,
    ERROR,
    CRITICAL
};

class LoggerUtil {
public:
    static void setupLogger();
    static void log(LogLevel level, const std::string& message);

private:
    static std::string getTimestamp();
    static std::string getLevelString(LogLevel level);

    static std::ofstream logFile;
    static LogLevel currentLevel;
};

// 为了方便使用，可以添加以下函数
inline void initLogger(const std::string& filename) {
    LoggerUtil::setupLogger();
}

inline void closeLogger() {
    // 如果需要，可以在这里添加关闭日志文件的逻辑
}

inline void log(const std::string& message) {
    LoggerUtil::log(LogLevel::INFO, message);
}
