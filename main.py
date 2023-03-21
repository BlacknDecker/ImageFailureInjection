import json
from pathlib import Path

from experiment_runner.EnvironmentParameters import EnvironmentParameters
from experiment_runner.ExperimentsController import ExperimentsController
from utils.Timer import Timer

# SETUP
env = EnvironmentParameters()
env.volume_root_directory = Path.cwd() / "experiment_runner" / "test_env"
env.sequences_directory = env.volume_root_directory / "dataset" / "sequences"
env.patch_root_directory = env.volume_root_directory / "patches"

experiments_conf = env.volume_root_directory / "experiments_config.json"

# Create Controller
controller = ExperimentsController(env, experiments_conf)

#### Run experiments #######
# results = controller.runExperiments()
# # Show results
# for res in results:
#     print(res)

#### Prepare and Run #########
with Timer("Experiments Preparation"):
    prepared = controller.prepareExperiments(["exp_0023", "exp_0033", "exp_0045", "exp_0115", "exp_0119"])
    # prepared = controller.prepareExperiments(["exp_0115"])

# Show results
print(" EXPERIMENTS PREPARATION ".center(40, "#"))
for res in prepared:
    print(res)

# with Timer("Experiments Run"):
#     results = controller.runPreparedExperiments(prepared)
# # Show results
# print(" EXPERIMENTS RUN ".center(40, "#"))
# for res in results:
#     print(res)