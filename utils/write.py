import os
import random
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from utils import root, pjoin

def find_ttf_file(font_name=None):
    """
    Finds the path to a TTF file in the specified directory.
    
    Args:
        font_name (str, optional): The name of the TTF file to search for (without the .ttf extension).
                                   If None or not found, a random TTF file from the directory will be returned.
    
    Returns:
        str: The path to the found TTF file, or a random one if the specific file is not found.
    """
    # Get all .ttf files in the directory
    directory = pjoin(root(), 'assets', 'fonts')
    
    ttf_files = [f for f in os.listdir(directory) if f.endswith('.ttf')]
    
    if not ttf_files:
        raise FileNotFoundError("No TTF files found in the specified directory.")
    
    # If font_name is provided, try to find it
    if font_name:
        for ttf_file in ttf_files:
            if ttf_file.lower() == f"{font_name.lower()}.ttf":
                cand_ttf = os.path.join(directory, ttf_file)
                if os.path.exists(cand_ttf):
                    return cand_ttf
                else:
                    return os.path.join(directory, random.choice(ttf_files))
    
    # If not found or font_name is None, return a random TTF file
    return os.path.join(directory, random.choice(ttf_files))


def text_to_png(text, font_size, font_path=None, output_path=None):
    """
    Generates a PNG image of the specified text using a specified TTF font.

    Args:
        text (str): The text to render.
        font_path (str): The path to the TTF font file.
        font_size (int): The size of the font to use.
        output_path (str): The path where the PNG file will be saved, if None will return png.
    """
    if not font_path:
        font_path = find_ttf_file()
    font = ImageFont.truetype(font_path, font_size)
    
    text_bbox = font.getbbox(text)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
   
    # Create a new image with a white background
    image = Image.new('RGBA', (text_width, text_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    
    draw.text((0, 0), text, font=font, fill=(0, 0, 0, 255))
    if output_path:
        image.save(output_path)
        return
    else:
        return image

def draw(imgp, conf, output_path="./output_img.png"):
    image = Image.open(imgp)
    draw = ImageDraw.Draw(image)
    for index, row in conf.iterrows():
        text = str(row['文字'])
        x = row['X']
        y = row['Y']
        size = row['大小']
        font = row['字体']
        # Determine the font path
        if font == 'default':
            font_path = find_ttf_file()
        else:
            font_path = pjoin(root(), 'assets', 'font', f'{font}.ttf')
            if not os.path.exists(font_path):
                font_path = find_ttf_file()
        
        # Load the font
        font = ImageFont.truetype(font_path, size)
        
        # Add the text to the image
        draw.text((x, y), text, font=font, fill=(0, 0, 0, 255))  # Black color
        
    image.save(output_path)
    return True
    
    
if __name__ == "__main__":
    # # Example usage
    # font_path = "/Users/mazeyu/NewEra/DraftSculptor/assets/fonts/person2.ttf"
    # output_path = "output_text.png"
    # text = "你好，我是人2号"
    # font_size = 100

    # text_to_png(text, font_path, font_size, output_path)
    # Example usage
    # font_name = None  # or specify a font name like "Arial" (without the .ttf extension)

    # ttf_path = find_ttf_file(font_name)
    # print(f"Selected TTF file: {ttf_path}")
    image_path = "/Users/mazeyu/NewEra/DraftSculptor/assets/templates/签收单模板.jpg"
    data = {
    "文字": ["Hello", "World", "测试", "Python", "图像"],
    "X": [50, 150, 250, 350, 450],
    "Y": [50, 150, 250, 350, 450],
    "大小": [200, 300, 400, 500, 660],
    "字体": ["Arial", "default", "default", "Courier", "default"]
    }
    df = pd.DataFrame(data)
    draw(image_path, df)
