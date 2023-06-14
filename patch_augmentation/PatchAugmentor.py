from pathlib import Path
import albumentations as A
import cv2
import numpy as np
from PIL import Image
from albumentations import PadIfNeeded


class PatchAugmentor:

    def __init__(self, target_height: int, target_width: int):
        self.transformations = self.__getTransformations(target_height, target_width)

    def augment(self, original: Image.Image, failure_type: str) -> Image.Image:
        # Convert target format
        patch_np = np.array(original)
        # Augment patch
        transformed = self.transformations[failure_type](image=patch_np)
        augmented_patch_np = transformed['image']
        # Convert back to the original format
        return Image.fromarray(augmented_patch_np)

    ### UTILS ###

    def __getTransformations(self, t_height: int, t_width: int):
        return {
            "rain": A.Compose([
                A.ShiftScaleRotate(scale_limit=(-0.5, 0.5), rotate_limit=90, border_mode=cv2.BORDER_WRAP,
                                   always_apply=True),
                A.LongestMaxSize(max_size=min((t_height, t_width)), always_apply=True),
                A.Rotate(border_mode=cv2.BORDER_WRAP, always_apply=True),
                A.PadIfNeeded(min_height=t_height, min_width=t_width,
                              position=PadIfNeeded.PositionType.RANDOM, border_mode=cv2.BORDER_WRAP,
                              always_apply=True),
            ]),

            "ice": A.Compose([
                A.ShiftScaleRotate(scale_limit=(-0.5, 0.5), rotate_limit=90, border_mode=cv2.BORDER_REFLECT_101,
                                   always_apply=True),
                A.LongestMaxSize(max_size=min((t_height, t_width)), always_apply=True),
                A.Rotate(border_mode=cv2.BORDER_REFLECT_101, always_apply=True),
                A.OneOf([
                    # Small patch
                    A.Compose([
                        A.PadIfNeeded(min_height=t_height, min_width=t_width,
                                      position=PadIfNeeded.PositionType.RANDOM, border_mode=cv2.BORDER_CONSTANT,
                                      value=(255, 255, 255, 0), always_apply=True),
                        A.Rotate(border_mode=cv2.BORDER_CONSTANT, value=(255, 255, 255, 0), always_apply=True),
                    ], p=0.8),
                    # Big patch
                    A.Compose([
                        A.PadIfNeeded(min_height=t_height, min_width=t_width,
                                      position=PadIfNeeded.PositionType.RANDOM, border_mode=cv2.BORDER_WRAP,
                                      always_apply=True),
                        A.Rotate(border_mode=cv2.BORDER_CONSTANT, value=(255, 255, 255, 0), p=0.3),
                    ], p=0.2),
                ], p=1.0),
            ]),

            "condensation": A.Compose([
                A.ShiftScaleRotate(scale_limit=(-0.5, 0.5), rotate_limit=90, border_mode=cv2.BORDER_REFLECT_101,
                                   always_apply=True),
                A.LongestMaxSize(max_size=min((t_height, t_width)), always_apply=True),
                A.OneOf([
                    # Small patch
                    A.Compose([
                        A.PadIfNeeded(min_height=t_height, min_width=t_width,
                                      position=PadIfNeeded.PositionType.RANDOM, border_mode=cv2.BORDER_CONSTANT,
                                      value=(255, 255, 255, 0), always_apply=True),
                    ], p=0.2),
                    # Big patch
                    A.Compose([
                        A.PadIfNeeded(min_height=t_height, min_width=t_width,
                                      position=PadIfNeeded.PositionType.RANDOM, border_mode=cv2.BORDER_REFLECT_101,
                                      always_apply=True),
                        A.Rotate(border_mode=cv2.BORDER_CONSTANT, value=(255, 255, 255, 0), p=0.3),
                    ], p=0.8),
                ], p=1.0),
            ]),

            "breakage": A.Compose([
                A.ShiftScaleRotate(scale_limit=(-0.5, 0.5), rotate_limit=90, border_mode=cv2.BORDER_REFLECT_101,
                                   always_apply=True),
                A.Flip(p=0.3),
                A.Transpose(p=0.3),
                A.LongestMaxSize(max_size=min((t_height, t_width)), always_apply=True),
                A.Rotate(border_mode=cv2.BORDER_REFLECT_101, always_apply=True),
                A.OneOf([
                    # Small patch
                    A.Compose([
                        A.PadIfNeeded(min_height=t_height, min_width=t_width,
                                      position=PadIfNeeded.PositionType.RANDOM, border_mode=cv2.BORDER_CONSTANT,
                                      value=(255, 255, 255, 0), always_apply=True),
                        A.Rotate(border_mode=cv2.BORDER_CONSTANT, value=(255, 255, 255, 0), always_apply=True),
                    ], p=0.8),
                    # Big patch
                    A.Compose([
                        A.PadIfNeeded(min_height=t_height, min_width=t_width,
                                      position=PadIfNeeded.PositionType.RANDOM, border_mode=cv2.BORDER_REFLECT_101,
                                      always_apply=True),
                        A.Rotate(border_mode=cv2.BORDER_CONSTANT, value=(255, 255, 255, 0), p=0.5),
                    ], p=0.2),
                ], p=1.0),
            ]),

            "dirt": A.Compose([
                A.ShiftScaleRotate(scale_limit=(-0.1, 0.1), rotate_limit=90, border_mode=cv2.BORDER_REFLECT_101,
                                   always_apply=True),
                A.Flip(p=0.3),
                A.Transpose(p=0.3),
                A.LongestMaxSize(max_size=min((t_height, t_width)), always_apply=True),
                A.Rotate(border_mode=cv2.BORDER_REFLECT_101, always_apply=True),
                A.OneOf([
                    # Small patch
                    A.Compose([
                        A.PadIfNeeded(min_height=t_height, min_width=t_width,
                                      position=PadIfNeeded.PositionType.RANDOM, border_mode=cv2.BORDER_CONSTANT,
                                      value=(255, 255, 255, 0), always_apply=True),
                        A.Rotate(border_mode=cv2.BORDER_CONSTANT, value=(255, 255, 255, 0), always_apply=True),
                    ], p=0.3),
                    # Big patch
                    A.Compose([
                        A.PadIfNeeded(min_height=t_height, min_width=t_width,
                                      position=PadIfNeeded.PositionType.RANDOM, border_mode=cv2.BORDER_REFLECT_101,
                                      always_apply=True),
                        A.Rotate(border_mode=cv2.BORDER_CONSTANT, value=(255, 255, 255, 0), p=0.3),
                    ], p=0.7),
                ], p=1.0),
            ])
        }
