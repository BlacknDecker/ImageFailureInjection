import logging
import os
import shutil
from InjectionManager import InjectionManager
from utils.Timer import Timer


# Config
sequence_folder = os.path.join(os.getcwd(), "input", "sequence_01")
failures = ["banding", "condensation"]

# Cleanup
shutil.rmtree(os.path.join(os.getcwd(), "output"))
os.mkdir(os.path.join(os.getcwd(), "output"))

# Init
IM = InjectionManager()
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

# Process
with Timer("Failure Injection"):
    IM.processSequence(sequence_folder, failures=failures)

