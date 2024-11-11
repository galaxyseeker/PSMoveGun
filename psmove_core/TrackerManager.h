#ifndef TRACKER_MANAGER_H
#define TRACKER_MANAGER_H

#include "DeviceInterface.h"

class ServerControllerView;

class TrackerManager {
public:
    void claimTrackingColorID(ServerControllerView* controller, eCommonTrackingColorID color_id);
    eCommonTrackingColorID allocateTrackingColorID();
    void freeTrackingColorID(eCommonTrackingColorID color_id);
    
    // ... 其他方法 ...
};

#endif // TRACKER_MANAGER_H
