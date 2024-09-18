import cv2
import numpy as np
import random

class Augmentation(object):
    def __init__(self, imgp, mode='default'):
        self.imgp = imgp
        self.mode = mode
        self.image = cv2.imread(imgp, cv2.IMREAD_GRAYSCALE)
        _, self.binary_image = cv2.threshold(self.image, 128, 255, cv2.THRESH_BINARY_INV)
        
    
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
                print(f"Ratio is {ratio}.")
                x_up, y_up = random.choice([0,1]), random.choice([0,1])
                if x_up and y_up:
                    print("UpUp")
                    return True if tarpoint[0] <= int(x+w*ratio) and tarpoint[1] <= int(y+h*ratio) else False
                elif x_up and not y_up:
                    print("UpDown")
                    return True if tarpoint[0] <= int(x+w*ratio) and tarpoint[1] > int(y+h*ratio) else False
                elif not x_up and y_up:
                    print("DownUp")
                    return True if tarpoint[0] > int(x+w*ratio) and tarpoint[1] <= int(y+h*ratio) else False
                else:
                    print("DownDown")
                    return True if tarpoint[0] > int(x+w*ratio) and tarpoint[1] > int(y+h*ratio) else False

            contour_points = [tuple(pt[0]) for pt in cnt if wrap_check(pt[0], x, y, w, h)]

            # Select a subset of points based on point_ratio
            try:
                selected_points = random.sample(contour_points, max(1, int(len(contour_points) * point_ratio)))
            except:
                pass
            points.extend(selected_points)

        return points
    
    def simulate_ink_spread_v3(self, spread_size=20, max_intensity=255, region_count=3, point_ratio=0.3):
        """
        Simulate ink spread for a few non-white pixels in a specified direction from detected corners/endpoints.

        :param image: Input binary image
        :param spread_size: How far the ink spreads from the center
        :param max_intensity: The maximum intensity for the ink (darker value)
        :param max_points: Maximum number of points for ink spread
        :return: Image with simulated ink spread
        """
        # Convert image to float for better manipulation
        
        direction = (random.randint(0,5), random.randint(0,5))
        direction = (0,2)
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

        return spread_image

    def simulate_ink_break(self, erosion_size=10, break_ratio=0.2):
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

            result_image = cv2.bitwise_not(result_image)
        return result_image

    def run(self):
        print(f"Processing {self.imgp}...")
        if self.mode == "default":
            is_spread = random.choice([0,1])
            is_spread = 0
        if is_spread:
            result_img = self.simulate_ink_spread_v3()
            return result_img
        else:
            result_img = self.simulate_ink_break()
            return result_img

if __name__ == "__main__":
    pass
    imgp = "/Users/mazeyu/NewEra/DraftSculptor/output.png"
    # while True:
    ag = Augmentation(imgp)
    
    res = ag.run()
    cv2.imwrite('result.png', res)
    
    