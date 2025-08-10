import tkinter as tk
import tkinter.font as tk_font
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from modules.fish import Fish
from widgets.title_bar import TitleBar

class MainPage(ttk.Frame):
    def __init__(self, master=None, parent=None):
        super().__init__(master)
        self.master = master
        self.pack(fill=BOTH,expand=YES)
        self.create_widgets()

    def create_widgets(self):
        self.title_bar = TitleBar(self.master, container=self)
        self.title_bar.pack(fill='x', expand=NO)

        self.form_widgets = ttk.Frame(self)
        self.form_widgets.pack(fill=BOTH, expand=YES, padx=12, pady=(0, 10))
        
        # 服务器选择区域
        server_frame = ttk.Frame(self.form_widgets)
        server_frame.pack(fill=X, pady=(0, 10))
        
        server_label = ttk.Label(server_frame, text="服务器：")
        server_label.pack(side=LEFT)
        
        self.server_var = tk.StringVar(value="tw")
        taiwan_radio = ttk.Radiobutton(server_frame, text="台服", variable=self.server_var, value="tw")
        taiwan_radio.pack(side=LEFT, padx=(10, 5))
        
        us_radio = ttk.Radiobutton(server_frame, text="美服", variable=self.server_var, value="na")
        us_radio.pack(side=LEFT, padx=(5, 0))
        
        # 控制按钮
        self.control_button = ttk.Button(self.form_widgets, text="开始钓鱼", 
                                        command=self.toggle_fishing, style="success.TButton")
        self.control_button.pack(fill=X, pady=(0, 0), ipady=0)
        
        # 初始化钓鱼对象
        self.fish = None
        self.is_fishing = False
    
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
        if self.fish and self.is_fishing:
            self.fish.stop()
        self.master.destroy()
        self.master.quit()

if __name__ == "__main__":
    app = ttk.Window("", "darkly")
    app.overrideredirect(True) 
    default_font = tk_font.nametofont("TkDefaultFont")
    app.attributes('-topmost', True)
    MainPage(app)
    app.mainloop()