import os
from cv2 import imread, COLOR_BGR2GRAY
from utils import root_path
import copy

fish_config = {
    "fish_hsv": {
        "blue": {
            "lower": [100, 130, 130],
            "upper": [110, 255, 255]
        },
        "green": {
            "lower": [40, 90, 90],
            "upper": [80, 255, 255]
        },
        "yellow": { # 特喵的游戏里的颜色明明是橙色啊！淦！
            "lower": [10, 0, 0],
            "upper": [30, 255, 255]
        },
        "red": {
            "lower": [0, 90, 0],
            "upper": [10, 255, 255]
        },
    },
    "monitoring": {
        "left": 730,
        "top": 48,
        "width": 430,
        "height": 42
    },
    "blue_qte": {
        "left": 1014,
        "top": 378,
        "width": 134,  
        "height": 17   
    },
    "key_qte": {
        "left": 740,
        "top": 340,
        "width": 436,
        "height": 70
    },
    "fish_color_point": [{
        "left": 1411,
        "top": 621,
        "width": 1,
        "height": 1
    }],
}

def load_fish_config(three_rod, fish_class):
    config_copy = copy.deepcopy(fish_config) 

    if three_rod:
        for i in range(3):
            config_copy["fish_color_point"].append({
                "left": 1411 + i * 54,
                "top": 621,
                "width": 1,
                "height": 1
            })

    print("fish_config")
    # 根据 fish_class 过滤颜色配置
    if 'green' not in fish_class:
        config_copy["fish_hsv"].pop("green")
    if 'blue' not in fish_class:
        config_copy["fish_hsv"].pop("blue")
    if 'yellow' not in fish_class: # 黄鱼也不要了？是不是有点过分了！
        config_copy["fish_hsv"].pop("yellow")

    return {
        "fish_hsv": config_copy["fish_hsv"],
        "monitoring": config_copy["monitoring"],
        "blue_qte": config_copy["blue_qte"],
        "key_qte": config_copy["key_qte"],
        "fish_color_point": config_copy["fish_color_point"],
    }

def load_templates(server, type):
    template_dir = f"{root_path()}/assets/fish_icons/{server}/{type}"
    templates = {}
        
    # 获取目录中的所有PNG文件
    print(os.listdir(template_dir))
    for file in os.listdir(template_dir):
        if file.lower().endswith('.png'):
            template_path = os.path.join(template_dir, file)
            template = imread(template_path, COLOR_BGR2GRAY)
            if template is not None:
                key_name = os.path.splitext(file)[0]
                templates[key_name] = template
                print(f"已加载状态模板: {key_name}, 尺寸: {template.shape}")
            else:
                print(f"警告: 无法读取模板 {file}")
                
    return templates