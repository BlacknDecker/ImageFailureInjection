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
            # process frames
            for frame in frames_path:
                # process frame
                self.injectors[failure].inject(frame, failure_folder)
