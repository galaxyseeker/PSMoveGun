#ifndef SERVER_DEVICE_VIEW_H
#define SERVER_DEVICE_VIEW_H

//-- includes -----
#include "DeviceInterface.h"
#include <chrono>

// -- declarations -----
// 添加前向声明
class IDeviceInterface;

class ServerDeviceView
{
public:
    ServerDeviceView(const int device_id);
    virtual ~ServerDeviceView();
    
    virtual bool open(const DeviceEnumerator *enumerator);
    virtual void close();

    virtual bool poll();
    virtual void publish();
    
    bool matchesDeviceEnumerator(const DeviceEnumerator *enumerator) const;
    
    // getters
    inline int getDeviceID() const
    { return m_deviceID; }
    
    virtual IDeviceInterface* getDevice() const=0;
    
    // Used for when you have to get device specific data
    template <class t_device_subclass>
    inline const t_device_subclass *castCheckedConst() const
    { 
        IDeviceInterface* device= getDevice();
        assert(device != nullptr);
        assert(device->getDeviceType() == t_device_subclass::getDeviceTypeStatic());
        const t_device_subclass *controller= static_cast<const t_device_subclass *>(device);

        return controller; 
    }
    template <class t_device_subclass>
    inline t_device_subclass *castChecked()
    {
        IDeviceInterface* device= getDevice();
        assert(device != nullptr);
        assert(device->getDeviceType() == t_device_subclass::getDeviceTypeStatic());
        t_device_subclass *controller= static_cast<t_device_subclass *>(device);

        return controller; 
    }    

    // Returns true if device opened successfully
    bool getIsOpen() const;
    inline bool getHasUnpublishedState()
    { return m_bHasUnpublishedState; }
    inline std::chrono::time_point<std::chrono::high_resolution_clock> getLastNewDataTimestamp() const
    { return m_lastNewDataTimestamp; }
    
    // setters
    inline void markStateAsUnpublished()
    { m_bHasUnpublishedState= true; }
    
protected:
    virtual bool allocate_device_interface(const DeviceEnumerator *enumerator) = 0;
    virtual void free_device_interface() = 0;
    virtual void publish_device_data_frame() = 0;

    bool m_bHasUnpublishedState;
    int m_pollNoDataCount;
    int m_sequence_number;
    std::chrono::time_point<std::chrono::high_resolution_clock> m_lastNewDataTimestamp;
    
private:
    int m_deviceID;
};

#endif // SERVER_DEVICE_VIEW_H
