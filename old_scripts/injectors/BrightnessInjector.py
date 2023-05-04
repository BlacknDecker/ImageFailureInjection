import os
from PIL import Image, ImageEnhance
import logging

from utils.FilePathManager import FilePathManager


class BrightnessInjector:

    def __init__(self):
        self.failure_name = "brightness"
        self.brightness_levels = [0, 0.3, 0.6, 1.5, 6, 7.5, 10, 15]
        # Save n of variants
        self.variants = len(self.brightness_levels)

    def inject(self, original_img_path, out_folder):
        logging.info(f"Processing: {FilePathManager.getFileName(original_img_path)}")
        original_img = Image.open(original_img_path)
        # apply brightness
        enhancer = ImageEnhance.Brightness(original_img)     # An enhancement factor of 0.0 gives a black image. A factor of 1.0 gives the original image.
        for factor in self.brightness_levels:
            logging.info(f"Applying Brightness factor: {factor}")
            injected_img = enhancer.enhance(factor)
            # save
            new_name = FilePathManager.addInjectionName(original_img_path, f"_Brightness_{factor}".replace(".", "-"))
            logging.info(f"Saving: {new_name}")
            out_dir = FilePathManager.getVariantOutputFolder(out_folder, self.brightness_levels.index(factor))
            injected_img.save(os.path.join(out_dir, new_name))


