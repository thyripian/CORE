import datetime
import logging
import os

from database_operations import DatabaseManager
from utilities import (DatabaseConfig, Keywords, confirm_selection,
                       init_logging, select_file, select_folder, setup_logging)
from utilities.configurations.configs import AppConfig
from utilities.logging.logging_utilities import error_handler

from .initialize_elasticsearch import InitElastic

logger = logging.getLogger(__name__)


class AppInitialization:
    availability = {}
    settings = None
    process_dir = None
    nlp = None
    connection_status = {}
    user_config_file = None
    logging_initialized = False
    initialized = False
    logfile = None
    keywords = None

    @classmethod
    @error_handler
    def initialize_application(cls, settings):
        print("Please wait...")
        if cls.initialized:
            logger.info("App already initialized. Skipping redundant initialization.")
            return

        cls.settings = settings
        InitElastic.elastic_init_interaction()
        cls.load_configurations(cls.settings)
        cls.set_database_connections()
        cls.run_connection_tests()
        cls.load_keywords(cls.user_config_file)
        cls.set_processing_directory()
        cls.initialized = True
        logger.info(f"Initialization flag = {cls.initialized}")
        return cls

    @classmethod
    def load_nlp(cls):
        cls.nlp = AppConfig.nlp

    @classmethod
    def load_configurations(cls, user_conf):
        DatabaseConfig()
        cls.availability = DatabaseConfig.availability
        logger.info(f"Availability: {cls.availability}")

        AppConfig.load_sys_config()
        try:
            cls.initialize_logging_process()
            print("Logging Initialized")
        except Exception as e:
            print(f"Error initializing logging: {e}")

        cls.user_config_file = cls.settings.get("user_config")

        try:
            AppConfig.load_user_config(cls.user_config_file)
            logger.info("Successfully loaded user config file:\n", cls.user_config_file)
        except Exception as e:
            logger.info(f"Error loading user configuration from settings: {e}")

        cls.load_nlp()
        logger.info("Configurations loaded successfully.")

    @classmethod
    def initialize_logging_process(cls):
        if cls.logging_initialized:
            logger.info("Logging already initialized. Skipping reinitialization.")
            return  # Skip if logging is already set up
        # Get the absolute path to the directory where this script is located
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the absolute path for the logs directory
        log_directory = os.path.join(base_dir, "..", "logs")
        print("LOG DIRECTORY: ", log_directory)

        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        log_filename = f"CORE_log_{current_date}.log"
        cls.logfile = log_filename

        # Set up logging with the constructed absolute paths
        setup_logging(log_directory=log_directory, log_filename=log_filename)
        init_logging(logging.getLogger(__name__))
        logging.getLogger(__name__).info("Logging set up successfully.")
        cls.logging_initialized = True

    @classmethod
    @error_handler
    def run_connection_tests(cls):
        DatabaseManager()
        DatabaseManager.test_initial_connections()
        cls.connection_status = DatabaseManager.connection_status
        logger.session(f"Connection Status: {cls.connection_status}")

    @classmethod
    @error_handler
    def set_database_connections(cls):
        failures = []

        if not cls.setup_postgres_conn():
            failures.append("PostgreSQL")

        if not cls.setup_elastic_conn():
            failures.append("Elasticsearch")

        if not cls.setup_sqlite_conn():
            failures.append("SQLite")

        if not failures:
            logger.info("All database connections were set successfully.")
        else:
            failure_message = ", ".join(failures)
            logger.error(
                f"Failed to set up the following database connections: {failure_message}"
            )

    @classmethod
    @error_handler(reraise=False)
    def setup_postgres_conn(cls):
        DatabaseConfig.set_postgres_conn_data()
        try:
            if DatabaseManager.try_postgresql_connection():
                logger.info("PostgreSQL connection set successfully.")
                return True
            else:
                logger.error("Failed to establish PostgreSQL connection.")
                return False
        except Exception as e:
            logger.error(f"PostgreSQL setup failed: {e}")
            return False

    @classmethod
    @error_handler(default_return_value=False, reraise=False)
    def setup_elastic_conn(cls):
        DatabaseConfig.set_elastic_conn_data(cls.user_config_file)
        try:
            es_client = DatabaseManager.get_elasticsearch_client()
            if es_client.ping():
                if DatabaseManager.ensure_index_exists(DatabaseConfig.elastic_index):
                    logger.info(
                        "Elasticsearch connection and index setup successfully."
                    )
                    return True
                else:
                    logger.error("Failed to ensure Elasticsearch index exists.")
            else:
                logger.error("Failed to ping Elasticsearch server.")
        except Exception as e:
            logger.error(f"Elasticsearch setup failed: {e}")
        return False

    @classmethod
    @error_handler(reraise=False)
    def setup_sqlite_conn(cls):
        DatabaseConfig.set_sqlite_conn_data()
        try:
            logger.info("SQLite connection set successfully.")
            return True
        except Exception as e:
            logger.error(f"SQLite setup failed: {e}")
            return False

    @classmethod
    @error_handler
    def load_keywords(cls, user_config=None):
        Keywords.load_latest_keywords(user_config=user_config)
        cls.keywords = Keywords.load_latest_keywords(user_config=user_config)
        logger.info("Keywords loaded successfully.")

    @classmethod
    @error_handler
    def select_processing_directory(cls):
        dir_confirmed = False
        while not dir_confirmed:
            cls.process_dir = select_folder("Select the directory to process.")
            logger.info(f"Selected dir: {cls.process_dir}")
            dir_confirmed = confirm_selection(
                "Processing Directory Selection",
                f"Process this directory?\n{cls.process_dir}",
            )
        logger.info(f"Processing directory selected: {cls.process_dir}")

    @classmethod
    @error_handler
    def set_processing_directory(cls):
        cls.process_dir = cls.settings.get("directory")
        logger.info(f"Processing directory set from settings: {cls.process_dir}")
