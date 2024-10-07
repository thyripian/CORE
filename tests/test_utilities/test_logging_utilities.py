import pytest
import logging
import os
from unittest import mock
from utilities.logging.logging_utilities import (
    session,
    setup_logging,
    init_logging,
    error_handler,
    SESSION_LEVEL_NUM,
    SESSION_LEVEL_NAME
)

# Test custom logging level
def test_custom_logging_level():
    logger = logging.getLogger('test_logger')
    with mock.patch.object(logger, '_log') as mock_log:
        logger.session('This is a session level message')
        mock_log.assert_called_once_with(SESSION_LEVEL_NUM, 'This is a session level message', ())

# Test setup logging
def test_setup_logging(tmp_path):
    log_directory = tmp_path / "logs"
    log_filename = "test_log.log"

    setup_logging(str(log_directory), log_filename)

    log_path = log_directory / log_filename
    assert log_path.exists()

    logger = logging.getLogger()
    logger.info("This is a test info message")

    with open(log_path, 'r') as log_file:
        logs = log_file.read()
        assert "This is a test info message" in logs

# Test init logging
def test_init_logging(tmp_path, caplog):
    log_directory = tmp_path / "logs"
    log_filename = "test_log.log"

    setup_logging(str(log_directory), log_filename)
    logger = logging.getLogger('utilities.logging_utilities')  # Use the correct logger name

    # Ensure the logger propagates messages to the root logger
    logger.propagate = True

    with caplog.at_level(logging.INFO):
        init_logging(logger)

    # Print captured messages for debugging
    for message in caplog.messages:
        print(f"Captured log message: {message}")

    # Check directly in the log file
    log_path = log_directory / log_filename
    with open(log_path, 'r') as log_file:
        log_contents = log_file.read()
        print(f"Log file contents:\n{log_contents}")

    # Check both captured logs and log file for expected messages
    expected_messages = [
        "REPORT DATA EXTRACTION PIPELINE (R-DEP)",
        "“Do or do not, there is no try.”",
        "Developed by Kevan White - 389 Data Team",
        "Current as of: 09 May 2024"
    ]

    for expected_message in expected_messages:
        assert any(expected_message in message for message in caplog.messages) or expected_message in log_contents

# Test error handler
def test_error_handler(caplog):
    @error_handler(default_return_value="default", reraise=False)
    def function_that_raises():
        raise ValueError("This is an error")

    with caplog.at_level(logging.ERROR):
        result = function_that_raises()

    assert result == "default"
    assert any("An error occurred in function_that_raises: This is an error" in message for message in caplog.messages)

# Test error handler with reraise
def test_error_handler_with_reraise():
    @error_handler(default_return_value="default", reraise=True)
    def function_that_raises():
        raise ValueError("This is an error")

    with pytest.raises(ValueError, match="This is an error"):
        function_that_raises()
