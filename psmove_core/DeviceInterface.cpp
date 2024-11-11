#include "DeviceInterface.h"

const char* CommonDeviceState::getDeviceTypeString(CommonDeviceState::eDeviceType device_type)
{
    switch (device_type)
    {
    case PSMove:
        return "PSMove";
    case PSNavi:
        return "PSNavi";
    case PSDualShock4:
        return "PSDualShock4";
    case PS3EYE:
        return "PSEYE";
    case Morpheus:
        return "Morpheus";
    case VirtualHMD:
        return "VirtualHMD";
    case VirtualController:
        return "VirtualController";
    default:
        return "UNKNOWN";
    }
}
