import os
from cv2 import imread, COLOR_BGR2GRAY
from utils import root_path

# 钓鱼配置相关的文件
def load_fish_config(server: str):
    fish_config = {
       "tw": {
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
            "fish_point": [{
                "left": 1411,
                "top": 511,
                "width": 1,
                "height": 1
            }],
        },
        "na": {
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
            "fish_point": [{
                "left": 1411,
                "top": 511,
                "width": 1,
                "height": 1
            }],
        }
    }
    return fish_config[server]

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