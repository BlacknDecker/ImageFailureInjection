import os


class FilePathManager:

    @staticmethod
    def getFileName(path):
        return ".".join(os.path.basename(path).split(".")[:-1])

    @staticmethod
    def getFileExtension(path):
        return os.path.basename(path).split(".")[-1]

    @staticmethod
    def addInjectionName(orig_path, injection_name):
        return FilePathManager.getFileName(orig_path) + "_" + injection_name + "." + FilePathManager.getFileExtension(orig_path)


