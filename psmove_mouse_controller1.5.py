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
from numba import jit
from ctypes import windll, Structure, c_long, byref
from enum import IntEnum


class PSMButtonState(IntEnum):
    UP = 0
    PRESSED = 1
    DOWN = 2
    RELEASED = 3

# 定义常量
MOUSEEVENTF_MOVE = 0x0001
# 控制器类型常量
PSMController_Move = 0
PSMController_Navi = 1
PSMController_Virtual = 2

class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

# 加载user32.dll
user32 = windll.user32

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
        self.sensitivity = 1.0
        self.running = True

        self.select_button_press_time = 0
        self.select_button_request_sent = False
        self.last_select_button_state = PSMButtonState.UP

        # 缓存屏幕分辨率
        self.screen_res_x, self.screen_res_y = pyautogui.size()

        self.screen_center_x = self.screen_res_x // 2
        self.screen_center_y = self.screen_res_y // 2

        result = psmove_dll.PSM_Initialize(b"localhost", b"9512", 1000)
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
        
        result = psmove_dll.PSM_StartControllerDataStream(self.controller_id, 0x00 | 0x01 | 0x04, 1000)
        print(f"PSM_StartControllerDataStream result: {result}")
        if result != 0:
            print(f"Failed to start controller data stream. Error code: {result}")
            psmove_dll.PSM_Shutdown()
            exit(1)
        
        # 虚拟屏幕参数
        self.screen_distance = 0.5  # 虚拟屏幕距离控制器的距离（米）
        self.screen_width = 0.5  # 虚拟屏幕宽度（米）
        self.screen_height = 0.4  # 虚拟屏幕高度（米）
        
        # 更新频率控制
        self.update_interval = 0.005  # 10ms
        self.last_update_time = 0
        
        # 使用deque作为平滑过滤器
        self.position_history = deque(maxlen=3)
        
        # 预分配numpy数组
        self.current_position = np.array([self.screen_res_x / 2, self.screen_res_y / 2], dtype=np.float32)
        self.target_position = self.current_position.copy()

        # 性能监控
        self.frame_count = 0
        self.last_fps_print_time = time.perf_counter()
        
        # 鼠标移动控制
        self.mouse_update_interval = 1 / 120  # 60Hz
        self.last_mouse_update_time = 0

#        print("PSMoveMouseController initialized successfully")

    def process_select_button_action(self, controller):
        current_time = int(time.time() * 1000)  # 当前时间（毫秒）

        # 根据控制器类型获取正确的按钮状态
        if controller.ControllerType == PSMController_Move:
            select_button_state = controller.ControllerState.PSMoveState.SelectButton
        else:
            print(f"Unsupported controller type: {controller.ControllerType}")
            return

        print(f"Raw Select button state: {select_button_state}")
        # 将原始状态映射到我们的枚举
        if select_button_state == 0:
            mapped_state = PSMButtonState.UP
        elif select_button_state == 1:
            mapped_state = PSMButtonState.PRESSED
        elif select_button_state == 2:
            mapped_state = PSMButtonState.DOWN
        elif select_button_state == 3:
            mapped_state = PSMButtonState.RELEASED
        else:
            print(f"Unknown button state: {select_button_state}")
            return
    
        if mapped_state != self.last_select_button_state:
            print(f"Select button state changed from {self.last_select_button_state} to {mapped_state}")
    
            if mapped_state == PSMButtonState.PRESSED:
                print("Select button PRESSED")
                self.select_button_press_time = current_time
            elif mapped_state == PSMButtonState.DOWN:
                print("Select button held DOWN")
                if not self.select_button_request_sent:
                    press_duration = current_time - self.select_button_press_time
                    if press_duration >= 250:  # 250毫秒
                        print("Select button held for 250ms")
                        self.move_mouse_to_center()
                        self.select_button_request_sent = True
            elif mapped_state == PSMButtonState.RELEASED:
                print("Select button RELEASED")
                self.select_button_request_sent = False
    
        self.last_select_button_state = mapped_state

    def move_mouse_to_center(self):
        center_x = self.screen_res_x // 2
        center_y = self.screen_res_y // 2
        self.move_mouse_abs(center_x, center_y)
        self.current_position = np.array([center_x, center_y], dtype=np.float32)
        self.target_position = self.current_position.copy()
        print(f"Moving mouse to center: ({center_x}, {center_y})")
		
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

    def print_controller_info(self, controller):
        print("控制器信息:")
        print(f"  控制器ID: {controller.ControllerID}")
        print(f"  控制器类型: {controller.ControllerType}")
        print(f"  控制器手持方式: {controller.ControllerHand}")
        print(f"  是否有效: {controller.bValid}")
        print(f"  是否已连接: {controller.IsConnected}")
        print("PSMove State:")
        psmove_state = controller.ControllerState.PSMoveState
        print(f"  Select Button: {psmove_state.SelectButton}")
        print(f"  Start Button: {psmove_state.StartButton}")
        print(f"  PS Button: {psmove_state.PSButton}")
        print(f"  Move Button: {psmove_state.MoveButton}")
        print(f"  Triangle Button: {psmove_state.TriangleButton}")

    @staticmethod
    def move_mouse(dx, dy):
        # 获取当前鼠标位置
        point = POINT()
        user32.GetCursorPos(byref(point))
        
        # 计算新位置
        x = point.x + int(dx)
        y = point.y + int(dy)
        
        # 移动鼠标
        user32.mouse_event(MOUSEEVENTF_MOVE, dx, dy, 0, 0)

    @staticmethod
    @jit(nopython=True)
    def quaternion_to_vector(w, x, y, z):
        x_vec = 2 * (x * z - w * y)
        y_vec = 2 * (y * z + w * x)
        z_vec = 1 - 2 * (x * x + y * y)
        return np.array([x_vec, y_vec, z_vec])

    @staticmethod
    @jit(nopython=True)
    def ray_plane_intersection(ray_direction, screen_distance):
        t = screen_distance / ray_direction[2]
        return t * ray_direction

    @staticmethod
    @jit(nopython=True)
    def intersection_to_screen_coords(intersection, screen_width, screen_height, screen_res_x, screen_res_y):
        x = (intersection[0] / screen_width + 0.5) * screen_res_x
        y = (-intersection[1] / screen_height + 0.5) * screen_res_y
        return x, y

    def smooth_position(self, new_position):
        self.position_history.append(new_position)
        return np.mean(self.position_history, axis=0)

    @staticmethod
    @jit(nopython=True)
    def interpolate_position(current, target, factor=0.6):
        return current + (target - current) * factor


    @staticmethod
    def move_mouse_abs(x, y):
        # 移动鼠标到绝对位置
        ctypes.windll.user32.SetCursorPos(int(x), int(y))


    def run(self):
        print("Starting controller loop...")
        check_interval = 5  # 每5秒检查一次
        last_check_time = time.time()

        last_x, last_y = self.screen_res_x // 2, self.screen_res_y // 2
		
        while self.running:
            #start_time = time.perf_counter()
            try:
                current_time = time.time()
				
                result = psmove_dll.PSM_Update()
                if result != 0:
                    continue

				# 获取控制器状态
                controller = psmove_dll.PSM_GetController(self.controller_id)
                print(f"kong制器类型: {controller.contents.ControllerType}")

                if not controller:
                    continue

                if controller.contents.ControllerType == PSMController_Move:  # PSMove 控制器
                    orientation = controller.contents.ControllerState.PSMoveState.Pose.Orientation
                    position = controller.contents.ControllerState.PSMoveState.Pose.Position
                    #buttons = controller.contents.ControllerState.PSMoveState.Buttons
                else:
                    print(f"不支持的控制器类型: {controller.contents.ControllerType}")
                    continue

                # 检查多个按钮的状态
                select_state = controller.contents.ControllerState.PSMoveState.SelectButton
                start_state = controller.contents.ControllerState.PSMoveState.StartButton
                square_state = controller.contents.ControllerState.PSMoveState.SquareButton
                move_state = controller.contents.ControllerState.PSMoveState.MoveButton
                trigger_state = controller.contents.ControllerState.PSMoveState.TriggerButton
                
                print(f"Button states - Select: {select_state}, Start: {start_state}, Square: {square_state}, Move: {move_state}, Trigger: {trigger_state}")


                # 处理 Select 按钮动作
                self.process_select_button_action(controller.contents)

                # 周期性检查按钮状态
                if current_time - last_check_time >= check_interval:
                    print(f"Periodic check - Select button state: {controller.contents.ControllerState.PSMoveState.SelectButton}")
                    last_check_time = current_time

                orientation = self.get_controller_orientation()
                if orientation:
                    direction = self.quaternion_to_vector(orientation.w, orientation.x, orientation.y, orientation.z)
                    intersection = self.ray_plane_intersection(direction, self.screen_distance)
                    x, y = self.intersection_to_screen_coords(intersection, self.screen_width, self.screen_height, self.screen_res_x, self.screen_res_y)
                    
                    smooth_pos = self.smooth_position(np.array([x, y], dtype=np.float32))
                    self.target_position = smooth_pos
                    
                    current_time = time.perf_counter()
                    if current_time - self.last_mouse_update_time >= self.mouse_update_interval:
                        self.current_position = self.interpolate_position(self.current_position, self.target_position)
                        new_x, new_y = int(self.current_position[0]), int(self.current_position[1])
                        dx, dy = new_x - last_x, new_y - last_y
                        self.move_mouse(dx, dy)
                        last_x, last_y = new_x, new_y
                        self.last_mouse_update_time = current_time

                # 性能监控
                self.frame_count += 1
                if current_time - self.last_fps_print_time >= 5.0:
                    fps = self.frame_count / (current_time - self.last_fps_print_time)
                    print(f"FPS: {fps:.2f}")
                    self.frame_count = 0
                    self.last_fps_print_time = current_time

            except Exception as e:
                print(f"Error in controller loop: {e}")
                import traceback
                traceback.print_exc()
				
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