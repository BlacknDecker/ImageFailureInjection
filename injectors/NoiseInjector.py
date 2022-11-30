import logging
import os
import cv2
import numpy as np

from utils.FilePathManager import FilePathManager


class NoiseInjector:

    def __init__(self):
        self.noise_factors = [0.2, 0.4, 0.6, 0.8, 1, 1.5, 2, 3, 4, 5]

    def inject(self, original_img_path, out_folder):
        # open image
        logging.info(f"Processing: {FilePathManager.getFileName(original_img_path)}")
        original = cv2.imread(original_img_path)
        # apply Speckle Noise
        for noise_level in self.noise_factors:
            logging.info(f"Appling Noise factor: {noise_level}")
            gauss = np.random.normal(0, noise_level, original.size)
            gauss = gauss.reshape((original.shape[0], original.shape[1], original.shape[2])).astype('uint8')
            noised = original + original * gauss
            # save
            new_name = FilePathManager.addInjectionName(original_img_path, f"_Noise_{noise_level}".replace(".", "-"))
            logging.info(f"Saving: {new_name}")
            cv2.imwrite(os.path.join(out_folder, new_name), noised)


