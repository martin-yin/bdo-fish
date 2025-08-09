import tkinter as tk
import tkinter.font as tk_font
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from title_bar import TitleBar

class MainPage(ttk.Frame):
    def __init__(self, master=None, parent=None):
        super().__init__(master)
        self.master = master
        self.pack(fill=BOTH,expand=YES)
        self.create_widgets()

    def create_widgets(self):
        self.title_bar = TitleBar(self.master, container=self, close_callback=self.on_close)
        self.title_bar.pack(fill='y', expand=YES)

        self.form_widgets = ttk.Frame(self)
        self.form_widgets.pack(fill=BOTH, expand=YES, padx=12, pady=0)
        
        server_frame = ttk.Frame(self.form_widgets)
        server_frame.pack(fill=X, pady=(0, 10))
        
        server_label = ttk.Label(server_frame, text="服务器：")
        server_label.pack(side=LEFT)
        
        self.server_var = tk.StringVar(value="台服")
        taiwan_radio = ttk.Radiobutton(server_frame, text="台服", variable=self.server_var, value="台服")
        taiwan_radio.pack(side=LEFT, padx=(10, 5))
        
        us_radio = ttk.Radiobutton(server_frame, text="美服", variable=self.server_var, value="美服")
        us_radio.pack(side=LEFT, padx=(5, 0))
        
        start_button = ttk.Button(self.form_widgets, text="开始钓鱼", 
                                 command=self.start_fishing, style="success.TButton")
        start_button.pack(fill=X, pady=(10, 0), ipady=0)
    
    
    def start_fishing(self):
        selected_server = self.server_var.get()
        print(f"开始在 {selected_server} 钓鱼")
    
    def on_close(self):
        self.master.destroy()
        self.master.quit()

if __name__ == "__main__":
    app = ttk.Window("", "darkly")
    app.geometry("260x130")
    app.overrideredirect(True) 
    font_size = int(14)
    default_font = tk_font.nametofont("TkDefaultFont")
    default_font.configure(size=font_size)
    app.attributes('-topmost', True)
    MainPage(app)
    app.mainloop()