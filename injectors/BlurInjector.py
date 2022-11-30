import os
import cv2
import logging

from utils.FilePathManager import FilePathManager


class BlurInjector:

    def __init__(self):
        self.blurring_range = 30

    def inject(self, original_img_path, out_folder):
        # open image
        logging.info(f"Processing: {FilePathManager.getFileName(original_img_path)}")
        img = cv2.imread(original_img_path)
        # apply blur
        for i in range(1, self.blurring_range):
            logging.info(f"Appling Blurring factor: {i}")
            blurred = cv2.blur(img, (i, i))
            # save
            new_name = FilePathManager.addInjectionName(original_img_path, f"_Blur_{i}-{i}")
            logging.info(f"Saving: {new_name}")
            cv2.imwrite(os.path.join(out_folder, new_name), blurred)



