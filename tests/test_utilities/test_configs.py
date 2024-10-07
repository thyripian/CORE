import pytest
from unittest import mock
from utilities.configurations.configs import AppConfig
import json
import logging

@pytest.fixture
def mock_open_user_config():
    user_config_data = json.dumps({
        "postgres": {}, "elasticsearch": {}, "sqlite": {}, "keywords": {}, "logging": {}
    })
    with mock.patch("builtins.open", mock.mock_open(read_data=user_config_data)):
        yield

@pytest.fixture
def mock_open_keywords():
    with mock.patch("builtins.open", mock.mock_open(read_data='["keyword1", "keyword2"]')):
        yield

def test_load_keywords(mock_open_keywords, caplog):
    AppConfig.system_config = {'keywords': {'default_path': "keywords.json"}}
    
    with caplog.at_level(logging.INFO):
        AppConfig.load_keywords()
    
    assert AppConfig.keywords == ["keyword1", "keyword2"]

    # Check log messages
    assert any("Loading keywords from keywords.json" in message for message in caplog.messages)

def test_load_user_config(mock_open_user_config, caplog):
    with mock.patch("utilities.configs.AppConfig.validate_configurations") as mock_validate:
        AppConfig.load_user_config("dummy_path")
        assert AppConfig.user_config is not None
        mock_validate.assert_called_once()

def test_validate_configurations(caplog):
    config = {
        'postgres': {}, 'elasticsearch': {}, 'sqlite': {}, 'keywords': {}, 'logging': {}
    }
    
    with caplog.at_level(logging.INFO):
        AppConfig.validate_configurations(config)

    # Check log messages
    expected_messages = [
        "Postgres configuration loaded successfully.",
        "Elasticsearch configuration loaded successfully.",
        "Sqlite configuration loaded successfully.",
        "Keywords configuration loaded successfully.",
        "Logging configuration loaded successfully."
    ]

    for message in expected_messages:
        assert any(message in log for log in caplog.messages)

def test_validate_configurations_missing_key(caplog):
    config = {
        'postgres': {}, 'elasticsearch': {}, 'sqlite': {}, 'keywords': {}
    }
    
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError, match="Logging configuration is missing in the configuration data."):
            AppConfig.validate_configurations(config)

    # Check log messages
    assert any("Logging configuration is missing in the configuration data." in message for message in caplog.messages)
