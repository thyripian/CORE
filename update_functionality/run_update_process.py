import datetime
import json
import logging
import os
import queue
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import requests

from data_processing import DataProcessingManager
from database_operations import DatabaseManager
from database_operations.elasticsearch_operations import ElasticsearchDatabase
from file_handling.extract_files import extract_files_from_directory
from initialization.init_app import AppInitialization
from utilities import DatabaseConfig
from utilities.configurations.configs import AppConfig
from utilities.keyword_loading import Keywords
from utilities.logging.logging_utilities import error_handler
from utilities.resource_management import calculate_dynamic_batch_size

# Get the absolute path to the directory where this script is located
base_dir = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger(__name__)

# This will store progress state for use by the API.
progress_state = {"current": 0, "total": 0, "message": "Not started"}
progress_lock = (
    threading.Lock()
)  # Ensure that updates to progress_state are thread-safe.


# Function to update the progress_state safely with a lock
def update_progress(current, total, message):
    global progress_state
    with progress_lock:
        progress_state["current"] = current
        progress_state["total"] = total
        progress_state["message"] = message
        logger.info(f"Progress Updated: {progress_state}")


def on_demand_initialization(user_config):
    logger.info("INITIALIZING DATABASE CONNECTIONS FOR UPDATE PROCESS")

    # Step 1: Set up configuration from user_config
    DatabaseConfig.set_conns(user_config)

    # Step 2: Fetch connection status from the main API (5005/api/availabilities)
    try:
        response = requests.get("http://localhost:5005/api/availabilities")
        response.raise_for_status()
        availabilities = response.json().get("connects")

        # Step 3: Update the connection statuses in DatabaseManager
        if availabilities:
            DatabaseManager.set_connection_status(availabilities)
            logger.info(
                f"Updated connection status from API: {DatabaseManager.connection_status}"
            )
        else:
            logger.error("Failed to retrieve connection statuses from the API")

    except requests.RequestException as e:
        logger.error(
            f"Error retrieving connection status from /api/availabilities: {e}"
        )

    # Step 4: Load additional configurations and initialize NLP
    logger.info(f"Update CWD: {os.getcwd()}")
    AppConfig.load_sys_config(file_path="../../config/sys_config.json")
    AppInitialization.load_nlp()

    # Step 5: Load Keywords
    try:
        AppInitialization.load_keywords(user_config=user_config)
        logger.info("Keywords loaded successfully for on-demand initialization.")
        logger.info(
            f"Keywords (from Keywords class) are as follows:\n {Keywords.keywords_list}"
        )
        logger.info(
            f"Keywords (from InitApp class) are as follows:\n {AppInitialization.keywords}"
        )
    except Exception as e:
        logger.error(f"Failed to load keywords during on-demand initialization: {e}")


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
    Function to handle checking for updates and processing new files in batches.
    """
    logger.info("********** STARTING UPDATE PROCESS ************")

    start_time = time.time()

    try:
        response = requests.get("http://localhost:5005/api/settings")
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

        total_files = sum(len(files) for files in documents.values())
        logger.info(f"TOTAL FILES: {total_files}")

        # Dynamically calculate batch size based on available resources
        dynamic_batch_size = calculate_dynamic_batch_size()
        logger.info(f"DYNAMIC BATCH SIZE SET TO: {dynamic_batch_size}")

        # Create a queue to manage the batches
        file_queue = queue.Queue()
        for ext, files in documents.items():
            for file_path in files:
                file_queue.put((ext, file_path))

        # Initialize progress tracking
        update_progress(0, total_files, "Starting the processing")

        processed_count = 0

        def process_batch():
            nonlocal processed_count
            while not file_queue.empty():
                batch = []
                for _ in range(dynamic_batch_size):
                    if not file_queue.empty():
                        batch.append(file_queue.get())

                if not batch:
                    break

                for ext, file_path in batch:
                    logger.info(f"Starting with file: {file_path}")
                    try:
                        file_hash = processing_manager.calculate_file_hash(file_path)
                        document = {
                            "file_hash": file_hash,
                            "file_path": file_path,
                        }
                        if not ElasticsearchDatabase().check_exists(
                            document["file_hash"]
                        ):
                            processing_manager.process_data(
                                {ext: [file_path]}, processed_count + 1, total_files
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

        # Using ThreadPoolExecutor to process files concurrently in batches
        with ThreadPoolExecutor(max_workers=dynamic_batch_size) as executor:
            futures = [
                executor.submit(process_batch) for _ in range(dynamic_batch_size)
            ]
            for future in futures:
                future.result()

        # Optionally export results
        if len(DatabaseConfig.all_info_df) > 0:
            results_path = AppConfig.fallback_csv_path
            DatabaseConfig.all_info_df.to_csv(results_path, index=False)
            logger.info(f"Results exported to {results_path}")

        update_progress(total_files, total_files, "Completed")

    end_time = time.time()
    total_time = end_time - start_time
    logger.info(f"Update process completed in {total_time:.2f} seconds.")

    logger.info("Update process completed.")
