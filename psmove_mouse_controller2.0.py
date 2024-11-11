"""
PS Move 鼠标控制器 v2.0

基于新的已经解决了所有引用问题的PSMoveService库，实现PSMove对鼠标的控制。

重写所有代码。

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
import psmove_data_fetcher

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
        self.data_fetcher = psmove_data_fetcher.PSMoveDataFetcher()
        if not self.data_fetcher.initialize():
            LoggerUtil.error("Failed to initialize PS Move Data Fetcher.")
            raise Exception("No PS Move controller found.")
        LoggerUtil.info("PS Move Data Fetcher initialized successfully.")

    def run(self):
        LoggerUtil.info("Starting data collection...")
        while True:
            try:
                pose_data = self.data_fetcher.get_pose_data()
                orientation = pose_data['orientation']
                position = pose_data['position']

                LoggerUtil.info(f"Orientation: w={orientation['w']:.2f}, x={orientation['x']:.2f}, "
                                f"y={orientation['y']:.2f}, z={orientation['z']:.2f}")
                LoggerUtil.info(f"Position: x={position['x']:.2f}, y={position['y']:.2f}, z={position['z']:.2f}")

                time.sleep(0.01)  # 短暂延迟以避免日志过多

            except Exception as e:
                LoggerUtil.error(f"Error in data collection loop: {e}")

    def stop(self):
        LoggerUtil.info("Stopping PS Move controller...")
        # 清理工作（如果需要）
        LoggerUtil.info("PS Move controller stopped.")

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
