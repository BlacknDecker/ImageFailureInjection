from PIL import Image
from numpy import*
import cv2
import logging
import os

from utils.FilePathManager import FilePathManager


class NodemosInjector:

    def __init__(self):
        pass

    def inject(self, original_img_path, out_folder):
        # open image
        logging.info(f"Processing: {FilePathManager.getFileName(original_img_path)}")
        original = cv2.imread(original_img_path)
        logging.info(f"Appling Nodemos")
        width, height, _ = original.shape
        # Create target array, twice the size of the original image
        resArray = zeros((2 * width, 2 * height, 3), dtype=uint8)
        # Map the RGB values in the original picture according to the BGGR pattern#
        # Blue
        resArray[::2, ::2, 2] = original[:, :, 2]
        # Green (top row of the Bayer matrix)
        resArray[1::2, ::2, 1] = original[:, :, 1]
        # Green (bottom row of the Bayer matrix)
        resArray[::2, 1::2, 1] = original[:, :, 1]
        # Red
        resArray[1::2, 1::2, 0] = original[:, :, 0]
        # Standardize
        resArray = cv2.cvtColor(resArray, cv2.COLOR_BGR2RGB)
        # Save
        injected = Image.fromarray(resArray, "RGB")
        new_name = FilePathManager.addInjectionName(original_img_path, f"_Nodemos")
        logging.info(f"Saving: {new_name}")
        injected.save(os.path.join(out_folder, new_name))

