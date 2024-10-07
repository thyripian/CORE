import os
import logging
import shutil
import pytest
from unittest import mock
from initialization.init_app import AppInitialization
from data_processing.data_processing_manager import DataProcessingManager
from file_handling.extract_files import extract_files_from_directory
from utilities.configurations.configs import AppConfig
from utilities.logging.logging_utilities import setup_logging, init_logging

@pytest.fixture
def setup_full_app_environment():
    input_dir = os.path.abspath("tests/synthetic_data")
    output_dir = os.path.abspath("tests/output")
    mock_config_file = os.path.abspath("config/test_user_config.json")
    sys_config_file = os.path.abspath("config/sys_config.json")

    # Ensure output directory is clean before running the test
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    return {
        "input_dir": input_dir,
        "output_dir": output_dir,
        "mock_config_file": mock_config_file,
        "sys_config_file": sys_config_file
    }

def test_full_application(setup_full_app_environment):
    env = setup_full_app_environment

    # Mock necessary functions and load the actual system config file
    with mock.patch("initialization.init_app.select_file", return_value=env["mock_config_file"]), \
         mock.patch("initialization.init_app.select_folder", return_value=env["input_dir"]), \
         mock.patch("initialization.init_app.confirm_selection", return_value=True):

        # Load system configuration
        AppConfig.load_sys_config(env["sys_config_file"])

        # Ensure NLP model is loaded
        assert AppConfig.nlp is not None, "NLP model is not loaded"

        # Initialize logging
        log_directory = os.path.join(os.getcwd(), 'logs')
        log_filename = "test_merlin_log.log"
        setup_logging(log_directory=log_directory, log_filename=log_filename)
        init_logging(logging.getLogger())

        # Initialize the application
        AppInitialization.initialize_application()

        # Extract files from the directory
        documents = extract_files_from_directory(env["input_dir"])

        # Initialize the processing manager and process data
        processing_manager = DataProcessingManager()
        processing_manager.process_data(documents)

        # Verify results
        results_path = AppConfig.fallback_csv_path
        assert os.path.exists(results_path), f"Results file {results_path} does not exist."
        
        with open(results_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) > 1, "Results file is empty or only contains header."

if __name__ == "__main__":
    pytest.main(["-s", "tests/test_full_app.py"])
