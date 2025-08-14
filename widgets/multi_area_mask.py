import tkinter as tk
from tkinter import Canvas, Button, Frame
import ctypes

class CTkMultiAreaMask:
    def __init__(self):
        self.__scale = 1
        self.areas = []  # 存储多个区域坐标 [(x, y, width, height), ...]
        self.win = None
        self.canvas = None
        
    def add_area(self, x, y, width, height):
        """添加一个区域坐标"""
        self.areas.append((x, y, width, height))
        
    def set_areas(self, areas_list):
        """设置多个区域坐标"""
        self.areas = areas_list.copy()
        
    def clear_areas(self):
        """清空所有区域"""
        self.areas.clear()
        
    def create_mask_overlay(self):
        """创建蒙版覆盖层，显示所有指定的区域"""
        if not self.areas:
            print("没有设置任何区域坐标")
            return
            
        # 初始化临时窗口
        self.win = tk.Tk()
        self.win.title("区域蒙版")
        self.win.attributes("-alpha", 0.7)  # 设置窗口半透明
        self.win.attributes("-fullscreen", True)  # 设置全屏
        self.win.attributes("-topmost", True)  # 设置窗口在最上层
        self.win.configure(bg='black')  # 设置背景为黑色
        self.win.update_idletasks()
        
        # 获取屏幕尺寸
        width, height = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
        
        # 获取DPI缩放比例
        self._calculate_scale()
        
        # 创建主框架
        main_frame = Frame(self.win, bg='black')
        main_frame.pack(fill='both', expand=True)
        
        # 创建画布
        self.canvas = Canvas(main_frame, width=width, height=height, bg="black", highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        # 绘制所有区域
        self._draw_areas()
        
        # 创建控制按钮框架
        button_frame = Frame(main_frame, bg='black')
        button_frame.pack(side='bottom', pady=10)
        
        # 添加控制按钮
        close_btn = Button(button_frame, text="关闭蒙版", command=self.close_mask, 
                          bg='red', fg='white', font=('Arial', 12, 'bold'))
        close_btn.pack(side='left', padx=5)
        
        refresh_btn = Button(button_frame, text="刷新显示", command=self._draw_areas,
                           bg='blue', fg='white', font=('Arial', 12, 'bold'))
        refresh_btn.pack(side='left', padx=5)
        
        # 绑定键盘事件
        self.win.bind('<Escape>', lambda e: self.close_mask())
        self.win.bind('<F5>', lambda e: self._draw_areas())
        
        # 显示提示信息
        info_text = f"显示 {len(self.areas)} 个区域 | 按ESC或点击关闭按钮退出 | F5刷新"
        self.canvas.create_text(width//2, 30, text=info_text, fill='white', 
                               font=('Arial', 14, 'bold'), tags="info")
        
        self.win.mainloop()
        
    def _calculate_scale(self):
        """计算DPI缩放比例"""
        try:
            user32 = ctypes.windll.user32
            gdi32 = ctypes.windll.gdi32
            dc = user32.GetDC(None)
            widthScale = gdi32.GetDeviceCaps(dc, 8)  # 分辨率缩放后的宽度
            width = gdi32.GetDeviceCaps(dc, 118)  # 原始分辨率的宽度
            self.__scale = width / widthScale if widthScale > 0 else 1
            user32.ReleaseDC(None, dc)
        except:
            self.__scale = 1
            
    def _draw_areas(self):
        """在画布上绘制所有区域"""
        if not self.canvas:
            return
            
        # 清除之前的绘制（除了信息文本）
        self.canvas.delete("area")
        
        # 绘制每个区域
        for i, (x, y, width, height) in enumerate(self.areas):
            # 转换坐标（考虑DPI缩放）
            display_x = int(x / self.__scale)
            display_y = int(y / self.__scale)
            display_width = int(width / self.__scale)
            display_height = int(height / self.__scale)
            
            # 绘制矩形框
            self.canvas.create_rectangle(
                display_x, display_y, 
                display_x + display_width, display_y + display_height,
                outline='red', width=3, fill='', tags="area"
            )
            
            # 添加区域标签
            label_text = f"区域{i+1}\n({x},{y})\n{width}x{height}"
            self.canvas.create_text(
                display_x + display_width//2, display_y + display_height//2,
                text=label_text, fill='yellow', font=('Arial', 10, 'bold'),
                tags="area"
            )
            
            # 添加区域编号
            self.canvas.create_text(
                display_x + 10, display_y + 10,
                text=str(i+1), fill='white', font=('Arial', 16, 'bold'),
                tags="area"
            )
            
    def close_mask(self):
        """关闭蒙版窗口"""
        if self.win:
            self.win.quit()
            self.win.destroy()
            self.win = None
            self.canvas = None
            
    def is_mask_active(self):
        """检查蒙版是否处于活动状态"""
        return self.win is not None and self.win.winfo_exists()


# 使用示例
if __name__ == "__main__":
    # 创建蒙版实例
    mask = CTkMultiAreaMask()
    
    # 添加多个区域坐标 (x, y, width, height)
    test_areas = [
        (100, 100, 200, 150),  # 区域1
        (400, 200, 300, 100),  # 区域2
        (700, 350, 250, 200),  # 区域3
        (200, 500, 400, 120),  # 区域4
    ]
    
    # 设置区域
    mask.set_areas(test_areas)
    
    # 创建主控制窗口
    root = tk.Tk()
    root.title("蒙版控制器")
    root.geometry("300x200")
    
    def show_mask():
        mask.create_mask_overlay()
        
    def add_new_area():
        # 示例：添加一个新区域
        import random
        x = random.randint(50, 800)
        y = random.randint(50, 600)
        w = random.randint(100, 300)
        h = random.randint(80, 200)
        mask.add_area(x, y, w, h)
        area_count_label.config(text=f"当前区域数量: {len(mask.areas)}")
        
    def clear_all_areas():
        mask.clear_areas()
        area_count_label.config(text=f"当前区域数量: {len(mask.areas)}")
    
    # 创建控制按钮
    Button(root, text="显示蒙版", command=show_mask, bg='green', fg='white', 
           font=('Arial', 12, 'bold')).pack(pady=10)
    
    Button(root, text="添加随机区域", command=add_new_area, bg='blue', fg='white',
           font=('Arial', 10)).pack(pady=5)
    
    Button(root, text="清空所有区域", command=clear_all_areas, bg='orange', fg='white',
           font=('Arial', 10)).pack(pady=5)
    
    area_count_label = tk.Label(root, text=f"当前区域数量: {len(mask.areas)}", 
                               font=('Arial', 10))
    area_count_label.pack(pady=10)
    
    root.mainloop()