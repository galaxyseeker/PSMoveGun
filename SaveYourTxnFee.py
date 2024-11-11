import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.font import Font
from PIL import Image, ImageTk
import winsound
import os
import pyttsx3
import logging
from datetime import datetime
from prettytable import PrettyTable
import io

# 定义颜色常量
BACKGROUND_COLOR = '#FFC0CB'  # 浅粉色背景
TEXT_COLOR = 'black'  # 文本颜色
HIGHLIGHT_COLOR = 'red'  # 高亮颜色（用于重要数值）
BUTTON_BG_COLOR = '#4CAF50'  # 按钮背景色
BUTTON_FG_COLOR = 'white'  # 按钮文字颜色
BUTTON_ACTIVE_BG_COLOR = '#45a049'  # 按钮激活时的背景色

# 自定义日志格式化器
class TableFormatter(logging.Formatter):
    def format(self, record):
        if isinstance(record.msg, PrettyTable):
            # 将表格转换为字符串
            table_str = record.msg.get_string()
            # 在每行前添加适当的空格，以便与时间戳对齐
            indented_table = '\n'.join(' ' * 26 + line for line in table_str.split('\n'))
            # 组合时间戳和表格
            return f"{self.formatTime(record, self.datefmt)} - \n{indented_table}"
        return super().format(record)

# 设置日志
logger = logging.getLogger('transaction_logger')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('transaction_log.txt', encoding='utf-8')  # 添加 encoding='utf-8'
formatter = TableFormatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# 创建一个表格来存储交易记录
transaction_table = PrettyTable()
transaction_table.field_names = ["时间", "股数", "股价", "每股佣金", "最大佣金%", "是否卖出", "总交易额", "总费用", "费用占比"]

# 初始化 TTS 引擎
engine = pyttsx3.init()

# 设置语音为中文
voices = engine.getProperty('voices')
for voice in voices:
    if "chinese" in voice.name.lower():  # 查找包含 "chinese" 的声音
        engine.setProperty('voice', voice.id)
        break

class ImageButton(tk.Canvas):
    def __init__(self, parent, image_path, width, height, command=None):
        # 增加高度以容纳悬停和点击效果
        super().__init__(parent, width=width, height=height+10, highlightthickness=0, bg=BACKGROUND_COLOR)
        self.command = command
        self.width = width
        self.height = height
        self.normal_position = 5  # 正常位置稍微向下移动
        self.hover_position = 0
        self.click_position = 8

        # 加载并调整图片大小
        self.image = Image.open(image_path)
        self.image = self.image.resize((width, height), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(self.image)

        # 在Canvas上创建图片，确保整个图像都显示
        self.button_image = self.create_image(width/2, self.normal_position, image=self.photo, anchor='n')

        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_click(self, event):
        self.move(self.button_image, 0, self.click_position - self.normal_position)

    def _on_release(self, event):
        self.move(self.button_image, 0, self.normal_position - self.click_position)
        if self.command:
            self.command()
        # 播放音效
        #try:
            #winsound.PlaySound("C:\\Windows\\Media\\chimes.wav", winsound.SND_FILENAME)
        #except:
         #   print("无法播放音效")

    def _on_enter(self, event):
        self.move(self.button_image, 0, self.hover_position - self.normal_position)
        # 播放卡塔声音效
        try:
            winsound.PlaySound(r"C:\Windows\Media\Windows Navigation Start.wav", winsound.SND_ASYNC)
        except:
            print("无法播放音效")

    def _on_leave(self, event):
        self.move(self.button_image, 0, self.normal_position - self.hover_position)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def calculate_fee(event=None):
    try:
        # 检查是否有空输入
        if not shares_entry.get() or not price_entry.get() or not per_share_fee_entry.get() or not max_fee_percentage_entry.get():
            raise ValueError("请填写所有输入框")

        shares = int(shares_entry.get())
        price = float(price_entry.get())
        per_share_fee = float(per_share_fee_entry.get())
        max_fee_percentage = float(max_fee_percentage_entry.get()) / 100
        is_sell = transaction_type.get()
        
        if shares <= 0 or price <= 0 or per_share_fee < 0 or max_fee_percentage < 0:
            raise ValueError("所有输入必须为正数")
        
        total_value = shares * price
        base_fee = shares * per_share_fee
        
        if base_fee < 2.98:
            fee = 2.98
            formula = "最低佣金: $2.98"
        elif base_fee > total_value * max_fee_percentage:
            fee = total_value * max_fee_percentage
            formula = f"佣金 = 交易总额 * {max_fee_percentage:.2%} = ${fee:.2f}"
        else:
            fee = base_fee
            formula = f"佣金 = 股数 * 每股佣金 = {shares} * ${per_share_fee:.5f} = ${fee:.2f}"
        
        # 计算证监会费用（仅在卖出时）
        sec_fee = 0
        if is_sell:
            sec_fee = max(0.01, total_value * 0.0000278)
            formula += f"\n证监会费用 = (0.01USD)或者(交易总额 * 0.0000278)中间的大者 = ${sec_fee:.2f}"
        
        total_fee = fee + sec_fee
        
        result_label.config(text=f"总交易费用: ", font=("Arial", 14, "bold"))
        result_amount_label.config(text=f"${total_fee:.2f}", font=("Arial", 14, "bold"), foreground=HIGHLIGHT_COLOR)
        
        formula_label.config(text=f"计算公式:\n{formula}")
        
        # 计算佣金占总交易额的百分比
        fee_percentage = (total_fee / total_value) * 100
        percentage_label.config(text=f"费用占比: ")
        percentage_amount_label.config(text=f"{fee_percentage:.4f}%", foreground=HIGHLIGHT_COLOR)
        
        # 显示交易总额
        total_value_label.config(text=f"交易总额: ")
        total_value_amount_label.config(text=f"${total_value:.2f}", foreground=HIGHLIGHT_COLOR)
        
        # 更新界面
        root.update()
        
        # 使用 TTS 朗读结果
        speak(f"总交易费用为 {total_fee:.4f} 美元，占交易总额的 {fee_percentage:.4f}%")
        
        # 添加记录到表格
        transaction_table.add_row([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            shares,
            f"${price:.2f}",
            f"${per_share_fee:.5f}",
            f"{max_fee_percentage*100:.2f}%",
            "是" if is_sell else "否",
            f"${total_value:.2f}",
            f"${total_fee:.2f}",
            f"{fee_percentage:.4f}%"
        ])
        
        # 将表格输出到日志文件
        logger.info(transaction_table)
        
    except ValueError as e:
        if str(e) == "invalid literal for int() with base 10: ''":
            error_message = "请输入有效的数字"
        else:
            error_message = str(e)
        messagebox.showerror("输入错误", error_message)
        speak("输入错误，请检查您的输入")
    except Exception as e:
        messagebox.showerror("计算错误", f"发生未知错误: {str(e)}")
        speak("计算过程中发生错误")

def on_escape(event):
    root.quit()

# 创建主窗口
root = tk.Tk()
root.title("AlexXu的证券服务商交易佣金计算器")

# 计算黄金比例的窗口大小
width = 800
height = int(width * 0.8)
root.geometry(f"{width}x{height}")

# 设置窗口大小不可调整
root.resizable(False, False)

# 设置背景颜色
root.configure(bg=BACKGROUND_COLOR)

# 创建样式
style = ttk.Style()
style.theme_use('clam')
style.configure('TLabel', background=BACKGROUND_COLOR, foreground=TEXT_COLOR, font=('Arial', 12))
style.configure('TEntry', font=('Arial', 12))
style.configure('TButton', font=('Arial', 12, 'bold'))
style.configure('TFrame', background=BACKGROUND_COLOR)
style.configure('TCheckbutton', background=BACKGROUND_COLOR, foreground=TEXT_COLOR, font=('Arial', 12))

# 自定义按钮样式
style.configure('Accent.TButton', background=BUTTON_BG_COLOR, foreground=BUTTON_FG_COLOR)
style.map('Accent.TButton', background=[('active', BUTTON_ACTIVE_BG_COLOR)])

# 创建主框架来居中内容
main_frame = ttk.Frame(root, padding="20 20 20 20", style='TFrame')
main_frame.pack(expand=True)

# 创建输入框架
input_frame = ttk.Frame(main_frame, padding="10 10 10 10", style='TFrame')
input_frame.pack()

# 创建并放置输入框和标签
shares_label = ttk.Label(input_frame, text="股数:")
shares_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
shares_entry = ttk.Entry(input_frame, width=20)
shares_entry.grid(row=0, column=1, padx=5, pady=5)

price_label = ttk.Label(input_frame, text="股价 (USD):")
price_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
price_entry = ttk.Entry(input_frame, width=20)
price_entry.grid(row=1, column=1, padx=5, pady=5)

per_share_fee_label = ttk.Label(input_frame, text="每股佣金 (USD):")
per_share_fee_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
per_share_fee_entry = ttk.Entry(input_frame, width=20)
per_share_fee_entry.insert(0, "0.01186")  # 默认值
per_share_fee_entry.grid(row=2, column=1, padx=5, pady=5)

max_fee_percentage_label = ttk.Label(input_frame, text="最大佣金百分比 (%):")
max_fee_percentage_label.grid(row=3, column=0, padx=5, pady=5, sticky="e")
max_fee_percentage_entry = ttk.Entry(input_frame, width=20)
max_fee_percentage_entry.insert(0, "2")  # 默认值
max_fee_percentage_entry.grid(row=3, column=1, padx=5, pady=5)

# 添加交易类型选择（复选框）
transaction_type = tk.BooleanVar()
transaction_type_checkbox = ttk.Checkbutton(input_frame, text="卖出交易", variable=transaction_type)
transaction_type_checkbox.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

# 创建计算按钮
calculate_button = ImageButton(main_frame, 
                               r"C:\Users\galax\Desktop\PSMoveGun\Programs\PSMoveGunProj\resource\galaxyseeker_A_line_picture_Buffett_holding_banknotes_in_the_ce_7c99dd80-e204-42cf-94bd-cb6d3598e498.webp", 
                               width=100, height=100, command=calculate_fee)
calculate_button.pack(pady=20)

# 创建结果框架
result_frame = ttk.Frame(main_frame, padding="10 10 10 10", style='TFrame')
result_frame.pack(fill='x')

# 创建结果显示标签
result_label = ttk.Label(result_frame, text="", font=("Arial", 14, "bold"))
result_label.pack(side='left', pady=5)
result_amount_label = ttk.Label(result_frame, text="", font=("Arial", 14, "bold"), foreground=HIGHLIGHT_COLOR)
result_amount_label.pack(side='left', pady=5)

formula_label = ttk.Label(result_frame, text="", wraplength=580)
formula_label.pack(pady=5)

percentage_frame = ttk.Frame(result_frame)
percentage_frame.pack(fill='x')
percentage_label = ttk.Label(percentage_frame, text="")
percentage_label.pack(side='left', pady=5)
percentage_amount_label = ttk.Label(percentage_frame, text="", foreground=HIGHLIGHT_COLOR)
percentage_amount_label.pack(side='left', pady=5)

total_value_frame = ttk.Frame(result_frame)
total_value_frame.pack(fill='x')
total_value_label = ttk.Label(total_value_frame, text="")
total_value_label.pack(side='left', pady=5)
total_value_amount_label = ttk.Label(total_value_frame, text="", foreground=HIGHLIGHT_COLOR)
total_value_amount_label.pack(side='left', pady=5)

# 设置默认按钮和绑定回车键
root.bind('<Return>', calculate_fee)

# 绑定ESC键
root.bind('<Escape>', on_escape)

# 让股数输入框获得焦点
shares_entry.focus_set()

# 添加版权信息
copyright_label = ttk.Label(root, text="© 2024 Alex Xu 版权所有", font=("Arial", 8), foreground=TEXT_COLOR)
copyright_label.pack(side='bottom', pady=10)

# 运行主循环
root.mainloop()