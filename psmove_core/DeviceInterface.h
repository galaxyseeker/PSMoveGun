#ifndef DEVICE_INTERFACE_H
#define DEVICE_INTERFACE_H

#include <string>
#include <vector>
#include <Eigen/Core>

class DeviceEnumerator;

// 定义 CommonDeviceState 结构
struct CommonDeviceState
{
    enum eDeviceClass
    {
        Controller = 0x00,
        TrackingCamera = 0x10,
        HeadMountedDisplay = 0x20
    };
    
    enum eDeviceType
    {
        PSMove = Controller + 0x00,
        PSNavi = Controller + 0x01,
        PSDualShock4 = Controller + 0x02,
        VirtualController = Controller + 0x03,
        SUPPORTED_CONTROLLER_TYPE_COUNT = Controller + 0x04,
        
        PS3EYE = TrackingCamera + 0x00,
        SUPPORTED_CAMERA_TYPE_COUNT = TrackingCamera + 0x01,
        
        Morpheus = HeadMountedDisplay + 0x00,
        VirtualHMD = HeadMountedDisplay + 0x01,
        SUPPORTED_HMD_TYPE_COUNT = HeadMountedDisplay + 0x02,

        INVALID_DEVICE_TYPE = 0xFF,
    };
    
    eDeviceType DeviceType;
    int PollSequenceNumber;
    
    inline CommonDeviceState()
    {
        clear();
    }
    
    inline void clear()
    {
        DeviceType = SUPPORTED_CONTROLLER_TYPE_COUNT; // invalid
        PollSequenceNumber = 0;
    }

    static const char *getDeviceTypeString(eDeviceType device_type);
};

// 定义 CommonDevicePosition 结构
struct CommonDevicePosition
{
    float x, y, z;

    inline void clear()
    {
        x = y = z = 0.f;
    }

    inline void set(float _x, float _y, float _z)
    {
        x = _x;
        y = _y;
        z = _z;
    }
};

// 定义 CommonDeviceQuaternion 结构
struct CommonDeviceQuaternion
{
    float x, y, z, w;

    inline void clear()
    {
        x = y = z = 0.f;
        w = 1.f;
    }
};

// 定义 CommonDevicePose 结构
struct CommonDevicePose
{
    CommonDevicePosition PositionCm;
    CommonDeviceQuaternion Orientation;

    void clear()
    {
        PositionCm.clear();
        Orientation.clear();
    }
};

// 定义 CommonControllerState 结构
struct CommonControllerState : CommonDeviceState
{
    enum ButtonState {
        Button_UP = 0x00,       // (00b) Not pressed
        Button_PRESSED = 0x01,  // (01b) Down for one frame only
        Button_DOWN = 0x03,     // (11b) Down for >1 frame
        Button_RELEASED = 0x02, // (10b) Up for one frame only
    };

    enum BatteryLevel {
        Batt_MIN = 0x00, /*!< Battery is almost empty (< 20%) */
        Batt_20Percent = 0x01, /*!< Battery has at least 20% remaining */
        Batt_40Percent = 0x02, /*!< Battery has at least 40% remaining */
        Batt_60Percent = 0x03, /*!< Battery has at least 60% remaining */
        Batt_80Percent = 0x04, /*!< Battery has at least 80% remaining */
        Batt_MAX = 0x05, /*!< Battery is fully charged (not on charger) */
        Batt_CHARGING = 0xEE, /*!< Battery is currently being charged */
        Batt_CHARGING_DONE = 0xEF, /*!< Battery is fully charged (on charger) */
    };

    enum RumbleChannel
    {
        ChannelAll,
        ChannelLeft,
        ChannelRight
    };

    enum BatteryLevel Battery;
    unsigned int AllButtons;                    // all-buttons, used to detect changes

    //TODO: high-precision timestamp. Need to do in hidapi?
    
    inline CommonControllerState()
    {
        clear();
    }

    inline void clear()
    {
        CommonDeviceState::clear();
        Battery = Batt_MAX;
        AllButtons = 0;
    }
};

// 添加以下定义
enum eCommonTrackingColorID {
    INVALID_COLOR = -1,
    // ... 其他颜色定义
};

enum eCommonTrackingShapeType {
    INVALID_SHAPE = -1,
    Sphere,
    LightBar,
    // ... 其他形状定义
};

struct CommonDeviceTrackingShape {
    eCommonTrackingShapeType shape_type;
    // ... 其他成员
};

struct CommonDeviceScreenLocation {
    float x, y;
    // ... 其他成员
};

struct CommonDeviceTrackingProjection {
    // ... 定义
};

struct CommonDevicePhysics {
    // ... 定义
};


struct DeviceData {
    // 定义设备数据结构
    std::vector<float> raw_sensor_data;
    // 可以添加其他需要的字段
};

struct IMUData {
    Eigen::Vector3f accelerometer;
    Eigen::Vector3f gyroscope;
    Eigen::Vector3f magnetometer;
    // 可以添加其他需要的字段，如时间戳
};


// 确保 IDeviceInterface 类有 getDeviceType 方法
class IDeviceInterface
{
public:
    enum ePollResult
    {
        _PollResultSuccessNoData,
        _PollResultSuccessNewData,
        _PollResultFailure,
    };

    virtual ~IDeviceInterface() {}

    virtual bool matchesDeviceEnumerator(const DeviceEnumerator *enumerator) const = 0;
    virtual bool open() = 0;
    virtual void close() = 0;
    virtual bool getIsOpen() const = 0;
    virtual ePollResult poll() = 0;

    // 添加 getControllerState 方法
    virtual const CommonControllerState* getControllerState() const = 0;

    // 其他必要的虚函数...
    
    // 添加新的虚函数
    virtual DeviceData getLatestData() const = 0;
    virtual int getDeviceID() const = 0;
    virtual IMUData getLatestIMUData() const = 0;

    virtual CommonDeviceState::eDeviceType getDeviceType() const = 0;
    virtual bool getTrackingColorID(eCommonTrackingColorID& out_tracking_color_id) const = 0;
    virtual bool setTrackingColorID(eCommonTrackingColorID tracking_color_id) = 0;
};

// 如果需要，可以添加其他相关的结构和枚举

#endif // DEVICE_INTERFACE_H
