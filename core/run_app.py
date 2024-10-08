import logging
import os
import sys

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
flag = None
logger = logging.getLogger(__name__)

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
print(root_dir)
# isort: off
from core import generic
from utilities.configurations.database_config import DatabaseConfig
from initialization.init_app import AppInitialization

# isort: on


def initialize_application_logic():
    """
    This function can be called directly to initialize the application logic
    without running Flask.
    """
    global flag
    try:
        if flag:
            return  # Skip if already initialized
        generic.initialize_backend()  # This will run the core logic for initialization
        flag = True
    except Exception as e:
        flag = False


def initialize():
    global flag
    try:
        if flag:
            logger.info("Application already initialized. Skipping reinitialization.")
            return  # Skip if already initialized
        logger.info("Initializing application...")
        generic.initialize_backend()
        flag = True
        logger.info("Application initialized successfully.")
    except Exception as e:
        flag = False
        logger.error(f"Application initialization failed: {str(e)}")
        # Do NOT use jsonify here, just log the error or handle it as necessary.


@app.route("/initialize", methods=["POST"])
def initialize_route():
    global flag
    if flag:
        return (
            jsonify(
                {"status": "success", "message": "Application is already initialized"}
            ),
            200,
        )  # Skip re-initialization

    try:
        generic.initialize_backend()
        flag = True
        return (
            jsonify(
                {"status": "success", "message": "Application initialized successfully"}
            ),
            200,
        )
    except Exception as e:
        flag = False
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/status", methods=["GET"])
def stat():
    global flag
    if flag is None:
        return jsonify({"status": "initializing"}), 503
    elif flag:
        return jsonify({"status": "ready"}), 200
    else:
        return jsonify({"status": "Initialization failed"}), 500


@app.route("/get_config", methods=["GET"])
def get_config():
    try:
        if AppInitialization.initialized:
            # Log and return the elastic_conn_data
            logger.info(
                f"Returning elastic_conn_data: {DatabaseConfig.elastic_conn_data}"
            )
            return jsonify(DatabaseConfig.elastic_conn_data), 200
        else:
            logger.error("Configuration not initialized")
            return jsonify({"error": "Configuration not initialized"}), 500
    except Exception as e:
        logger.error(f"Error in /get_config: {str(e)}")
        return jsonify({"error": f"Error retrieving configuration: {str(e)}"}), 500


@app.route("/get_settings", methods=["GET"])
def get_settings():
    try:
        if AppInitialization.initialized:
            logger.info(
                f"Returning settings from backend: {AppInitialization.settings}"
            )
            return jsonify(AppInitialization.settings), 200
        else:
            logger.error("Backend not initialized.")
            return jsonify({"error": "Backend not initialized"}), 500
    except Exception as e:
        logger.error(f"Unable to retrieve settings.json from backend: {str(e)}")
        return (
            jsonify({"error": f"Unable to retrieve settings from backend: {str(e)}"}),
            500,
        )


@app.route("/get_logfile", methods=["GET"])
def get_logfile():
    try:
        if AppInitialization.initialized:
            logger.info(
                f"Returning logile name from backend: {AppInitialization.logfile}"
            )
            return jsonify({"logfile_name": AppInitialization.logfile}), 200
        else:
            logger.error("Backend not initialized.")
            return jsonify({"error": "Backend not initialized"}), 500
    except Exception as e:
        logger.error("Unable to retrieve logfile name from backend.")
        return jsonify({"error": f"Unable to retrieve logfile name: {str(e)}"}), 500


@app.route("/get_availabilities", methods=["GET"])
def get_availabilities():
    try:
        if AppInitialization.initialized:
            availabilities = {
                "available": AppInitialization.availability,
                "connects": AppInitialization.connection_status,
            }
            logger.info(f"Returning logile name from backend: {availabilities}")
            return jsonify(availabilities), 200
        else:
            logger.error("Backend not initialized.")
            return jsonify({"error": "Backend not initialized"}), 500
    except Exception as e:
        logger.error("Unable to retrieve availabilities from backend.")
        return jsonify({"error": f"Unable to retrieve availabilities: {str(e)}"}), 500


if __name__ == "__main__":
    # Initialize the application when the server starts
    initialize()  # This will now just log the errors instead of using jsonify
    app.run(debug=False, port=5005)
