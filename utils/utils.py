import os
import pandas as pd
from PIL import Image
import numpy as np
import cv2

def root():
    starting_path = os.path.dirname(os.path.abspath(__file__))
    path_parts = starting_path.split(os.sep)
    for i in range(len(path_parts)):
        if path_parts[i] == 'DraftSculptor':
            return os.sep.join(path_parts[:i+1])
    return None

def pjoin(*x):
    return os.path.join(*x)

def check_format(df_):
    if os.path.exists(df_):
        file_name = df_
        if file_name.endswith('.xlsx'):
            df = pd.read_excel(file_name)
        elif file_name.endswith('.csv'):
            df = pd.read_csv(file_name)
        else:
            print("Unsupported file format.")
            return
    else:
        df = df_
    required_columns = {"文字", "X", "Y", "大小", "字体"}
    if not required_columns.issubset(df.columns):
        print("File does not contain the required columns.")
        return
    for i, row in df.iterrows():
        if not isinstance(row["文字"], (str, pd._libs.missing.NAType)):
            # print(f"Row {i+1}: '文字' should be a string or a file path.")
            row["文字"] = str(row["文字"])
        if not isinstance(row["X"], (int, float)):
            print(f"Row {i+1}: 'X' should be a number.")
            return
        if not isinstance(row["Y"], (int, float)):
            print(f"Row {i+1}: 'Y' should be a number.")
            return
        if not isinstance(row["大小"], (int, float)):
            print(f"Row {i+1}: '大小' should be a number.")
            return
        if not isinstance(row["字体"], str):
            print(f"Row {i+1}: '字体' should be a string.")
            return
    return df

def add_white_background(pil_img) -> np.ndarray:
    """
    Add a white background to a transparent PNG image and return the image in OpenCV format.

    Args:
        pil_img (PIL.Image.Image): Input transparent background image in PIL format.

    Returns:
        cv2_img (numpy.ndarray): Output image with a white background in OpenCV format.
    """
    # Ensure the image is in RGBA mode to handle transparency
    pil_img = pil_img.convert("RGBA")

    # Create a white background image with the same size as the original image
    white_bg = Image.new("RGBA", pil_img.size, (255, 255, 255, 255))

    # Paste the original image onto the white background
    white_bg.paste(pil_img, (0, 0), pil_img)

    # Convert the image to RGB (to remove alpha channel)
    pil_img_rgb = white_bg.convert("RGB")

    # Convert the PIL image to a NumPy array (which is in OpenCV format)
    cv2_img = np.array(pil_img_rgb)

    # Convert RGB to BGR format (OpenCV uses BGR format)
    cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_RGB2BGR)

    return cv2_img


def remove_white_background(image) -> Image:
    """
    Removes white background from an image by making white regions transparent.
    
    Args:
        image: Input image, either a cv2 image (numpy array) or a PIL image.

    Returns:
        Image: A PIL image with white background removed (transparent background).
    """
    # If input is a PIL image, convert it to an OpenCV image (numpy array)
    if isinstance(image, Image.Image):
        image = np.array(image)
        # Convert RGB to RGBA if the image does not have an alpha channel
        if image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)
    
    # Check if the input is already in RGBA
    elif image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

    # Define the white color range (adjust values as needed)
    lower_white = np.array([100, 100, 100, 0])  # Lower threshold for white
    upper_white = np.array([255, 255, 255, 255])  # Upper threshold for white

    # Create a mask where white areas are detected
    white_mask = cv2.inRange(image, lower_white, upper_white)

    # Set the alpha channel of the white areas to 0 (make it transparent)
    image[white_mask == 255] = [0, 0, 0, 0]

    # Convert the OpenCV image back to PIL format
    pil_image = Image.fromarray(cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_BGRA2RGBA))

    return pil_image


CHAR_MAP = [['a', 'A'], ['b', 'B'], ['c', 'C'], ['d', 'D'], ['e', 'E'], ['f', 'F'], ['g', 'G'], ['h', 'H'], ['i', 'I'], ['j', 'J'], ['k', 'K'], ['l', 'L'], ['m', 'M'], ['n', 'N'], ['o', 'O'], ['p', 'P'], ['q', 'Q'], ['r', 'R'], ['s', 'S'], ['t', 'T'], ['u', 'U'], ['v', 'V'], ['w', 'W'], ['x', 'X'], ['y', 'Y'], ['z', 'Z'], [',', '，'], ['.', '、'], ['(', '（'], [')', '）'], ['!', '！'], ['?', '？'], ['·', '、'], [' ', '空格'], ['-', '空格']]
LAY_CAHR_MAP = [item for sublist in CHAR_MAP for item in sublist]

def find_substitude(char: str) -> list:
    for pair in CHAR_MAP:
        if char in pair:
            for x in pair:
                if x != char:
                    return x
    return None

def can_substitude(char):
    return char in LAY_CAHR_MAP

def write_log(file_path, content):
    with open(file_path, 'a') as file:
        file.write(content + '\n')

    

if __name__ == "__main__":
    # draftsculptor_path = root()
    # if draftsculptor_path:
    #     print(f"'Draftsculptor' found at: {draftsculptor_path}")
    # else:
    #     print("'Draftsculptor' directory not found.")
    # print(pjoin("a", "b"))

    # img = Image.open(r'C:\Users\H3C\WorkSpace\GXC\DraftSculptor\assets\imgs\张\char0.png')
    # white_back = add_white_background(img)
    # cv2.imwrite("white_back.png", white_back)
    imgp = r"C:\Users\H3C\WorkSpace\GXC\DraftSculptor\xxx.png"
    img = Image.open(imgp)
    img_png = remove_white_background(img)
    img_png.save("img_png.png")