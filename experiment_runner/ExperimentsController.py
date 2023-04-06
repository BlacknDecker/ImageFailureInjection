import json
from pathlib import Path
from typing import List, TypedDict, Union, Optional

from experiment_runner.EnvironmentParameters import EnvironmentParameters
from experiment_runner.ExperimentParameters import ExperimentParameters
from experiment_runner.ExperimentRunner import ExperimentRunner
from experiment_runner.ExperimentStatus import ExperimentStatus


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

    def prepareExperiments(self, experiment_names: List[str] = None) -> List[ExperimentStatus]:
        experiments = self.__selectExperiments(experiment_names)
        # Prepare selected experiments
        preparation_status = []
        for experiment in experiments:
            runner = ExperimentRunner(self.env, experiment)
            status = runner.createExperimentWorkload()
            preparation_status.append(status)
        return preparation_status

    def runPreparedExperiments(self, ongoing_experiments: List[ExperimentStatus], remove_workload=False) -> List[ExperimentStatus]:
        # Run the experiments
        run_status = []
        for ongoing_status in ongoing_experiments:
            experiment = self.__getExperimentByName(ongoing_status.experiment_name)
            runner = ExperimentRunner(self.env, experiment)
            status = runner.run(ongoing_status, remove_workload)
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
            ep = ExperimentParameters()
            ep.experiment_name = exp_conf["experiment_name"]
            ep.sequence = exp_conf["sequence_name"]
            ep.failure_type = exp_conf["failure_type"]
            ep.failure_variant = exp_conf["failure_variant"]
            ep.injection_position = exp_conf["injection_position"]
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
        run_status = runner.run(preparation_status, remove_workload)
        # Return result
        return run_status

