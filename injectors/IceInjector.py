import logging
from PIL import Image, ImageEnhance
import os

from utils.FilePathManager import FilePathManager


class IceInjector:

    def __init__(self, ice_patch_folder):
        self.ice_patch_paths = []
        self.blending_factor = 0.2
        self.brightness_factor = 1.6
        # Check if provided folder exists
        if not os.path.exists(ice_patch_folder) or not os.path.isdir(ice_patch_folder):
            raise NotADirectoryError
        # Retrieve patches
        for filename in os.listdir(ice_patch_folder):
            if filename.endswith(".png"):
                self.ice_patch_paths.append(os.path.join(ice_patch_folder, filename))

    def inject(self, original_img_path, out_folder):
        # open image
        logging.info(f"Processing: {FilePathManager.getFileName(original_img_path)}")
        original = Image.open(original_img_path)
        for patch_path in self.ice_patch_paths:
            logging.info(f"Appling Ice Patch: {os.path.basename(patch_path)}")
            # patch = Image.open(patch_path).convert(original.mode)
            # patch = patch.resize(original.size)
            # patched = Image.blend(original, patch, self.blending_factor)
            # enhancer = ImageEnhance.Brightness(patched)
            # patched = enhancer.enhance(self.brightness_factor)
            patched = original.copy()
            patch = Image.open(patch_path).convert("RGBA")
            patched.paste(patch, (0, 0), patch)
            # save
            patch_name = FilePathManager.getFileName(patch_path)
            new_name = FilePathManager.addInjectionName(original_img_path, f"_{patch_name.title()}")
            logging.info(f"Saving: {new_name}")
            patched.save(os.path.join(out_folder, new_name))


