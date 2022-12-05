import os
import logging
import random
import cv2
import injectors.automold.Automold as am
import injectors.automold.Helpers as hp

from utils.FilePathManager import FilePathManager


class FlareInjector:

    def __init__(self):
        self.failure_name = "flare"
        # Save n of variants
        self.variants = 1

    def inject(self, original_img_path, out_folder):
        # open image
        logging.info(f"Processing: {FilePathManager.getFileName(original_img_path)}")
        original = cv2.imread(original_img_path)
        flare_angle = random.randint(1, 100)
        flare_radius = random.randrange(250, 400, 50)
        logging.info(f"Applying Flare: Angle {flare_angle}, Radius {flare_radius}")
        flare_image = am.add_sun_flare(original, flare_center=-1, angle=flare_angle, no_of_flare_circles=4,
                                       src_radius=flare_radius)
        # save
        new_name = FilePathManager.addInjectionName(original_img_path, f"_Flare_A{flare_angle}_R{flare_radius}".replace(".", "-"))
        logging.info(f"Saving: {new_name}")
        out_dir = FilePathManager.getVariantOutputFolder(out_folder, 0)
        cv2.imwrite(os.path.join(out_dir, new_name), flare_image)
