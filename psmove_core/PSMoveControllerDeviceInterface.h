#ifndef PSMOVE_CONTROLLER_DEVICE_INTERFACE_H
#define PSMOVE_CONTROLLER_DEVICE_INTERFACE_H

#include "DeviceInterface.h"

class PSMoveControllerDeviceInterface : public IDeviceInterface
{
public:
    explicit PSMoveControllerDeviceInterface(int device_id);
    virtual ~PSMoveControllerDeviceInterface();

    bool matchesDeviceEnumerator(const DeviceEnumerator *enumerator) const override;
    bool open() override;
    void close() override;
    bool getIsOpen() const override;
    ePollResult poll() override;
    const CommonControllerState* getControllerState() const override;
    DeviceData getLatestData() const override;
    int getDeviceID() const override;
    IMUData getLatestIMUData() const override;
    CommonDeviceState::eDeviceType getDeviceType() const override;
    bool getTrackingColorID(eCommonTrackingColorID& out_tracking_color_id) const override;
    bool setTrackingColorID(eCommonTrackingColorID tracking_color_id) override;

    bool getIsBluetooth() const;

private:
    int m_device_id;
    bool m_is_open;
    CommonControllerState m_controller_state;
    DeviceData m_latest_data;
    IMUData m_latest_imu_data;
    eCommonTrackingColorID m_tracking_color_id;
};
#endif // PSMOVE_CONTROLLER_DEVICE_INTERFACE_H

