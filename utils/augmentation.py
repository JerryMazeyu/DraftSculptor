import cv2
import numpy as np
import random
from PIL import Image

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


class Augmentation(object):
    def __init__(self, source, mode='default'):
        
        if isinstance(source, str):  # image path
            self.imgp = imgp
            self.image = cv2.imread(imgp, cv2.IMREAD_GRAYSCALE)
        elif isinstance(source, Image.Image):  # PIL
            if source.mode == 'RGBA':
                self.image = add_white_background(source)
            else:
                self.image = np.array(source)                
        else:  # cv2
            self.image = source
        
        self.mode = mode
        # self.image = cv2.imread(imgp, cv2.IMREAD_GRAYSCALE)
        _, self.binary_image = cv2.threshold(self.image, 128, 255, cv2.THRESH_BINARY_INV)
        if len(self.binary_image.shape) == 3:
            self.binary_image = cv2.cvtColor(self.binary_image, cv2.COLOR_RGB2GRAY)
        
    
    def _find_ink_spread_points(self, threshold=50, region_count=3, point_ratio=0.2,  box_size=20):
        """
        Find small regions where ink spread might start, and select a portion of the points within each region.

        :param image: Input binary image (inverted: text is white, background is black)
        :param threshold: Canny edge detection threshold
        :param region_count: Number of small regions to select
        :param point_ratio: The ratio of points in each region that will spread ink
        :return: List of points where ink spread might start
        """
        # Use Canny edge detection to find edges in the image
        edges = cv2.Canny(self.image, threshold, threshold * 2)
        
        # Find contours from the edges
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Sort contours by area to find larger writing regions
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        # Limit the number of regions based on region_count
        
        selected_contours = random.choices(contours, k=region_count)
        
        points = []
        for cnt in selected_contours:
            # For each contour, flatten it to get all the points
            x, y, w, h = cv2.boundingRect(cnt)
            
            def wrap_check(tarpoint, x, y, w, h):
                ratio = random.uniform(0.2, 0.8)
                x_up, y_up = random.choice([0,1]), random.choice([0,1])
                if x_up and y_up:
                    return True if tarpoint[0] <= int(x+w*ratio) and tarpoint[1] <= int(y+h*ratio) else False
                elif x_up and not y_up:
                    return True if tarpoint[0] <= int(x+w*ratio) and tarpoint[1] > int(y+h*ratio) else False
                elif not x_up and y_up:
                    return True if tarpoint[0] > int(x+w*ratio) and tarpoint[1] <= int(y+h*ratio) else False
                else:
                    return True if tarpoint[0] > int(x+w*ratio) and tarpoint[1] > int(y+h*ratio) else False

            contour_points = [tuple(pt[0]) for pt in cnt if wrap_check(pt[0], x, y, w, h)]

            # Select a subset of points based on point_ratio
            try:
                selected_points = random.sample(contour_points, max(1, int(len(contour_points) * point_ratio)))
            except:
                pass
            points.extend(selected_points)

        return points
    
    def simulate_ink_spread_v3(self, spread_size=20, max_intensity=255, region_count=3, point_ratio=0.6):
        """
        Simulate ink spread for a few non-white pixels in a specified direction from detected corners/endpoints.
        
        return: Image with simulated ink spread
        """
        # Convert image to float for better manipulation
        
        direction = (random.randint(0,5), random.randint(0,5))
        # direction = (0,2)
        print(f"Direction is {direction}.")
        spread_image = self.binary_image.copy().astype(np.float32)

        # Find a few points where ink spread should start (non-white areas)
        try:
            spread_points = self._find_ink_spread_points(region_count=region_count, point_ratio=point_ratio)
        except:
            print("Can not find ink spread.")
            return self.binary_image
        
        # Create an empty mask to accumulate the spread effect
        mask = np.zeros_like(spread_image, dtype=np.float32)

        # Get direction for spreading
        dx, dy = direction
        
        for point in spread_points:
            cx, cy = point

            # Create the spread effect for each selected point
            for i in range(spread_size):
                intensity = max_intensity * (1 - i / spread_size)
                nx, ny = int(cx + dx * i), int(cy + dy * i)
                
                # Ensure the spread stays within image bounds
                if 0 <= nx < self.binary_image.shape[1] and 0 <= ny < self.binary_image.shape[0]:
                    if spread_image[ny, nx] != 255:  # Only apply to non-white pixels
                        mask[ny, nx] = max(mask[ny, nx], intensity)

        # Subtract mask from the original image to simulate ink spread
        spread_image += mask
        spread_image = 255 - spread_image
        # spread_image = np.clip(spread_image, 0, 255).astype(np.uint8)
        spread_image = cv2.cvtColor(spread_image, cv2.COLOR_GRAY2RGB)
        return spread_image

    def simulate_ink_break(self, erosion_size=5, break_ratio=0.2):
        """
        Simulate ink breakage by applying erosion to a random part of the connected components (contours).
        
        :param image: Input binary image (inverted: text is white, background is black)
        :param erosion_size: Size of the erosion kernel
        :param break_ratio: Ratio of the connected component to apply the break (0 to 1)
        :return: Image with simulated ink break
        """
        # Step 1: Detect connected components (contours)
        contours, _ = cv2.findContours(self.binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Step 2: Create an erosion kernel
        kernel = np.ones((erosion_size, erosion_size), np.uint8)

        # Step 3: Copy the original image for processing
        result_image = self.binary_image.copy()

        # Step 4: Loop over each contour (connected component)
        for cnt in contours:
            # Get bounding box for each contour
            x, y, w, h = cv2.boundingRect(cnt)
            
            # Create a subregion of the contour to apply erosion
            break_region_width = int(w * break_ratio)
            break_region_height = int(h * break_ratio)
            
            # Randomly select the starting point for the break region
            break_x = random.randint(x, x + w - break_region_width)
            break_y = random.randint(y, y + h - break_region_height)
            
            # Define the subregion to erode
            break_region = result_image[break_y:break_y + break_region_height, break_x:break_x + break_region_width]
            
            # Step 5: Apply erosion to the selected subregion
            eroded_region = cv2.erode(break_region, kernel, iterations=1)
            
            # Step 6: Replace the eroded region back into the original image
            result_image[break_y:break_y + break_region_height, break_x:break_x + break_region_width] = eroded_region
            # result_image = cv2.bitwise_not(result_image)
        result_image = 255 - result_image
        result_image = cv2.cvtColor(result_image, cv2.COLOR_GRAY2RGB)
        return result_image

    def run(self):
        if self.mode == "default":
            is_spread = random.choice([0,1])
        if is_spread:
            print("Spread augmentation.")
            result_img = self.simulate_ink_spread_v3()
        else:
            print("Break augmentation.")
            result_img = self.simulate_ink_break()
        result_img = remove_white_background(Image.fromarray(result_img.astype(np.uint8)))
        return result_img

if __name__ == "__main__":
    pass
    imgp = r"C:\Users\H3C\WorkSpace\GXC\DraftSculptor\output_text.png"
    img_pil = Image.open(imgp)
    # while True:
    ag = Augmentation(img_pil)
    
    res = ag.run()
    res.save('result.png')
    
    