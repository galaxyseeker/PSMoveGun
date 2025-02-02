#ifndef DEVICE_PLATFORM_INTERFACE_H
#define DEVICE_PLATFORM_INTERFACE_H

#include <string>

// 使用前向声明而不是完整的类定义
class DeviceEnumerator;

// HID设备接口
class HidDeviceInterface
{
public:
    virtual ~HidDeviceInterface() {}

    virtual bool open(const char *path) = 0;
    virtual void close() = 0;
    virtual bool isOpen() const = 0;
    virtual int write(const unsigned char *data, int length) = 0;
    virtual int read(unsigned char *data, int length) = 0;
    virtual std::string getSerial() const = 0;
};

// 创建设备枚举器的工厂函数声明
DeviceEnumerator* create_device_enumerator();

// 创建HID设备接口的工厂函数声明
HidDeviceInterface* create_hid_device_interface();

#endif // DEVICE_PLATFORM_INTERFACE_H
