from pathlib import Path
from typing import List

from PIL import Image


class PatchInjector:

    def __init__(self, failure_type: str):
        self.injector_type = "PATCH"
        self.apply_type = self.__getPatchApplyType(failure_type)

    def inject(self, original: Image.Image, patch: Image.Image) -> Image.Image:
        if self.apply_type == "PASTE":
            patched = original.copy()
            patched.paste(patch, (0, 0), patch)
            return patched
        else:
            raise NotImplementedError(f"'{self.apply_type}' is not currently supported!")

    ### Utils ###

    def __getPatchApplyType(self, failure_type: str) -> str:
        return "PASTE"  # FIXME: change depending on failure type
