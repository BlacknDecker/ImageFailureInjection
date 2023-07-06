import subprocess
from pathlib import Path


##############################################
# Script to create a plot of comparison
#  between multiple experiment (in the same campaign)
##############################################


# Config
# ENV_FOLDER = Path.cwd() / "experiment_runner" / "test_env"
ENV_FOLDER = Path.cwd() / "../inj_volume/"
# OUT_FOLDER = Path.cwd()/"test_plotting"

GT_POSES_FOLDER = ENV_FOLDER / "dataset" / "poses"
RESULTS_FOLDER = ENV_FOLDER / "results"
OUT_FOLDER = RESULTS_FOLDER / "summary" / "plots"


### Select Sequence ###
sequence = input("Inserire il numero di sequenza: ")
sequence = str(sequence).zfill(2)   # Add leading zero

### Select Experiments ###
# find available experiments
available_experiments = []
for f in RESULTS_FOLDER.iterdir():
    if f.is_dir():
        dir_name = f.name
        if len(dir_name.split("_")):
            if dir_name.split("_")[0] == sequence:
                available_experiments.append(dir_name)
# display
print(f"Available Experiments:")
nominal_index = None
for i in range(len(available_experiments)):
    if "nominal" in available_experiments[i]:
        nominal_index = i
    else:
        print(f"{i} - {available_experiments[i]}")
print(f"{len(available_experiments)} - ALL")
# Select
raw_selection = input("Choose the experiments (comma separated): ")
if int(raw_selection.split(",")[0]) == len(available_experiments):  # Selected ALL
    selected_index = list(range(len(available_experiments)))
    selected_index.remove(nominal_index)
else:   # get selected elements
    selected_index = [int(s) for s in raw_selection.split(",") if s != ""]

### Create Plot ###
# Create command string
cmd = f"evo_traj tum "
cmd += f"{RESULTS_FOLDER/available_experiments[nominal_index]}/{available_experiments[nominal_index]}_poses.txt "   # Nominal
for ind in selected_index:
    cmd += f"{RESULTS_FOLDER/available_experiments[ind]}/{available_experiments[ind]}_poses.txt "                   # Selected experiments
cmd += f"--ref {GT_POSES_FOLDER}/{sequence}.tum "   # Ground Truth
cmd += "-as --align_origin --plot_mode xz "     # Options
cmd += f"--save_plot {OUT_FOLDER/'plot_comparison.png'}"
# Execute
print(f"Executing: {cmd}")
completed_process = subprocess.run(cmd, stderr=subprocess.PIPE, shell=True, text=True)
print("Done!")

