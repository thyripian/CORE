import logging

import requests

from initialization.init_app import AppInitialization

from .elasticsearch_operations import ElasticsearchDatabase
from .fallback_operations import CSVFailsafe
from .postgres_operations import PostgreSQLDatabase
from .sqlite_operations import SQLiteDatabase

logger = logging.getLogger(__name__)


class DatabaseFactory:
    @staticmethod
    def get_database(db_name=None):
        logger.info("Inside GET_DATABASE")
        """
        Retrieves an instance of the first available database class based on the configured availability.
        """
        if AppInitialization.connection_status:
            connection_status = AppInitialization.connection_status
            logger.info(f"Using APP INIT connection status: {connection_status}")
        else:
            response = requests.get("http://localhost:5005/get_availabilities")
            response.raise_for_status()
            connection_status = response.json().get("connects")
            logger.info(
                f"Using API and requests connection status: {connection_status}"
            )

        if db_name is None:
            if connection_status["elasticsearch"]:
                logger.info("Availability says ELASTIC is available.")
                return ElasticsearchDatabase()
            elif connection_status["postgresql"]:
                logger.info("Availability says POSTGRES is available.")
                return PostgreSQLDatabase()
            elif connection_status["sqlite"]:
                logger.info("Availability says SQLITE is available.")
                return SQLiteDatabase()
            else:
                logger.info("FALLING BACK TO CSV")
                return CSVFailsafe()

        elif db_name is not None:
            if db_name == "elasticsearch":
                return ElasticsearchDatabase()
            elif db_name == "postgresql":
                return PostgreSQLDatabase()
            elif db_name == "sqlite":
                return SQLiteDatabase()
            elif db_name == "pandas":
                return CSVFailsafe()
