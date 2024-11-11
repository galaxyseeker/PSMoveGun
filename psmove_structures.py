import ctypes

# 常量定义
PSMOVESERVICE_MAX_CONTROLLER_COUNT = 5
PSMOVESERVICE_CONTROLLER_SERIAL_LEN = 18

# 结构体定义
class PSMVector2f(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float),
                ("y", ctypes.c_float)]

class PSMVector3f(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float),
                ("y", ctypes.c_float),
                ("z", ctypes.c_float)]

class PSMQuatf(ctypes.Structure):
    _fields_ = [("w", ctypes.c_float),
                ("x", ctypes.c_float),
                ("y", ctypes.c_float),
                ("z", ctypes.c_float)]

class PSMPosef(ctypes.Structure):
    _fields_ = [("Orientation", PSMQuatf),
                ("Position", PSMVector3f)]

class PSMPSMoveCalibratedSensorData(ctypes.Structure):
    _fields_ = [("Magnetometer", PSMVector3f),
                ("Accelerometer", PSMVector3f),
                ("Gyroscope", PSMVector3f)]

class PSMTrackingProjection(ctypes.Structure):
    _fields_ = [("shape", ctypes.c_int),
                ("shape_center", PSMVector2f),
                ("shape_radii", PSMVector2f)]

class PSMRawTrackerData(ctypes.Structure):
    _fields_ = [("TrackerID", ctypes.c_int),
                ("ValidProjections", ctypes.c_uint32),
                ("ProjectionCenterPixel", PSMVector2f),
                ("ScreenLocation", PSMVector2f),
                ("RelativePositionCm", PSMVector3f),
                ("RelativeOrientation", PSMQuatf),
                ("TrackingProjections", PSMTrackingProjection * 2)]

class PSMPhysicsData(ctypes.Structure):
    _fields_ = [("Velocity", PSMVector3f),
                ("Acceleration", PSMVector3f),
                ("AngularVelocity", PSMVector3f),
                ("AngularAcceleration", PSMVector3f)]

class PSMPSMove(ctypes.Structure):
    _fields_ = [
        ("bHasValidHardwareCalibration", ctypes.c_bool),
        ("bIsTrackingEnabled", ctypes.c_bool),
        ("bIsCurrentlyTracking", ctypes.c_bool),
        ("bIsOrientationValid", ctypes.c_bool),
        ("bIsPositionValid", ctypes.c_bool),
        ("bHasUnpublishedState", ctypes.c_bool),
        ("DevicePath", ctypes.c_char * 256),
        ("DeviceSerial", ctypes.c_char * 128),
        ("AssignedHostSerial", ctypes.c_char * 128),
        ("PairedToHost", ctypes.c_bool),
        ("ConnectionType", ctypes.c_int),
        ("TrackingColorType", ctypes.c_int),
        ("Pose", PSMPosef),
        ("PhysicsData", PSMPhysicsData),
        ("RawSensorData", PSMPSMoveCalibratedSensorData),
        ("CalibratedSensorData", PSMPSMoveCalibratedSensorData),
        ("RawTrackerData", PSMRawTrackerData),
        ("TriangleButton", ctypes.c_int),
        ("CircleButton", ctypes.c_int),
        ("CrossButton", ctypes.c_int),
        ("SquareButton", ctypes.c_int),
        ("SelectButton", ctypes.c_int),
        ("StartButton", ctypes.c_int),
        ("PSButton", ctypes.c_int),
        ("MoveButton", ctypes.c_int),
        ("TriggerButton", ctypes.c_int),
        ("BatteryValue", ctypes.c_int),
        ("TriggerValue", ctypes.c_ubyte),
        ("Rumble", ctypes.c_ubyte),
        ("LED_r", ctypes.c_ubyte),
        ("LED_g", ctypes.c_ubyte),
        ("LED_b", ctypes.c_ubyte),
        ("ResetPoseButtonPressTime", ctypes.c_longlong),
        ("bResetPoseRequestSent", ctypes.c_bool),
        ("bPoseResetButtonEnabled", ctypes.c_bool),
    ]

class PSMControllerState(ctypes.Union):
    _fields_ = [("PSMoveState", PSMPSMove)]

class PSMController(ctypes.Structure):
    _fields_ = [
        ("ControllerID", ctypes.c_int),
        ("ControllerType", ctypes.c_int),
        ("ControllerHand", ctypes.c_int),
        ("ControllerSerial", ctypes.c_char * PSMOVESERVICE_CONTROLLER_SERIAL_LEN),
        ("ParentControllerSerial", ctypes.c_char * PSMOVESERVICE_CONTROLLER_SERIAL_LEN),
        ("ControllerState", PSMControllerState),
        ("bValid", ctypes.c_bool),
        ("OutputSequenceNum", ctypes.c_int),
        ("InputSequenceNum", ctypes.c_int),
        ("IsConnected", ctypes.c_bool),
        ("DataFrameLastReceivedTime", ctypes.c_longlong),
        ("DataFrameAverageFPS", ctypes.c_float),
        ("ListenerCount", ctypes.c_int)
    ]

class PSMControllerList(ctypes.Structure):
    _fields_ = [
        ("controller_id", ctypes.c_int * PSMOVESERVICE_MAX_CONTROLLER_COUNT),
        ("controller_type", ctypes.c_int * PSMOVESERVICE_MAX_CONTROLLER_COUNT),
        ("controller_hand", ctypes.c_int * PSMOVESERVICE_MAX_CONTROLLER_COUNT),
        ("controller_serial", (ctypes.c_char * PSMOVESERVICE_CONTROLLER_SERIAL_LEN) * PSMOVESERVICE_MAX_CONTROLLER_COUNT),
        ("parent_controller_serial", (ctypes.c_char * PSMOVESERVICE_CONTROLLER_SERIAL_LEN) * PSMOVESERVICE_MAX_CONTROLLER_COUNT),
        ("count", ctypes.c_int)
    ]