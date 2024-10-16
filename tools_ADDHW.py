import os
import cv2
import numpy as np
from utils import root
from pathlib import Path


# ================================================================
tar = '邸'
img_path = f'handwrites\\{tar}.png'  # 需要被解构的图像
mode = f"single:{tar}"  # single:X 指的是所有的字都是统一种，冒号后是该字 multi则只负责分割，需要手动重组 
para = 10  # 调节参数（如果字内部分离则调大些）
threshold = 100  # 背景色阈值（若背景比较暗则调小）
# ================================================================



def clear_background_and_detect_characters(image_path, mode, para, threshold):
    # 读取图片
    img = cv2.imread(image_path)
    if not img:  # 中文windows上无法解析
        from PIL import Image
        img_pil = Image.open(img_path)
        img = np.array(img_pil)
    # 将图像转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 应用二值化处理，清除背景，假设背景是白色
    _, binary_img = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)

    # 使用形态学操作去除噪声，并将字符区域连接起来
    kernel = np.ones((para,para), np.uint8)
    processed_img = cv2.dilate(binary_img, kernel, iterations=1)

    # 检测字的轮廓
    contours, _ = cv2.findContours(processed_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 依次处理每个字的轮廓，裁剪出每个字
    cropped_images = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # 通过bounding box裁剪出单个字
        cropped_char = img[y:y+h, x:x+w]
        
        cropped_char_rgba = cv2.cvtColor(cropped_char, cv2.COLOR_BGR2BGRA) 
        
        # 设置近似白色和近似黑色的阈值
        lower_white = np.array([threshold, threshold, threshold, 0])  # **背景接近白色的最低值**
        upper_white = np.array([255, 255, 255, 255])  # **背景接近白色的最高值**

        # 创建掩码，将背景部分设为透明
        white_mask = cv2.inRange(cropped_char_rgba, lower_white, upper_white)  # **生成白色掩码**
        
        # 设置所有白色背景的alpha通道为0，其他部分保持不变
        cropped_char_rgba[white_mask == 255] = [0, 0, 0, 0]  # **将背景部分的Alpha设为0**
        
        
        cropped_images.append(cropped_char_rgba)
    
    result_dir = os.path.join(root(), "character_result")
    if not os.path.exists(result_dir):
        os.mkdir(result_dir, mode=0o777)

    if mode.startswith("single"):
        char_name = mode.split(":")[1]
        result_dir = os.path.join(result_dir, char_name)
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
    
    for i, char_img in enumerate(cropped_images):
        cv2.imwrite(os.path.join(root(), "character_result", f"char{i}.png"), char_img)
    return True

if __name__ == "__main__":
    clear_background_and_detect_characters(image_path=img_path, mode=mode, para=para, threshold=threshold)
