from pathlib import Path
from typing import Optional


class ExperimentStatus:

    def __init__(self, experiment_name: str):
        self.experiment_name = experiment_name
        self.prepared = False
        self.run_status = False
        self.result_folder: Optional[Path] = None
        self.error_message = ""

    def isPrepared(self):
        return self.prepared

    def isCompleted(self):
        return self.run_status

    def __str__(self) -> str:
        es = f"[{self.experiment_name}]\n"
        es += f"Prepared: {self.prepared}\n"
        if self.prepared:
            es += f"Executed: {self.run_status}\n"
            if self.run_status:
                es += f"Results: {self.result_folder}\n"
                return es
        # In case of failure show error message
        if len(self.error_message) > 0:
            es += f"Error: {self.error_message}\n"
        return es


