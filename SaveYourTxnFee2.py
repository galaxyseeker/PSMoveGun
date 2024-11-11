import tkinter as tk
from PIL import Image, ImageTk
import os
import glob
import random
from settings import BG_IMAGE_PATH_PATTERN

def get_random_background():
    bg_images = glob.glob(BG_IMAGE_PATH_PATTERN)
    if not bg_images:
        raise FileNotFoundError(f"No background images found matching pattern: {BG_IMAGE_PATH_PATTERN}")
    return random.choice(bg_images)

# 创建主窗口
root = tk.Tk()
root.title("AlexXu的证券服务商交易佣金计算器")

# 计算黄金比例的窗口大小
width = 800
height = int(width * 0.8)  # 使用黄金比例
root.geometry(f"{width}x{height}")

# 设置窗口大小不可调整
root.resizable(False, False)

# 随机选择并加载背景图片
try:
    bg_image_path = get_random_background()
    bg_image = Image.open(bg_image_path)
    bg_image = bg_image.resize((width, height), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)

    # 创建一个标签来显示背景图片
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
except FileNotFoundError as e:
    print(f"Error: {e}")
    # 如果找不到背景图片，使用纯色背景
    root.configure(bg='lightgray')

# 运行主循环
root.mainloop()
