import itertools
import json
from math import ceil
from pathlib import Path
from typing import List

##############################################
# Generates the experiments_config.json file
##############################################


# Init
# base_directory = Path.cwd() / "experiment_runner" / "test_env"  # Test only
base_directory = Path.cwd() / "../inj_volume"
sequences_directory = base_directory / "dataset" / "sequences"
patch_root_directory = base_directory / "patches"
# Get info
sequences = [seq for seq in sequences_directory.iterdir() if seq.is_dir()]
sequences.sort()
patches = [patch for patch in patch_root_directory.iterdir() if patch.is_dir()]
patches.sort()

# Setup
CREATE_NOMINAL_RUN = True
WARMUP_FRAMES = 10
INJECTION_POINTS_PERCENTAGES = [33]  # Injection at 1/3 of the sequence
MAX_VARIANTS = None     # Set max number of experiments for failure type, cycling on the variants, default=MAX(len(variants))
SINGLE_SEQUENCE = None  # Specify a sequence number (integer) to create experiments only for a given sequence

# Setup
experiments = []
exp_counter = 1
# Cut sequences if requested
if SINGLE_SEQUENCE is not None and SINGLE_SEQUENCE < len(sequences):
    sequences = [sequences[SINGLE_SEQUENCE]]


### UTILS ###

def __getMaxVariants(fail_types: List[Path]) -> int:
    variants = []
    for patch in fail_types:
        patch_vars = len(list(patch.glob("*.png")))
        variants.append(patch_vars)
    return max(variants)


def __getFailureExpVariants(failure: Path, max_variants: int) -> List[int]:
    fail_var_n = len(list(failure.glob("*.png")))
    reps = ceil(max_variants / fail_var_n)
    variants = list(range(fail_var_n))
    variants = list(itertools.repeat(variants, reps))
    variants = list(itertools.chain.from_iterable(variants))
    return variants[:max_variants]  # cut at required len


def getExperimentsFailureVariants(fail_types: List[Path], max_variants: int = None) -> dict:
    if not max_variants:
        max_variants = __getMaxVariants(fail_types)
    exps = {}
    for fail in fail_types:
        exps[fail.name] = __getFailureExpVariants(fail, max_variants)
    return exps


### ### ### ###


### RUN ###

# Generate experiments
for sequence in sequences:
    # Get the steady sequence length (the sequence without the warmup frames)
    camera_path = sequence / "image_0"
    steady_sequence_len = len(list(camera_path.glob("*.png"))) - WARMUP_FRAMES
    if steady_sequence_len <= 0:
        raise IndexError(f"The sequence {sequence.name} is too short!")

    # Create Nominal Run
    if CREATE_NOMINAL_RUN:
        experiments.append({
            "experiment_name": f"{sequence.name}_nominal",
            "sequence_name": f"{sequence.name}",
            "failure_type": f"none",
            "failure_variant": 0,
            "patch_name": f"",
            "injection_position": -1,
            "sequence_size": len(list(camera_path.glob("*.png")))
        })

    # Create Sequence Experiments
    failure_variants = getExperimentsFailureVariants(patches, MAX_VARIANTS)
    for patch in patches:
        patch_variants = failure_variants[patch.name]
        for variant in patch_variants:
            for injection_percentage in INJECTION_POINTS_PERCENTAGES:
                # Calculate the injection point
                injection_point = (steady_sequence_len * injection_percentage) // 100
                # Create the experiment configuration
                experiments.append({
                    "experiment_name": f"exp_{str(exp_counter).zfill(4)}",
                    "sequence_name": f"{sequence.name}",
                    "failure_type": f"{patch.name}",
                    "failure_variant": variant,
                    "patch_name": f"{list(patch.glob('*.png'))[variant].name}",
                    "injection_position": WARMUP_FRAMES + injection_point,
                    "sequence_size": len(list(camera_path.glob("*.png")))
                })
                # Increase experiment id
                exp_counter += 1

# Save
content = json.dumps(experiments, indent=2, default=str)
save_path = base_directory / "experiments_config.json"
with open(save_path, "w") as f:
    f.write(content)

# print(content)
print(f"TOTAL EXPERIMENTS: {len(experiments)}")
