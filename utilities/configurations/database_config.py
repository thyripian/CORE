import importlib
import logging

import pandas as pd

from initialization.config_manager import ConfigManager
from utilities.configurations.configs import AppConfig

logger = logging.getLogger(__name__)


class DatabaseConfig:
    es_client = None
    all_info_df = None
    postgres_conn_data = {}
    elastic_conn_data = {}
    elastic_index = None
    sqlite_conn_data = {}
    sqlite_directory = None
    availability = {}

    postgresql_available = False
    elasticsearch_available = False
    sqlite_available = False
    pandas_available = False

    postgres_config = None
    elastic_config = None
    sqlite_config = None

    # Initializing availability as a dictionary at the class level
    availability = {
        "postgresql": False,
        "elasticsearch": False,
        "sqlite": False,
        "fallback": False,
    }

    def __init__(self):
        self.check_availability()
        if self.availability["fallback"]:
            DatabaseConfig.all_info_df = pd.DataFrame()

    @classmethod
    def check_availability(cls):
        cls.availability["postgresql"] = cls.try_import(
            "psycopg2", "from psycopg2 import pool"
        )
        cls.availability["elasticsearch"] = cls.try_import(
            "elasticsearch",
            "from elasticsearch import Elasticsearch, exceptions as es_exceptions",
        )
        cls.availability["sqlite"] = cls.try_import("sqlite3")
        cls.availability["fallback"] = cls.try_import("pandas", "import pandas as pd")

    @classmethod
    def try_import(cls, module_name, import_statement=None):
        try:
            if import_statement:
                # Dynamically import module using importlib for safety
                importlib.import_module(import_statement)
            else:
                importlib.import_module(module_name)

            logger.info("%s Available: True", module_name.capitalize())
            return True
        except ModuleNotFoundError:
            logger.error(
                "Failed to import %s, %s operations will not be available.",
                module_name,
                module_name.capitalize()
            )
            return False


    @classmethod
    def set_keyword_dir(cls):
        keyword_config = ConfigManager.get_user_config("keywords")
        if keyword_config:
            cls.keyword_dir = keyword_config["keyword_dir"]
        else:
            default_keyword_dir = AppConfig.system_config.get("keywords", None).get(
                "default_path"
            )
            logger.error(
                "Unable to identify keyword directory using selected config file."
            )
            logger.info("Defaulting keyword directory to: %s", default_keyword_dir)
            cls.keyword_dir = default_keyword_dir
        return cls.keyword_dir

    @classmethod
    def set_postgres_conn_data(cls):
        if not cls.postgres_config:
            cls.postgres_config = ConfigManager.get_user_config("postgres")
        if cls.postgres_config:
            cls.postgres_conn_data = cls.postgres_config
        else:
            logger.error(
                "PostgreSQL configuration is missing in the configuration data."
            )
            cls.postgres_conn_data = None

    @classmethod
    def set_elastic_conn_data(cls, user_config=None):
        logger.info("INSIDE SET_ELASTIC_CONN_DATA")
        if not cls.elastic_config:
            cls.elastic_config = user_config.get("elasticsearch")
        logger.info("ELASTIC CONFIG: %s", cls.elastic_config)

        if cls.elastic_config:
            cls.elastic_conn_data = cls.elastic_config
            cls.elastic_index = cls.elastic_conn_data.get("index", "")
            if not cls.elastic_index:
                logger.error(
                    "Elasticsearch index configuration is missing in the configuration data."
                )
        else:
            logger.error(
                "Elasticsearch configuration is missing in the configuration data."
            )
            cls.elastic_conn_data = None
        return cls.elastic_conn_data

    @classmethod
    def set_sqlite_conn_data(cls):
        if not cls.sqlite_config:
            cls.sqlite_config = ConfigManager.get_user_config("sqlite")
        if cls.sqlite_config:
            cls.sqlite_conn_data = cls.sqlite_config
            cls.sqlite_directory = cls.sqlite_conn_data.get("sqlite_directory", "")
        else:
            logger.error("SQLite configuration is missing in the configuration data.")
            cls.sqlite_conn_data = None
            cls.sqlite_directory = None

    @classmethod
    def set_fallback_dataframe(cls):
        cls.all_info_df = pd.DataFrame()

    @classmethod
    def get_fallback_dataframe(cls):
        return cls.all_info_df

    @classmethod
    def set_conns(cls, user_config):
        cls.elastic_config = user_config.get("elasticsearch")
        cls.postgres_config = user_config.get("postgres")
        cls.sqlite_config = user_config.get("sqlite")
        cls.set_elastic_conn_data()
        cls.set_postgres_conn_data()
        cls.set_sqlite_conn_data()
        cls.set_fallback_dataframe()
