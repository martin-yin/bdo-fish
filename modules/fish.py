
import threading
import time
from mss import mss
from modules.fish_config import load_fish_config, load_templates
from utils import hsv_color_match, match_key_list, match_template_multi
from pynput import keyboard

class Fish:
    def __init__(self, server):
        self.is_running = False
        self.regions = load_fish_config(server)
        self.templates = load_templates(server)
        self.thread = None
        self.current_state = "monitoring"

    def get_status(self):
        return "运行中" if self.is_running else "已停止"

    def start(self):
        """开始钓鱼"""
        if self.is_running is False and self.thread is None:
            self.is_running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            return True
        return False
    
    def stop(self):
        """停止钓鱼"""
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)
            return True

    def capture_region(self, region_name: str):
        region = self.regions[region_name]
        
        try:
            with mss.mss() as sct:
                monitor = {
                    "left": region["left"],
                    "top": region["top"],
                    "width": region["width"],
                    "height": region["height"]
                }
                
                screenshot = sct.grab(monitor)
                return screenshot
            
        except Exception as e:
            print(f"截图失败: {e}")
            return None

    def _run(self):
        """钓鱼主循环"""
        while self.is_running:
            print("钓鱼中...")
            time.sleep(2)
            if self.current_state == "monitoring":
                result = self.handle_monitoring_status(self.capture_region("monitoring"))
                if result == "continue":
                    continue
            if self.current_state == "blue_qte":
                result = self.handle_fishing_status(self.capture_region("blue_qte"))
                if result == "continue":
                    continue
            if self.current_state == "key_qte":
                self.handle_key_qte_status(self.capture_region("key_qte"))
                self.current_state = "monitoring"
        

    def handle_monitoring_status(self, status_image):
        """处理监控状态"""
        if status_image is None:
            time.sleep(1)
            return "continue"

        (status, confidence) = match_template_multi(status_image, self.templates['monitoring'])

        if status == "find_some_one" and confidence >= 0.95:
            print("检测到find_some_one状态，按下空格键进入拉扯状态")
            keyboard.press_and_release('space')
            print("等待1.5秒进入拉扯状态……")
            time.sleep(1.5)
            self.current_state = "fishing"
            print("切换到拉扯检测模式")
        
        if status == "start":
            print("检测到start状态，按下空格键开始钓鱼")
            keyboard.press_and_release('space')
            print("等待10秒进入检测状态……")
            time.sleep(10)

        if status == "waiting":
            print("检测到waiting状……")
            time.sleep(1)


    def handle_fishing_status(self, fishing_image):
        """处理拉扯状态"""
        try:
            if fishing_image is None:
                time.sleep(0.1)
                return "continue"
            # 蓝色的 qte 检测
            blue_detected = hsv_color_match(fishing_image, np.array([100, 50, 50]), np.array([130, 255, 255]))
            if blue_detected: 
                print("等待2.1秒进入按键输入状态...")
                self.current_state = "key_qte"
                time.sleep(2.1)
            else:
                time.sleep(0.1)
                return "continue"
        except Exception as e:
            print(f"蓝色检测失败: {e}")
            time.sleep(0.1)
            return "continue"

    def handle_key_qte_status(self, key_qte_image):
        """处理按键输入状态"""
        if key_qte_image is None:
            time.sleep(0.1)
            return "continue"
        result = match_key_list(key_qte_image, self.templates['key_qte'])
        if len(result) > 0:
            print(result)
            for key_name, x, y, confidence in result:
                print(f"检测到按键: {key_name} 在位置: ({x}, {y}) 置信度: {confidence:.2f}")
                keyboard.press(key_name)
                time.sleep(0.1)
                keyboard.release(key_name)
                time.sleep(0.1)
            print("所有按键输入完成")
            print("按键输入阶段完成，等待3秒判断鱼的颜色")
            time.sleep(3)  # 等待3秒再继续监控
            keyboard.press_and_release('r')
            print("按下R键")
            # 检测特定地方的 hsv 是否是蓝色 绿色 和 白色的
            self.current_state = "monitoring"
            time.sleep(1)
        else:
            time.sleep(0.1)
            return "continue"
        
        
