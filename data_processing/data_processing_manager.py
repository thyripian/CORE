import hashlib
import logging
import os
import pickle
import sys

import requests

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

# isort: off
from data_extraction.image_extractors import (
    extract_images_from_excel,
    extract_images_from_pdf,
    extract_images_from_pptx,
    extract_images_from_word,
)
from data_extraction.text_extractors import (
    extract_text_from_excel,
    extract_text_from_pdf,
    extract_text_from_pptx,
    extract_text_from_word,
)
from data_processing.info_processing import extract_info
from database_operations.db_manager import DatabaseManager
from database_operations.hash_checker import HashChecker
from utilities import data_preparation
from utilities.logging.logging_utilities import error_handler

# isort: on

logger = logging.getLogger(__name__)


class DataProcessingManager:
    db_manager = DatabaseManager()

    file_type_mapping = {
        "docx": {"text": extract_text_from_word, "image": extract_images_from_word},
        "xlsx": {"text": extract_text_from_excel, "image": extract_images_from_excel},
        "pptx": {"text": extract_text_from_pptx, "image": extract_images_from_pptx},
        "pdf": {"text": extract_text_from_pdf, "image": extract_images_from_pdf},
    }

    def __init__(self):
        response = requests.get("http://localhost:5005/api/availabilities")
        response.raise_for_status()
        available = response.json().get("available")
        connects = response.json().get("connects")
        logger.info(
            f"The DataProcessingManager has identified the following library availabilities: \n\t{available}"
        )
        logger.info(
            f"The DataProcessingManager has identified the following available database connections: \n\t{connects}"
        )

    @classmethod
    @error_handler(reraise=True)
    def process_data(cls, file_path_dict, f_num, lens):
        # total_files = sum(len(files) for files in file_path_dict.values())
        # cls.progress = progress_window.ProgressWindow(total_items=total_files)
        logger.info(f"Processing file {f_num} of {lens}")
        try:
            for ext, files in file_path_dict.items():
                for file_path in files:
                    logger.info(f"FILE EXT RECEIVED IN PROCESSING MANGER: {ext}")
                    file_hash = cls.calculate_file_hash(file_path)
                    filename = os.path.basename(file_path)

                    # # Check if the file hash already exists in the database to prevent re-processing (change at deployment)
                    if HashChecker.check_hash_exists(file_hash):
                        logger.info(
                            f"Skipping {filename}, already processed / exists in database."
                        )
                        continue

                    file_type = file_path.split(".")[-1]
                    logger.info(f"FILE EXT EXTRACTED BY LOGIC: {file_type}")
                    extractor = cls.file_type_mapping.get(file_type)
                    logger.info(f"EXTRACTOR RESULTS: {extractor}")
                    logger.info(f"EXTRACTOR RESULTING TYPE: {type(extractor)}")

                    logger.info(f"FILE PATH ATTEMPTING TO BE PROCESSED: {file_path}")

                    if extractor:
                        text_data = (
                            extractor["text"](file_path)
                            if "text" in extractor
                            else None
                        )
                        logger.info(f"TEXT_DATA: {text_data}")
                        logger.info(f"TEXT_DATA TYPE: {type(text_data)}")
                        image_data = (
                            extractor["image"](file_path)
                            if "image" in extractor
                            else None
                        )
                        logger.info(f"IMAGE DATA: {image_data}")
                        logger.info(f"IMAGE DATA TYPE: {type(image_data)}")

                        logger.info(f"Text data bool: {bool(text_data)}")
                        try:
                            if text_data:
                                extracted_data = extract_info(text_data)
                                logger.info(
                                    f"Extracted data type: {type(extracted_data)}"
                                )
                        except Exception as e:
                            logger.error(f"Unable to extract data from text_data: {e}")

                        try:
                            if image_data:
                                try:
                                    image_data = (
                                        pickle.dumps(image_data) if image_data else None
                                    )
                                    logger.info(f"Image data type: {type(image_data)}")
                                except Exception as e:
                                    # logger.info(f"Error attempting image compression: {e}")
                                    raise
                        except Exception as e:
                            logger.error(f"Unable to pickle image data: {e}")

                    try:
                        processed_data = cls.preprocess_data(
                            file_path, extracted_data, image_data, file_hash
                        )
                        logger.info(f"Processed {file_path}")
                    except Exception as e:
                        logger.error(f"Unable to preprocess extracted data: {e}")
                        # Save the processed data
                    try:
                        cls.save_data(processed_data)
                        logger.info(f"Successfully saved {file_path }")
                    except Exception as e:
                        logger.error(f"Unable to save preprocessed data: {e}")
            #         cls.progress.update_progress()
        except Exception as e:
            logger.error(f"UNABLE TO PROCESS FILE: {e}")
        # cls.progress.close()
        logger.info("FILE PROCESSED")

    @classmethod
    def calculate_file_hash(cls, file_path):
        """
        Calculates and returns the SHA256 hash of the given file.
        This hash is used as a unique identifier for files to check for duplicates.
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Reading the file in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @classmethod
    def preprocess_data(cls, file_path, data, image_data, file_hash):
        processed_data = data_preparation.prepare_data(
            file_path, data, image_data, file_hash
        )
        return processed_data

    @classmethod
    def save_data(cls, data):
        cls.db_manager.save_data(data)
