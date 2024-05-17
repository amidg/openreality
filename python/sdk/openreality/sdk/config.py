import os
import tomli

class ConfigParser:
    def __init__(self, file: str):
        # check file
        self._file = file
        self._file_exists = os.path.isfile(self._file)

        # read file as tomli
        self._config = {}
        if self._file_exists:
            with open(self._file, "rb") as file:
                self._config = tomli.load(file)
        else:
            raise FileNotFoundError(f"File {self._file} does not exist")

    @property
    def config(self):
        return self._config
