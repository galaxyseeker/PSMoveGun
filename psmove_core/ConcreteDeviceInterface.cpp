#include "ConcreteDeviceInterface.h"
#include "DeviceEnumerator.h"
#include <iostream>

ConcreteDeviceInterface::ConcreteDeviceInterface(int device_id)
    : m_device_id(device_id), m_is_open(false)
{
}

ConcreteDeviceInterface::~ConcreteDeviceInterface()
{
    if (m_is_open)
    {
        close();
    }
}

bool ConcreteDeviceInterface::matchesDeviceEnumerator(const DeviceEnumerator *enumerator) const
{
    // 实现设备匹配逻辑
    // 这里需要根据实际情况来判断设备是否匹配
    return true; // 临时返回值，需要根据实际逻辑修改
}

bool ConcreteDeviceInterface::open()
{
    if (!m_is_open)
    {
        // 实现设备打开逻辑
        // 这里需要添加实际的设备打开代码
        m_is_open = true;
        std::cout << "Device " << m_device_id << " opened." << std::endl;
    }
    return m_is_open;
}

void ConcreteDeviceInterface::close()
{
    if (m_is_open)
    {
        // 实现设备关闭逻辑
        // 这里需要添加实际的设备关闭代码
        m_is_open = false;
        std::cout << "Device " << m_device_id << " closed." << std::endl;
    }
}

bool ConcreteDeviceInterface::getIsOpen() const
{
    return m_is_open;
}

IDeviceInterface::ePollResult ConcreteDeviceInterface::poll()
{
    if (!m_is_open)
    {
        return _PollResultFailure;
    }

    // 实现数据轮询逻辑
    // 这里需要添加实际的数据读取代码
    // 更新 m_controller_state, m_latest_data, 和 m_latest_imu_data

    return _PollResultSuccessNewData; // 假设每次都有新数据
}

const CommonControllerState* ConcreteDeviceInterface::getControllerState() const
{
    return &m_controller_state;
}

DeviceData ConcreteDeviceInterface::getLatestData() const
{
    return m_latest_data;
}

int ConcreteDeviceInterface::getDeviceID() const
{
    return m_device_id;
}

IMUData ConcreteDeviceInterface::getLatestIMUData() const
{
    return m_latest_imu_data;
}

CommonDeviceState::eDeviceType ConcreteDeviceInterface::getDeviceType() const
{
    // 根据实际情况返回适当的设备类型
    return CommonDeviceState::PSMove;  // 假设这是一个 PSMove 控制器
}

bool ConcreteDeviceInterface::getTrackingColorID(eCommonTrackingColorID& out_tracking_color_id) const
{
    out_tracking_color_id = m_tracking_color_id;
    return true;
}

bool ConcreteDeviceInterface::setTrackingColorID(eCommonTrackingColorID tracking_color_id)
{
    m_tracking_color_id = tracking_color_id;
    return true;
}
