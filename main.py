import os
import logging

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
from injectors.RandomSnowInjector import RandomSnowInjector
from injectors.RandomRainInjector import RandomRainInjector
from injectors.SharpnessInjector import SharpnessInjector


### SETUP ###
original = os.path.join(os.getcwd(), "original_example.png")
out_folder = os.path.join(os.getcwd(), "out", "test")
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
# logging.basicConfig(filename='injection.log', level=logging.INFO)

# Injectors
brightness = BrightnessInjector()
blur = BlurInjector()
banding = BandingInjector(os.path.join(os.getcwd(), "injectors", "banding"))
lensBreakage = BreakageInjector(os.path.join(os.getcwd(), "injectors", "lensBroken"))
chromaticAberration = ChromaticAberrationInjector()     # NB: VERY slow!
condensation = CondensationInjector(os.path.join(os.getcwd(), "injectors", "condensation"))
deadPixels = DeadPixelsInjector()
dirt = DirtInjector(os.path.join(os.getcwd(), "injectors", "lensDirt"))
grayscale = GrayscaleInjector()
ice = IceInjector(os.path.join(os.getcwd(), "injectors", "ice"))
nodemos = NodemosInjector()
noise = NoiseInjector()
rain = RainInjector(os.path.join(os.getcwd(), "injectors", "rain"))     # FIXME: doesn't blend too well
sharpness = SharpnessInjector()
flare = FlareInjector()
randomSnow = RandomSnowInjector()   # Works, but is not that realistic
randomRain = RandomRainInjector()

# TEST
brightness.inject(original, out_folder)
blur.inject(original, out_folder)
banding.inject(original, out_folder)
lensBreakage.inject(original, out_folder)
chromaticAberration.inject(original, out_folder)
condensation.inject(original, out_folder)
deadPixels.inject(original, out_folder)
dirt.inject(original, out_folder)
grayscale.inject(original, out_folder)
ice.inject(original, out_folder)
nodemos.inject(original, out_folder)
noise.inject(original, out_folder)
rain.inject(original, out_folder)
sharpness.inject(original, out_folder)
flare.inject(original, out_folder)
randomSnow.inject(original, out_folder)
randomRain.inject(original, out_folder)
