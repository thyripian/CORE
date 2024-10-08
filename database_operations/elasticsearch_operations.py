import logging
import os

from database_operations import DatabaseManager
from database_operations.base_database import BaseDatabase
from utilities import DatabaseConfig
from utilities.logging.logging_utilities import error_handler

logger = logging.getLogger(__name__)


class ElasticsearchDatabase(BaseDatabase):
    _es_client = None  # Class-level variable for the Elasticsearch client

    @classmethod
    def get_elasticsearch_client(cls):
        """
        Class method to fetch the Elasticsearch client, only fetching it once.
        """
        if cls._es_client is None:
            cls._es_client = DatabaseManager.get_elasticsearch_client()
        return cls._es_client

    @classmethod
    @error_handler
    def check_exists(cls, hash_value):
        """
        Class method to check if a hash value exists in Elasticsearch.
        """
        logger.info("INSIDE ELASTIC / CHECK EXISTS")

        # Get Elasticsearch client using the class method
        es = cls.get_elasticsearch_client()
        if es:
            logger.info(f"ES CLIENT SET: {es}")
        else:
            logger.error("UNABLE TO PULL ES CLIENT")
            return False  # Return early if ES client is not available

        try:
            logger.info(f"INDEX NAME FROM DB CONFIG: {DatabaseConfig.elastic_index}")
            index_name = DatabaseConfig.elastic_index

            # Perform search in Elasticsearch
            response = es.search(index=index_name, query={"term": {"_id": hash_value}})

            # Extracting file name from the file_path and logging it
            if response["hits"]["total"]["value"] > 0:
                file_path = response["hits"]["hits"][0]["_source"].get(
                    "file_path", None
                )
                if file_path:
                    file_name = os.path.basename(file_path)  # Extract the file name
                    logger.info(f"File exists: {file_name}")
                return True
            else:
                logger.info("File does not exist.")
                return False
        except Exception as e:
            logger.error(f"Error checking existence of hash: {e}")
            return False

    @classmethod
    @error_handler
    def get_last_processed_date(cls):
        """
        Class method to get the last processed date from Elasticsearch.
        """
        es = cls.get_elasticsearch_client()
        query = {
            "size": 1,
            "sort": [{"processed_time": {"order": "desc"}}],
            "_source": ["processed_time"],
        }
        index_name = DatabaseConfig.elastic_index
        res = es.search(index=index_name, body=query)
        if res["hits"]["hits"]:
            return res["hits"]["hits"][0]["_source"]["processed_time"]
        return None

    @classmethod
    @error_handler
    def save_data(cls, info):
        """
        Class method to save data to Elasticsearch.
        """
        es = cls.get_elasticsearch_client()

        if es is None:
            logger.error("Elasticsearch client is not initialized.")
            return False

        index_name = DatabaseConfig.elastic_index
        status = DatabaseManager.ensure_index_exists(index_name)
        logger.info(f"Elastic index status :: EXISTS? :: {status}")

        if status:
            # Document preparation and indexing logic for Elasticsearch
            logger.info("\tAttempting to create Elastic doc.")
            es_doc = {
                "SHA256_hash": info["file_hash"],
                "highest_classification": info["highest_classification"],
                "caveats": info["caveats"],
                "file_path": info["file_path"],
                "locations": info["locations"],
                "timeframes": info["timeframes"],
                "subjects": info["subjects"],
                "topics": info["topics"],
                "keywords": info["keywords"],
                "MGRS": info["MGRS"],
                "images": info["images"],
                "full_text": info["full_text"],
                "processed_time": info["processed_time"],
            }

            # Create a shallow copy of es_doc and remove 'images' and 'full_text' from it
            log_doc = es_doc.copy()
            log_doc.pop("images", None)  # Remove 'images' key if it exists
            log_doc.pop("full_text", None)  # Remove 'full_text' key if it exists

            # Log the modified dictionary without 'images' and 'full_text'
            logger.info(f"DOC: \n{log_doc}")

            logger.info("\tElastic doc created.")

            logger.info("\n\t>>> Trying to store to Elastic index <<<\n")
            es.index(index=index_name, id=info["file_hash"], document=es_doc)
            logger.info("\n\t\tDATA STORED TO ELASTIC INDEX.")

            return True

    @classmethod
    @error_handler
    def delete_data(cls):
        """
        Placeholder class method for deleting data from Elasticsearch.
        """
        pass
