import json
import logging
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from utilities.configurations.configs import AppConfig


@pytest.fixture
def mock_sys_config():
    return {
        "logging": {"log_directory": "./logs"},
        "nlp": {"model": "en_core_web_sm"},
        "keywords": {"default_path": "./utilities/default_keywords"},
        "output": {"fallback_csv": "~/Downloads/MERLIN_fallback_test.csv"},
        "testing_mode": {"testing_flag": True},
    }


def test_load_sys_config(mock_sys_config, caplog):
    logging.basicConfig(level=logging.INFO)  # Basic configuration for testing
    caplog.set_level(logging.INFO)
    # Convert dictionary to JSON string and use it as file content
    mock_data = json.dumps(mock_sys_config)
    with patch("builtins.open", mock_open(read_data=mock_data)), patch(
        "json.load", return_value=mock_sys_config
    ), patch(
        "utilities.configs.load", return_value="mocked_nlp_model"
    ) as mock_load, patch(
        "os.path.expanduser",
        return_value="/home/user/Downloads/MERLIN_fallback_test.csv",
    ):
        AppConfig.load_sys_config()

        # Check that the configuration has been loaded correctly
        assert AppConfig.system_config == mock_sys_config
        assert AppConfig.nlp == "mocked_nlp_model"
        assert AppConfig.TESTING is True
        assert (
            AppConfig.fallback_csv_path
            == "\\home\\user\\Downloads\\MERLIN_fallback_test.csv"
        )

        # Check that the external load function was called correctly
        mock_load.assert_called_once_with("en_core_web_sm")
        # Check logging information
        assert "en_core_web_sm" in caplog.text
        assert "TESTING FLAG: True" in caplog.text
