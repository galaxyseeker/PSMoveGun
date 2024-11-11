#include "TrackerManager.h"
#include "ServerControllerView.h"

void TrackerManager::claimTrackingColorID(ServerControllerView* controller, eCommonTrackingColorID color_id) {
    // 实现逻辑
}

eCommonTrackingColorID TrackerManager::allocateTrackingColorID() {
    // 实现逻辑
    return eCommonTrackingColorID::INVALID_COLOR; // 临时返回值
}

void TrackerManager::freeTrackingColorID(eCommonTrackingColorID color_id) {
    // 实现逻辑
}
