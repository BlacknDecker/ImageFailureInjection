import os
import logging
import shutil

from injectors.BandingInjector import BandingInjector
from injectors.BlurInjector import BlurInjector
from injectors.BreakageInjector import BreakageInjector
from injectors.BrightnessInjector import BrightnessInjector
from injectors.ChromaticAberrationInjector import ChromaticAberrationInjector
from injectors.CondensationInjector import CondensationInjector
from injectors.DeadPixelsInjector import DeadPixelsInjector
from injectors.DirtInjector import DirtInjector
from injectors.FlareInjector import FlareInjector
from injectors.GrayscaleInjector import GrayscaleInjector
from injectors.IceInjector import IceInjector
from injectors.NodemosInjector import NodemosInjector
from injectors.NoiseInjector import NoiseInjector
from injectors.RainInjector import RainInjector
from injectors.RandomRainInjector import RandomRainInjector
from injectors.SharpnessInjector import SharpnessInjector


class InjectionManager:

    def __init__(self):
        self.output_folder = os.path.join(os.getcwd(), "output")
        self.injectors = {
            "brightness": BrightnessInjector(),
            "blur": BlurInjector(),
            "banding": BandingInjector(os.path.join(os.getcwd(), "injectors", "banding")),
            "lensBreakage": BreakageInjector(os.path.join(os.getcwd(), "injectors", "lensBroken")),
            "chromaticAberration": ChromaticAberrationInjector(),  # NB: VERY slow!
            "condensation": CondensationInjector(os.path.join(os.getcwd(), "injectors", "condensation")),
            "deadPixels": DeadPixelsInjector(),
            "dirt": DirtInjector(os.path.join(os.getcwd(), "injectors", "lensDirt")),
            "grayscale": GrayscaleInjector(),
            "ice": IceInjector(os.path.join(os.getcwd(), "injectors", "ice")),
            "nodemos": NodemosInjector(),
            "noise": NoiseInjector(),
            "rain": RainInjector(os.path.join(os.getcwd(), "injectors", "rain")),
            "sharpness": SharpnessInjector(),
            "flare": FlareInjector()
            # "randomRain": RandomRainInjector()
        }
        self.failure_variants = {
            "brightness": 8,
            "blur": 29,
            "banding": 2,
            "lensBreakage": 15,
            "chromaticAberration": 1,
            "condensation": 3,
            "deadPixels": 7,
            "dirt": 36,
            "grayscale": 1,
            "ice": 4,
            "nodemos": 1,
            "noise": 10,
            "rain": 5,
            "sharpness": 6,
            "flare": 1
            # "randomRain": RandomRainInjector()
        }

    def processSequence(self, sequence_folder, failures=None):
        # Get sequence name (folder name)
        seq_name = os.path.basename(sequence_folder)
        # Get frames
        frames_path = []
        for filename in os.listdir(sequence_folder):
            if filename.endswith(".png"):
                frames_path.append(os.path.join(sequence_folder, filename))
        # Create output directory
        out_path = os.path.join(self.output_folder, seq_name)
        os.mkdir(out_path)
        # For every (selected) failure -> process every frame
        if failures is None:
            failures = self.injectors.keys()
        for failure in failures:
            # create failure folder
            failure_folder = os.path.join(out_path, failure)
            os.mkdir(failure_folder)
            variants_folder = []
            for i in range(self.failure_variants[failure]):
                var_folder = os.path.join(failure_folder, f"variant_{i}")
                os.mkdir(var_folder)
                variants_folder.append(var_folder)
            # process frames
            for frame in frames_path:
                # process frame
                self.injectors[failure].inject(frame, failure_folder)
                # divide failure variations into subfolders
                processed_frames = []
                for filename in os.listdir(failure_folder):
                    if filename.endswith(".png"):
                        processed_frames.append(filename)
                if len(processed_frames) != self.failure_variants[failure]:
                    raise Exception("Failure Variants Mismatch!")
                else:
                    # move to folder
                    for i in range(self.failure_variants[failure]):
                        src_p = os.path.join(failure_folder, processed_frames[i])
                        original_framename = processed_frames[i].split("__")[0] + "." + processed_frames[i].split(".")[-1]
                        dst_p = os.path.join(variants_folder[i], original_framename)
                        shutil.move(src_p, dst_p)

