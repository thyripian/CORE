# STILL BEING BUILT --> NEEDS LOGIC FOR SETTING DIRECTORY

import logging
import sqlite3
import os
import json
from utilities import DatabaseConfig
from .db_manager import DatabaseManager
from utilities.logging.logging_utilities import error_handler
from database_operations.base_database import BaseDatabase

logger = logging.getLogger(__name__)

class SQLiteDatabase(BaseDatabase):
    def __init__(self):
        self.conn_params = DatabaseManager.sqlite_database

    def check_exists(self, hash_value):
            with sqlite3.connect(self.conn_params) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT EXISTS(SELECT 1 FROM reports WHERE SHA256_hash=?)", (hash_value,))
                return cursor.fetchone()[0]

    @error_handler
    def save_data(self, info):
        """
        Save data to an SQLite database as a fallback mechanism when other databases are unavailable.

        This function creates a SQLite database if it does not exist and stores the provided information
        by serializing complex data structures into strings where necessary.

        :param info: Dictionary containing extracted information from the document.
        :param file_hash: SHA256 hash of the file being processed.
        :param directory: Directory path where the SQLite database will be saved.
        """
        logger.info(f"Type of info: {type(info)}")
        if not isinstance(info, dict):
            logger.error("Expected 'info' to be a dictionary.")
            return False
        
        db_full_path = self.conn_params
        logger.info(f"Saving data to {db_full_path}")
        # Connection and cursor setup for SQLite
        conn = sqlite3.connect(db_full_path)
        c = conn.cursor()
        # Create the reports table if it doesn't already exist
        c.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                SHA256_hash TEXT PRIMARY KEY,
                highest_classification TEXT,
                caveats TEXT,
                file_path TEXT,
                locations TEXT,
                timeframes TEXT,
                subjects TEXT,
                topics TEXT,
                keywords TEXT,
                MGRS TEXT,
                images TEXT,
                full_text TEXT
            )
        ''')

        # Insert or replace the information into the SQLite database
        c.execute('''
            INSERT INTO reports (
                SHA256_hash,
                highest_classification,
                caveats,
                file_path,
                locations,
                timeframes,
                subjects,
                topics,
                keywords,
                MGRS,
                images,
                full_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(SHA256_hash) DO UPDATE SET
                highest_classification = excluded.highest_classification,
                caveats = excluded.caveats,
                file_path = excluded.file_path,
                locations = excluded.locations,
                timeframes = excluded.timeframes,
                subjects = excluded.subjects,
                topics = excluded.topics,
                keywords = excluded.keywords,
                MGRS = excluded.MGRS,
                images = excluded.images,
                full_text = excluded.full_text
        ''', (
            info['file_hash'], 
            info['highest_classification'], 
            info['caveats'], 
            info['file_path'],
            info['locations'], 
            info['timeframes'], 
            info['subjects'], 
            info['topics'],
            info['keywords'], 
            info['MGRS'], 
            info['images'], 
            info['full_text']
        ))
        conn.commit()
        conn.close()
        logger.info(f"\t\tSaved fallback data to SQLite at {db_full_path}")
        return True
    
    @error_handler
    def delete_data():
        pass