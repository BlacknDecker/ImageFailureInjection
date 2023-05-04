import os
import cv2
import logging

import old_scripts.injectors.automold.Automold as am
from utils.FilePathManager import FilePathManager


class RandomSnowInjector:

    def __init__(self):
        self.failure_name = "randomSnow"
        # Save n of variants
        self.variants = 10

    def inject(self, original_img_path, out_folder):
        # open image
        logging.info(f"Processing: {FilePathManager.getFileName(original_img_path)}")
        original = cv2.imread(original_img_path)
        for i in range(self.variants):
            injected = am.add_snow(original)
            # save
            new_name = FilePathManager.addInjectionName(original_img_path, f"_RandomSnow_{i}".replace(".", "-"))
            logging.info(f"Saving: {new_name}")
            out_dir = FilePathManager.getVariantOutputFolder(out_folder, i)
            cv2.imwrite(os.path.join(out_dir, new_name), injected)

