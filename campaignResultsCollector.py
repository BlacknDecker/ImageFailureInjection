import os
import shutil
import tarfile
from pathlib import Path
from distutils.dir_util import copy_tree

##############################################
# Script to collect all the results obtained
#  during a campaign of experiments
##############################################

STORAGE_FOLDER = Path("/data/puccetti/vo_experiments/")
BACKUP_FOLDER = STORAGE_FOLDER / "backup"
RESULTS_FOLDER = Path("/data/puccetti/inj_volume/results/")


### Utilities ###
def check_privileges() -> None:
    if not os.environ.get("SUDO_UID") and os.geteuid() != 0:
        raise PermissionError("You need to run this script with sudo or as root!")


def removeRawData(results_dir: Path) -> None:
    for fold in results_dir.iterdir():
        raw_out_folder = fold / "raw_outputs"
        if raw_out_folder.exists():
            shutil.rmtree(raw_out_folder)


def make_tarfile(archive_name: str, to_archive: Path, destination: Path) -> Path:
    archive_path = destination/f"{archive_name}.tar.gz"
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(to_archive, arcname=to_archive.name)
    return archive_path


def setPathPrivilegeAndOwnership(data_path: Path):
    os.chmod(data_path, mode=0o775)
    shutil.chown(data_path, user="puccetti", group="puccetti")


### Main ###
# Check if user has privileges
check_privileges()
# Show results folder path
print(f"Results folder: {RESULTS_FOLDER}")
# Remove raw data
removeRawData(RESULTS_FOLDER)
# Select archive name
archive_str = input("Campaign name (used for the Archive): ")
# Create a copy in the storage for easy access
print("Coping results folder in the storage...")
campaign_storage_path = STORAGE_FOLDER / archive_str
copy_tree(str(RESULTS_FOLDER), str(campaign_storage_path))
# Compress results
print("Compressing results folder...")
archive_path = make_tarfile(archive_str, RESULTS_FOLDER, BACKUP_FOLDER)
print(f"Saved archive: {archive_path}")
print(f"Consultation Copy: {str(campaign_storage_path)}")
# Change permissions and ownership
setPathPrivilegeAndOwnership(archive_path)
setPathPrivilegeAndOwnership(campaign_storage_path)
