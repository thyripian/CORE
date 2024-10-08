import logging
from unittest import mock

import pytest

from initialization.config_manager import ConfigManager
from utilities.configurations.database_config import DatabaseConfig


@pytest.fixture
def mock_config_manager():
    with mock.patch(
        "initialization.config_manager.ConfigManager.get_user_config"
    ) as mock_get_config:
        yield mock_get_config


def test_set_keyword_dir(mock_config_manager, caplog):
    # Test with a mock configuration
    mock_config_manager.return_value = {"keyword_dir": "/mock/keyword/dir"}
    assert DatabaseConfig.set_keyword_dir() == "/mock/keyword/dir"


def test_set_postgres_conn_data(mock_config_manager, caplog):
    # Test with a mock configuration
    mock_config_manager.return_value = {"host": "localhost", "port": 5432}
    DatabaseConfig.set_postgres_conn_data()
    assert DatabaseConfig.postgres_conn_data == {"host": "localhost", "port": 5432}


def test_set_elastic_conn_data(mock_config_manager, caplog):
    # Test with a mock configuration
    mock_config_manager.return_value = {
        "host": "localhost",
        "port": 9200,
        "index": "test_index",
    }
    DatabaseConfig.set_elastic_conn_data()
    assert DatabaseConfig.elastic_conn_data == {
        "host": "localhost",
        "port": 9200,
        "index": "test_index",
    }


def test_set_sqlite_conn_data(mock_config_manager, caplog):
    # Test with a mock configuration
    mock_config_manager.return_value = {"sqlite_directory": "/mock/sqlite/dir"}
    DatabaseConfig.set_sqlite_conn_data()
    assert DatabaseConfig.sqlite_conn_data == {"sqlite_directory": "/mock/sqlite/dir"}
