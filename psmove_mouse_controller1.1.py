import ctypes
import os
import pyautogui
import tkinter as tk
import threading
import time

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
class PSMQuatf(ctypes.Structure):
    _fields_ = [("w", ctypes.c_float),
                ("x", ctypes.c_float),
                ("y", ctypes.c_float),
                ("z", ctypes.c_float)]

class PSMVector3f(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float),
                ("y", ctypes.c_float),
                ("z", ctypes.c_float)]

class PSMPosef(ctypes.Structure):
    _fields_ = [("Orientation", PSMQuatf),
                ("Position", PSMVector3f)]

class PSMPSMove(ctypes.Structure):
    _fields_ = [
        ("Pose", PSMPosef),
        ("MoveButton", ctypes.c_int),
    ]

class PSMControllerState(ctypes.Union):
    _fields_ = [("PSMoveState", PSMPSMove)]

class PSMController(ctypes.Structure):
    _fields_ = [
        ("ControllerID", ctypes.c_int),
        ("ControllerType", ctypes.c_int),
        ("ControllerHand", ctypes.c_int),
        ("ControllerState", PSMControllerState),
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

# 定义函数参数类型和返回类型
psmove_dll.PSM_Initialize.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
psmove_dll.PSM_Initialize.restype = ctypes.c_int

psmove_dll.PSM_GetControllerList.argtypes = [ctypes.POINTER(PSMControllerList), ctypes.c_int]
psmove_dll.PSM_GetControllerList.restype = ctypes.c_int

psmove_dll.PSM_StartControllerDataStream.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
psmove_dll.PSM_StartControllerDataStream.restype = ctypes.c_int

psmove_dll.PSM_GetController.argtypes = [ctypes.c_int]
psmove_dll.PSM_GetController.restype = ctypes.POINTER(PSMController)

psmove_dll.PSM_Shutdown.argtypes = []
psmove_dll.PSM_Shutdown.restype = ctypes.c_int

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
            exit(1)
        
        self.controller_id = controller_list[0]
        print(f"Using controller ID: {self.controller_id}")
        
        result = psmove_dll.PSM_StartControllerDataStream(self.controller_id, 0x01 | 0x04, 1000)
        print(f"PSM_StartControllerDataStream result: {result}")
        if result != 0:
            print(f"Failed to start controller data stream. Error code: {result}")
            exit(1)
        
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
    
    def run(self):
        print("Starting controller loop...")
        while self.running:
            try:
                controller = psmove_dll.PSM_GetController(self.controller_id)
                if controller:
                    orientation = controller.contents.ControllerState.PSMoveState.Pose.Orientation
                    print(f"Orientation: w={orientation.w:.2f}, x={orientation.x:.2f}, y={orientation.y:.2f}, z={orientation.z:.2f}")
                    
                    # 使用 y 和 z 分量来移动鼠标
                    dx = int(orientation.y * self.sensitivity * 100)
                    dy = int(orientation.z * self.sensitivity * 100)
                    print(f"Attempting to move mouse: dx={dx}, dy={dy}")
                    pyautogui.moveRel(dx, dy, duration=0.1)
                    
                    button_state = controller.contents.ControllerState.PSMoveState.MoveButton
                    print(f"Move button state: {button_state}")
                    if button_state == 0x01:  # PSMButtonState_PRESSED
                        print("Click!")
                        pyautogui.click()
                else:
                    print("Failed to get controller data")
            except Exception as e:
                print(f"Error in controller loop: {e}")
            
            time.sleep(0.05)
        print("Controller loop ended")
    
    def set_sensitivity(self, value):
        self.sensitivity = float(value)
    
    def stop(self):
        self.running = False
        psmove_dll.PSM_Shutdown()

class SettingsGUI:
    def __init__(self, controller):
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("PS Move Mouse Controller Settings")
        self.root.geometry("300x200")  # 设置窗口大小
        
        self.sensitivity_label = tk.Label(self.root, text="Sensitivity", font=("Arial", 14))
        self.sensitivity_label.pack(pady=10)
        
        self.sensitivity_scale = tk.Scale(self.root, from_=0.1, to=2.0, resolution=0.1,
                                          orient=tk.HORIZONTAL, length=200,
                                          command=self.update_sensitivity)
        self.sensitivity_scale.set(1.0)
        self.sensitivity_scale.pack(pady=10)
        
        self.quit_button = tk.Button(self.root, text="Quit", command=self.quit, height=2, width=10)
        self.quit_button.pack(pady=20)
        
    def update_sensitivity(self, value):
        self.controller.set_sensitivity(value)
        
    def quit(self):
        self.controller.stop()
        self.root.quit()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        print("Starting PS Move Mouse Controller...")
        controller = PSMoveMouseController()
        settings = SettingsGUI(controller)
        
        print("Starting controller thread...")
        controller_thread = threading.Thread(target=controller.run)
        controller_thread.start()
        
        print("Starting GUI...")
        settings.run()
        
        print("Waiting for controller thread to finish...")
        controller_thread.join()
        print("Controller thread finished")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Shutting down PSMove client...")
        psmove_dll.PSM_Shutdown()
        print("PSMove client shut down")