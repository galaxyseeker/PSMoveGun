#ifndef MATH_EIGEN_H
#define MATH_EIGEN_H

#define _USE_MATH_DEFINES
#include <cmath>

// 如果 M_PI 未定义，我们自己定义它
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#include <Eigen/Core>
#include <Eigen/Geometry>

// 定义常用的 Eigen 类型
typedef Eigen::Matrix<float, 3, 1> Vector3f;
typedef Eigen::Matrix<float, 4, 1> Vector4f;
typedef Eigen::Matrix<float, 3, 3> Matrix3f;
typedef Eigen::Matrix<float, 4, 4> Matrix4f;
typedef Eigen::Quaternion<float> Quaternionf;

// 可以添加一些常用的数学函数
namespace MathEigen {

inline float clamp(float value, float min, float max) {
    return (value < min) ? min : ((value > max) ? max : value);
}

inline Vector3f clamp(const Vector3f& v, float min, float max) {
    return Vector3f(
        clamp(v.x(), min, max),
        clamp(v.y(), min, max),
        clamp(v.z(), min, max)
    );
}

// 将欧拉角（度）转换为四元数
inline Quaternionf eulerAnglesToQuaternion(float pitch, float yaw, float roll) {
    return Quaternionf(Eigen::AngleAxisf(static_cast<float>(pitch * M_PI / 180.0), Vector3f::UnitX())
                     * Eigen::AngleAxisf(static_cast<float>(yaw   * M_PI / 180.0), Vector3f::UnitY())
                     * Eigen::AngleAxisf(static_cast<float>(roll  * M_PI / 180.0), Vector3f::UnitZ()));
}

// 将四元数转换为欧拉角（度）
inline Vector3f quaternionToEulerAngles(const Quaternionf& q) {
    auto euler = q.toRotationMatrix().eulerAngles(0, 1, 2);
    return Vector3f(
        static_cast<float>(euler.x() * 180.0 / M_PI),
        static_cast<float>(euler.y() * 180.0 / M_PI),
        static_cast<float>(euler.z() * 180.0 / M_PI)
    );
}

} // namespace MathEigen

#endif // MATH_EIGEN_H
