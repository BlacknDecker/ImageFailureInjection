import os
import cv2
import logging

import injectors.automold.Automold as am
from utils.FilePathManager import FilePathManager


class RandomSnowInjector:

    def __init__(self):
        pass

    def inject(self, original_img_path, out_folder):
        # open image
        logging.info(f"Processing: {FilePathManager.getFileName(original_img_path)}")
        original = cv2.imread(original_img_path)
        for i in range(10):
            injected = am.add_snow(original)
            # save
            new_name = FilePathManager.addInjectionName(original_img_path,
                                                        f"_RandomSnow_{i}".replace(".", "-"))
            logging.info(f"Saving: {new_name}")
            cv2.imwrite(os.path.join(out_folder, new_name), injected)

