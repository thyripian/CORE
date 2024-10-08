import json
import os

from utilities import DatabaseConfig
from utilities.logging.logging_utilities import error_handler


class Keywords:
    keywords_list = []

    @classmethod
    @error_handler
    def load_latest_keywords(cls):
        cls.directory_path = DatabaseConfig.set_keyword_dir()
        # List all JSON files in the given directory that include "keywords" in their name
        files = [
            os.path.join(cls.directory_path, f)
            for f in os.listdir(cls.directory_path)
            if f.endswith(".json") and "keywords" in f.lower()
        ]

        # Find the most recently modified file
        latest_file = max(files, key=os.path.getmtime)

        # Load and return the keywords from the most recent file
        with open(latest_file) as f:
            cls.keywords_list = json.load(f)
            return cls.keywords_list
