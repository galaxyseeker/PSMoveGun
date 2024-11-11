"""
PS Move 鼠标控制器 v1.6

当前版本正在解决的问题：
1. 鼠标移动的优化，特别是处理移动出屏幕的情况。
2. 将一些结构体和函数进行封装，放入到工具文件和类中。

尚未解决的问题：
1. 按键事件的处理仍需完善。

TODO:
1. 改进按键事件处理逻辑。
2. 进一步优化鼠标移动的平滑度和精确度。
3. 实现当控制器指向超出屏幕边缘时停止移动鼠标，并在控制器指向回到屏幕范围内时从新位置继续移动。
"""

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
import numpy as np
from psmove_logger_util import LoggerUtil
from psmove_structures import (
    PSMVector2f, PSMVector3f, PSMQuatf, PSMPosef, PSMPSMoveCalibratedSensorData,
    PSMTrackingProjection, PSMRawTrackerData, PSMPhysicsData, PSMPSMove,
    PSMControllerState, PSMController, PSMControllerList, PSMOVESERVICE_MAX_CONTROLLER_COUNT,
    PSMOVESERVICE_CONTROLLER_SERIAL_LEN
)

# 在文件开头设置日志
LoggerUtil.setup_logger()

# 在整个文件中，将所有的 print 语句替换为相应的日志调用
# 例如：
# print("Error message") 变为 LoggerUtil.error("Error message")
# print("Warning message") 变为 LoggerUtil.warning("Warning message")
# print("Info message") 变为 LoggerUtil.info("Info message")
# print("Debug message") 变为 LoggerUtil.debug("Debug message")

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
    LoggerUtil.error(f"Error loading PSMoveClient_CAPI.dll: {e}")
    exit(1)

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
            LoggerUtil.error(f"Failed to initialize PSMove client. Error code: {result}")
            exit(1)
        
        controller_list = self.get_controller_list()
        if not controller_list:
            LoggerUtil.warning("No controllers found or failed to get controller list")
            psmove_dll.PSM_Shutdown()
            exit(1)
        
        self.controller_id = controller_list[0]
        LoggerUtil.info(f"Using controller ID: {self.controller_id}")
        
        result = psmove_dll.PSM_AllocateControllerListener(self.controller_id)
        LoggerUtil.info(f"PSM_AllocateControllerListener result: {result}")
        if result != 0:
            LoggerUtil.error(f"Failed to allocate controller listener. Error code: {result}")
            psmove_dll.PSM_Shutdown()
            exit(1)
        
        result = psmove_dll.PSM_StartControllerDataStream(self.controller_id, 0x00 | 0x01 | 0x04, 1000)
        LoggerUtil.info(f"PSM_StartControllerDataStream result: {result}")
        if result != 0:
            LoggerUtil.error(f"Failed to start controller data stream. Error code: {result}")
            psmove_dll.PSM_Shutdown()
            exit(1)
        
        # 虚拟屏幕参数
        self.screen_distance = 0.4  # 减小虚拟屏幕距离（米）
        self.screen_width = 0.6  # 增加虚拟屏幕宽度（米）
        self.screen_height = 0.45  # 增加虚拟屏幕高度（米）
        
        # 更新频率控制
        self.update_interval = 0.005  # 10ms
        self.last_update_time = 0
        
        # 使用deque作为平滑过滤器
        self.position_history = deque(maxlen=5)  # 减少历史记录长度以获得更快的响应
        
        # 预分配numpy数组
        self.current_position = np.array([self.screen_res_x / 2, self.screen_res_y / 2], dtype=np.float32)
        self.target_position = self.current_position.copy()

        # 性能监控
        self.frame_count = 0
        self.last_fps_print_time = time.perf_counter()
        
        # 鼠标移动控制
        self.mouse_update_interval = 1 / 120  # 60Hz
        self.last_mouse_update_time = 0

        # 添加鼠标移动阈值
        self.mouse_move_threshold = 0.2  # 像素
        
        # 添加低通滤波器参数
        self.filter_weight = 0.3  # 增加滤波器权重以获得更快的响应

        # 添加死区
        self.deadzone = 1  # 减小死区以允许更小的移动

        # 调整平滑参数
        self.interpolation_factor = 0.2  # 增加插值因子以获得更快的响应

        # 调整参数
        self.sensitivity_x = 10.0  # 增加水平灵敏度
        self.sensitivity_y = 8.0   # 增加垂直灵敏度
        self.deadzone = 0.05       # 减小死区
        self.mouse_move_threshold = 0.01  # 减小移动阈值
        self.stabilization_time = 0.1  # 减少稳定时间

        # 添加初始稳定时间
        self.stabilization_time = 1.0  # 1秒的稳定时间
        self.start_time = time.time()

        # 添加检查间隔
        self.check_interval = 5  # 每5秒检查一次
        self.last_check_time = time.time()

    def process_select_button_action(self, controller):
        current_time = int(time.time() * 1000)  # 当前时间（毫秒）

        # 根据控制器类型获取正确的按钮状态
        if controller.ControllerType == PSMController_Move:
            select_button_state = controller.ControllerState.PSMoveState.SelectButton
        else:
            LoggerUtil.warning(f"Unsupported controller type: {controller.ControllerType}")
            return

        LoggerUtil.debug(f"Raw Select button state: {select_button_state}")
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
            LoggerUtil.warning(f"Unknown button state: {select_button_state}")
            return
    
        if mapped_state != self.last_select_button_state:
            LoggerUtil.debug(f"Select button state changed from {self.last_select_button_state} to {mapped_state}")
    
            if mapped_state == PSMButtonState.PRESSED:
                LoggerUtil.debug("Select button PRESSED")
                self.select_button_press_time = current_time
            elif mapped_state == PSMButtonState.DOWN:
                LoggerUtil.debug("Select button held DOWN")
                if not self.select_button_request_sent:
                    press_duration = current_time - self.select_button_press_time
                    if press_duration >= 250:  # 250毫秒
                        LoggerUtil.debug("Select button held for 250ms")
                        self.move_mouse_to_center()
                        self.select_button_request_sent = True
            elif mapped_state == PSMButtonState.RELEASED:
                LoggerUtil.debug("Select button RELEASED")
                self.select_button_request_sent = False
    
        self.last_select_button_state = mapped_state

    def move_mouse_to_center(self):
        center_x = self.screen_res_x // 2
        center_y = self.screen_res_y // 2
        self.move_mouse_abs(center_x, center_y)
        self.current_position = np.array([center_x, center_y], dtype=np.float32)
        self.target_position = self.current_position.copy()
        LoggerUtil.debug(f"Moving mouse to center: ({center_x}, {center_y})")
		
    def get_controller_list(self):
        controller_list = PSMControllerList()
        result = psmove_dll.PSM_GetControllerList(ctypes.byref(controller_list), 1000)
        LoggerUtil.info(f"PSM_GetControllerList result: {result}")
        
        if result != 0:
            LoggerUtil.error(f"Failed to get controller list. Error code: {result}")
            return []
        
        LoggerUtil.info(f"Controller count: {controller_list.count}")
        return [controller_list.controller_id[i] for i in range(controller_list.count)]

    def get_controller_orientation(self):
        orientation = PSMQuatf()
        result = psmove_dll.PSM_GetControllerOrientation(self.controller_id, ctypes.byref(orientation))
        if result == 0:  # PSMResult_Success
            return orientation
        LoggerUtil.warning(f"Failed to get controller orientation. Result: {result}")
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
        LoggerUtil.debug(f"Mouse moved by ({dx}, {dy})")

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
    def interpolate_position(current, target, factor=0.2):
        return current + (target - current) * factor

    @staticmethod
    def move_mouse_abs(x, y):
        # 移动鼠标到绝对位置
        ctypes.windll.user32.SetCursorPos(int(x), int(y))

    def update_mouse_position(self, x, y):
        # 应用灵敏度
        x = (x - self.screen_res_x / 2) * self.sensitivity_x + self.screen_res_x / 2
        y = (y - self.screen_res_y / 2) * self.sensitivity_y + self.screen_res_y / 2

        # 使用平滑算法而不是卡尔曼滤波器
        new_position = np.array([x, y])
        smoothed_position = self.smooth_position(new_position)
        
        filtered_x, filtered_y = smoothed_position

        LoggerUtil.debug(f"Raw: ({x:.2f}, {y:.2f}), Filtered: ({filtered_x:.2f}, {filtered_y:.2f})")

        return filtered_x, filtered_y

    def run(self):
        LoggerUtil.info("Starting controller loop...")
        check_interval = 5  # 每5秒检查一次
        last_check_time = time.time()

        last_x, last_y = self.screen_res_x // 2, self.screen_res_y // 2
        
        while self.running:
            try:
                current_time = time.time()
				
                result = psmove_dll.PSM_Update()
                if result != 0:
                    LoggerUtil.warning(f"PSM_Update failed with result: {result}")
                    continue

				# 获取控制器状态
                controller = psmove_dll.PSM_GetController(self.controller_id)
                if not controller:
                    LoggerUtil.warning("Failed to get controller")
                    continue

                LoggerUtil.debug(f"Controller type: {controller.contents.ControllerType}")

                if controller.contents.ControllerType == PSMController_Move:
                    orientation = controller.contents.ControllerState.PSMoveState.Pose.Orientation
                    position = controller.contents.ControllerState.PSMoveState.Pose.Position
                    #buttons = controller.contents.ControllerState.PSMoveState.Buttons
                else:
                    LoggerUtil.warning(f"Unsupported controller type: {controller.contents.ControllerType}")
                    continue

                # 检查多个按钮的状态
                select_state = controller.contents.ControllerState.PSMoveState.SelectButton
                start_state = controller.contents.ControllerState.PSMoveState.StartButton
                square_state = controller.contents.ControllerState.PSMoveState.SquareButton
                move_state = controller.contents.ControllerState.PSMoveState.MoveButton
                trigger_state = controller.contents.ControllerState.PSMoveState.TriggerButton
                
                #print(f"Button states - Select: {select_state}, Start: {start_state}, Square: {square_state}, Move: {move_state}, Trigger: {trigger_state}")


                # 处理 Select 按钮动作
                self.process_select_button_action(controller.contents)

                # 周期性检查按钮状态
                if current_time - self.last_check_time >= self.check_interval:
                    LoggerUtil.info(f"Periodic check - Select button state: {controller.contents.ControllerState.PSMoveState.SelectButton}")
                    self.last_check_time = current_time

                orientation = self.get_controller_orientation()
                if orientation:
                    direction = self.quaternion_to_vector(orientation.w, orientation.x, orientation.y, orientation.z)
                    intersection = self.ray_plane_intersection(direction, self.screen_distance)
                    x, y = self.intersection_to_screen_coords(intersection, self.screen_width, self.screen_height, self.screen_res_x, self.screen_res_y)
                    
                    smooth_pos = self.smooth_position(np.array([x, y], dtype=np.float32))
                    self.target_position = smooth_pos
                    
                    current_time = time.perf_counter()
                    if current_time - self.last_mouse_update_time >= self.mouse_update_interval:
                        self.current_position = self.interpolate_position(self.current_position, self.target_position, self.interpolation_factor)
                        new_x, new_y = int(self.current_position[0]), int(self.current_position[1])
                        dx, dy = new_x - last_x, new_y - last_y
                        self.move_mouse(dx, dy)
                        last_x, last_y = new_x, new_y
                        self.last_mouse_update_time = current_time

                # 性能监控
                self.frame_count += 1
                if current_time - self.last_fps_print_time >= 5.0:
                    fps = self.frame_count / (current_time - self.last_fps_print_time)
                    LoggerUtil.info(f"FPS: {fps:.2f}")
                    self.frame_count = 0
                    self.last_fps_print_time = current_time

            except Exception as e:
                LoggerUtil.error(f"Error in controller loop: {e}")
                import traceback
                LoggerUtil.error(traceback.format_exc())
        
        LoggerUtil.info("Controller loop ended")

    def stop(self):
        LoggerUtil.info("Stopping PSMoveMouseController...")
        self.running = False
        psmove_dll.PSM_Shutdown()
        LoggerUtil.info("PSMoveMouseController stopped")

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
        LoggerUtil.info("Starting PS Move Mouse Controller...")
        controller = PSMoveMouseController()
        settings = SettingsGUI(controller)
        
        LoggerUtil.info("Starting controller thread...")
        controller_thread = threading.Thread(target=controller.run)
        controller_thread.daemon = True
        controller_thread.start()
        
        LoggerUtil.info("Starting GUI...")
        settings.run()
        
    except Exception as e:
        LoggerUtil.error(f"An error occurred: {e}")
        import traceback
        LoggerUtil.error(traceback.format_exc())
    finally:
        LoggerUtil.info("Shutting down PSMove client...")
        if 'controller' in locals():
            controller.stop()
        LoggerUtil.info("PSMove client shut down")
        os._exit(0)