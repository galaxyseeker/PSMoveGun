#ifndef SERVER_CONTROLLER_VIEW_H
#define SERVER_CONTROLLER_VIEW_H

#include "ServerDeviceView.h"
#include "PoseFilterInterface.h"
#include "PSMoveControllerDeviceInterface.h"
#include <memory>
#include <Eigen/Geometry>

class ControllerOpticalPoseEstimation;

class ServerControllerView : public ServerDeviceView
{
public:
    ServerControllerView(int device_id);
    virtual ~ServerControllerView();

    bool open(const DeviceEnumerator *enumerator) override;
    void close() override;

    IDeviceInterface* getDevice() const override { return m_device.get(); }
    CommonDevicePose getFilteredPose(float prediction_time) const;
    const CommonControllerState* getState() const;

    bool allocate_device_interface(const DeviceEnumerator *enumerator) override;
    void free_device_interface() override;
    void publish_device_data_frame() override;

    void updateOpticalPoseEstimation(class TrackerManager* tracker_manager);
    void updateStateAndPredict();

private:
    void resetPoseFilter();
    void updatePoseFilter(const IMUData& imu_data);

    std::unique_ptr<PSMoveControllerDeviceInterface> m_device;
    std::unique_ptr<ControllerOpticalPoseEstimation> m_multicam_pose_estimation;
    int m_lastPollSeqNumProcessed;
    std::chrono::time_point<std::chrono::high_resolution_clock> m_last_filter_update_timestamp;
    bool m_last_filter_update_timestamp_valid;

    // 姿态过滤相关成员
    Eigen::Quaternionf m_orientation;
    Eigen::Vector3f m_position;
    Eigen::Vector3f m_velocity;
    Eigen::Vector3f m_angular_velocity;
};

#endif // SERVER_CONTROLLER_VIEW_H
