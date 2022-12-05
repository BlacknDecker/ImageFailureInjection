from PIL import Image, ImageEnhance
import os
import logging

from utils.FilePathManager import FilePathManager


class SharpnessInjector:

    def __init__(self):
        self.failure_name = "sharpness"
        self.sharpness_factors = [-5, -4, -3, -2, -1, 0]
        # Save n of variants
        self.variants = self.sharpness_factors

    def inject(self, original_img_path, out_folder):
        # open image
        logging.info(f"Processing: {FilePathManager.getFileName(original_img_path)}")
        original = Image.open(original_img_path)
        for factor in self.sharpness_factors:
            logging.info(f"Applying Sharpness Factor: {factor}")
            enhancer = ImageEnhance.Sharpness(original)
            injected = enhancer.enhance(factor)
            # save
            new_name = FilePathManager.addInjectionName(original_img_path, f"_Sharpness_{factor}".replace(".", "-"))
            logging.info(f"Saving: {new_name}")
            out_dir = FilePathManager.getVariantOutputFolder(out_folder, self.sharpness_factors.index(factor))
            injected.save(os.path.join(out_dir, new_name))
