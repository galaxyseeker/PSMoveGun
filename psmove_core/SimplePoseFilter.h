#ifndef SIMPLE_POSE_FILTER_H
#define SIMPLE_POSE_FILTER_H

#include "PoseFilterInterface.h"
#include <Eigen/Geometry>

class SimplePoseFilter : public IPoseFilter {
public:
    SimplePoseFilter() : m_orientation(Eigen::Quaternionf::Identity()), m_position(Eigen::Vector3f::Zero()) {}

    void update(float delta_time, const PoseFilterPacket& packet) override {}
    bool getIsOrientationStateValid() const override { return true; }
    bool getIsPositionStateValid() const override { return true; }
    void recenterOrientation(const Eigen::Quaternionf& q_pose) override {}

    Eigen::Quaternionf getOrientation(float prediction_time) const {
        return m_orientation;
    }
    Eigen::Vector3f getPositionCm(float prediction_time) const {
        return m_position;
    }
    Eigen::Vector3f getAngularVelocityRadPerSec() const override { return Eigen::Vector3f::Zero(); }
    Eigen::Vector3f getAngularAccelerationRadPerSecSqr() const override { return Eigen::Vector3f::Zero(); }
    Eigen::Vector3f getVelocityCmPerSec() const override { return Eigen::Vector3f::Zero(); }
    Eigen::Vector3f getAccelerationCmPerSecSqr() const override { return Eigen::Vector3f::Zero(); }

    // 添加这些方法以匹配 ServerControllerView.cpp 中的调用
    void updateIMUData(const IMUData& imu_data) {}
    void predict() {}

private:
    Eigen::Quaternionf m_orientation;
    Eigen::Vector3f m_position;
};

#endif // SIMPLE_POSE_FILTER_H
