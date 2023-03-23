from pathlib import Path
from typing import List, Optional

from PIL import Image


class PatchLoader:

    def __init__(self, patch_src: Path):
        self.patches_dir = patch_src

    def loadPatch(self, failure_type: str, failure_variant: int, calibration_frame: Image.Image) -> Image.Image:
        if failure_type == "none":
            return Image.new("RGBA", calibration_frame.size)    # Blank image
        if self.__patchExists(failure_type, failure_variant):
            patch_dir = self.patches_dir / failure_type
            patch_variants_path = list(patch_dir.glob("*.png"))
            patch = Image.open(patch_variants_path[failure_variant])
            patch = patch.convert(calibration_frame.mode).resize(calibration_frame.size)
            return patch

    ### Utils ###

    def __patchExists(self, failure_type: str, failure_variant: int) -> bool:
        failure_types = self.__getAvailableFailureTypes()
        if failure_type in failure_types:
            patch_dir = self.patches_dir / failure_type
            patch_variants_path = list(patch_dir.glob("*.png"))
            if 0 <= failure_variant < len(patch_variants_path):
                return True
            else:
                raise IndexError(
                    f"Failure Variant '{failure_variant}' does not exist for Failure Type '{failure_type}'!")
        else:
            raise TypeError(f"Failure Type '{failure_type}' does not exist!")

    def __getAvailableFailureTypes(self) -> List[str]:
        failure_types = []
        for pp in self.patches_dir.iterdir():
            if pp.is_dir() and not pp.parts[-1].endswith("__"):
                failure_types.append(pp.parts[-1])
        return failure_types
