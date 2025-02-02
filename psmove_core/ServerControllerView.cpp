#include "ServerControllerView.h"
#include "DeviceEnumerator.h"
#include "TrackerManager.h"
#include <iostream>
#include "PoseFilterInterface.h"
#include "DeviceInterface.h"
#include <Eigen/Dense>
#include "MathUtility.h"
#include "ServerControllerView.h"
#include "DeviceEnumerator.h"
#include "TrackerManager.h"
#include "ConcretePoseFilter.h"
#include "ConcreteDeviceInterface.h"  // 添加这行
#include "PSMoveController.h"
#include "DeviceManager.h"
// 添加必要的头文件，可能包括 PSMove API 的头文件

// 添加 ControllerOpticalPoseEstimation 的前向声明或包含其头文件
class ControllerOpticalPoseEstimation {
public:
    void clear() {}
    // 添加其他必要的方法
};

ServerControllerView::ServerControllerView(int device_id)
    : ServerDeviceView(device_id)
    , m_lastPollSeqNumProcessed(-1)
    , m_last_filter_update_timestamp_valid(false)
{
    std::cout << "ServerControllerView constructor called with device_id: " << device_id << std::endl;
}

bool ServerControllerView::open(const DeviceEnumerator *enumerator)
{
    bool bSuccess = ServerDeviceView::open(enumerator);

    if (bSuccess)
    {
        IDeviceInterface *device = getDevice();

        if (device && device->getDeviceType() == CommonDeviceState::PSMove)
        {
            PSMoveControllerDeviceInterface* psmoveController = static_cast<PSMoveControllerDeviceInterface*>(device);
            if (psmoveController && psmoveController->getIsBluetooth())
            {
                resetPoseFilter();
                if (m_multicam_pose_estimation) {
                    m_multicam_pose_estimation->clear();
                }

                eCommonTrackingColorID tracking_color_id;
                if (device->getTrackingColorID(tracking_color_id) && tracking_color_id != eCommonTrackingColorID::INVALID_COLOR)
                {
                    // Implement claimTrackingColorID
                }
                else
                {
                    // Implement allocateTrackingColorID and setTrackingColorID
                }
            }
        }

        m_lastPollSeqNumProcessed = -1;
    }

    m_last_filter_update_timestamp = std::chrono::high_resolution_clock::now();
    m_last_filter_update_timestamp_valid = false;

    return bSuccess;
}

const CommonControllerState* ServerControllerView::getState() const
{
    if (m_device)
    {
        return m_device->getControllerState();
    }
    return nullptr;
}

bool ServerControllerView::allocate_device_interface(const DeviceEnumerator *enumerator)
{
    m_device = std::make_unique<PSMoveControllerDeviceInterface>(getDeviceID());
    return m_device != nullptr;
}

void ServerControllerView::publish_device_data_frame()
{
    if (m_device)
    {
        auto data = m_device->getLatestData();
        // 发布数据的逻辑...
    }
}

void ServerControllerView::updateStateAndPredict()
{
    if (m_device)
    {
        auto imu_data = m_device->getLatestIMUData();
        updatePoseFilter(imu_data);
    }
}

void ServerControllerView::resetPoseFilter()
{
    m_orientation = Eigen::Quaternionf::Identity();
    m_position = Eigen::Vector3f::Zero();
    m_velocity = Eigen::Vector3f::Zero();
    m_angular_velocity = Eigen::Vector3f::Zero();
}

void ServerControllerView::free_device_interface()
{
    m_device.reset();
}

void ServerControllerView::close()
{
    if (m_device)
    {
        m_device->close();
    }
    free_device_interface();
}

ServerControllerView::~ServerControllerView()
{
    close();
}

CommonDevicePose ServerControllerView::getFilteredPose(float prediction_time) const
{
    CommonDevicePose pose;
    pose.Orientation.w = m_orientation.w();
    pose.Orientation.x = m_orientation.x();
    pose.Orientation.y = m_orientation.y();
    pose.Orientation.z = m_orientation.z();
    
    pose.PositionCm.x = m_position.x();
    pose.PositionCm.y = m_position.y();
    pose.PositionCm.z = m_position.z();

    return pose;
}

void ServerControllerView::updatePoseFilter(const IMUData& imu_data)
{
    // 实现基本的姿态更新逻辑
    // 这里只是一个简单的示例，实际实现可能需要更复杂的算法
    float dt = 0.01f; // 假设固定的时间步长，实际应该根据时间戳计算

    // 更新方向
    Eigen::Quaternionf deltaRotation = Eigen::Quaternionf::FromTwoVectors(
        Eigen::Vector3f::UnitY(),
        imu_data.accelerometer.normalized());
    m_orientation = m_orientation * deltaRotation;

    // 更新位置（简单积分）
    m_position += m_velocity * dt;
    m_velocity += imu_data.accelerometer * dt;

    // 更新角速度
    m_angular_velocity = imu_data.gyroscope;
}

// Implement other methods as needed

