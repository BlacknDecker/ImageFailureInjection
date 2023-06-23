import json
import os
import shutil
from pathlib import Path
from typing import List, TypedDict, Union, Optional

from experiment_runner.EnvironmentParameters import EnvironmentParameters
from experiment_runner.ExperimentParameters import ExperimentParameters
from experiment_runner.ExperimentRunner import ExperimentRunner
from experiment_runner.ExperimentStatus import ExperimentStatus
from utils.Timer import Timer
from utils.TimerOneLine import TimerOneLine


class ExperimentConfig(TypedDict):
    experiment_name: str
    sequence_name: str
    failure_type: str
    failure_variant: int
    injection_position: int


class ExperimentsController:

    def __init__(self, environment: EnvironmentParameters, experiments_config: Path):
        self.env = environment
        self.experiments = self.__parseConfig(experiments_config)
        self.experiments_log_folder = self.env.volume_root_directory/"results"/"run_logs"
        self.summary_folder = self.env.volume_root_directory / "results" / "summary"
        # Create summary and log folder if not exists
        os.makedirs(self.experiments_log_folder, exist_ok=True)
        os.makedirs(self.summary_folder, exist_ok=True)

    def prepareExperiments(self, experiment_names: List[str] = None) -> List[ExperimentStatus]:
        experiments = self.__selectExperiments(experiment_names)
        # Prepare selected experiments
        preparation_status = []
        for experiment in experiments:
            runner = ExperimentRunner(self.env, experiment)
            status = runner.createExperimentWorkload()
            preparation_status.append(status)
        return preparation_status

    def runPreparedExperiments(self, ongoing_experiments: List[ExperimentStatus], remove_workload=True) -> List[ExperimentStatus]:
        # Run the experiments
        run_status = []
        for ongoing_status in ongoing_experiments:
            experiment = self.__getExperimentByName(ongoing_status.experiment_name)
            runner = ExperimentRunner(self.env, experiment)
            # Run experiment
            with TimerOneLine(f"Run: {ongoing_status.experiment_name}"):
                status = runner.run(ongoing_status, remove_workload)
            # Save results
            with open(self.experiments_log_folder/f"{status.experiment_name}.json", "w") as f:
                f.write(json.dumps(status.todict(), indent=4, default=str))
            run_status.append(status)
        return run_status

    def runExperiments(self, experiments_name: List[str] = None) -> List[ExperimentStatus]:
        # Select Experiments
        experiments = self.__selectExperiments(experiments_name)
        # Run selected experiments
        experiments_status = []
        for experiment in experiments:
            experiments_status.append(self.__runExperiment(experiment, remove_workload=True))
        return experiments_status

    ### Utils ###

    def __parseConfig(self, config_path: Path) -> List[ExperimentParameters]:
        configs = self.__getExperimentsConfig(config_path)
        experiments = []
        for exp_conf in configs:
            ep = ExperimentParameters(exp_conf)
            experiments.append(ep)
        return experiments

    def __getExperimentsConfig(self, experiments_config: Path):
        with open(experiments_config, "r") as f:
            return json.load(f)

    def __selectExperiments(self, experiment_names):
        if experiment_names is not None:
            experiments = self.__getExperimentsByName(experiment_names)
        else:
            experiments = self.experiments
        return experiments

    def __getExperimentsByName(self, experiment_names: List[str]) -> List[ExperimentParameters]:
        experiments = []
        for experiment_name in experiment_names:
            experiments.append(self.__getExperimentByName(experiment_name))
        return experiments

    def __getExperimentByName(self, experiment_name: str) -> ExperimentParameters:
        return next(filter(lambda x: x.experiment_name == experiment_name, self.experiments))

    def __runExperiment(self, experiment: ExperimentParameters, remove_workload: bool) -> ExperimentStatus:
        runner = ExperimentRunner(self.env, experiment)
        preparation_status = runner.createExperimentWorkload()
        # Run experiment
        with TimerOneLine(f"Run: {preparation_status.experiment_name}"):
            run_status = runner.run(preparation_status, remove_workload)
        # Save results
        with open(self.experiments_log_folder/f"{run_status.experiment_name}_status.json", "w") as f:
            f.write(json.dumps(run_status.todict(), indent=4, default=str))
        # Return result
        return run_status
