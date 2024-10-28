import logging

import requests

from initialization.init_app import AppInitialization
from utilities.logging.logging_utilities import error_handler

from .db_factory import DatabaseFactory

logger = logging.getLogger(__name__)


class HashChecker:
    """
    A class responsible for checking the existence of a hash across various storage systems,
    stopping on the first success but always including a check against the Pandas DataFrame.
    """

    @staticmethod
    @error_handler
    def check_hash_exists(hash_value):
        """
        Checks if the hash exists in the available and connected databases according to the priority list,
        and always checks the Pandas DataFrame as a final step, stopping at the first successful check.
        """
        # Priority order of database services
        priority_order = ["elasticsearch", "postgresql", "sqlite"]

        response = requests.get("http://localhost:5005/api/availabilities")
        response.raise_for_status()
        connects = response.json().get("connects")
        # Check databases in order of priority
        for service_key in priority_order:
            if AppInitialization.connection_status.get(service_key) or connects.get(
                service_key
            ):
                logger.info(f"Checking for hash in {service_key}...")
                db = DatabaseFactory.get_database(service_key)
                if db and db.check_exists(hash_value):
                    logger.info(f"Hash found in {service_key}.")
                    return True
                else:
                    logger.info(
                        f"No hash found in {service_key}. Checking Pandas DataFrame next."
                    )
                    break  # Stop checking other databases once the first connected is queried

        # Always check the Pandas DataFrame last
        db = DatabaseFactory.get_database("pandas")
        if db and db.check_exists(hash_value):
            logger.info("Hash found in Pandas DataFrame.")
            return True
        else:
            logger.info("No hash found in Pandas DataFrame.")

        # If no hash is found after all checks
        logger.warning(
            "Hash not found in any available databases or the Pandas DataFrame."
        )
        return False
