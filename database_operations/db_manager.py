import logging
import os
from contextlib import contextmanager
from importlib import import_module

from utilities import DatabaseConfig
from utilities.configurations.configs import AppConfig
from utilities.logging.logging_utilities import error_handler

logger = logging.getLogger(__name__)


class DatabaseManager:
    es_client = None
    pg_pool = None
    sqlite_database = None
    availability = DatabaseConfig.availability
    connection_status = {
        "elasticsearch": None,
        "postgresql": None,
        "sqlite": None,
        "fallback": True,  # Assuming fallback is always available
    }
    service_mapping = {
        "elasticsearch": (
            "database_operations.elasticsearch_operations",
            "ElasticsearchDatabase",
        ),
        "postgresql": ("database_operations.postgres_operations", "PostgreSQLDatabase"),
        "sqlite": ("database_operations.sqlite_operations", "SQLiteDatabase"),
        "fallback": ("database_operations.fallback_operations", "CSVFailsafe"),
    }
    imports_tested = False

    def __init__(self):
        # Immediately test the imports when the instance is created
        if not DatabaseManager.imports_tested:
            self.test_imports()
            DatabaseManager.imports_tested = True

    @classmethod
    @error_handler
    def dynamic_import(cls, module_name, class_name):
        try:
            module = import_module(module_name)
            return getattr(module, class_name)
        except ImportError as e:
            logger.error(f"Error importing {module_name}: {e}")
            return None
        except AttributeError as e:
            logger.error(f"Error accessing {class_name} in {module_name}: {e}")
            return None

    @error_handler
    def test_imports(self):
        for service_key, (module_name, class_name) in type(
            self
        ).service_mapping.items():
            service_class = type(self).dynamic_import(module_name, class_name)
            if service_class:
                # instance = service_class()
                logger.session(
                    f"{service_key} : {module_name}, {class_name} able to be set correctly."
                )
            else:
                logger.error(
                    f"{service_key} : {module_name}, {class_name} unable to be set."
                )

    @classmethod
    @error_handler
    def test_initial_connections(cls):
        """
        Tests the initial database connections and updates the connection status.
        This method should be called at the start of the application to verify that all configured databases are accessible.
        """
        cls.connection_status["elasticsearch"] = cls.try_elasticsearch_connection()
        cls.connection_status["postgresql"] = cls.try_postgresql_connection()
        cls.connection_status["sqlite"] = cls.try_sqlite_connection()
        # Update fallback status if necessary, for now, we assume it's always true.
        logger.info(
            f"Initial database connections tested. \n\nRESULTS:\n\t\t{cls.connection_status}"
        )

    @classmethod
    @error_handler(reraise=True)
    def try_elasticsearch_connection(cls):
        if "elasticsearch" in cls.availability and cls.availability["elasticsearch"]:
            cls.get_elasticsearch_client()
            if cls.es_client.ping():
                logger.info("Elasticsearch connection successful.")
                return True
            else:
                logger.info(
                    "Elasticsearch connection unavailable with the current user configuration"
                )
                return False
        else:
            logger.info(
                "Elasticsearch not avaiable as a Python import. Unable to test user configuration details."
            )
            return False

    @classmethod
    @error_handler(reraise=True)
    def try_postgresql_connection(cls):
        if "postgresql" in cls.availability and cls.availability["postgresql"]:
            try:
                with cls.get_postgres_connection() as conn:
                    # If the connection is successfully established, do a simple operation
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT 1"
                    )  # Execute a simple query to test the connection
                    cursor.close()
                    logger.info("PostgreSQL connection successful.")
                    return True
            except Exception as e:
                logger.error(f"Failed to execute test query on PostgreSQL: {e}")
                return False
        else:
            logger.info(
                "PostgreSQL connection unavailable with the current user configuration."
            )
            return False

    @classmethod
    @error_handler(reraise=True)
    def try_sqlite_connection(cls):
        if "sqlite" in cls.availability and cls.availability["sqlite"]:
            from sqlite3 import connect

            cls.get_sqlite_databse()
            conn = connect(
                cls.sqlite_database
            )  # Ensure cls.sqlite_database is correctly initialized
            if conn:
                conn.close()
                logger.info("SQLite connection successful.")
                return True
        else:
            logger.info(
                "SQLite connection unavailable with the current user configuration."
            )
            return False

    @classmethod
    @error_handler(reraise=True)
    def get_elasticsearch_client(cls):
        import copy
        import time

        time.sleep(5)
        logger.info(f"DB MANAGER ES CLIENT: {cls.es_client}")
        if cls.es_client is None:
            try:
                # Fetch and deep copy the Elasticsearch connection info
                elastic_conn_info = copy.deepcopy(DatabaseConfig.elastic_conn_data)
                logger.info(
                    f"ELASTIC CONN DATA COPIED FROM DB CONFIG: {elastic_conn_info}"
                )

                # Extract the hosts information
                hosts = elastic_conn_info.get("hosts")
                logger.info(f"TYPE HOSTS: {type(hosts)}")
                logger.info(f"HOSTS TEXT: {hosts}")
                logger.info(f"Elastic Conn Info: {elastic_conn_info}")
                logger.info(f"Before type check: TYPE HOSTS: {type(hosts)}")
                logger.info(f"HOSTS TEXT: {hosts}")

                # Check if hosts is indeed a list
                if not isinstance(hosts, list):
                    raise ValueError(f"Hosts is not a list: {hosts}")

                # Import Elasticsearch client and instantiate it
                from elasticsearch import Elasticsearch

                cls.es_client = Elasticsearch(
                    hosts,
                    basic_auth=(
                        elastic_conn_info.get("basic_auth", {}).get("user"),
                        elastic_conn_info.get("basic_auth", {}).get("password"),
                    ),
                    verify_certs=elastic_conn_info.get("verify_certs"),
                    ca_certs=elastic_conn_info.get("ca_certs"),
                    max_retries=1,
                    retry_on_timeout=True,
                )

                # Log the successful creation of the Elasticsearch client
                print(f"Elasticsearch client successfully created: {cls.es_client}")
                logging.info(
                    f"Elasticsearch client successfully created: {cls.es_client}"
                )

            # Handle specific connection errors and log them
            except Exception as e:
                print(f"Error during Elasticsearch client creation: {str(e)}")
                logging.error(f"Error during Elasticsearch client creation: {str(e)}")
                raise e

        return cls.es_client

    @classmethod
    @error_handler
    def ensure_index_exists(cls, index_name):
        es = cls.get_elasticsearch_client()
        if not es.indices.exists(index=index_name):
            index_settings = {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                    "analysis": {
                        "tokenizer": {
                            "edge_ngram_tokenizer": {
                                "type": "edge_ngram",
                                "min_gram": 2,
                                "max_gram": 10,
                                "token_chars": ["letter", "digit"],
                            }
                        },
                        "analyzer": {
                            "edge_ngram_analyzer": {
                                "type": "custom",
                                "tokenizer": "edge_ngram_tokenizer",
                                "filter": ["lowercase"],
                            }
                        },
                    },
                },
                "mappings": {
                    "properties": {
                        "SHA256_hash": {"type": "keyword"},
                        "highest_classification": {"type": "text"},
                        "caveats": {"type": "text"},
                        "file_path": {"type": "keyword"},
                        "locations": {"type": "text"},
                        "timeframes": {"type": "text"},
                        "subjects": {"type": "text"},
                        "topics": {"type": "text"},
                        "keywords": {"type": "text"},
                        "MGRS": {
                            "type": "text",
                            "analyzer": "edge_ngram_analyzer",
                            "search_analyzer": "standard",
                        },
                        "images": {"type": "text"},
                        "full_text": {"type": "text"},
                        "processed_time": {"type": "date"},
                    }
                },
            }
            es.indices.create(index=index_name, body=index_settings)
            print(f"Index {index_name} created.")
            return False
        else:
            print(f"Index {index_name} already exists.")
            return True

    @classmethod
    @error_handler
    def create_postgres_pool(cls):
        if cls.pg_pool is None:
            from psycopg2 import pool

            postgres_conn_info = DatabaseConfig.postgres_conn_data
            cls.pg_pool = pool.SimpleConnectionPool(
                minconn=postgres_conn_info["minconn"],
                maxconn=postgres_conn_info["maxconn"],
                user=postgres_conn_info["user"],
                password=postgres_conn_info["password"],
                host=postgres_conn_info["host"],
                port=postgres_conn_info["port"],
                database=postgres_conn_info["database"],
            )
        return cls.pg_pool

    @classmethod
    @error_handler(reraise=True)
    @contextmanager
    def get_postgres_connection(cls):
        if cls.pg_pool is None:
            cls.create_postgres_pool()
        conn = cls.pg_pool.getconn()
        try:
            yield conn
        finally:
            cls.pg_pool.putconn(conn)

    @classmethod
    @error_handler(reraise=True)
    def get_sqlite_databse(cls):
        directory = DatabaseConfig.sqlite_directory
        cls.sqlite_database = os.path.join(directory, "cab_report_fallback.db")

    @classmethod
    def get_service_module(cls, service_key):
        """
        Dynamically imports and returns an instance of the database service class
        based on the provided service_key.
        """
        if service_key not in cls.service_mapping:
            logger.error(f"No service configuration found for {service_key}")
            return None

        module_name, class_name = cls.service_mapping[service_key]
        try:
            module = import_module(module_name)
            service_class = getattr(module, class_name)
            return service_class()  # Instantiate the class
        except (ImportError, AttributeError) as e:
            logger.error(
                f"Error importing or initializing {class_name} from {module_name}: {e}"
            )
            return None

    @classmethod
    def save_data(cls, data, retry_limit=2):
        # Order of priority for database services
        priority_order = ["elasticsearch", "postgresql", "sqlite", "fallback"]
        # priority_order = ['postgresql', 'sqlite', 'fallback'] # FOR TESTING POSTGRESQL
        if AppConfig.TESTING:
            print("Attempting to save to ALL databases for testing purposes.")
            # In testing mode, try to save to all databases, regardless of success
            for service_key in priority_order:
                service_module = cls.get_service_module(service_key)
                if service_module:
                    service_module.save_data(data)  # No need to check the return value
                    logger.info(f"Data saved successfully using {service_key}.")
            return True  # Optionally, you can return True to indicate testing save was attempted
        else:
            for service_key in priority_order:
                available = cls.connection_status.get(service_key, False)
                if not available:
                    continue

                service_module = cls.get_service_module(service_key)
                if service_module:
                    attempt = 0
                    while attempt < retry_limit:
                        try:
                            if service_module.save_data(data):
                                logger.info(
                                    f"Data saved successfully using {service_key}."
                                )
                                return True
                        except Exception as e:
                            logger.error(
                                f"Attempt {attempt + 1} to save data using {service_key} failed: {e}"
                            )
                        attempt += 1

            # If no service succeeded, attempt to save with CSV fallback
            logger.error("All attempts failed, falling back to CSV storage.")
            fallback_module = cls.get_service_module("fallback")
            if fallback_module:
                attempt = 0
                while attempt < retry_limit:
                    try:
                        if fallback_module.save_data(data):
                            logger.info("Data saved successfully using fallback CSV.")
                            return True
                    except Exception as e:
                        logger.error(f"Fallback save attempt {attempt + 1} failed: {e}")
                    finally:
                        attempt += 1

            return False
