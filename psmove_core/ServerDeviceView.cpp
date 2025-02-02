#include "ServerDeviceView.h"
#include "DeviceEnumerator.h"
#include <iostream>
#include <chrono>

ServerDeviceView::ServerDeviceView(const int device_id)
    : m_deviceID(device_id)
    , m_bHasUnpublishedState(false)
    , m_pollNoDataCount(0)
    , m_sequence_number(0)
{
}

ServerDeviceView::~ServerDeviceView()
{
}

bool ServerDeviceView::open(const DeviceEnumerator *enumerator)
{
    bool bSuccess = allocate_device_interface(enumerator);

    if (bSuccess)
    {
        m_bHasUnpublishedState = true;
        m_lastNewDataTimestamp = std::chrono::high_resolution_clock::now();
    }

    return bSuccess;
}

void ServerDeviceView::close()
{
    free_device_interface();
}

bool ServerDeviceView::poll()
{
    bool bNewData = false;

    IDeviceInterface *device = getDevice();

    if (device != nullptr)
    {
        switch (device->poll())
        {
        case IDeviceInterface::_PollResultSuccessNewData:
            m_bHasUnpublishedState = true;
            m_lastNewDataTimestamp = std::chrono::high_resolution_clock::now();
            m_pollNoDataCount = 0;
            ++m_sequence_number;
            bNewData = true;
            break;
        case IDeviceInterface::_PollResultSuccessNoData:
            ++m_pollNoDataCount;
            break;
        case IDeviceInterface::_PollResultFailure:
            std::cerr << "ServerDeviceView::poll() - Failed to poll device " << m_deviceID << std::endl;
            break;
        }
    }

    return bNewData;
}

void ServerDeviceView::publish()
{
    if (m_bHasUnpublishedState)
    {
        publish_device_data_frame();
        m_bHasUnpublishedState = false;
    }
}

bool ServerDeviceView::matchesDeviceEnumerator(const DeviceEnumerator *enumerator) const
{
    IDeviceInterface *device = getDevice();

    return (device != nullptr) ? device->matchesDeviceEnumerator(enumerator) : false;
}

bool ServerDeviceView::getIsOpen() const
{
    IDeviceInterface *device = getDevice();

    return (device != nullptr) && device->getIsOpen();
}
