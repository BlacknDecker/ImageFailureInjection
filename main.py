import json
import random
from pathlib import Path

import numpy as np

from experiment_runner.EnvironmentParameters import EnvironmentParameters
from experiment_runner.ExperimentsController import ExperimentsController
from experiment_runner.ResultsManager import ResultsManager
from experiment_runner.VOModel import VOModel
from utils.Timer import Timer


# CONFIG
SEED = 42069
VO_MODEL = VOModel.RETRAINED

# SETUP
random.seed(SEED)
np.random.seed(SEED)
env = EnvironmentParameters()
# env.volume_root_directory = Path.cwd() / "experiment_runner" / "test_env"
env.volume_root_directory = Path("/data/puccetti/inj_volume/")
env.sequences_directory = env.volume_root_directory / "dataset" / "sequences"
env.patch_root_directory = env.volume_root_directory / "patches"

experiments_conf = env.volume_root_directory / "experiments_config.json"

# Create Controller
controller = ExperimentsController(env, experiments_conf)

#### Run experiments #######
# results = controller.runExperiments(VO_MODEL)
# # Show results
# for res in results:
#     print(res)

#### Prepare and Run #########
with Timer("Experiments Preparation"):
    prepared = controller.prepareExperiments(["04_nominal", "exp_0089"])
    # prepared = controller.prepareExperiments(["exp_0115"])

# Show results
print(" EXPERIMENTS PREPARATION ".center(40, "#"))
for res in prepared:
    print(res)

with Timer("Experiments Run"):
    results = controller.runPreparedExperiments(prepared, VO_MODEL)
# Show results
print(" EXPERIMENTS RUN ".center(40, "#"))
for res in results:
    print(res)
# CREATE SUMMARY
print("Creating Summary...")
res_m = ResultsManager(env, experiments_conf)
res_m.createSummary(results)
print("Done!")
