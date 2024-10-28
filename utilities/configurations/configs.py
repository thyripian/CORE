import json
import logging
import os
from pathlib import Path

from spacy import load

from ..logging.logging_utilities import error_handler

logger = logging.getLogger(__name__)


class AppConfig:
    user_config = None
    system_config = None
    nlp = None
    keywords = None
    TESTING = False
    fallback_csv_path = None
    logger.info(f"Application working directory: {os.getcwd()}")

    @classmethod
    def load_sys_config(cls, file_path=None):
        """
        Load the system configuration from a specified JSON file. This configuration
        includes application-wide settings such as paths and external model specifications.

        Args:
            file_path (str): Path to the system configuration JSON file.
                             Default is "./configs/sys_config.json".

        Loads:
            - NLP model specified in the configuration.
            - Fallback CSV path from system configuration.
            - Initializes system configuration settings.
        """
        if file_path is None:
            # Get the absolute path to the directory where this script is located
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # Construct the absolute path for the sys_config.json file
            file_path = os.path.join(base_dir, "..", "..", "config", "sys_config.json")

        with open(file_path) as sys_config_file:
            cls.system_config = json.load(sys_config_file)
            cls.nlp = load(cls.system_config["nlp"]["model"])
            logger.info(f"NLP model loaded: {cls.system_config['nlp']['model']}")
            cls.TESTING = cls.system_config["testing_mode"]["testing_flag"]
            logger.info(f"TESTING FLAG: {cls.TESTING}")
            cls.fallback_csv_path = str(
                Path(os.path.expanduser(cls.system_config["output"]["fallback_csv"]))
            )

    @classmethod
    def load_user_config(cls, config_dict):
        """
        Load the user configuration from a provided dictionary. This configuration
        includes user-specific settings for the application.

        Args:
            config_dict (dict): Dictionary containing user configuration settings.

        Loads:
            - User-specific configurations.
        """
        # Directly assign the dictionary to the user_config class variable
        cls.user_config = config_dict

        # Optionally, validate the configurations
        cls.validate_configurations(cls.user_config)

        logger.info("User configuration loaded successfully.")

    @classmethod
    def validate_configurations(cls, config):
        logger = logging.getLogger(__name__)
        """
        Validates the necessary keys in the loaded configuration.
        Args:
            config (dict): Configuration data to validate.
        """
        necessary_keys = ["postgres", "elasticsearch", "sqlite", "keywords", "logging"]
        for key in necessary_keys:
            if key not in config:
                logger.error(
                    f"{key.capitalize()} configuration is missing in the configuration data."
                )
                raise ValueError(
                    f"{key.capitalize()} configuration is missing in the configuration data."
                )
            else:
                logger.info(f"{key.capitalize()} configuration loaded successfully.")

    @classmethod
    @error_handler
    def load_keywords(cls, file_path=None):
        """
        Load keywords from a JSON file specified by the path or use the default path
        defined in the system configuration.

        Args:
            file_path (str, optional): Path to the JSON file containing keywords. If None,
                                       the default path from the system configuration is used.

        Updates:
            - Keywords list for the application's use.
        """
        if not file_path:
            file_path = cls.system_config["keywords"]["default_path"]
        logger.info(f"Loading keywords from {file_path}")
        with open(file_path) as keywords_file:
            cls.keywords = json.load(keywords_file)
