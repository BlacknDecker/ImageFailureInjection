import os
import logging
import cv2

import old_scripts.injectors.automold.Automold as am
from utils.FilePathManager import FilePathManager


class RandomRainInjector:

    def __init__(self):
        self.failure_name = "randomRain"
        self.rain_types = ['drizzle', 'heavy', 'torrential']
        self.variants_per_rain_type = 5
        # Save n of variants
        self.variants = len(self.rain_types) * self.variants_per_rain_type

    def inject(self, original_img_path, out_folder):
        # open image
        logging.info(f"Processing: {FilePathManager.getFileName(original_img_path)}")
        original = cv2.imread(original_img_path)
        var_count = 0
        for rain in self.rain_types:
            logging.info(f"Applying {rain.title()} Rain")
            for i in range(self.variants_per_rain_type):
                injected = am.add_rain(original, rain_type=rain)
                # save
                new_name = FilePathManager.addInjectionName(original_img_path, f"_Rain{rain.title()}_{i}")
                logging.info(f"Saving: {new_name}")
                out_dir = FilePathManager.getVariantOutputFolder(out_folder, var_count)
                var_count += 1
                cv2.imwrite(os.path.join(out_dir, new_name), injected)

