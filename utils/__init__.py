import cv2
import numpy as np
from typing import List, Tuple, Dict, Optional
import os

def root_path():
    current_path = os.path.dirname(os.path.abspath(__file__))
    root_path = os.path.dirname(current_path)
    return root_path


# 单图匹配
def match_template(image: np.ndarray, template: np.ndarray, threshold: float = 0.8) -> List[Tuple[int, int, float]]:
    """
    在图像中匹配模板
    :param image: 目标图像
    :param template: 模板图像
    :param threshold: 匹配阈值
    :return: 匹配结果列表 [(x, y, confidence), ...]
    """
    img_h, img_w = image.shape[:2]
    tmpl_h, tmpl_w = template.shape[:2]
    
    if tmpl_h > img_h or tmpl_w > img_w:
        return []
    
    if len(image.shape) == 3:
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        image_gray = image
        
    if len(template.shape) == 3:
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    else:
        template_gray = template
    
    result = cv2.matchTemplate(image_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    
    locations = np.where(result >= threshold)
    matches = []
    
    for pt in zip(*locations[::-1]):
        confidence = result[pt[1], pt[0]]
        matches.append((pt[0], pt[1], confidence))
    
    matches.sort(key=lambda x: x[2], reverse=True)
    
    return matches

# 多图匹配找到置信度最高的一张图片
def match_template_multi(image: np.ndarray, templates: Dict[str, np.ndarray], threshold: float = 0.8) -> Optional[Tuple[str, List[Tuple[int, int, float]]]]:
    """
    在图像中匹配多个模板
    :param image: 目标图像
    :param templates: 模板字典 {name: template}
    :param threshold: 匹配阈值
    :return: 匹配结果 (name, [(x, y, confidence), ...])
    """
    best_match = (None, None, None)
    best_confidence = 0
    
    for name, template in templates.items():
        matches = match_template(image, template, threshold)
        if matches and matches[0][2] > best_confidence:
            best_confidence = matches[0][2]
            best_match = (name, matches, best_confidence)
    
    return best_match


def match_key_list(image: np.ndarray, key_templates: Dict[str, np.ndarray], threshold: float = 0.8, merge_distance: int = 10) -> List[Tuple[str, int, int, float]]:
    """
    在图像中匹配所有按键模板
    :param image: 目标图像
    :param key_templates: 按键模板字典 {key_name: template}
    :param threshold: 匹配阈值
    :param merge_distance: 合并相近匹配的距离阈值（像素）
    :return: 所有匹配结果列表 [(key_name, x, y, confidence), ...]
    """
    all_matches = []
    
    for key_name, template in key_templates.items():
        matches = match_template(image, template, threshold)
        for x, y, confidence in matches:
            all_matches.append((key_name, x, y, confidence))
    
    # 去除相近位置的重复匹配，保留置信度最高的
    filtered_matches = []
    all_matches.sort(key=lambda x: x[3], reverse=True)  # 先按置信度排序
    
    for match in all_matches:
        key_name, x, y, confidence = match
        # 检查是否与已有匹配过于接近
        is_duplicate = False
        for existing_match in filtered_matches:
            existing_key, existing_x, _, _ = existing_match
            if (key_name == existing_key and 
                abs(x - existing_x) <= merge_distance):

                is_duplicate = True
                break
        
        if not is_duplicate:
            filtered_matches.append(match)
    
    filtered_matches.sort(key=lambda x: x[1])
    return filtered_matches 


def hsv_color_match(image: np.ndarray, lower_hsv: np.ndarray, upper_hsv: np.ndarray, threshold: float = 0.05) -> List[Tuple[int, int, float]]:
    """
    在图像中匹配HSV颜色范围
    :param image: 目标图像
    :param lower_hsv: 下限HSV值
    :param upper_hsv: 上限HSV值
    :param threshold: 匹配阈值
    :return: 匹配结果列表 [(x, y, confidence), ...]
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)

    hsv_pixels = cv2.countNonZero(mask)
    total_pixels = image.shape[0] * image.shape[1]
    hsv_ratio = hsv_pixels / total_pixels
    print(f"HSV颜色匹配比例: {hsv_ratio}")
    print(f"HSV匹配像素: {hsv_pixels}")
    print(f"HSV总像素: {total_pixels}")

    return hsv_ratio > threshold