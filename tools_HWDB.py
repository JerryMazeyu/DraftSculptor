import struct
import os
import cv2
import numpy as np

# 文件路径
input_file = 'assets/imgs.raw/HWDB1.1trn_gnt'
output_dir = 'character_result'

# 确保输出目录存在
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

names = [os.path.join(input_file, x) for x in os.listdir(input_file)]

for ind, name in enumerate(names):
    print(f"{ind}/{len(names)} Process {name}...")
    # 解析单个字符图像
    with open(name, 'rb') as f:
        while True:
            # 读取头部信息：样本大小(4字节)
            header = f.read(4)
            if not header:
                break
            sample_size = struct.unpack('<I', header)[0]

            # 读取标签 (2字节, GBK 编码)
            label_bytes = f.read(2)
            label = struct.unpack('<H', label_bytes)[0]
            label_char = struct.pack('H', label).decode('gbk')

            # 读取图像宽高 (2字节分别表示宽和高)
            width = struct.unpack('<H', f.read(2))[0]
            height = struct.unpack('<H', f.read(2))[0]

            # 读取图像数据
            image_data = f.read(width * height)
            image = np.frombuffer(image_data, dtype=np.uint8).reshape((height, width))
            
            # 图像处理：将字迹调整为水笔风格，更加潦草，并设置透明背景
            # 1. 使用膨胀操作让笔画变得更粗
            kernel = np.ones((2, 2), np.uint8)
            image = cv2.dilate(image, kernel, iterations=1)

            # 2. 使用阈值分割像素，小于阈值的设置为0，大于阈值的设置为255
            threshold_value = 200
            _, image = cv2.threshold(image, threshold_value, 255, cv2.THRESH_BINARY)

            # 4. 将白色背景变为透明
            image_rgba = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA) 

            threshold = 200
            lower_white = np.array([threshold, threshold, threshold, 0])  # **背景接近白色的最低值**
            upper_white = np.array([255, 255, 255, 255])  # **背景接近白色的最高值**

            # 创建掩码，将背景部分设为透明
            white_mask = cv2.inRange(image_rgba, lower_white, upper_white)  # **生成白色掩码**
            
            # 设置所有白色背景的alpha通道为0，其他部分保持不变
            image_rgba[white_mask == 255] = [0, 0, 0, 0]  # **将背景部分的Alpha设为0**
            image = image_rgba

            # 保存图像为 PNG 文件        
            label_dir = os.path.join(output_dir, label_char)
            if not os.path.exists(label_dir):
                os.makedirs(label_dir)
            output_path = os.path.join(label_dir, f'{label_char}_{f.tell()}.png')
            cv2.imwrite(output_path, image)

            print(f'Saved: {output_path}')

print("All images have been extracted.")