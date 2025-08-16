
import threading
import time
import numpy as np
from PIL import Image
import mss
from modules.fish_config import load_fish_config, load_templates
from utils import hsv_color_match, match_key_list, match_template_multi
import keyboard
from cv2 import cvtColor, inRange, COLOR_RGB2BGR, COLOR_RGB2HSV

class Fish:
    def __init__(self, server, three_rod: bool, fish_class):
        self.is_running = False
        self.fish_config = load_fish_config(three_rod, fish_class)
        self.monitoring_templates = load_templates(server, 'monitoring')
        self.key_qte_template = load_templates(server, 'key_qte')
        self.thread = None
        self.current_state = "monitoring"
        self.fishing_detection_count = 0  # 拉扯状态检测次数计数器
        self.max_fishing_detection = 100  # 最大检测次数

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
        region = self.fish_config[region_name]
        
        try:
            with mss.mss() as sct:
                monitor = {
                    "left": region["left"],
                    "top": region["top"],
                    "width": region["width"],
                    "height": region["height"]
                }
                
                screenshot = sct.grab(monitor)
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                
                img_array = np.array(img)
                img_bgr = cvtColor(img_array, COLOR_RGB2BGR)
                return img_bgr
            
        except Exception as e:
            print(f"截图失败: {e}")
            return None

    def capture_fish_point_pixel(self):
        """捕获鱼点像素并返回RGB颜色值或RGB颜色值数组"""
        try:
            fish_color_point = self.fish_config["fish_color_point"]
            pixel_rgb_list = []
            with mss.mss() as sct:
                for region in fish_color_point:
                    screenshot = sct.grab(region)
                    img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
                    img_array = np.array(img)
                    # 获取像素的RGB值 (取第一个像素，因为只截取了1x1的区域)
                    pixel_rgb = img_array[0, 0]
                    pixel_rgb_list.append(pixel_rgb)
            return pixel_rgb_list
                
        except Exception as e:
            print(f"捕获鱼点像素失败: {e}")
            return None

    def check_fish_pix_color(self, pixel_rgb_list):
        """检测鱼点像素是否在指定的HSV颜色范围内"""
        if pixel_rgb_list is None:
            return None

        fish_hsv = self.fish_config["fish_hsv"]

        for pixel in pixel_rgb_list:
            for color_name, color_range in fish_hsv.items():
                rgb_pixel = np.uint8([[pixel]])
                hsv_pixel = cvtColor(rgb_pixel, COLOR_RGB2HSV)[0][0]
                if inRange(np.array([[hsv_pixel]]), np.array(color_range["lower"]), np.array(color_range["upper"]))[0][0] > 0:
                    return True  # 直接跳出所有循环
        return None  # 循环结束后未找到匹配颜色

    def _run(self):
        """钓鱼主循环"""
        while self.is_running:
            print(f"当前状态 {self.current_state}")
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
            time.sleep(2)
        

    def handle_monitoring_status(self, status_image):
        """处理监控状态"""
        if status_image is None:
            time.sleep(1)
            return "continue"
        (status, _, confidence) = match_template_multi(status_image, self.monitoring_templates)
        if status == "find_some_one":
            print("检测到find_some_one状态，按下空格键进入拉扯状态")
            keyboard.press_and_release('space')
            print("等待1.5秒进入拉扯状态……")
            time.sleep(1.5)
            self.current_state = "blue_qte"
            self.fishing_detection_count = 0  # 重置拉扯状态检测计数器
            print("切换到拉扯检测模式")
            return "continue"
        
        if status == "start":
            print("检测到start状态，按下空格键开始钓鱼")
            keyboard.press_and_release('space')
            print("等待2秒进入检测状态……")
            time.sleep(2)
            return "continue"


        if status == "waiting":
            print("检测到waiting状……")
            time.sleep(1)
            return "continue"


    def handle_fishing_status(self, fishing_image):
        """处理拉扯状态"""
        try:
            if fishing_image is None:
                self.fishing_detection_count += 1
                if self.fishing_detection_count >= self.max_fishing_detection:
                    print(f"拉扯状态检测失败次数达到{self.max_fishing_detection}次，返回监控状态")
                    self.current_state = "monitoring"
                    self.fishing_detection_count = 0  # 重置计数器
                    return "continue"
                time.sleep(0.1)
                return "continue"
            
            blue_detected = hsv_color_match(fishing_image, np.array([100, 130, 130]), np.array([110, 255, 255]))
            print(f"蓝色检测结果: {blue_detected}")
            
            if blue_detected: 
                keyboard.press_and_release('space')
                print("等待2.2秒进入按键输入状态...")
                time.sleep(2.2)
                self.current_state = "key_qte"
                self.fishing_detection_count = 0  # 检测成功，重置计数器
                return "continue"
            else:
                self.fishing_detection_count += 1
                print(f"没有检测到结果，当前检测次数: {self.fishing_detection_count}/{self.max_fishing_detection}")
                
                if self.fishing_detection_count >= self.max_fishing_detection:
                    print(f"拉扯状态检测失败次数达到{self.max_fishing_detection}次，返回监控状态")
                    self.current_state = "monitoring"
                    self.fishing_detection_count = 0  # 重置计数器
                    return "continue"
                
                time.sleep(0.05)
                return "continue"
        except Exception as e:
            self.fishing_detection_count += 1
            print(f"蓝色检测失败: {e}，当前检测次数: {self.fishing_detection_count}/{self.max_fishing_detection}")
            
            if self.fishing_detection_count >= self.max_fishing_detection:
                print(f"拉扯状态检测失败次数达到{self.max_fishing_detection}次，返回监控状态")
                self.current_state = "monitoring"
                self.fishing_detection_count = 0  # 重置计数器
                return "continue"
            
            time.sleep(0.1)
            return "continue"

    def handle_key_qte_status(self, key_qte_image):
        """处理按键输入状态"""
        if key_qte_image is None:
            time.sleep(0.1)
            return "continue"

        result = match_key_list(key_qte_image, self.key_qte_template)
        if len(result) > 0:
            print(result)
            for key_name, _, _, confidence in result:
                print(f"检测到按键: {key_name} 置信度: {confidence:.2f}")
                keyboard.press(key_name)
                time.sleep(0.1)
                keyboard.release(key_name)
                time.sleep(0.1)
            print("所有按键输入完成")
            print("按键输入阶段完成，等待2.5秒判断鱼的颜色")
            time.sleep(3)
        else:
            print("没有需要输入的按键，等待1秒后按下R")
            time.sleep(1)
        # 捕获鱼点像素并检测颜色
        isInFishHsv = self.check_fish_pix_color(self.capture_fish_point_pixel())
        if isInFishHsv != None:
            keyboard.press_and_release('r')
            print("按下R键")
            self.current_state = "monitoring"
        return "continue"
