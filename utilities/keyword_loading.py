import json
import os

from utilities import DatabaseConfig
from utilities.logging.logging_utilities import error_handler


class Keywords:
    keywords_list = []

    @classmethod
    @error_handler
    def load_latest_keywords(cls, user_config=None):
        # Use the passed user_config to set the keyword directory if provided
        if user_config:
            cls.directory_path = user_config.get("keywords", {}).get(
                "keyword_dir", None
            )
        else:
            # Fallback to DatabaseConfig's set_keyword_dir method if user_config is not provided
            cls.directory_path = DatabaseConfig.set_keyword_dir()

        # If directory_path is still None after trying both options, raise an error
        if cls.directory_path is None:
            raise ValueError(
                "Keyword directory path could not be determined. Please provide a valid user configuration."
            )

        # List all JSON files in the given directory that include "keywords" in their name
        try:
            files = [
                os.path.join(cls.directory_path, f)
                for f in os.listdir(cls.directory_path)
                if f.endswith(".json") and "keywords" in f.lower()
            ]
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Keyword directory '{cls.directory_path}' does not exist."
            )

        # Find the most recently modified file
        if not files:
            raise FileNotFoundError(
                f"No keyword files found in directory: {cls.directory_path}"
            )

        latest_file = max(files, key=os.path.getmtime)

        # Load and return the keywords from the most recent file
        with open(latest_file) as f:
            cls.keywords_list = json.load(f)
            return cls.keywords_list
