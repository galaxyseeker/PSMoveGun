#ifndef PSMOVE_CONTROLLER_H
#define PSMOVE_CONTROLLER_H

#include "ConcreteDeviceInterface.h"

class PSMoveController : public ConcreteDeviceInterface
{
public:
    PSMoveController(int device_id);
    bool getIsBluetooth() const;
    // ... 其他方法 ...
};

#endif // PSMOVE_CONTROLLER_H
