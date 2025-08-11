import tkinter as tk
import ttkbootstrap as ttk
from PIL import ImageTk, Image
from ttkbootstrap.constants import *
from utils import root_path

class TitleBar(tk.Frame):
    def __init__(self, master=None, container=None, close_callback=None):
        super().__init__(master)
        self.master = master
        self.container = container
        self.close_callback = close_callback
        self.save_timer = None  # 用于延迟保存的定时器
        self.create_widgets()

    def create_widgets(self):
        self.title_bar = ttk.Frame(self.container) 
        self.title_bar.pack(fill="x", anchor="center", padx=12, pady=12) 
        path = root_path()
        logo_icon = Image.open(f"{path}/assets/logo.ico")
        close_icon = Image.open(f"{path}/assets/close.png")
        icon_size = (16,16)  
        logo_icon_resized = logo_icon.resize(icon_size, Image.LANCZOS)
        close_icon_resized = close_icon.resize(icon_size, Image.LANCZOS)

        self.logo_icon_photo = ImageTk.PhotoImage(logo_icon_resized)
        self.close_icon_photo = ImageTk.PhotoImage(close_icon_resized)

 
        self.logo_label = ttk.Label(
            self.title_bar,
            image=self.logo_icon_photo,
        )
        # 为 logo 绑定拖拽事件
        self.logo_label.bind('<Button-1>', self.clickwin)
        self.logo_label.bind('<B1-Motion>', self.dragwin)
        self.logo_label.bind('<ButtonRelease-1>', self.on_drag_end)

        self.title_bar.bind('<Button-1>', self.clickwin)
        self.title_bar.bind('<B1-Motion>', self.dragwin)
        self.title_bar.bind('<ButtonRelease-1>', self.on_drag_end)
        self.title_label = ttk.Label(
            self.title_bar,
            text="钓鱼助手",
        )
        # 为标题文字绑定拖拽事件
        self.title_label.bind('<Button-1>', self.clickwin)
        self.title_label.bind('<B1-Motion>', self.dragwin)
        self.title_label.bind('<ButtonRelease-1>', self.on_drag_end)
        
        self.close_label = ttk.Label(
            self.title_bar,
            image=self.close_icon_photo,
        )
        self.close_label.bind('<Button-1>', self.on_close_click)

        self.logo_label.pack(side=LEFT, padx=(0, 0), pady=0)
        self.title_label.pack(side=LEFT, padx=(4, 0), pady=0)
        self.close_label.pack(side=RIGHT, padx=(0), pady=0)

        spacer = ttk.Frame(self.title_bar)
        # 为空白区域绑定拖拽事件
        spacer.bind('<Button-1>', self.clickwin)
        spacer.bind('<B1-Motion>', self.dragwin)
        spacer.bind('<ButtonRelease-1>', self.on_drag_end)
        spacer.pack(fill=X, expand=True)

    def clickwin(self, event):
        # 补偿 padx 和 pady 的偏移
        self._offsetx = event.x + 12  # 加上 padx=12
        self._offsety = event.y + 12  # 加上 pady=12

    def dragwin(self, event):
        x = self.master.winfo_pointerx() - self._offsetx
        y = self.master.winfo_pointery() - self._offsety
        self.master.geometry(f'+{x}+{y}')
        # 延迟保存位置，避免拖拽过程中频繁保存
        self.schedule_save_position(x, y)
    
    def on_drag_end(self, event):
        """拖拽结束时立即保存位置"""
        self.save_current_position()
    
    def schedule_save_position(self, x, y):
        """延迟保存位置，避免频繁保存"""
        if self.save_timer:
            self.master.after_cancel(self.save_timer)
        self.save_timer = self.master.after(500, lambda: self.save_window_position(x, y))

    def on_close_click(self, event):
        if self.close_callback is not None:
            self.close_callback()
            return
            
        self.master.destroy()
        self.master.quit()