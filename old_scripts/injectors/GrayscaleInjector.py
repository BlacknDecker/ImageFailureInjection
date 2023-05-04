import numpy as np
import logging
from matplotlib import pyplot as plt
from matplotlib import image as mpimg
import os

from utils.FilePathManager import FilePathManager


class GrayscaleInjector:

    def __init__(self):
        self.failure_name = "grayscale"
        # Save n of variants
        self.variants = 1

    def inject(self, original_img_path, out_folder):
        # open image
        logging.info(f"Processing: {FilePathManager.getFileName(original_img_path)}")
        original = mpimg.imread(original_img_path)
        logging.info(f"Applying Grayscale")
        gray = self.__rgb2gray(original)
        # save
        new_name = FilePathManager.addInjectionName(original_img_path, f"_Grayscale")
        logging.info(f"Saving: {new_name}")
        out_dir = FilePathManager.getVariantOutputFolder(out_folder, 0)
        plt.imsave(os.path.join(out_dir, new_name), gray)

    def __rgb2gray(self, rgb):
        return np.dot(rgb[..., :3], [0.2989, 0.5870, 0.1140])
