import fileinput
import os
import shutil
import subprocess
from pathlib import Path

from experiment_runner.EnvironmentParameters import EnvironmentParameters
from experiment_runner.ExperimentParameters import ExperimentParameters
from experiment_runner.ExperimentStatus import ExperimentStatus
from sequence_injectors.SequenceInjector import SequenceInjector


class ExperimentRunner:

    def __init__(self, environment: EnvironmentParameters, experiment_params: ExperimentParameters):
        self.env = environment
        self.experiment = experiment_params

    def createExperimentWorkload(self, override=True) -> ExperimentStatus:
        status = ExperimentStatus(self.experiment.experiment_name)
        # Avoid accidental override
        if self.__experimentWorkloadIsAvailable():
            if not override:
                status.error_message = f"Experiment '{self.experiment.experiment_name}' already exists for sequence '{self.experiment.sequence}'!"
                return status
        # create workload
        sequence_directory = self.env.sequences_directory / self.experiment.sequence
        frames_dir = sequence_directory / "image_0"
        try:
            injector = SequenceInjector(frames_dir, self.env.patch_root_directory, sequence_directory)
            injector.injectSequence(self.experiment.experiment_name,
                                    self.experiment.injection_position,
                                    self.experiment.failure_type,
                                    self.experiment.failure_variant)
        except Exception as e:
            status.error_message = str(e)
        else:
            status.prepared = True
        return status

    def run(self, ongoing_status: ExperimentStatus, remove_workload=False) -> ExperimentStatus:
        if self.__experimentWorkloadIsAvailable():
            try:
                self.__editExperimentRunConfiguration()
                self.__editKittiRunConfiguration()
                run_status = self.__launchDocker(ongoing_status)
                if remove_workload:
                    self.__freeWorkload()
                return run_status
            except Exception as e:
                ongoing_status.error_message = str(e)
                return ongoing_status
        else:
            if ongoing_status.error_message == "":
                ongoing_status.error_message = "Experiment workload is not available!"
            return ongoing_status

    def getResultsFolder(self) -> Path:
        return self.env.volume_root_directory / "results" / f"{self.experiment.sequence}_{self.experiment.experiment_name}"

    # Check if the experiment sequence has been created
    def __experimentWorkloadIsAvailable(self) -> bool:
        sequence_directory = self.env.sequences_directory / self.experiment.sequence
        experiment_directory = sequence_directory / self.experiment.experiment_name
        if experiment_directory.exists():
            if len(list(experiment_directory.glob('*.png'))) > 0:
                return True
        return False

    def __editExperimentRunConfiguration(self):
        run_config_path = self.env.volume_root_directory / "run_model.sh"
        # Read run configuration file
        with open(run_config_path, "r") as f:
            run_config_lines = f.readlines()
        # Edit run config
        for i in range(len(run_config_lines)):
            line = run_config_lines[i]
            # Change sequence
            if "seq_num=" in line:
                run_config_lines[i] = f'seq_num="{self.experiment.sequence}"\n'
            # Change experiment name
            if "camera=" in line:
                run_config_lines[i] = f'camera="{self.experiment.experiment_name}"\n'
        # Save edited run config
        with open(run_config_path, "w") as f:
            f.writelines(run_config_lines)
        # Done

    def __editKittiRunConfiguration(self):
        run_config_path = self.env.volume_root_directory / "kitti_superpoint_supergluematch.yaml"
        # Read configuration file
        with open(run_config_path, "r") as f:
            run_config_lines = f.readlines()
        # Edit run config
        for i in range(len(run_config_lines)):
            line = run_config_lines[i]
            # Change sequence
            if "sequence:" in line:
                run_config_lines[i] = f"  sequence: '{self.experiment.sequence}'\n"
        # Save edited run config
        with open(run_config_path, "w") as f:
            f.writelines(run_config_lines)
        # Done

    def __launchDocker(self, ongoing_status: ExperimentStatus) -> ExperimentStatus:
        cmd = f'docker run --rm -v "{self.env.volume_root_directory}":/inj_data/ --gpus all odometry'
        try:
            completed_process = subprocess.run(cmd, stderr=subprocess.PIPE, shell=True, text=True)
        except Exception as e:
            ongoing_status.error_message = str(e)
        else:
            # Check for errors in the execution
            if completed_process.stderr:
                ongoing_status.error_message = completed_process.stderr
            else:
                # Execution completed
                ongoing_status.run_status = True
                ongoing_status.result_folder = self.getResultsFolder()
        return ongoing_status

    def __freeWorkload(self):
        if self.__experimentWorkloadIsAvailable():
            # Get folders
            results_folder = self.getResultsFolder()
            sequence_directory = self.env.sequences_directory / self.experiment.sequence
            experiment_directory = sequence_directory / self.experiment.experiment_name
            # save last frame (which is for sure injected) in the results folder as a sample
            frames = list(experiment_directory.glob("*.png"))
            frames.sort()
            if os.path.isdir(results_folder):
                shutil.copy(frames[-1], results_folder)
            # Delete workload folder
            shutil.rmtree(experiment_directory)
