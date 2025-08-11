import tkinter as tk
import tkinter.font as tk_font
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from modules.fish import Fish
from widgets.title_bar import TitleBar
from utils import load_settings, global_settings, save_settings

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
        self.control_button.pack(fill=X, pady=(0, 0), ipady=0)
        
        # 初始化钓鱼对象
        self.fish = None
        self.is_fishing = False
        
        # 加载配置并应用到界面
        self.load_and_apply_settings()
    
    def load_and_apply_settings(self):
        """加载配置文件并应用到界面组件"""
        if global_settings:
            # 应用服务器选择
            if 'server' in global_settings:
                self.server_var.set(global_settings['server'])
            
            # 应用鱼竿选择
            if 'rod' in global_settings:
                self.rod_var.set(global_settings['rod'])
            
            # 应用鱼类选择
            if 'fish' in global_settings:
                fish_settings = global_settings['fish']
                if 'green' in fish_settings:
                    self.green_fish_var.set(fish_settings['green'])
                if 'blue' in fish_settings:
                    self.blue_fish_var.set(fish_settings['blue'])
                if 'yellow' in fish_settings:
                     self.yellow_fish_var.set(fish_settings['yellow'])
        else:
            print("No settings found, using defaults")
    
    def save_current_settings(self):
        """保存当前界面设置到配置文件"""
        current_settings = {
            'server': self.server_var.get(),
            'rod': self.rod_var.get(),
            'fish': {
                'green': self.green_fish_var.get(),
                'blue': self.blue_fish_var.get(),
                'yellow': self.yellow_fish_var.get()
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
        
        server_label = ttk.Label(server_frame, text="服务器：",  width=6)
        server_label.pack(side=LEFT)
        
        self.server_var = tk.StringVar(value="tw")
        taiwan_radio = ttk.Radiobutton(server_frame, text="台服", variable=self.server_var, value="tw")
        taiwan_radio.pack(side=LEFT, padx=(10, 5))
        
        us_radio = ttk.Radiobutton(server_frame, text="美服", variable=self.server_var, value="na")
        us_radio.pack(side=LEFT, padx=(5, 0))
    
    def create_fish_choice(self, parent):
        fish_frame = ttk.Frame(parent)
        fish_frame.pack(fill=X, pady=(0, 10))
        fish_label = ttk.Label(fish_frame, text="鱼：", width=6)
        fish_label.pack(side=LEFT)
        self.green_fish_var = tk.BooleanVar(value=False)
        self.blue_fish_var = tk.BooleanVar(value=False)
        self.yellow_fish_var = tk.BooleanVar(value=True)
        green_check = ttk.Checkbutton(fish_frame, text="绿鱼", variable=self.green_fish_var)
        green_check.pack(side=LEFT, padx=(10, 5))
        blue_check = ttk.Checkbutton(fish_frame, text="蓝鱼", variable=self.blue_fish_var)
        blue_check.pack(side=LEFT, padx=(10, 5))
        yellow_check = ttk.Checkbutton(fish_frame, text="黄鱼", variable=self.yellow_fish_var)
        yellow_check.pack(side=LEFT, padx=(10, 5))

    def get_selected_fish(self):
        """获取选中的鱼类列表"""
        selected_fish = []
        if self.green_fish_var.get():
            selected_fish.append("green")
        if self.blue_fish_var.get():
            selected_fish.append("blue")
        if self.yellow_fish_var.get():
            selected_fish.append("yellow")
        return selected_fish

    def create_rod(self, parent):
        rod_frame = ttk.Frame(parent)
        rod_frame.pack(fill=X, pady=(0, 10))
        rod_label = ttk.Label(rod_frame, text="鱼竿：", width=6)
        rod_label.pack(side=LEFT)
        
        # 鱼竿下拉框选择
        self.rod_var = tk.StringVar(value="巴洛斯钓竿")
        rod_options = ["巴雷诺斯鱼竿", "凉风鱼竿", "梅迪亚鱼竿"]
        rod_combobox = ttk.Combobox(rod_frame, textvariable=self.rod_var, values=rod_options, state="readonly", width=15)
        rod_combobox.pack(side=LEFT, padx=(10, 5))

    def toggle_fishing(self):
        """切换钓鱼状态"""
        if not self.is_fishing:
            self.start_fishing()
        else:
            self.stop_fishing()
    
    def start_fishing(self):
        """开始钓鱼"""
        selected_server = self.server_var.get()
        self.fish = Fish(selected_server)
        
        if self.fish.start():
            self.is_fishing = True
            self.control_button.config(text="停止钓鱼", style="danger.TButton")
            # 开始状态检查
            self.check_status()
            print(f"开始在 {selected_server} 钓鱼")

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

    
    def on_close(self):
        """关闭窗口时的清理工作"""
        # 保存当前设置
        self.save_current_settings()
        
        if self.fish and self.is_fishing:
            self.fish.stop()
        
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