import logging
import os
import sys
import threading

import requests
from flask import Flask, jsonify
from flask_cors import CORS

# Ensure the base directory is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utilities.logging.logging_utilities import init_logging  # isort: skip
from utilities.logging.logging_utilities import setup_logging

logfile_response = requests.get("http://localhost:5005/get_logfile")
logfile_response.raise_for_status()
logfile = logfile_response.json().get("logfile_name")
setup_logging(log_filename=logfile, log_directory="../../logs")
logger = logging.getLogger(__name__)

from update_functionality import run_update_process  # isort: skip

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for all routes

initialized = False


@app.route("/status", methods=["GET"])
def status():
    # Perform any necessary checks to determine if the service is ready
    global initialized
    initialized = True  # Replace with actual readiness checks
    if initialized:
        return jsonify({"status": "ready"}), 200
    else:
        return jsonify({"status": "initializing"}), 503


@app.route("/api/progress", methods=["GET"])
def get_progress():
    return jsonify(run_update_process.progress_state)


@app.route("/api/check-for-updates", methods=["POST"])
def check_for_updates():
    logger.info("RECEIVED REQUEST TO START UPDATE PROCESS")

    def run_check_updates():
        try:
            run_update_process.run_process()
        except Exception as e:
            logger.error(f"Exception in update process: {e}", exc_info=True)
            run_update_process.progress_state["message"] = f"Failed: {str(e)}"

    threading.Thread(target=run_check_updates).start()
    return jsonify({"message": "Processing started"})


@app.errorhandler(Exception)
def handle_exception(e):
    response = {"error": str(e)}
    return jsonify(response), 500


if __name__ == "__main__":
    app.run(
        port=5001, debug=False, threaded=True
    )  # Ensure this port matches what you're using in the frontend
