import cv2
import logging
from PIL import Image
from random import seed
from random import randint
import os

from utils.FilePathManager import FilePathManager


class DeadPixelsInjector:

    def __init__(self):
        self.failure_name = "deadPixels"
        self.seed = 1
        self.pixels_configuration = [1, 50, 200, 500, 1000]
        # Save n of variants
        self.variants = len(self.pixels_configuration) + 2

    def inject(self, original_img_path, out_folder):
        # open image
        logging.info(f"Processing: {FilePathManager.getFileName(original_img_path)}")
        original = cv2.imread(original_img_path)
        # Apply random dead_pixels
        var_count = 0
        for dead_pixels in self.pixels_configuration:
            logging.info(f"Applying Random Dead Pixels: {dead_pixels}")
            degraded = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
            height, width, _ = degraded.shape
            for pixel in range(dead_pixels):
                x = randint(1, height-1)
                y = randint(1, width-1)
                degraded[x, y] = (0, 0, 0)   # blank pixel
            # Save
            degraded = Image.fromarray(degraded)    # Convert matrix to Image
            new_name = FilePathManager.addInjectionName(original_img_path, f"_DeadPixels_{dead_pixels}")
            out_dir = FilePathManager.getVariantOutputFolder(out_folder, var_count)
            var_count += 1
            degraded.save(os.path.join(out_dir, new_name))
        # Apply blank lines
        logging.info(f"Applying Random Blank Lines")
        for conf in ["DeadPixelsVCL", "DeadPixels3L"]:
            degraded = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
            height, width, _ = degraded.shape
            if conf == "DeadPixelsVCL":
                # Vertical Central Line
                y = int(width/2)
                degraded[:, y] = (0, 0, 0)
            elif conf == "DeadPixels3L":
                # 3 Lines: 2 vertical and 1 Horizontal
                x = int(height/2)
                y = int(width/2)
                degraded[:, y] = (0, 0, 0)
                degraded[x + 100, :] = (0, 0, 0)
                degraded[x - 100, :] = (0, 0, 0)
            # Save
            degraded = Image.fromarray(degraded)  # Convert matrix to Image
            new_name = FilePathManager.addInjectionName(original_img_path, f"_{conf}")
            out_dir = FilePathManager.getVariantOutputFolder(out_folder, var_count)
            var_count += 1
            degraded.save(os.path.join(out_dir, new_name))


