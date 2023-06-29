import fileinput
import os
import shutil
import subprocess
from pathlib import Path

from experiment_runner.EnvironmentParameters import EnvironmentParameters
from experiment_runner.ExperimentParameters import ExperimentParameters
from experiment_runner.ExperimentStatus import ExperimentStatus
from experiment_runner.VOModel import VOModel
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
            self.__collectPatchSample()
        except Exception as e:
            status.error_message = str(e)
        else:
            status.prepared = True
        return status

    def run(self, ongoing_status: ExperimentStatus, vo_model:VOModel, remove_workload=False) -> ExperimentStatus:
        if self.__experimentWorkloadIsAvailable():
            if self.__nominalResultsAreAvailable():
                # Run the experiment
                try:
                    self.__editExperimentRunConfiguration()
                    self.__editKittiRunConfiguration()
                    run_status = self.__launchDocker(ongoing_status, vo_model)
                    if remove_workload:
                        self.__freeWorkload()
                    return run_status
                except Exception as e:
                    ongoing_status.error_message = str(e)
                    return ongoing_status
            else:
                ongoing_status.error_type = "Configuration"
                ongoing_status.updateErrorMessage("Nominal run results are not available! Run the nominal sequence first!")
        else:
            ongoing_status.error_type = "Runtime"
            ongoing_status.updateErrorMessage("Experiment workload is not available!")
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

    # Check that nominal run results are available (if this is not a nominal run)
    def __nominalResultsAreAvailable(self) -> bool:
        # Check if this is a nominal run
        if "nominal" in self.experiment.experiment_name:
            # if its nominal we can skip the check
            return True
        # Check nominal results folder
        results_directory = self.env.volume_root_directory / "results"
        seq = self.experiment.sequence
        nominal_run_name = f"{seq}_{seq}_nominal"
        nominal_dir = results_directory / nominal_run_name
        if nominal_dir.exists():
            # check if keypoints are available
            kpts_dir = nominal_dir / "raw_outputs" / f"{nominal_run_name}_poses"
            if kpts_dir.exists():
                if len(list(kpts_dir.glob("*_kpts.npy"))):
                    return True
        # In all the other cases the results are not available
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

    def __launchDocker(self, ongoing_status: ExperimentStatus, vo_model:VOModel) -> ExperimentStatus:
        cmd = f'docker run --rm -v "{self.env.volume_root_directory}":/inj_data/ --gpus all {vo_model}'
        try:
            completed_process = subprocess.run(cmd, stderr=subprocess.PIPE, shell=True, text=True)
        except Exception as e:
            ongoing_status.error_message = str(e)
        else:
            # Check for errors in the execution
            error_data = completed_process.stderr
            if "Traceback (most recent call last):" in error_data:
                ongoing_status.error_type = "Exception"
                ongoing_status.error_message = error_data
            elif "docker: Error" in error_data:
                ongoing_status.error_type = "DockerError"
                ongoing_status.error_message = error_data
            else:
                # Execution completed
                ongoing_status.run_status = True
        # Always add the results path
        ongoing_status.result_folder = self.getResultsFolder()
        return ongoing_status

    def __freeWorkload(self):
        if self.__experimentWorkloadIsAvailable():
            # Get folders
            results_folder = self.env.volume_root_directory / "results"
            sequence_directory = self.env.sequences_directory / self.experiment.sequence
            experiment_directory = sequence_directory / self.experiment.experiment_name
            # save last frame (which is for sure injected) in the results folder as a sample
            frames = list(experiment_directory.glob("*.png"))
            frames.sort()
            if os.path.isdir(results_folder):
                sample_folder = results_folder/"experiment_samples"
                os.makedirs(sample_folder, exist_ok=True)
                sample_name = f"{self.experiment.sequence}_{self.experiment.experiment_name}_frame_{frames[-1].parts[-1]}"
                shutil.copyfile(frames[-1], sample_folder/sample_name)
            # Delete workload folder
            shutil.rmtree(experiment_directory)

    def __collectPatchSample(self):
        # Move patch samples into the results folder
        src_folder = self.env.volume_root_directory / "patches" / "summary"
        dst_folder = self.env.volume_root_directory / "results" / "patch_samples"
        os.makedirs(dst_folder, exist_ok=True)
        for patch_sample in src_folder.glob('*.png'):
            shutil.move(patch_sample, dst_folder)
        # Remove summary folder from patches dir
        shutil.rmtree(src_folder)
