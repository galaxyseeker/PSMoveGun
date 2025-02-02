#ifndef CONCRETE_POSE_FILTER_H
#define CONCRETE_POSE_FILTER_H

#include "PoseFilterInterface.h"

class ConcretePoseFilter : public IPoseFilter {
public:
    ConcretePoseFilter();
    ~ConcretePoseFilter() override;

    void update(float delta_time, const PoseFilterPacket& packet) override;
    bool getIsOrientationStateValid() const override;
    bool getIsPositionStateValid() const override;
    Eigen::Quaternionf getOrientation(float prediction_time) const override;
    Eigen::Vector3f getPositionCm(float prediction_time) const override;
    Eigen::Vector3f getAngularVelocityRadPerSec() const override;
    Eigen::Vector3f getAngularAccelerationRadPerSecSqr() const override;
    Eigen::Vector3f getVelocityCmPerSec() const override;
    Eigen::Vector3f getAccelerationCmPerSecSqr() const override;
    void recenterOrientation(const Eigen::Quaternionf& q) override;

    // 添加新的方法
   // void updateOpticalData(const OpticalData& optical_data) override;
    void updateIMUData(const IMUData& imu_data) override;
    void predict() override;

private:
    // 添加必要的成员变量
    Eigen::Quaternionf m_orientation;
    Eigen::Vector3f m_position;
    // ... 其他必要的状态变量
};

#endif // CONCRETE_POSE_FILTER_H
