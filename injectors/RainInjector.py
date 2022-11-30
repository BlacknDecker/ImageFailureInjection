import logging
from PIL import Image, ImageEnhance
import os

from utils.FilePathManager import FilePathManager


class RainInjector:

    def __init__(self, rain_patch_folder):
        self.rain_patch_paths = []
        self.blending_factor = 0.5
        self.brightness_factor = 1.6
        # Check if provided folder exists
        if not os.path.exists(rain_patch_folder) or not os.path.isdir(rain_patch_folder):
            raise NotADirectoryError
        # Retrieve patches
        for filename in os.listdir(rain_patch_folder):
            if filename.endswith(".png"):
                self.rain_patch_paths.append(os.path.join(rain_patch_folder, filename))

    def inject(self, original_img_path, out_folder):
        # open image
        logging.info(f"Processing: {FilePathManager.getFileName(original_img_path)}")
        original = Image.open(original_img_path)
        for patch_path in self.rain_patch_paths:
            logging.info(f"Appling Rain Patch: {os.path.basename(patch_path)}")
            patch = Image.open(patch_path).convert("RGBA")
            patch = patch.resize(original.size)
            # Metodo classico
            # patched = Image.blend(original, patch, self.blending_factor)
            # enhancer = ImageEnhance.Brightness(patched)
            # patched = enhancer.enhance(self.brightness_factor)
            # Metodo alternativo
            patched = original.copy()
            patched.paste(patch, (0, 0), patch)
            # save
            patch_name = FilePathManager.getFileName(patch_path)
            new_name = FilePathManager.addInjectionName(original_img_path, f"_{patch_name.title()}")
            logging.info(f"Saving: {new_name}")
            patched.save(os.path.join(out_folder, new_name))





