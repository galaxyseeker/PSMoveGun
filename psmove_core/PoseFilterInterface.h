#ifndef POSE_FILTER_INTERFACE_H
#define POSE_FILTER_INTERFACE_H

#include <Eigen/Geometry>
#include "DeviceInterface.h"
#include <chrono>

// 前向声明
class IPoseFilter;

struct PoseSensorPacket {
    // ... (保持原有内容)
};

struct PoseFilterPacket : PoseSensorPacket {
    // ... (保持原有内容)
};

class PoseFilterSpace
{
public:
    EIGEN_MAKE_ALIGNED_OPERATOR_NEW
    
    PoseFilterSpace();

    inline void setIdentityGravity(const Eigen::Vector3f &identityGravity)
    { m_IdentityGravity = identityGravity; }
    inline void setIdentityMagnetometer(const Eigen::Vector3f &identityMagnetometer)
    { m_IdentityMagnetometer = identityMagnetometer; }

    inline void setCalibrationTransform(const Eigen::Matrix3f &calibrationTransform)
    { m_CalibrationTransform = calibrationTransform; }
    inline void setSensorTransform(const Eigen::Matrix3f &sensorTransform)
    { m_SensorTransform = sensorTransform; }

    Eigen::Vector3f getGravityCalibrationDirection() const;
    Eigen::Vector3f getMagnetometerCalibrationDirection() const;

    void createFilterPacket(
        const PoseSensorPacket &sensorPacket,
        const IPoseFilter *poseFilter,
        PoseFilterPacket &outFilterPacket) const;

private:
    Eigen::Vector3f m_IdentityGravity;
    Eigen::Vector3f m_IdentityMagnetometer;

    Eigen::Matrix3f m_CalibrationTransform;
    Eigen::Matrix3f m_SensorTransform;
};

struct PoseFilterConstants {
    // ... (保持原有内容)
};

class IPoseFilter {
public:
    virtual ~IPoseFilter() = default;
    virtual void update(float delta_time, const PoseFilterPacket& packet) = 0;
    virtual bool getIsOrientationStateValid() const = 0;
    virtual bool getIsPositionStateValid() const = 0;
    virtual Eigen::Quaternionf getOrientation(float prediction_time) const = 0;
    virtual Eigen::Vector3f getPositionCm(float prediction_time) const = 0;
    virtual Eigen::Vector3f getAngularVelocityRadPerSec() const = 0;
    virtual Eigen::Vector3f getAngularAccelerationRadPerSecSqr() const = 0;
    virtual Eigen::Vector3f getVelocityCmPerSec() const = 0;
    virtual Eigen::Vector3f getAccelerationCmPerSecSqr() const = 0;
    virtual void recenterOrientation(const Eigen::Quaternionf& q) = 0;
    
    // 添加这些新的虚函数
    virtual void updateIMUData(const IMUData& imu_data) = 0;
    virtual void predict() = 0;
};

#endif // POSE_FILTER_INTERFACE_H
