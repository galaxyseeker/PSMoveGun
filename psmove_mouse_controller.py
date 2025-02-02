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


class PSMoveMouseController:
    def __init__(self):
        self.sensitivity = 1.0
        self.running = True
        
        # 初始化PSMoveService客户端
        result = psmove_dll.PSM_Initialize(b"localhost", b"9512", 1000)
        if result != 0:  # PSMResult_Success
            print("Failed to initialize PSMove client")
            exit(1)
        
        # 获取控制器列表
        controller_list = self.get_controller_list()
        if len(controller_list) == 0:
            print("No controllers found")
            exit(1)
        
        self.controller_id = controller_list[0]
        
        # 启动控制器数据流
        result = psmove_dll.PSM_StartControllerDataStream(self.controller_id, 0x01 | 0x04, 1000)
        if result != 0:
            print("Failed to start controller data stream")
            exit(1)
        
    def get_controller_list(self):
        class PSMControllerList(ctypes.Structure):
            _fields_ = [("controller_id", ctypes.c_int * 4),
                        ("controller_type", ctypes.c_int * 4),
                        ("count", ctypes.c_int)]
        
        controller_list = PSMControllerList()
        result = psmove_dll.PSM_GetControllerList(ctypes.byref(controller_list), 1000)
        if result != 0:
            return []
        return [controller_list.controller_id[i] for i in range(controller_list.count)]
    
    def run(self):
        while self.running:
            controller = psmove_dll.PSM_GetController(self.controller_id)
            if controller:
                # 读取方向数据
                orientation = controller.contents.ControllerState.PSMoveState.Pose.Orientation
                
                # 使用方向数据移动鼠标
                dx = int(orientation.x * self.sensitivity * 10)
                dy = int(orientation.y * self.sensitivity * 10)
                pyautogui.moveRel(dx, dy)
                
                # 检查按钮状态
                if controller.contents.ControllerState.PSMoveState.MoveButton == 0x01:  # PSMButtonState_PRESSED
                    pyautogui.click()
            
            time.sleep(0.01)
    
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
        
        self.sensitivity_scale = tk.Scale(self.root, from_=0.1, to=2.0, resolution=0.1,
                                          orient=tk.HORIZONTAL, label="Sensitivity",
                                          command=self.update_sensitivity)
        self.sensitivity_scale.set(1.0)
        self.sensitivity_scale.pack()
        
        self.quit_button = tk.Button(self.root, text="Quit", command=self.quit)
        self.quit_button.pack()
        
    def update_sensitivity(self, value):
        self.controller.set_sensitivity(value)
        
    def quit(self):
        self.controller.stop()
        self.root.quit()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    controller = PSMoveMouseController()
    settings = SettingsGUI(controller)
    
    controller_thread = threading.Thread(target=controller.run)
    controller_thread.start()
    
    settings.run()
    
    controller_thread.join()