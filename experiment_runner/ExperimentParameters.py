

class ExperimentParameters:
    experiment_name: str
    sequence: str
    failure_type: str
    failure_variant: int
    patch_name: str
    injection_position: int

    def __init__(self, raw_config:dict):
        self.experiment_name = raw_config["experiment_name"]
        self.sequence = raw_config["sequence_name"]
        self.failure_type = raw_config["failure_type"]
        self.failure_variant = raw_config["failure_variant"]
        self.patch_name = raw_config["patch_name"]
        self.injection_position = raw_config["injection_position"]

