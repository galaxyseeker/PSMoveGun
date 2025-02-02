#ifndef DEVICE_MANAGER_H
#define DEVICE_MANAGER_H

#include <memory>
#include "DeviceInterface.h"
#include "DevicePlatformInterface.h"
#include "TrackerManager.h"

class ServerControllerView;
typedef std::shared_ptr<ServerControllerView> ServerControllerViewPtr;

class DeviceManager {
public:
    static DeviceManager* getInstance();
    ServerControllerViewPtr getControllerViewPtr(int controller_id);
    TrackerManager* m_tracker_manager;

    // 添加其他必要的方法...

private:
    DeviceManager() {} // 私有构造函数，防止直接实例化
    static DeviceManager* s_instance;

    // 添加其他必要的成员变量...
};
#endif // DEVICE_MANAGER_H

