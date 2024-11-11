#include "psmove_data_fetcher.h"
#include "psmove_core/ServerControllerView.h"
#include "psmove_core/DeviceManager.h"
#include "psmove_core/LoggerUtil.h"
#include <iostream>
#include <thread>
#include <chrono>

PSMoveDataFetcher& PSMoveDataFetcher::getInstance() {
    static PSMoveDataFetcher instance;
    return instance;
}

PSMoveDataFetcher::PSMoveDataFetcher() : m_controller_view(nullptr) {
    LoggerUtil::log(LogLevel::INFO, "PSMoveDataFetcher constructor called");
}

PSMoveDataFetcher::~PSMoveDataFetcher() {
    LoggerUtil::log(LogLevel::INFO, "PSMoveDataFetcher destructor called");
}

bool PSMoveDataFetcher::initialize() {
    LoggerUtil::log(LogLevel::INFO, "Initializing PSMoveDataFetcher");
    
    DeviceManager* device_manager = DeviceManager::getInstance();
    if (!device_manager) {
        LoggerUtil::log(LogLevel::ERROR, "Failed to get DeviceManager instance");
        return false;
    }

    // 添加设备管理器更新
    device_manager->update();

    m_controller_view = device_manager->getControllerViewPtr(0);
    if (!m_controller_view) {
        LoggerUtil::log(LogLevel::ERROR, "Failed to get controller view");
        return false;
    }

    // 添加更多日志来显示控制器状态
    LoggerUtil::log(LogLevel::INFO, "Got controller view, attempting to open...");

    if (!m_controller_view->open(nullptr)) {
        LoggerUtil::log(LogLevel::ERROR, "Failed to open controller");
        return false;
    }

    // 等待控制器完全初始化
    int retry_count = 0;
    const int max_retries = 5;
    while (!m_controller_view->getIsOpen() && retry_count < max_retries) {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        device_manager->update();
        retry_count++;
    }

    if (m_controller_view->getIsOpen()) {
        LoggerUtil::log(LogLevel::INFO, "Controller opened successfully");
    } else {
        LoggerUtil::log(LogLevel::ERROR, "Controller failed to open after retries");
        return false;
    }

    LoggerUtil::log(LogLevel::INFO, "Controller initialized successfully");
    return true;
}

CommonDevicePose PSMoveDataFetcher::get_pose_data() {
    if (!m_controller_view) {
        LoggerUtil::log(LogLevel::ERROR, "Controller not initialized.");
        throw std::runtime_error("Controller not initialized.");
    }

    LoggerUtil::log(LogLevel::DEBUG, "Getting pose data");
    return m_controller_view->getFilteredPose(0.0f); // 使用0预测时间
}

bool PSMoveDataFetcher::isControllerConnected() const {
    if (!m_controller_view) {
        LoggerUtil::log(LogLevel::DEBUG, "Controller view is null");
        return false;
    }
    
    bool isOpen = m_controller_view->getIsOpen();
    LoggerUtil::log(LogLevel::DEBUG, 
        std::string("Controller connection status: ") + (isOpen ? "Open" : "Closed"));
    return isOpen;
}
