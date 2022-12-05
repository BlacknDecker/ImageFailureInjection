from PIL import Image, ImageEnhance
import os
import logging

from utils.FilePathManager import FilePathManager


class BreakageInjector:

    def __init__(self, breakage_patch_folder):
        self.failure_name = "lensBreakage"
        self.break_patch_paths = []
        self.blending_factor = 0.5
        self.brightness_factor = 1.6
        # Check if provided folder exists
        if not os.path.exists(breakage_patch_folder) or not os.path.isdir(breakage_patch_folder):
            raise NotADirectoryError
        # Retrieve patches
        for filename in os.listdir(breakage_patch_folder):
            if filename.endswith(".png"):
                self.break_patch_paths.append(os.path.join(breakage_patch_folder, filename))
        # Save n of variants
        self.variants = len(self.break_patch_paths)

    def inject(self, original_img_path, out_folder):
        # open image
        logging.info(f"Processing: {FilePathManager.getFileName(original_img_path)}")
        original = Image.open(original_img_path)
        for patch_path in self.break_patch_paths:
            logging.info(f"Applying Breakage Patch: {os.path.basename(patch_path)}")
            patch = Image.open(patch_path).convert(original.mode)
            patch = patch.resize(original.size)
            patched = Image.blend(original, patch, self.blending_factor)
            enhancer = ImageEnhance.Brightness(patched)
            patched = enhancer.enhance(self.brightness_factor)
            # save
            patch_name = FilePathManager.getFileName(patch_path)
            new_name = FilePathManager.addInjectionName(original_img_path, f"_{patch_name.title()}")
            logging.info(f"Saving: {new_name}")
            out_dir = FilePathManager.getVariantOutputFolder(out_folder, self.break_patch_paths.index(patch_path))
            patched.save(os.path.join(out_dir, new_name))


