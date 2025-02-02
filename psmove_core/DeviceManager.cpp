#include "DeviceManager.h"
#include "ServerControllerView.h"

DeviceManager* DeviceManager::s_instance = nullptr;

DeviceManager* DeviceManager::getInstance()
{
    if (s_instance == nullptr)
    {
        s_instance = new DeviceManager();
    }
    return s_instance;
}

std::shared_ptr<ServerControllerView> DeviceManager::getControllerViewPtr(int controller_id)
{
    return std::make_shared<ServerControllerView>(controller_id);
}

// 实现其他必要的方法...
