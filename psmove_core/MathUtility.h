#include <Eigen/Geometry>

inline Eigen::Quaternionf eigen_quaternion_concatenate(const Eigen::Quaternionf& q1, const Eigen::Quaternionf& q2) {
    return q1 * q2;
}

inline Eigen::Quaternionf eigen_euler_angles_to_quaternionf(const Eigen::Vector3f& euler) {
    return Eigen::Quaternionf(Eigen::AngleAxisf(euler.x(), Eigen::Vector3f::UnitX())
                            * Eigen::AngleAxisf(euler.y(), Eigen::Vector3f::UnitY())
                            * Eigen::AngleAxisf(euler.z(), Eigen::Vector3f::UnitZ()));
}
