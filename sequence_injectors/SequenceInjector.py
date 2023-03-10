import json
import os
from concurrent.futures import ThreadPoolExecutor, Future, as_completed, wait, FIRST_COMPLETED
from pathlib import Path
from typing import Dict, TypedDict

from PIL import Image


# DataClass for type inference
class FutureInfo(TypedDict):
    name: str
    position: int
    inject: bool


class SequenceInjector:

    def __init__(self, sequence_src: Path, patch_src: Path, experiment_dst: Path) -> None:
        # Directories
        self.frames_dir = sequence_src
        self.patches_dir = patch_src
        self.output_dir = experiment_dst
        # Frames
        self.frames_name = []
        for frame_name in os.listdir(self.frames_dir):
            if frame_name.endswith(".png"):
                self.frames_name.append(str(frame_name))
        # Patches
        self.failure_types = []
        for pp in self.patches_dir.iterdir():
            if pp.is_dir() and not pp.parts[-1].endswith("__"):
                self.failure_types.append(pp.parts[-1])

    def injectSequence(self, experiment_name: str, injection_position: int, failure_type: str,
                       failure_variant: int) -> None:
        with ThreadPoolExecutor() as executor:
            loading_frames = self.__loadFrames(executor)
            self.__markFramesToInject(loading_frames, injection_position)
            processing_frames = self.__processFrames(executor, loading_frames, failure_type, failure_variant)
            # Save
            experiment_dir = self.__createExperimentFolder(experiment_name)
            saving_frames = self.__saveExperimentFrames(executor, processing_frames, experiment_dir)
            # Done
            wait(saving_frames)

    def __loadFrames(self, executor: ThreadPoolExecutor) -> Dict[Future, FutureInfo]:
        loading = {}
        for frame_name in self.frames_name:
            frame_path = self.frames_dir / frame_name
            loading_frame = {
                executor.submit(self.__loadFrame, frame_path): {
                    "name": frame_name,
                    "position": self.frames_name.index(frame_name),
                    "inject": False
                }
            }
            loading.update(loading_frame)
        return loading

    def __loadFrame(self, frame_path: Path) -> Image:
        return Image.open(frame_path).convert("RGBA")

    def __markFramesToInject(self, loading_frames: Dict[Future, FutureInfo], injection_position: int) -> None:
        for frame_info in loading_frames.values():
            if frame_info["position"] >= injection_position:
                frame_info["inject"] = True

    def __processFrames(self, executor: ThreadPoolExecutor, loading_frames: Dict[Future, FutureInfo], failure_type: str,
                        failure_variant: int) -> Dict[Future, FutureInfo]:
        processing = {}
        # Wait first loaded image to get info
        future_frame, _ = wait(loading_frames, return_when=FIRST_COMPLETED)
        example_frame = next(iter(future_frame)).result()
        # Get patch
        patch = self.__loadPatch(failure_type, failure_variant, example_frame)
        apply_type = self.__getPatchApplyType(failure_type)  # TODO: Get patch params if needed
        for future_frame in as_completed(loading_frames):
            frame_info = loading_frames[future_frame]
            if frame_info["inject"]:
                processing_frame = {
                    executor.submit(self.__applyPatch, future_frame.result(), patch, apply_type): frame_info
                }
            else:
                # If the frame doesn't need to be processed
                processing_frame = {
                    future_frame: frame_info
                }
            # Add the future + the info
            processing.update(processing_frame)
        return processing

    def __loadPatch(self, failure_type: str, failure_variant: int, example_frame: Image.Image) -> Image.Image:
        if failure_type in self.failure_types:
            patch_dir = self.patches_dir / failure_type
            patch_variants_path = list(patch_dir.glob("*.png"))
            if 0 <= failure_variant < len(patch_variants_path):
                patch = Image.open(patch_variants_path[failure_variant])
                patch = patch.convert(example_frame.mode).resize(example_frame.size)
                return patch
            else:
                raise IndexError(
                    f"Failure Variant '{failure_variant}' does not exist for Failure Type '{failure_type}'!")
        else:
            raise TypeError(f"Failure Type '{failure_type}' does not exist!")

    def __getPatchApplyType(self, failure_type: str) -> str:
        return "PASTE"  # FIXME: change depending on failure type

    def __applyPatch(self, original: Image.Image, patch: Image.Image, apply_type: str) -> Image.Image:
        if apply_type == "PASTE":
            patched = original.copy()
            patched.paste(patch, (0, 0), patch)
            return patched
        else:
            raise NotImplementedError(f"'{apply_type}' is not currently supported!")

    def __createExperimentFolder(self, experiment_name: str) -> Path:
        exp_directory = self.output_dir / experiment_name
        os.makedirs(exp_directory, exist_ok=True)
        # TODO: empty folder if exists?
        return exp_directory

    def __saveExperimentFrames(self, executor: ThreadPoolExecutor, processing_frames: Dict[Future, FutureInfo],
                               experiment_dir: Path) -> Dict[Future, FutureInfo]:
        saving = {}
        for future_frame in as_completed(processing_frames):
            frame_info = processing_frames[future_frame]
            frame_out_path = experiment_dir / frame_info["name"]
            saving_frame = {
                executor.submit(self.__saveFrame, future_frame.result(), frame_out_path): frame_info
            }
            # add to futures dict
            saving.update(saving_frame)
        return saving

    def __saveFrame(self, frame: Image.Image, frame_path: Path) -> None:
        frame.save(frame_path)
