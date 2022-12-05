import os
import cv2
import logging

from utils.FilePathManager import FilePathManager


class BlurInjector:

    def __init__(self):
        self.failure_name = "blur"
        self.blurring_range = 30
        # Save n of variants
        self.variants = self.blurring_range

    def inject(self, original_img_path, out_folder):
        # open image
        logging.info(f"Processing: {FilePathManager.getFileName(original_img_path)}")
        img = cv2.imread(original_img_path)
        # apply blur
        for i in range(1, self.variants + 1):
            logging.info(f"Applying Blurring factor: {i}")
            blurred = cv2.blur(img, (i, i))
            # save
            new_name = FilePathManager.addInjectionName(original_img_path, f"_Blur_{i}")
            logging.info(f"Saving: {new_name}")
            out_dir = FilePathManager.getVariantOutputFolder(out_folder, i)
            cv2.imwrite(os.path.join(out_dir, new_name), blurred)



