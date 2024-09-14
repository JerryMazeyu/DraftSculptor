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

def solution_helper(chara_dict):
        combined_list = [item for sublist in chara_dict.values() for item in sublist]
        freq = Counter(combined_list)
        max_frequency = max(freq.values())
        max_frequency_items = [item for item, count in freq.items() if count == max_frequency]
        solution = random.choice(max_frequency_items)
        result = {}
        for k,v in chara_dict.items():
            if solution[0] in v:
                result[k] = solution
            else:
                result[k] = random.choice(v)
        return result

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
    directory = pjoin(root(), 'assets')

    solutions = find_all_combinations(directory, text)
    if solutions == []:
        return Image.new('RGBA', (font_height, font_height), (255, 255, 255, 0))
    else:
        solution = random.choice(solutions)
        solution_dict = {}
        for chara in solution:
            chara_imgs = os.listdir(pjoin(directory, chara))
            chara_names = [x.split('.') for x in chara_imgs if x.endswith('.png')]
            solution_dict[chara] = chara_names
        solution = solution_helper(solution_dict)
        for char, img_name in solution.items():
            char_path = pjoin(directory, char, f"img_name.png")
            pass
        


    def find_images_for_character(character: str):
        """
        Helper function to find all images for a single character.
        """
        char_path = os.path.join(directory, character)
        if os.path.exists(char_path) and os.path.isdir(char_path):
            images = os.listdir(char_path)
            return [img for img in images if img.endswith('.png')]
        return []
    
    # Try to find the entire word as a single directory
    text_path = os.path.join(path, text)
    if os.path.exists(text_path) and os.path.isdir(text_path):
        # If a folder for the whole text exists, randomly select one image from it
        images = os.listdir(text_path)
        matched_images = [img for img in images if img.endswith('.png')]
        if matched_images:
            selected_image = random.choice(matched_images)
            image_path = os.path.join(text_path, selected_image)
            image = Image.open(image_path)
            # Resize by keeping the height fixed to `font_height`
            aspect_ratio = image.width / image.height
            new_width = int(aspect_ratio * font_height)
            resized_image = image.resize((new_width, font_height))
            return resized_image
    
    # If the entire word doesn't exist, split the text into characters and combine their images
    char_images = []
    for char in text:
        char_images.append(find_images_for_character(char))
    
    if not all(char_images):
        raise ValueError(f"Could not find images for all characters in '{text}'")
    
    # Choose matching images if possible, otherwise randomly select
    first_char_images = char_images[0]
    second_char_images = char_images[1]
    
    combined_image = None
    for first_image in first_char_images:
        if first_image in second_char_images:
            # If there's a matching image, select it for both characters
            first_image_path = os.path.join(path, text[0], first_image)
            second_image_path = os.path.join(path, text[1], first_image)
            first_img = Image.open(first_image_path)
            second_img = Image.open(second_image_path)
            combined_image = (first_img, second_img)
            break
    
    if not combined_image:
        # If no matching images, select randomly
        first_image_path = os.path.join(path, text[0], random.choice(first_char_images))
        second_image_path = os.path.join(path, text[1], random.choice(second_char_images))
        first_img = Image.open(first_image_path)
        second_img = Image.open(second_image_path)
        combined_image = (first_img, second_img)
    
    # Resize both images by height and combine horizontally
    first_img, second_img = combined_image
    aspect_ratio_1 = first_img.width / first_img.height
    aspect_ratio_2 = second_img.width / second_img.height
    new_width_1 = int(aspect_ratio_1 * font_height)
    new_width_2 = int(aspect_ratio_2 * font_height)
    first_img = first_img.resize((new_width_1, font_height))
    second_img = second_img.resize((new_width_2, font_height))
    
    # Create a new image with the combined width
    combined_width = new_width_1 + new_width_2
    combined_image = Image.new('RGBA', (combined_width, font_height))
    
    # Paste the two images side by side
    combined_image.paste(first_img, (0, 0))
    combined_image.paste(second_img, (new_width_1, 0))
    
    return combined_image

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
    for _, row in conf.iterrows():
        text = str(row['文字'])
        x = int(row['X'])
        y = int(row['Y'])
        size = int(row['大小'])
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
    
    # image_path = "/Users/mazeyu/NewEra/DraftSculptor/assets/templates/签收单模板.jpg"
    # data = {
    # "文字": ["Hello", "World", "测试", "Python", "图像"],
    # "X": [50, 150, 250, 350, 450],
    # "Y": [50, 150, 250, 350, 450],
    # "大小": [200, 300, 400, 500, 660],
    # "字体": ["Arial", "default", "default", "Courier", "default"]
    # }
    # df = pd.DataFrame(data)
    # draw(image_path, df)

    # handwrite_path = r"C:\Users\H3C\WorkSpace\GXC\DraftSculptor\assets\imgs"
    # text = "da"
    # combinations = find_all_combinations(handwrite_path, text)
    # print(combinations)
    from collections import Counter

    def find_max_common_combinations(chara_dict):
        combined_list = [item for sublist in chara_dict.values() for item in sublist]
        freq = Counter(combined_list)
        max_frequency = max(freq.values())
        max_frequency_items = [item for item, count in freq.items() if count == max_frequency]
        solution = random.choice(max_frequency_items)
        result = {}
        for k,v in chara_dict.items():
            if solution[0] in v:
                result[k] = solution
            else:
                result[k] = random.choice(v)
        return result



    example_dict = {
    "A": ['a', 'b', 'c'],
    "B": ['a', 'c', 'd'],
    "C": ['1', '2', '3']
    }

    result = find_max_common_combinations(example_dict)
    for combo in result:
        print(combo)