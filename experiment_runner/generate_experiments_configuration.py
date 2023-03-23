import json
from pathlib import Path


### Generates the experiments_config.json file ###

# Init
base_directory = Path.cwd() / "test_env"
sequences_directory = base_directory / "dataset" / "sequences"
patch_root_directory = base_directory / "patches"
# Get info
sequences = [seq for seq in sequences_directory.iterdir() if seq.is_dir()]
sequences.sort()
patches = [patch for patch in patch_root_directory.iterdir() if patch.is_dir()]
patches.sort()

# Setup
WARMUP_FRAMES = 10
INJECTION_POINTS_PERCENTAGES = [33, 66]

# Generate PATCHES experiments
experiments = []
for sequence in sequences:
    # Get the steady sequence length (the sequence without the warmup frames)
    camera_path = sequence / "image_0"
    steady_sequence_len = len(list(camera_path.glob("*.png"))) - WARMUP_FRAMES
    if steady_sequence_len <= 0:
        raise IndexError(f"The sequence {sequence.name} is too short!")

    for patch in patches:
        patch_variants = len(list(patch.glob("*.png")))
        for variant in range(patch_variants):
            for injection_percentage in INJECTION_POINTS_PERCENTAGES:
                # Calculate the injection point
                injection_point = (steady_sequence_len * injection_percentage) // 100
                # Create the experiment configuration
                experiments.append({
                    "experiment_name": f"exp_{str(len(experiments)+1).zfill(4)}",
                    "sequence_name": f"{sequence.name}",
                    "failure_type": f"{patch.name}",
                    "failure_variant": variant,
                    "patch_name": f"{list(patch.glob('*.png'))[variant].name}",
                    "injection_position": WARMUP_FRAMES + injection_point
                })


# Create Nominal Run
for sequence in sequences:
    experiments.append({
        "experiment_name": f"{sequence.name}_nominal",
        "sequence_name": f"{sequence.name}",
        "failure_type": f"none",
        "failure_variant": 0,
        "patch_name": f"",
        "injection_position": -1
    })


# Save
content = json.dumps(experiments, indent=2, default=str)
save_path = base_directory / "experiments_config.json"
with open(save_path, "w") as f:
    f.write(content)

# print(content)
print(f"TOTAL EXPERIMENTS: {len(experiments)}")

