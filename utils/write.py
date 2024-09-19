import os
import random
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from utils import root, pjoin
from collections import Counter
from augmentation import Augmentation


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

def find_all_combinations(path: str, text: str):
    """
    Finds all possible combinations of subdirectories in the given path that can form the target text.
    
    Args:
        path (str): The base directory where subdirectories are located.
        text (str): The target text to form using subdirectories.
    
    Returns:
        List[List[str]]: A list of lists, where each inner list represents a combination of subdirectories 
                         that can be used to form the text.
    """
    # Helper function for recursion
    def find_combinations(prefix: str, remaining_text: str):
        if not remaining_text:
            return [[]]  # Base case: if no text is left, return an empty combination
        
        # List to store all valid combinations
        valid_combinations = []
        
        # Iterate through possible substrings
        for i in range(1, len(remaining_text) + 1):
            # Get the current substring
            current_substr = remaining_text[:i]
            
            # Check if this substring has a corresponding directory
            current_path = os.path.join(prefix, current_substr)
            if os.path.exists(current_path) and os.path.isdir(current_path):
                # Recursively find combinations for the remaining text
                remaining_combinations = find_combinations(prefix, remaining_text[i:])
                
                # Add the current substring to each valid combination of the remaining text
                for combination in remaining_combinations:
                    valid_combinations.append([current_substr] + combination)
        
        return valid_combinations
    
    # Call the helper function with the base path and the full text
    return find_combinations(path, text)

def get_chara_dict(comb):
    directory = pjoin(root(), 'assets', 'imgs')
    chara_dict = {}
    for chara in comb:
        chara[chara] = [x.split('.')[0] for x in os.listdir(pjoin(directory))]
    return chara_dict

def find_solution(chara_dict):
    """
    example_dict = {
    "A": ['a', 'b', 'c'],
    "B": ['a', 'c', 'd'],
    "C": ['1', '2', '3']
    }
    result = find_solution(example_dict)
    """
    combined_list = [item for sublist in chara_dict.values() for item in sublist]
    freq = Counter(combined_list)
    max_frequency = max(freq.values())
    max_frequency_items = [item for item, count in freq.items() if count == max_frequency]
    solution = random.choice(max_frequency_items)
    result = {}
    for k,v in chara_dict.items():
        if solution in v:
            result[k] = solution
        else:
            result[k] = random.choice(v)
    return result

def concat_images_horizontally(image_paths, target_height):
    """
    Concatenate multiple PNG images horizontally and resize them to the specified height.
    
    Args:
    image_paths (list of str): List of file paths for the PNG images.
    target_height (int): The desired height for the output image.
    
    Returns:
    Image object: The concatenated image.
    """
    
    images = []
    
    # Resize images to the specified height and append them to the list
    for image_path in image_paths:
        img = Image.open(image_path).convert("RGBA")

        # Calculate the new width to maintain aspect ratio
        aspect_ratio = img.width / img.height
        new_width = int(aspect_ratio * target_height)
        resized_img = img.resize((new_width, target_height))
        images.append(resized_img)
    
    # Get the total width of the concatenated image
    total_width = sum(img.width for img in images)
    
    # Create a new blank image with the total width and specified height
    concatenated_image = Image.new('RGBA', (total_width, target_height), (255, 255, 255, 0))
    
    # Paste images one by one from left to right
    current_x = 0
    for img in images:
        concatenated_image.paste(img, (current_x, 0), img)
        current_x += img.width
    
    return concatenated_image

def use_handswrite(text, font_height: int) -> Image:
    """
    Finds images for a target text. If the entire text exists as a directory, selects an image from it. 
    If not, splits the text into characters and combines images from corresponding directories by 
    prioritizing matching filenames. The final image is resized to match the specified font height.
    
    Args:
        path (str): The directory where images are stored.
        text (str): The target text to search for.
        font_height (int): The desired height for resizing the image.

    Returns:
        Image: A PIL Image object of the resized image.
    """
    directory = pjoin(root(), 'assets', 'imgs')

    combinations = find_all_combinations(directory, text)
    if combinations == []:
        font_p = find_ttf_file()
        print("Cannot find solution, use font.")
        return text_to_png(text, font_height, font_p)
        # return Image.new('RGBA', (font_height, font_height), (255, 255, 255, 0))
    else:
        combination = random.choice(combinations)
        print(f"Combination is {combination}.")
        solution_dict = {}
        for chara in combination:
            chara_imgs = os.listdir(pjoin(directory, chara))
            chara_names = [x.split('.')[0] for x in chara_imgs if x.endswith('.png')]
            solution_dict[chara] = chara_names
        solution = find_solution(solution_dict)
        print(f"Solution is {solution}.")
        solution_list = []
        for char, img_name in solution.items():
            char_path = pjoin(directory, char, f"{img_name}.png")
            solution_list.append(char_path)
        img = concat_images_horizontally(solution_list, font_height)
        
        return img

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

def overlay_png_on_background(background, png_image, position=(0, 0)):
    """
    Overlay a transparent PNG image on top of a background image at the specified position.
    
    Args:
    background (PIL.Image): The background image (can be any mode like RGB, RGBA).
    png_image (PIL.Image): The PNG image with transparency (must have an alpha channel).
    position (tuple of int): The (x, y) position where the PNG will be placed on the background.
    
    Returns:
    PIL.Image: The combined image with the PNG overlaid on the background.
    """
    
    # Ensure both images are in RGBA mode (so they have alpha channels)
    background = background.convert("RGBA")
    png_image = png_image.convert("RGBA")
    
    # Get position where the PNG will be placed
    x, y = position
    
    # Get dimensions of the background and PNG image
    bg_width, bg_height = background.size
    png_width, png_height = png_image.size
    
    # Check if the PNG will fit within the background at the specified position
    if x + png_width > bg_width or y + png_height > bg_height:
        raise ValueError("PNG image exceeds the background dimensions at the specified position.")
    
    # Create a copy of the background to avoid modifying the original
    combined_image = background.copy()
    
    # Paste the PNG image onto the background, using the PNG's alpha channel as the mask
    combined_image.paste(png_image, (x, y), png_image)
    
    return combined_image

def draw(imgp, conf, output_path="./output_img.png"):
    image = Image.open(imgp)
    for _, row in conf.iterrows():
        text = str(row['文字'])
        x = int(row['X'])
        y = int(row['Y'])
        size = int(row['大小'])
        font = row['字体']
        if font == 'hand':
            text_img = use_handswrite(text, font_height=size)
            # image.paste(text_img, (x, y))
            image = overlay_png_on_background(image, text_img, (x, y))
        elif font == 'default':
            # draw = ImageDraw.Draw(image)
            # font = ImageFont.truetype(font_path, size)
            font_path = find_ttf_file()
            text_png = text_to_png(text, size, font_path)
            aug = Augmentation(text_png)
            text_png_aug = aug.run()
            image = overlay_png_on_background(image, text_png_aug, (x, y))
            # draw.text((x, y), text, font=font, fill=(0, 0, 0, 255))  # Black color
        else:
            # draw = ImageDraw.Draw(image)
            font_path = pjoin(root(), 'assets', 'font', f'{font}.ttf')
            if not os.path.exists(font_path):
                font_path = find_ttf_file()
            text_png = text_to_png(text, size, font_path)
            aug = Augmentation(text_png)
            text_png_aug = aug.run()
            image = overlay_png_on_background(image, text_png_aug, (x, y))
            # font = ImageFont.truetype(font_path, size)
            # draw.text((x, y), text, font=font, fill=(0, 0, 0, 255))  # Black color
        
    image.save(output_path)
    return True
    
    
if __name__ == "__main__":
    # Example usage
    # font_path = "/Users/mazeyu/NewEra/DraftSculptor/assets/fonts/person2.ttf"
    # output_path = "output_text.png"
    # text = "你好，我是人2号"
    # font_size = 100

    # text_to_png(text, font_size, font_path=font_path, output_path=output_path)
    # Example usage
    # font_name = None  # or specify a font name like "Arial" (without the .ttf extension)

    # ttf_path = find_ttf_file(font_name)
    # print(f"Selected TTF file: {ttf_path}")
    
    image_path = r"C:\Users\H3C\WorkSpace\GXC\DraftSculptor\assets\templates\签收单模板.jpg"
    data = {
    "文字": ["张三", "李四", "你好我是马泽宇"],
    "X": [283, 609, 1609],
    "Y": [628, 624, 635],
    "大小": [100, 100, 110],
    "字体": ["hand", "hand", "default"]
    }
    df = pd.DataFrame(data)
    draw(image_path, df)
