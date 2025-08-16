import tkinter as tk
import tkinter.font as tk_font
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from modules.fish import Fish
from widgets.title_bar import TitleBar
from utils import load_settings, global_settings, save_settings
from widgets.multi_area_mask import CTkMultiAreaMask

class MainPage(ttk.Frame):
    def __init__(self, master=None, parent=None):
        super().__init__(master)
        self.master = master
        self.pack(fill=BOTH,expand=YES)
        self.create_widgets()

    def create_widgets(self):
        self.title_bar = TitleBar(self.master, container=self, close_callback=self.on_close)

        self.title_bar.pack(fill='x', expand=NO)

        self.form_widgets = ttk.Frame(self)
        self.form_widgets.pack(fill=BOTH, expand=YES, padx=12, pady=(0, 12))
        # 服务器选择区域
        self.create_server(self.form_widgets)
        self.create_rod(self.form_widgets)
        self.create_fish_choice(self.form_widgets)
        # 控制按钮
        self.control_button = ttk.Button(self.form_widgets, text="开始钓鱼", 
                                        command=self.toggle_fishing, style="success.TButton")
        self.control_button.pack(fill=X, pady=(0, 5), ipady=0)
        
        # 截图控制按钮
        self.mask_button = ttk.Button(self.form_widgets, text="显示截图区域", 
                                     command=self.show_area_mask, style="info.TButton")
        self.mask_button.pack(fill=X, pady=(0, 0), ipady=0)
        
        # 初始化钓鱼对象
        self.fish = None
        self.is_fishing = False
        
        # 初始化截图对象
        self.area_mask = CTkMultiAreaMask()
        self.setup_default_areas()
        
        # 加载配置并应用到界面
        self.load_and_apply_settings()
    
    def load_and_apply_settings(self):
        """加载配置文件并应用到界面组件"""
        if global_settings:
            # 应用服务器选择
            if 'server' in global_settings:
                self.server_var.set(global_settings['server'])
            
            # 应用鱼竿选择
            if 'three_rod' in global_settings:
                self.three_rod_var.set(global_settings['three_rod'])
            
            # 应用鱼类选择
            if 'fish' in global_settings:
                fish_settings = global_settings['fish']
                if 'green' in fish_settings:
                    self.green_fish_var.set(fish_settings['green'])
                if 'blue' in fish_settings:
                    self.blue_fish_var.set(fish_settings['blue'])
                if 'yellow' in fish_settings:
                     self.yellow_fish_var.set(fish_settings['yellow'])
                if 'red' in fish_settings:
                    self.red_fish_var.set(fish_settings['red'])

        else:
            print("No settings found, using defaults")
    
    def save_current_settings(self):
        """保存当前界面设置到配置文件"""
        current_settings = {
            'server': self.server_var.get(),
            'three_rod': self.three_rod_var.get(),
            'fish': {
                'green': self.green_fish_var.get(),
                'blue': self.blue_fish_var.get(),
                'yellow': self.yellow_fish_var.get(),
                'red': self.red_fish_var.get()
            },
            'pos': {
                'x': self.master.winfo_x(),
                'y': self.master.winfo_y(),
            }
        }
        save_settings(current_settings)

    def create_server(self, parent):
        server_frame = ttk.Frame(parent)
        server_frame.pack(fill=X, pady=(0, 10))
        
        server_label = ttk.Label(server_frame, text="服务器：",  width=10)
        server_label.pack(side=LEFT)
        
        self.server_var = tk.StringVar(value="tw")
        taiwan_radio = ttk.Radiobutton(server_frame, text="台服", variable=self.server_var, value="tw")
        taiwan_radio.pack(side=LEFT, padx=(10, 5))
        
        us_radio = ttk.Radiobutton(server_frame, text="美服", variable=self.server_var, value="na")
        us_radio.pack(side=LEFT, padx=(5, 0))
    
    def create_fish_choice(self, parent):
        fish_frame = ttk.Frame(parent)
        fish_frame.pack(fill=X, pady=(0, 10))
        fish_label = ttk.Label(fish_frame, text="需要的鱼类：", width=10)
        fish_label.pack(side=LEFT)
        self.green_fish_var = tk.BooleanVar(value=False)
        self.blue_fish_var = tk.BooleanVar(value=False)
        self.yellow_fish_var = tk.BooleanVar(value=True)
        self.red_fish_var = tk.BooleanVar(value=True)
        green_check = ttk.Checkbutton(fish_frame, text="绿鱼", variable=self.green_fish_var)
        green_check.pack(side=LEFT, padx=(10, 5))
        blue_check = ttk.Checkbutton(fish_frame, text="蓝鱼", variable=self.blue_fish_var)
        blue_check.pack(side=LEFT, padx=(10, 5))
        yellow_check = ttk.Checkbutton(fish_frame, text="黄鱼", variable=self.yellow_fish_var)
        yellow_check.pack(side=LEFT, padx=(10, 5))
        red_check = ttk.Checkbutton(fish_frame, text="红鱼", variable=self.red_fish_var, state="disabled")
        red_check.pack(side=LEFT, padx=(10, 5))

    def get_fish_class(self):
        """获取选中的鱼类列表"""
        fish_class = []
        if self.green_fish_var.get():
            fish_class.append("green")
        if self.blue_fish_var.get():
            fish_class.append("blue")
        if self.yellow_fish_var.get():
            fish_class.append("yellow")
        fish_class.append("red")
        return fish_class

    def create_rod(self, parent):
        rod_frame = ttk.Frame(parent)
        rod_frame.pack(fill=X, pady=(0, 10))
        rod_label = ttk.Label(rod_frame, text="当前鱼竿：", width=10)
        rod_label.pack(side=LEFT)
        self.three_rod_var = tk.BooleanVar(value=False)
        three_rod_check = ttk.Checkbutton(rod_frame, text="三浮竿/凉风竿", variable=self.three_rod_var)
        three_rod_check.pack(side=LEFT, padx=(10, 5))

    def toggle_fishing(self):
        """切换钓鱼状态"""
        if not self.is_fishing:
            self.start_fishing()
        else:
            self.stop_fishing()
    
    def start_fishing(self):
        """开始钓鱼"""
        server = self.server_var.get()
        self.fish = Fish(server, self.three_rod_var.get(), self.get_fish_class())

        
        if self.fish.start():
            self.is_fishing = True
            self.control_button.config(text="停止钓鱼", style="danger.TButton")
            # 开始状态检查
            self.check_status()

    def stop_fishing(self):
        """停止钓鱼"""
        if self.fish and self.fish.stop():
            self.is_fishing = False
            self.control_button.config(text="开始钓鱼", style="success.TButton")
            print("停止钓鱼")
    
    def check_status(self):
        """定期检查钓鱼状态"""
        if self.fish and self.is_fishing:
            status = self.fish.get_status()
            if status == "已停止" and self.is_fishing:
                # 钓鱼意外停止
                self.is_fishing = False
                self.control_button.config(text="开始钓鱼", style="success.TButton")
                self.status_display.config(foreground="red")
            # 每秒检查一次状态
            self.master.after(1000, self.check_status)

    
    def setup_default_areas(self):
        """设置默认的监控区域"""
        # 从fish_config中获取默认区域坐标
        default_areas = [
            (730, 48, 430, 42),    # monitoring区域
            (1014, 378, 134, 17),  # blue_qte区域
            (740, 340, 436, 70),   # key_qte区域
            (1411, 621, 1, 1),     # fish_color_point区域
        ]
        self.area_mask.set_areas(default_areas)
    
    def show_area_mask(self):
        """显示截图区域"""
        try:
            self.area_mask.create_mask_overlay()
        except Exception as e:
            print(f"显示截图时出错: {e}")
    
    def on_close(self):
        """关闭窗口时的清理工作"""
        # 保存当前设置
        self.save_current_settings()
        
        # 停止钓鱼
        if self.fish and self.is_fishing:
            self.fish.stop()
        
        # 关闭截图（如果打开的话）
        if hasattr(self, 'area_mask') and self.area_mask.is_mask_active():
            self.area_mask.close_mask()
        
        self.master.destroy()
        self.master.quit()

if __name__ == "__main__":
    app = ttk.Window("", "darkly")
    app.overrideredirect(True) 
    default_font = tk_font.nametofont("TkDefaultFont")
    app.attributes('-topmost', True)
    load_settings()
    MainPage(app)
    app.mainloop()