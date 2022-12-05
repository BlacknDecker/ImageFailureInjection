from PIL import Image
import os
import logging

from utils.FilePathManager import FilePathManager


class CondensationInjector:

    def __init__(self, condensation_patch_folder):
        self.failure_name = "condensation"
        self.condensation_patch_paths = []
        # Check if provided folder exists
        if not os.path.exists(condensation_patch_folder) or not os.path.isdir(condensation_patch_folder):
            raise NotADirectoryError
        # Retrieve patches
        for filename in os.listdir(condensation_patch_folder):
            if filename.endswith(".png"):
                self.condensation_patch_paths.append(os.path.join(condensation_patch_folder, filename))
        # Save n of variants
        self.variants = len(self.condensation_patch_paths)

    def inject(self, original_img_path, out_folder):
        # open image
        logging.info(f"Processing: {FilePathManager.getFileName(original_img_path)}")
        original = Image.open(original_img_path)
        for patch_path in self.condensation_patch_paths:
            logging.info(f"Applying Condensation Patch: {os.path.basename(patch_path)}")
            patch = Image.open(patch_path).convert("RGBA")
            patch = patch.resize(original.size)
            patched = original.copy()
            patched.paste(patch, (0, 0), patch)
            # save
            patch_name = FilePathManager.getFileName(patch_path)
            new_name = FilePathManager.addInjectionName(original_img_path, f"_{patch_name.title()}")
            logging.info(f"Saving: {new_name}")
            out_dir = FilePathManager.getVariantOutputFolder(out_folder, self.condensation_patch_paths.index(patch_path))
            patched.save(os.path.join(out_dir, new_name))
