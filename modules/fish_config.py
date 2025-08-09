import os
import cv2
from utils.path import root_path

# 钓鱼配置相关的文件
def load_fish_config(server: str):
    fish_config = {
        "tw": {
            "monitoring": {
                "left": 1640,
                "top": 442,
                "width": 560,
                "height": 50
            },
            "blue_qte": {
                "left": 1998,
                "top": 880,
                "width": 172,  
                "height": 22   
            },
            "key_qte": {
                "left": 1678,
                "top": 790,
                "width": 502,
                "height": 120
            },
        },
        "na": {
            "monitoring": {
                "left": 1640,
                "top": 442,
                "width": 560,
                "height": 50
            },
            "blue_qte": {
                "left": 1998,
                "top": 880,
                "width": 172,  
                "height": 22   
            },
            "key_qte": {
                "left": 1678,
                "top": 790,
                "width": 502,
                "height": 120
            },
        }
    }
    return fish_config[server]

def load_templates(server):
    template_dir = f"{root_path()}/assets/fish_icons/{server}"
    templates = {}
        
    # 获取目录中的所有PNG文件
    for file in os.listdir(template_dir):
        if file.lower().endswith('.png'):
            template_path = os.path.join(template_dir, file)
            template = cv2.imread(template_path, cv2.COLOR_BGR2GRAY)
            if template is not None:
                templates[file] = template
                print(f"已加载状态模板: {file}, 尺寸: {template.shape}")
            else:
                print(f"警告: 无法读取模板 {file}")
                
    return templates