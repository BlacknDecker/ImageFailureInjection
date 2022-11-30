from PIL import Image
import os
import logging

from utils.FilePathManager import FilePathManager


class BandingInjector:

    def __init__(self, banding_patch_folder):
        self.banding_patch_paths = []
        self.blending_factors = [0.02, 0.05]    # FIXME: change if patch changes!
        # Check if provided folder exists
        if not os.path.exists(banding_patch_folder) or not os.path.isdir(banding_patch_folder):
            raise NotADirectoryError
        # Retrieve patches
        for filename in os.listdir(banding_patch_folder):
            if filename.endswith(".png") or filename.endswith(".jpg"):
                self.banding_patch_paths.append(os.path.join(banding_patch_folder, filename))

    def inject(self, original_img_path, out_folder):
        # open image
        logging.info(f"Processing: {FilePathManager.getFileName(original_img_path)}")
        original = Image.open(original_img_path)
        for i in range(len(self.banding_patch_paths)):
            patch_path = self.banding_patch_paths[i]
            logging.info(f"Appling Banding Patch: {os.path.basename(patch_path)}")
            patch = Image.open(patch_path).convert(original.mode)
            patch = patch.resize(original.size)
            patched = Image.blend(original, patch, self.blending_factors[i])
            # save
            patch_name = FilePathManager.getFileName(patch_path)
            new_name = FilePathManager.addInjectionName(original_img_path, f"_{patch_name.title()}")
            logging.info(f"Saving: {new_name}")
            patched.save(os.path.join(out_folder, new_name))

