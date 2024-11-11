#include "LoggerUtil.h"
#include <iostream>
#include <chrono>  // 添加这行
#include <ctime>
#include <sstream>
#include <iomanip>

// 定义静态成员变量
std::ofstream LoggerUtil::logFile;
LogLevel LoggerUtil::currentLevel = LogLevel::DEBUG;

void LoggerUtil::setupLogger() {
    logFile.open("PSMoveGun.log", std::ios::out | std::ios::trunc);
    if (!logFile.is_open()) {
        std::cerr << "Failed to open log file." << std::endl;
    }
}

void LoggerUtil::log(LogLevel level, const std::string& message) {
    if (level >= currentLevel) {
        std::string logMessage = getTimestamp() + " - " + getLevelString(level) + " - " + message + "\n";
        logFile << logMessage;
        logFile.flush();
        std::cout << logMessage;  // Also print to console
    }
}

std::string LoggerUtil::getTimestamp() {
    auto now = std::chrono::system_clock::now();
    auto in_time_t = std::chrono::system_clock::to_time_t(now);
    std::stringstream ss;
    ss << std::put_time(std::localtime(&in_time_t), "%Y-%m-%d %X");
    return ss.str();
}

std::string LoggerUtil::getLevelString(LogLevel level) {
    switch (level) {
        case LogLevel::DEBUG: return "DEBUG";
        case LogLevel::INFO: return "INFO";
        case LogLevel::WARNING: return "WARNING";
        case LogLevel::ERROR: return "ERROR";
        case LogLevel::CRITICAL: return "CRITICAL";
        default: return "UNKNOWN";
    }
}
