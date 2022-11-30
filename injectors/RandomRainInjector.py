import os
import logging
import cv2

import injectors.automold.Automold as am
from utils.FilePathManager import FilePathManager


class RandomRainInjector:

    def __init__(self):
        self.rain_types = ['drizzle', 'heavy', 'torrential']

    def inject(self, original_img_path, out_folder):
        # open image
        logging.info(f"Processing: {FilePathManager.getFileName(original_img_path)}")
        original = cv2.imread(original_img_path)
        for rain in self.rain_types:
            logging.info(f"Appling {rain.title()} Rain")
            for i in range(10):
                injected = am.add_rain(original, rain_type=rain)
                # save
                new_name = FilePathManager.addInjectionName(original_img_path,
                                                            f"_Rain{rain.title()}_{i}")
                logging.info(f"Saving: {new_name}")
                cv2.imwrite(os.path.join(out_folder, new_name), injected)

