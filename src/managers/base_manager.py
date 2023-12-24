import os
import json
from typing import Any


class Manager:
    """
    Base class providing methods for reading and modifying JSON files
    """

    def __init__(self, file_path: str):
        self.file_path = file_path

        if not os.path.exists(file_path):
            with open(file_path, "w") as file:
                json.dump({}, file)

    def _read_data(self) -> Any:
        with open(self.file_path, "r") as file:
            return json.load(file)

    def _write_data(self, data) -> None:
        with open(self.file_path, "w") as file:
            json.dump(data, file, indent=4)
