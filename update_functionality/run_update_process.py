import datetime
import json
import logging
import os

import requests

from data_processing import DataProcessingManager
from database_operations.elasticsearch_operations import ElasticsearchDatabase
from file_handling.extract_files import extract_files_from_directory
from initialization.init_app import AppInitialization
from utilities import DatabaseConfig
from utilities.configurations.configs import AppConfig
from utilities.logging.logging_utilities import error_handler

# Get the absolute path to the directory where this script is located
base_dir = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger(__name__)

progress_state = {"current": 0, "total": 0, "message": "Not started"}


def update_progress(current, total, message):
    global progress_state
    progress_state["current"] = current
    progress_state["total"] = total
    progress_state["message"] = message
    logger.info(
        f"Progress Updated: {progress_state}"
    )  # Add print to confirm it's being called


def on_demand_initialization(user_config):
    logger.info("INITIALIZING ES_CLIENT FOR UPDATE PROCESS")
    # DatabaseConfig.set_elastic_conn_data(user_config)
    DatabaseConfig.set_conns(user_config)
    logger.info(f"Update CWD: {os.getcwd()}")
    AppConfig.load_sys_config(file_path="../../config/sys_config.json")


# Helper function to get the most recent file creation date
def get_most_recent_file_creation_date(directory):
    most_recent_date = None

    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_creation_time = os.path.getctime(file_path)  # Get file creation time
            file_creation_date = datetime.datetime.fromtimestamp(
                file_creation_time, tz=datetime.timezone.utc
            )  # Convert to UTC

            if not most_recent_date or file_creation_date > most_recent_date:
                most_recent_date = file_creation_date

    return most_recent_date


@error_handler
def run_process():
    """
    Function to handle checking for updates and processing new files.
    """
    # logger.info("Starting update process.")
    logger.info("********** STARTING UPATE PROCESS ************")

    try:
        response = requests.get(
            "http://localhost:5005/get_settings"
        )  # Adjust port if needed
        response.raise_for_status()
        settings = response.json()
        logger.info(f"Fetched config: {settings}")
    except Exception as e:
        logger.info(f"Failed to connect to run_app API: {str(e)}")
        settings = {}

    process_dir = settings.get("directory", None)
    user_config = settings.get("user_config", None)

    if not process_dir or not user_config:
        update_progress(0, 0, "Missing configuration settings")
        return

    logger.info(f"Processing directory passed to update func: {process_dir}")
    logger.info(f"Config passed to update func: {user_config}")

    on_demand_initialization(user_config)

    # Check if the most recent processed date is before today
    last_processed_date = ElasticsearchDatabase.get_last_processed_date()
    logger.info(f"LAST PROCESSED DATE: {last_processed_date}")
    # if last_processed_date:
    #     last_processed_date = datetime.datetime.fromisoformat(last_processed_date)
    #     today = datetime.datetime.now(datetime.timezone.utc).date()
    #     if last_processed_date.date() >= today:
    #         update_progress(0, 0, 'No new updates. Last processed date is today or later.')
    #         return
    # Convert Elasticsearch last processed date to datetime if available
    # Get the most recent file creation date in the processing directory
    most_recent_file_creation_date = get_most_recent_file_creation_date(process_dir)
    logger.info(f"MOST RECENT FILE CREATION DATE: {most_recent_file_creation_date}")

    if not most_recent_file_creation_date:
        update_progress(0, 0, "No files found in the directory")
        return

    if last_processed_date:
        last_processed_date = datetime.datetime.fromisoformat(last_processed_date)

        # Compare the two dates
        if last_processed_date >= most_recent_file_creation_date:
            update_progress(
                0,
                0,
                "No new updates. Last processed date is more recent than or equal to the newest file.",
            )
            return

    if process_dir:
        # Process files from the selected directory
        documents = extract_files_from_directory(process_dir)
        processing_manager = DataProcessingManager()

        total_files = sum(
            len(files) for files in documents.values()
        )  # Total number of files
        logger.info(f"TOTAL FILES: {total_files}")
        processed_count = 0

        for ext, files in documents.items():
            for file_path in files:
                logger.info(f"Starting with file: {file_path}")
                # Generate file hash using the correct method name
                # logger.info("Attempting to generate hash value.")
                file_hash = processing_manager.calculate_file_hash(file_path)
                # logger.info(f"GENERATED HASH: {file_hash}")

                # Create a document metadata dictionary
                document = {
                    "file_hash": file_hash,
                    "file_path": file_path,
                    # Include other metadata fields as needed
                }
                # logging.info(f"DOCUMENT OBJECT: {document}")
                f_num = processed_count + 1
                # Check if the file has already been processed
                logger.info("Attempting to check if hash value exists in elastic.")
                try:
                    if not ElasticsearchDatabase().check_exists(document["file_hash"]):
                        lens = len(files)
                        # Process the single file by passing it in a dictionary structure
                        # logger.info(f"Sending the following data to processing manager: \n{ext, file_path,f_num,lens}")
                        processing_manager.process_data({ext: [file_path]}, f_num, lens)
                        processed_count += 1
                        update_progress(
                            processed_count,
                            total_files,
                            f"Processing file {processed_count} of {total_files}",
                        )
                    else:
                        logger.info("File already exists. Skipping.")
                        processed_count += 1
                        update_progress(
                            processed_count,
                            total_files,
                            f"Processing file {processed_count} of {total_files}",
                        )
                except Exception as e:
                    logger.error(f"Unable to process data: {e}")

        # Optionally export results
        if len(DatabaseConfig.all_info_df) > 0:
            results_path = AppConfig.fallback_csv_path
            DatabaseConfig.all_info_df.to_csv(results_path, index=False)
            logger.info(f"Results exported to {results_path}")

        update_progress(total_files, total_files, "Completed")

    logging.getLogger(__name__).info("Update process completed.")
    # print("Update process completed.")
