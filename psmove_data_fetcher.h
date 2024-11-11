#ifndef PSMOVE_DATA_FETCHER_H
#define PSMOVE_DATA_FETCHER_H

#include "psmove_core/DeviceInterface.h"
#include <memory>

class ServerControllerView;

class PSMoveDataFetcher {
public:
    static PSMoveDataFetcher& getInstance();

    bool initialize();
    CommonDevicePose get_pose_data();
    bool isControllerConnected() const;

private:
    PSMoveDataFetcher();
    ~PSMoveDataFetcher();
    PSMoveDataFetcher(const PSMoveDataFetcher&) = delete;
    PSMoveDataFetcher& operator=(const PSMoveDataFetcher&) = delete;

    std::shared_ptr<ServerControllerView> m_controller_view;
};

#endif // PSMOVE_DATA_FETCHER_H
