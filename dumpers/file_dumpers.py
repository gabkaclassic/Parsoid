from typing import Dict
import json
import os
from dumpers.dumper import Dumper
from uuid import uuid4
import zipfile


class FileDumper(Dumper):

    DEFAULT_DIR = "./tmp"

    def __init__(self, directory: str = None):
        self.directory = directory or self.DEFAULT_DIR
        self.filename = None
        self.filepath = None

    def preprocessing(self):
        pass

    def postprocessing(self):
        pass

    def dump(self, data: Dict, filename: str = None):

        self.preprocessing()

        if not os.path.exists(self.directory):
            os.mkdir(path=self.directory)
        self.filename = filename or str(uuid4())
        self.filepath = os.path.join(self.directory, f"{self.filename}.json")
        with open(self.filepath, "w") as file:
            json.dump(data, file, sort_keys=True, ensure_ascii=False)

        self.postprocessing()


class ZIPDumper(FileDumper):

    def postprocessing(self):
        zip_filename = f"{self.filename}.zip"

        with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, self.directory)
                    zipf.write(file_path, arcname)

        zip_filepath = os.path.join(self.directory, zip_filename)
        os.replace(zip_filename, zip_filepath)
