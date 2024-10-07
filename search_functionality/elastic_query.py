import sys
import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from elasticsearch import Elasticsearch, ConnectionError, NotFoundError
import logging



root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
from utilities.logging.logging_utilities import setup_logging, init_logging
# settings_response = requests.get('http://localhost:5005/get_settings')
# settings_response.raise_for_status()
# settings = settings_response.json()
logfile_response = requests.get('http://localhost:5005/get_logfile')
logfile_response.raise_for_status()
logfile = logfile_response.json().get("logfile_name")
# log_dir = settings.get("user_config", None).get("logging", None).get("log_directory", None)
setup_logging(log_filename=logfile, log_directory="../../logs")
logger = logging.getLogger(__name__)
# init_logging(logger)

try:
    from database_operations.db_manager import DatabaseManager
    from initialization.init_app import AppInitialization
    from utilities.configurations.configs import AppConfig
    db_flag = True
    config_flag = True
    logger.info("Successfully imported DatabaseManager, AppInitialization, and AppConfig")
except ImportError as e:
    db_flag = False
    config_flag = False
    logger.error(f"Error importing DatabaseManager, AppInitialization, or AppConfig: {e}")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for all routes

clin = None
initialized = False
# Fetch configuration from run_app.py
try:
    response = requests.get('http://localhost:5005/get_config')  # Adjust port if needed
    response.raise_for_status()
    elastic_conn_info = response.json()
    logger.info(f"Fetched config: {elastic_conn_info}")
except Exception as e:
    logger.info(f"Failed to connect to run_app API: {str(e)}")
    elastic_conn_info = {}

if elastic_conn_info:
    from elasticsearch import Elasticsearch
    hosts = elastic_conn_info.get('hosts')
    logger.info(f"Before type check: TYPE HOSTS: {type(hosts)}")
    logger.info(f"HOSTS TEXT: {hosts}")
    # Check if hosts is indeed a list
    if not isinstance(hosts, list):
        raise ValueError(f"Hosts is not a list: {hosts}")
    clin = Elasticsearch(
        hosts,
        basic_auth=(
            elastic_conn_info.get('basic_auth', {}).get('user'),
            elastic_conn_info.get('basic_auth', {}).get('password')
        ),
        verify_certs=elastic_conn_info.get('verify_certs'),
        ca_certs=elastic_conn_info.get('ca_certs'),
        max_retries=1,
        retry_on_timeout=True
    )
initialized = True
def query_elasticsearch(query):
    if not clin:
        logger.info("Elasticsearch client is not available")
        return [], 0
    try:
        index = elastic_conn_info.get('index')
        response = clin.search(
            index=index,
            query={
                "match": {
                    "full_text": query
                }
            },
            size=100
        )
        records = []
        total_hits = response['hits']['total']['value']
        if response['hits']['hits']:
            for doc in response['hits']['hits']:
                mgrs = doc['_source'].get('MGRS', "[]")
                if isinstance(mgrs, str):
                    mgrs = json.loads(mgrs)
                record = {
                    'file_path': doc['_source']['file_path'].split('\\')[-1],
                    'processed_time': doc['_source']['processed_time'],
                    'MGRS': mgrs
                }
                records.append(record)
        return records, total_hits
    except ConnectionError as e:
        logger.error(f"ConnectionError querying Elasticsearch: {e}")
        return [], 0
    except NotFoundError as e:
        logger.error(f"Index not found in Elasticsearch: {e}")
        return [], 0
    except Exception as e:
        logger.error(f"Error querying Elasticsearch: {e}")
        return [], 0

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'No query provided'}), 400

    # Perform the search query
    try:
        records, total_hits = query_elasticsearch(query)
        if not records:
            return jsonify({'error': 'No documents found'}), 404
        return jsonify({'total_hits': total_hits, 'records': records})
    except Exception as e:
        logger.error(f"Error handling search request: {e}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/search-init-status', methods=['GET'])
def search_init_status():
    global initialized
    if initialized:
        return jsonify({"status": "Initialized successfully"}), 200
    else:
        return jsonify({"status": "Search functionality not initialized."}), 500

if __name__ == '__main__':
    app.run(debug=False, port=5000)
