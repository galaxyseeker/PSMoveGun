import ctypes
import os
import pyautogui
import tkinter as tk
import threading
import time
import math
import numpy as np
import sys
from collections import deque


# 获取当前脚本的绝对路径
dll_path = r"C:\Users\galax\Desktop\PSMoveGun\Tools\PSMoveService_0.9_alpha9.0.1\bin\PSMoveClient_CAPI.dll"

# 加载 DLL
try:
    psmove_dll = ctypes.CDLL(os.path.abspath(dll_path))
except OSError as e:
    print(f"Error loading PSMoveClient_CAPI.dll: {e}")
    exit(1)

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

# 定义函数参数和返回类型
psmove_dll.PSM_Initialize.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
psmove_dll.PSM_Initialize.restype = ctypes.c_int

psmove_dll.PSM_GetControllerList.argtypes = [ctypes.POINTER(PSMControllerList), ctypes.c_int]
psmove_dll.PSM_GetControllerList.restype = ctypes.c_int

psmove_dll.PSM_StartControllerDataStream.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
psmove_dll.PSM_StartControllerDataStream.restype = ctypes.c_int

psmove_dll.PSM_GetController.argtypes = [ctypes.c_int]
psmove_dll.PSM_GetController.restype = ctypes.POINTER(PSMController)

psmove_dll.PSM_Update.argtypes = []
psmove_dll.PSM_Update.restype = ctypes.c_int

psmove_dll.PSM_Shutdown.argtypes = []
psmove_dll.PSM_Shutdown.restype = ctypes.c_int

psmove_dll.PSM_AllocateControllerListener.argtypes = [ctypes.c_int]
psmove_dll.PSM_AllocateControllerListener.restype = ctypes.c_int

psmove_dll.PSM_GetControllerOrientation.argtypes = [ctypes.c_int, ctypes.POINTER(PSMQuatf)]
psmove_dll.PSM_GetControllerOrientation.restype = ctypes.c_int

class PSMoveMouseController:
    def __init__(self):
        print("Initializing PSMoveMouseController...")
        self.sensitivity = 1.0
        self.running = True
        
        result = psmove_dll.PSM_Initialize(b"localhost", b"9512", 1000)
        print(f"PSM_Initialize result: {result}")
        if result != 0:
            print(f"Failed to initialize PSMove client. Error code: {result}")
            exit(1)
        
        controller_list = self.get_controller_list()
        if not controller_list:
            print("No controllers found or failed to get controller list")
            psmove_dll.PSM_Shutdown()
            exit(1)
        
        self.controller_id = controller_list[0]
        print(f"Using controller ID: {self.controller_id}")
        
        result = psmove_dll.PSM_AllocateControllerListener(self.controller_id)
        print(f"PSM_AllocateControllerListener result: {result}")
        if result != 0:
            print(f"Failed to allocate controller listener. Error code: {result}")
            psmove_dll.PSM_Shutdown()
            exit(1)
        
        result = psmove_dll.PSM_StartControllerDataStream(self.controller_id, 0x01 | 0x04, 1000)
        print(f"PSM_StartControllerDataStream result: {result}")
        if result != 0:
            print(f"Failed to start controller data stream. Error code: {result}")
            psmove_dll.PSM_Shutdown()
            exit(1)
        
        # 虚拟屏幕参数
        self.screen_distance = 0.5  # 虚拟屏幕距离控制器的距离（米）
        self.screen_width = 0.5  # 虚拟屏幕宽度（米）
        self.screen_height = 0.3  # 虚拟屏幕高度（米）
        
        # 获取实际屏幕分辨率
        self.screen_res_x, self.screen_res_y = pyautogui.size()
        
        # 平滑过滤器
        self.position_history = deque(maxlen=5)
        
        # 更新频率控制
        self.update_interval = 0.005  # 5ms
        self.last_update_time = 0
        
		# 插值移动
        self.current_position = np.array([self.screen_res_x / 2, self.screen_res_y / 2])
        self.target_position = self.current_position.copy()

        self.frame_count = 0
        self.last_fps_print_time = time.time()

        print("PSMoveMouseController initialized successfully")

        print("PSMoveMouseController initialized successfully")
    
    def get_controller_list(self):
        controller_list = PSMControllerList()
        result = psmove_dll.PSM_GetControllerList(ctypes.byref(controller_list), 1000)
        print(f"PSM_GetControllerList result: {result}")
        
        if result != 0:
            print(f"Failed to get controller list. Error code: {result}")
            return []
        
        print(f"Controller count: {controller_list.count}")
        return [controller_list.controller_id[i] for i in range(controller_list.count)]

    def get_controller_orientation(self):
        orientation = PSMQuatf()
        result = psmove_dll.PSM_GetControllerOrientation(self.controller_id, ctypes.byref(orientation))
        if result == 0:  # PSMResult_Success
            return orientation
        return None

    def quaternion_to_vector(self, q):
        # 将四元数转换为指向控制器前方的单位向量
        x = 2 * (q.x * q.z - q.w * q.y)
        y = 2 * (q.y * q.z + q.w * q.x)
        z = 1 - 2 * (q.x * q.x + q.y * q.y)
        return np.array([x, y, z])

    def ray_plane_intersection(self, ray_direction):
        # 假设控制器位置为原点 (0, 0, 0)
        # 虚拟屏幕平面方程：z = screen_distance
        t = self.screen_distance / ray_direction[2]
        intersection = t * ray_direction
        return intersection

    def intersection_to_screen_coords(self, intersection):
        # 将交点映射到屏幕坐标
        x = (intersection[0] / self.screen_width + 0.5) * self.screen_res_x
        y = (-intersection[1] / self.screen_height + 0.5) * self.screen_res_y
        return int(x), int(y)

    def smooth_position(self, new_position):
        self.position_history.append(new_position)
        return np.mean(self.position_history, axis=0)

    def interpolate_position(self, current, target, factor=0.4):
        return current + (target - current) * factor

    def run(self):
        print("Starting controller loop...")
        while self.running:
            start_time = time.time()
            
            try:
                result = psmove_dll.PSM_Update()
                if result != 0:
                    continue

                orientation = self.get_controller_orientation()
                if orientation:
                    direction = self.quaternion_to_vector(orientation)
                    intersection = self.ray_plane_intersection(direction)
                    x, y = self.intersection_to_screen_coords(intersection)
                    
                    smooth_x, smooth_y = self.smooth_position(np.array([x, y]))
                    self.target_position = np.array([smooth_x, smooth_y])
                    
                    current_time = time.time()
                    if current_time - self.last_update_time >= self.update_interval:
                        self.current_position = self.interpolate_position(self.current_position, self.target_position)
                        pyautogui.moveTo(int(self.current_position[0]), int(self.current_position[1]))
                        self.last_update_time = current_time

                # 性能监控
                self.frame_count += 1
                if current_time - self.last_fps_print_time >= 1.0:
                    fps = self.frame_count / (current_time - self.last_fps_print_time)
                    print(f"FPS: {fps:.2f}")
                    self.frame_count = 0
                    self.last_fps_print_time = current_time

            except Exception as e:
                print(f"Error in controller loop: {e}")
            
            elapsed_time = time.time() - start_time
            sleep_time = max(0.001, 0.01 - elapsed_time)
            time.sleep(sleep_time)

        print("Controller loop ended")

    def stop(self):
        print("Stopping PSMoveMouseController...")
        self.running = False
        psmove_dll.PSM_Shutdown()
        print("PSMoveMouseController stopped")

    def set_sensitivity(self, value):
        self.sensitivity = float(value)


class SettingsGUI:
    def __init__(self, controller):
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("PS Move Mouse Controller Settings")
        self.root.geometry("300x200")
        
        self.sensitivity_label = tk.Label(self.root, text="Sensitivity", font=("Arial", 14))
        self.sensitivity_label.pack(pady=10)
        
        self.sensitivity_scale = tk.Scale(self.root, from_=0.1, to=2.0, resolution=0.1,
                                          orient=tk.HORIZONTAL, length=200,
                                          command=self.update_sensitivity)
        self.sensitivity_scale.set(1.0)
        self.sensitivity_scale.pack(pady=10)
        
        self.quit_button = tk.Button(self.root, text="Quit", command=self.quit, height=2, width=10)
        self.quit_button.pack(pady=20)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def update_sensitivity(self, value):
        self.controller.set_sensitivity(value)
        
    def quit(self):
        self.on_closing()
        
    def on_closing(self):
        self.controller.stop()
        self.root.quit()
        self.root.destroy()
        os._exit(0)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        print("Starting PS Move Mouse Controller...")
        controller = PSMoveMouseController()
        settings = SettingsGUI(controller)
        
        print("Starting controller thread...")
        controller_thread = threading.Thread(target=controller.run)
        controller_thread.daemon = True
        controller_thread.start()
        
        print("Starting GUI...")
        settings.run()
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Shutting down PSMove client...")
        if 'controller' in locals():
            controller.stop()
        print("PSMove client shut down")
        os._exit(0)