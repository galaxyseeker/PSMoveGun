#include "PSMoveController.h"

PSMoveController::PSMoveController(int device_id) : ConcreteDeviceInterface(device_id) {
    // 初始化代码
}

bool PSMoveController::getIsBluetooth() const {
    // 实现逻辑
    return true; // 临时返回值
}

// 实现其他必要的方法...
