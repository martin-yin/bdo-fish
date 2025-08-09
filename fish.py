
import threading
import time

class Fish:
    def __init__(self, server):
        print("初始化钓鱼")
        self.server = server
        self.is_running = False
        self.thread = None
        
    def start(self):
        """开始钓鱼"""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            return True
        return False
    
    def stop(self):
        """停止钓鱼"""
        if self.is_running:
            self.is_running = False
            print(f"停止在 {self.server} 钓鱼")
            return True
        return False
    
    def _run(self):
        """钓鱼主循环"""
        while self.is_running:
            print("钓鱼中...")
            time.sleep(2)  # 模拟钓鱼过程
            
    def get_status(self):
        """获取钓鱼状态"""
        return "运行中" if self.is_running else "已停止"

# 全局事件对象，用于兼容性
fish_event = threading.Event()
