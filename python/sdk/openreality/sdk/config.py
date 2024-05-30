import os
import tomli

class ConfigParser:
    def __init__(self, file: str):
        # check file
        self._file = file
        if not os.path.isfile(self._file):
            raise FileNotFoundError(f"File {self._file} does not exist")
            return

        # read file as tomli
        self._config = {}
        with open(self._file, "rb") as file:
            self._config = tomli.load(file)

    @property
    def config(self):
        return self._config
