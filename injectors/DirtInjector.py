from PIL import Image, ImageEnhance
import os
import logging

from utils.FilePathManager import FilePathManager


class DirtInjector:

    def __init__(self, dirt_patch_folder):
        self.dirt_patch_paths = []
        self.blending_factor = 0.5
        self.brightness_factor = 1.6
        # Check if provided folder exists
        if not os.path.exists(dirt_patch_folder) or not os.path.isdir(dirt_patch_folder):
            raise NotADirectoryError
        # Retrieve patches
        for filename in os.listdir(dirt_patch_folder):
            if filename.endswith(".png"):
                self.dirt_patch_paths.append(os.path.join(dirt_patch_folder, filename))

    def inject(self, original_img_path, out_folder):
        # open image
        logging.info(f"Processing: {FilePathManager.getFileName(original_img_path)}")
        original = Image.open(original_img_path)
        for patch_path in self.dirt_patch_paths:
            logging.info(f"Appling Dirt Patch: {os.path.basename(patch_path)}")
            patch = Image.open(patch_path).convert(original.mode)
            patch = patch.resize(original.size)
            patched = Image.blend(original, patch, self.blending_factor)
            enhancer = ImageEnhance.Brightness(patched)
            patched = enhancer.enhance(self.brightness_factor)
            # save
            patch_name = FilePathManager.getFileName(patch_path)
            new_name = FilePathManager.addInjectionName(original_img_path, f"_{patch_name.title()}")
            logging.info(f"Saving: {new_name}")
            patched.save(os.path.join(out_folder, new_name))


