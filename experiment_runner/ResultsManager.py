import json
from pathlib import Path
from typing import List
import pandas as pd

from experiment_runner.EnvironmentParameters import EnvironmentParameters
from experiment_runner.ExperimentParameters import ExperimentParameters
from experiment_runner.ExperimentStatus import ExperimentStatus


class ResultsManager:

    def __init__(self, environment: EnvironmentParameters, experiments_config: Path):
        self.env = environment
        self.experiments_log_folder = self.env.volume_root_directory / "results" / "run_logs"
        self.experiment_configs = self.__parseConfig(experiments_config)
        self.summary_folder = self.env.volume_root_directory / "results" / "summary"

    def createSummary(self, experiment_results: List[ExperimentStatus]) -> None:
        status_s = []
        conf_s = []
        # Collect Info
        for exp_status in experiment_results:
            exp_config = self.__getExperimentConfig(exp_status.experiment_name)
            # STATUS
            status_row = {
                "experiment": exp_status.experiment_name,
                "sequence": exp_config.sequence,
                "prepared": exp_status.prepared,
                "run": exp_status.run_status,
                "error_type": exp_status.error_type,
                "log": self.experiments_log_folder / f"{exp_status.experiment_name}_status.json",
                "notes": ""
            }
            status_s.append(status_row)
            # CONFIGURATION
            conf_row = {
                "experiment": exp_status.experiment_name,
                "sequence": exp_config.sequence,
                "failure": exp_config.failure_type,
                "variant": exp_config.failure_variant,
                "patch": exp_config.patch_name,
                "injection_frame": exp_config.injection_position
            }
            conf_s.append(conf_row)
            # METRICS
            # TODO: retrieve experiment metrics
        # Create DFs
        status_df = pd.DataFrame(status_s)
        conf_df = pd.DataFrame(conf_s)
        ## Create EXCEL ##
        summary_path = self.summary_folder / "summary.xlsx"
        writer = pd.ExcelWriter(summary_path, engine='xlsxwriter')
        # Sheets
        status_df.to_excel(writer, sheet_name=f"status")
        conf_df.to_excel(writer, sheet_name=f"config")
        # Save
        writer.close()
        ### Create CSV ###
        status_df.to_csv(self.summary_folder / "status_summary.csv", encoding='utf-8')
        conf_df.to_csv(self.summary_folder / "configuration_summary.csv", encoding='utf-8')
        # Done

    ### UTILS ###

    def __parseConfig(self, config_path: Path) -> List[ExperimentParameters]:
        configs = self.__loadExperimentsConfig(config_path)
        experiments = []
        for exp_conf in configs:
            ep = ExperimentParameters(exp_conf)
            experiments.append(ep)
        return experiments

    def __loadExperimentsConfig(self, experiments_config: Path):
        with open(experiments_config, "r") as f:
            return json.load(f)

    def __getExperimentConfig(self, experiment_name: str) -> ExperimentParameters:
        return next(filter(lambda x: x.experiment_name == experiment_name, self.experiment_configs))
