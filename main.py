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
VO_MODEL = VOModel.BASE
VOLUME_PATH = Path("/data/puccetti/inj_volume/")
SELECTED_EXPERIMENTS = ["04_nominal", "exp_0324"]   # None for ALL

# SETUP
random.seed(SEED)
np.random.seed(SEED)
env = EnvironmentParameters()
# env.volume_root_directory = Path.cwd() / "experiment_runner" / "test_env"
env.volume_root_directory = VOLUME_PATH
env.sequences_directory = env.volume_root_directory / "dataset" / "sequences"
env.patch_root_directory = env.volume_root_directory / "patches"

experiments_conf = env.volume_root_directory / "experiments_config.json"

# Create Controller
controller = ExperimentsController(env, experiments_conf)

if SELECTED_EXPERIMENTS is None:
    #### Run ALL experiments #######
    results = controller.runExperiments(VO_MODEL)
    # Show results
    for res in results:
        print(res)
else:
    #### Prepare SELECTED experiments #########
    with Timer("Experiments Preparation"):
        prepared = controller.prepareExperiments(SELECTED_EXPERIMENTS)
    # Show prepared
    print(" EXPERIMENTS PREPARATION ".center(40, "#"))
    for res in prepared:
        print(res)
    #### Run SELECTED experiments #########
    with Timer("Experiments Run"):
        results = controller.runPreparedExperiments(prepared, VO_MODEL)
    # Show results
    print(" EXPERIMENTS RUN ".center(40, "#"))
    for res in results:
        print(res)

## CREATE SUMMARY ##
print("Creating Summary...")
res_m = ResultsManager(env, experiments_conf)
res_m.createSummary(results)
print("Done!")
