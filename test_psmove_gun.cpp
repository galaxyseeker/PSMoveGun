#include "psmove_data_fetcher.h"
#include "psmove_core/LoggerUtil.h"
#include <iostream>
#include <sstream>

int main() {
    initLogger("PSMoveGun.log");
    log("Starting PSMove Gun test program");

    PSMoveDataFetcher& fetcher = PSMoveDataFetcher::getInstance();
    
    if (fetcher.initialize()) {
        log("Fetcher initialized successfully.");
        
        bool isConnected = fetcher.isControllerConnected();
        log("Controller connected: " + std::string(isConnected ? "Yes" : "No"));
        
        if (isConnected) {
            try {
                CommonDevicePose pose = fetcher.get_pose_data();
                std::stringstream ss;
                ss << "Pose data: Position(" << pose.PositionCm.x << ", " << pose.PositionCm.y << ", " << pose.PositionCm.z 
                   << "), Orientation(" << pose.Orientation.w << ", " << pose.Orientation.x << ", " << pose.Orientation.y << ", " << pose.Orientation.z << ")";
                log(ss.str());
            } catch (const std::exception& e) {
                LoggerUtil::log(LogLevel::ERROR, "Error getting pose data: " + std::string(e.what()));
            }
        }
    } else {
        log("Failed to initialize fetcher.");
    }
    
    log("PSMove Gun test program finished");
    closeLogger();
    return 0;
}
