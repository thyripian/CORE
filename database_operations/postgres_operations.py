import logging

from database_operations.base_database import BaseDatabase
from database_operations.db_manager import DatabaseManager
from utilities.logging.logging_utilities import error_handler

logger = logging.getLogger(__name__)


class PostgreSQLDatabase(BaseDatabase):
    # def __init__(self):
    #     self.pool = DatabaseManager.get_postgres_connection()

    @error_handler
    def check_exists(self, hash_value):
        """
        Checks if a report identified by hash_value
        already exists in the PostgreSQL database.
        """
        with DatabaseManager.get_postgres_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT EXISTS(SELECT 1 FROM reports WHERE SHA256_hash=%s)",
                    (hash_value,),
                )
                exists = cursor.fetchone()[0]
            # self.pool.putconn(conn)
        return exists

    @error_handler
    def save_data(self, info):
        """
        Insert or update data in the PostgreSQL database.
        """
        with DatabaseManager.get_postgres_connection() as conn:
            with conn.cursor() as cursor:
                sql = (
                    "INSERT INTO reports (SHA256_hash, highest_classification, caveats, file_path, locations, "
                    "timeframes, subjects, topics, keywords, MGRS, images, full_text) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                    "ON CONFLICT (SHA256_hash) DO UPDATE "
                    "SET highest_classification = EXCLUDED.highest_classification, "
                    "caveats = EXCLUDED.caveats, "
                    "file_path = EXCLUDED.file_path, "
                    "locations = EXCLUDED.locations, "
                    "timeframes = EXCLUDED.timeframes, "
                    "subjects = EXCLUDED.subjects, "
                    "topics = EXCLUDED.topics, "
                    "keywords = EXCLUDED.keywords, "
                    "MGRS = EXCLUDED.MGRS, "
                    "images = EXCLUDED.images, "
                    "full_text = EXCLUDED.full_text;"
                )

                cursor.execute(
                    sql,
                    (
                        info["file_hash"],
                        info["highest_classification"],
                        info["caveats"],
                        info["file_path"],
                        info["locations"],
                        info["timeframes"],
                        info["subjects"],
                        info["topics"],
                        info["keywords"],
                        info["MGRS"],
                        info["images"],
                        info["full_text"],
                    ),
                )
                # cursor.execute(sql, (info['file_hash'], ...))
                conn.commit()
            # self.pool.putconn(conn)
        return True

    @error_handler
    def delete_data(self, hash_value):
        """
        Optionally implement the delete method if needed.
        If a standardized delete method is made in the
        abstract method, use the commented out line.
        """
        pass
        # return super().delete_data(hash_value)
