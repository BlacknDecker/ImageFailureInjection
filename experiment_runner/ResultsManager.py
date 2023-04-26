import csv
import json
from pathlib import Path
from statistics import mean
from typing import List, Dict
import pandas as pd

from experiment_runner.EnvironmentParameters import EnvironmentParameters
from experiment_runner.ExperimentParameters import ExperimentParameters
from experiment_runner.ExperimentStatus import ExperimentStatus
from utils.TelegramNotifier import TelegramNotifier


class ResultsManager:

    def __init__(self, environment: EnvironmentParameters, experiments_config: Path):
        self.env = environment
        self.experiments_log_folder = self.env.volume_root_directory / "results" / "run_logs"
        self.experiment_configs = self.__parseConfig(experiments_config)
        self.summary_folder = self.env.volume_root_directory / "results" / "summary"
        self.notifier = TelegramNotifier(Path.cwd()/"secrets.json")

    def createSummary(self, experiment_results: List[ExperimentStatus]) -> None:
        status_s = []
        conf_s = []
        metric_s = []
        # Collect Info
        for exp_status in experiment_results:
            exp_config = self.__getExperimentConfig(exp_status.experiment_name)
            # STATUS
            log_path = self.experiments_log_folder / f"{exp_status.experiment_name}_status.json"
            status_row = {
                "experiment": exp_status.experiment_name,
                "sequence": exp_config.sequence,
                "prepared": exp_status.prepared,
                "run": exp_status.run_status,
                "error_type": exp_status.error_type,
                # "log": log_path,
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
            metric_row = {
                "experiment": exp_status.experiment_name,
            }
            metric_row.update(self.__getMetrics(exp_status))
            metric_s.append(metric_row)
        # Create DFs
        status_df = pd.DataFrame(status_s)
        conf_df = pd.DataFrame(conf_s)
        metric_df = pd.DataFrame(metric_s)
        ## Create EXCEL ##
        summary_path = self.summary_folder / "summary.xlsx"
        writer = pd.ExcelWriter(summary_path, engine='xlsxwriter')
        # Sheets
        status_df.to_excel(writer, sheet_name=f"status")
        conf_df.to_excel(writer, sheet_name=f"config")
        metric_df.to_excel(writer, sheet_name=f"metrics")
        # Add formatting
        self.__addExcelConditionalFormatting(writer, "status", len(status_s))
        # Save
        writer.close()
        ### Create CSV ###
        status_df.to_csv(self.summary_folder / "status_summary.csv", encoding='utf-8')
        conf_df.to_csv(self.summary_folder / "configuration_summary.csv", encoding='utf-8')
        metric_df.to_csv(self.summary_folder / "metrics_summary.csv", encoding='utf-8')
        ### Notify User ###
        self.__notifyUser(status_s)
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

    def __getMetrics(self, exp_status: ExperimentStatus) -> dict:
        # Get POSES metrics
        metrics = self.__getPosesMetrics(exp_status)
        # Get KEYPOINTS metrics
        kpts_metrics = self.__getKeypointsMetrics(exp_status)
        # Collect and save
        metrics.update(kpts_metrics)
        return metrics

    def __getPosesMetrics(self, exp_status:ExperimentStatus) -> dict:
        metrics = {
            "APE": "",
            "RPE_Trans": "",
            "RPE_Rot": ""
        }
        # Fill metrics
        if exp_status.result_folder is not None:
            m_path = exp_status.result_folder / "metrics.txt"
            if m_path.exists():
                with open(m_path, "r") as f:
                    lines = f.readlines()
                # collect metrics
                metrics = {}
                for line in lines:
                    if "APE" in line:
                        metrics["APE"] = line.split(":")[-1].strip().split(" ")[0]
                    elif "RPE Trans" in line:
                        metrics["RPE_Trans"] = line.split(":")[-1].strip().split(" ")[0]
                    elif "RPE Rot" in line:
                        metrics["RPE_Rot"] = line.split(":")[-1].strip().split(" ")[0]
       # done
        return metrics

    def __getKeypointsMetrics(self, exp_status: ExperimentStatus) -> dict:
        metrics = {
            "kpts_rate": "",
            "kpts_match_rate": ""
        }
        if exp_status.result_folder is not None:
            k_path = exp_status.result_folder / "keypoints.csv"
            if k_path.exists():
                with open(k_path, newline='') as csvfile:
                    reader = csv.DictReader(csvfile)
                    kpts_rate = []
                    kpts_match_rate = []
                    for row in reader:
                        kpts_rate.append(int(row["exp_kpts"])/int(row["gt_kpts"]))
                        kpts_match_rate.append(int(row["matches"])/int(row["gt_kpts"]))
                # get the average
                metrics["kpts_rate"] = str(round(mean(kpts_rate), 2))
                metrics["kpts_match_rate"] = str(round(mean(kpts_match_rate), 2))
        return metrics

    def __addExcelConditionalFormatting(self, writer: pd.ExcelWriter, sheet_name:str, sheet_len:int):
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        # Define format
        format_yellow = workbook.add_format({'bg_color': '#FFEB9C',
                                             'font_color': '#9C6500'})
        # Status - RUN ERROR
        worksheet.conditional_format(f"E2:E{sheet_len+1}",
                                     {
                                         'type': 'cell',
                                         'criteria': '==',
                                         'value': False,
                                         'format': format_yellow
                                     })

    def __notifyUser(self, status_list: List[Dict]):
        # Get required Info:
        total_exps = len(status_list)
        prepared_exps = [exp["prepared"] for exp in status_list].count(True)
        ran_exp = [exp["run"] for exp in status_list].count(True)
        # Create Notification message
        msg = "*BATCH RUN TERMINATED*\n"
        msg += f"_Experiments:_ {total_exps}\n"
        msg += f"_Prepared:_ {prepared_exps}\n"
        msg += f"_Completed:_ {ran_exp}\n"
        # Notify
        self.notifier.notify(msg)
