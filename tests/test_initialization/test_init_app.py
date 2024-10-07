import os
import logging
import pytest
from unittest import mock
from initialization.init_app import AppInitialization
from utilities.configurations.configs import AppConfig
from utilities import DatabaseConfig, Keywords
from database_operations import DatabaseManager
from initialization.initialize_elasticsearch import InitElastic

@pytest.fixture(autouse=True)
def setup_logging():
    logging.basicConfig(level=logging.DEBUG)

def test_initialize_application():
    with mock.patch.object(InitElastic, 'elastic_init_interaction'), \
         mock.patch.object(AppInitialization, 'load_configurations'), \
         mock.patch.object(AppInitialization, 'set_database_connections'), \
         mock.patch.object(AppInitialization, 'run_connection_tests'), \
         mock.patch.object(AppInitialization, 'load_keywords'), \
         mock.patch.object(AppInitialization, 'select_processing_directory'):
        
        app_init = AppInitialization.initialize_application()
        
        assert app_init == AppInitialization

def test_load_configurations():
    with mock.patch.object(DatabaseConfig, '__init__', return_value=None), \
         mock.patch.object(DatabaseConfig, 'availability', {'postgresql': True, 'elasticsearch': True, 'sqlite': True, 'fallback': True}), \
         mock.patch.object(AppConfig, 'load_sys_config'), \
         mock.patch.object(AppInitialization, 'setup_logging'), \
         mock.patch('initialization.init_app.select_file', return_value='mock_config_file'), \
         mock.patch('initialization.init_app.confirm_selection', return_value=True), \
         mock.patch('builtins.open', mock.mock_open(read_data='{"some_key": "some_value"}')), \
         mock.patch.object(AppConfig, 'load_user_config'), \
         mock.patch.object(AppConfig, 'nlp', 'mock_nlp_model'):
        
        AppInitialization.load_configurations()
        
        assert AppInitialization.availability == {'postgresql': True, 'elasticsearch': True, 'sqlite': True, 'fallback': True}
        assert AppInitialization.nlp == 'mock_nlp_model'

def test_setup_logging():
    with mock.patch('os.makedirs'), \
         mock.patch('os.path.exists', return_value=False), \
         mock.patch('utilities.setup_logging'), \
         mock.patch('utilities.init_logging'):
        
        AppInitialization.setup_logging()
        
        os.makedirs.assert_called_with(os.path.join(os.getcwd(), 'logs'))

def test_run_connection_tests():
    with mock.patch.object(DatabaseManager, '__init__', return_value=None), \
         mock.patch.object(DatabaseManager, 'test_initial_connections'), \
         mock.patch.object(DatabaseManager, 'connection_status', {'status': 'ok'}):
        
        AppInitialization.run_connection_tests()
        
        assert AppInitialization.connection_status == {'status': 'ok'}

def test_set_database_connections():
    with mock.patch.object(AppInitialization, 'setup_postgres_conn', return_value=True), \
         mock.patch.object(AppInitialization, 'setup_elastic_conn', return_value=True), \
         mock.patch.object(AppInitialization, 'setup_sqlite_conn', return_value=True):
        
        AppInitialization.set_database_connections()

def test_setup_postgres_conn():
    with mock.patch.object(DatabaseConfig, 'set_postgres_conn_data'), \
         mock.patch.object(DatabaseManager, 'try_postgresql_connection', return_value=True):
        
        assert AppInitialization.setup_postgres_conn()

def test_setup_elastic_conn():
    with mock.patch.object(DatabaseConfig, 'set_elastic_conn_data'), \
         mock.patch.object(DatabaseManager, 'get_elasticsearch_client', return_value=mock.Mock(ping=lambda: True)), \
         mock.patch.object(DatabaseManager, 'ensure_index_exists', return_value=True):
        
        assert AppInitialization.setup_elastic_conn()

def test_setup_sqlite_conn():
    with mock.patch.object(DatabaseConfig, 'set_sqlite_conn_data'):
        
        assert AppInitialization.setup_sqlite_conn()

def test_load_keywords():
    with mock.patch.object(Keywords, 'load_latest_keywords'):
        
        AppInitialization.load_keywords()

def test_select_processing_directory():
    with mock.patch('initialization.init_app.select_folder', return_value='mock_dir'), \
         mock.patch('initialization.init_app.confirm_selection', return_value=True):
        
        AppInitialization.select_processing_directory()
        
        assert AppInitialization.process_dir == 'mock_dir'
