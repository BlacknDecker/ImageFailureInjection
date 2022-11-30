from PIL import Image, ImageEnhance
import os
import logging

from utils.FilePathManager import FilePathManager


class SharpnessInjector:

    def __init__(self):
        self.sharpness_factors = [-5, -4, -3, -2, -1, 0]

    def inject(self, original_img_path, out_folder):
        # open image
        logging.info(f"Processing: {FilePathManager.getFileName(original_img_path)}")
        original = Image.open(original_img_path)
        for factor in self.sharpness_factors:
            logging.info(f"Appling Sharpness Factor: {factor}")
            enhancer = ImageEnhance.Sharpness(original)
            injected = enhancer.enhance(factor)
            # save
            new_name = FilePathManager.addInjectionName(original_img_path, f"_Sharpness_{factor}".replace(".", "-"))
            logging.info(f"Saving: {new_name}")
            injected.save(os.path.join(out_folder, new_name))
