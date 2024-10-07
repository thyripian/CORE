# import os
# import requests
# import socket
# import subprocess
# import logging
# import signal
# from utilities.dialogues.selection_dialogues import confirm_selection
# from database_operations.db_manager import DatabaseManager

# logger = logging.getLogger(__name__)

# class InitElastic:
#     es_process = None

#     @classmethod
#     def is_elasticsearch_running(cls, host='localhost', port=9200):
#         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#             return s.connect_ex((host, port)) == 0

#     @classmethod
#     def start_elasticsearch(cls):
#         """Start Elasticsearch by specifying the working directory in subprocess and allow the script to continue running."""
#         script_dir = os.path.dirname(os.path.abspath(__file__))
#         batch_file_dir = os.path.abspath(os.path.join(script_dir, "..", "config"))
#         helper_batch_file = os.path.join(batch_file_dir, "run_elasticsearch.bat")

#         # Log file setup
#         log_file_dir = os.path.abspath(os.path.join(script_dir, "..", "logs"))
#         log_file_path = os.path.join(log_file_dir, "elasticsearch_output.log")

#         with open(log_file_path, 'w') as f:
#             # Start the batch file using cmd /c to avoid termination prompts
#             command = f"cmd /c {helper_batch_file}"
#             cls.es_process = subprocess.Popen(
#                 command,
#                 stdout=f,
#                 stderr=subprocess.STDOUT,
#                 cwd=batch_file_dir
#             )

#         logger.info("Elasticsearch process started, PID: {}".format(cls.es_process.pid))

#     @classmethod
#     def elastic_init_interaction(cls):
#         if not cls.is_elasticsearch_running():
#             logger.info("Elasticsearch is not running.")
#             if confirm_selection("Start Elasticsearch", "Elasticsearch is not currently running. Would you like to start it now?"):
#                 cls.start_elasticsearch()
#             else:
#                 logger.info("User elected to not start Elasticsearch service. The application may not function as intended.")
#         else:
#             logger.info("Elasticsearch is already running.")

#     @classmethod
#     def stop_elasticsearch(cls):
#         """Stops the Elasticsearch process using the stored process handle."""
#         if cls.es_process:
#             try:
#                 cls.es_process.terminate()  # Sends SIGTERM equivalent on Windows
#                 cls.es_process.wait(10)  # Wait up to 10 seconds for the process to exit
#                 logger.info("Elasticsearch has been stopped successfully.")
#             except Exception as e:
#                 logger.error(f"Failed to stop Elasticsearch: {e}")
#                 try:
#                     cls.es_process.kill()  # Forces termination if SIGTERM doesn't work
#                     logger.info("Elasticsearch force-stopped successfully.")
#                 except Exception as ex:
#                     logger.error(f"Failed to force-stop Elasticsearch: {ex}")
#         else:
#             logger.info("No Elasticsearch process was found to stop.")

#     @classmethod
#     def stop_elasticsearch_api(cls):
#         try:
#             es_client = DatabaseManager.get_elasticsearch_client()  # Assuming DatabaseManager is the class name
#             # Adjust the endpoint as necessary. This is just a placeholder since newer versions of ES might not support direct shutdown via API like this.
#             response = es_client.transport.perform_request('POST', '/_cluster/nodes/_local/_shutdown')
#             if response.get('acknowledged', False):
#                 logger.info("Elasticsearch has been shut down successfully via API.")
#             else:
#                 logger.error("Failed to shut down Elasticsearch: Elasticsearch did not acknowledge the shutdown.")
#         except Exception as e:
#             logger.error(f"Failed to shut down Elasticsearch via API: {e}")

import os
import socket
import subprocess
import time
import logging
from utilities.dialogues.selection_dialogues import confirm_selection
from utilities.dialogues.progress_window import ProgressWindow
from database_operations.db_manager import DatabaseManager  # Assuming this is where get_elasticsearch_client is defined

logger = logging.getLogger(__name__)

class InitElastic:
    es_process = None

    @classmethod
    def is_elasticsearch_running(cls, host='localhost', port=9200):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex((host, port)) == 0

    @classmethod
    def start_elasticsearch(cls):
        """Start Elasticsearch by specifying the working directory in subprocess and allow the script to continue running."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        batch_file_dir = os.path.abspath(os.path.join(script_dir, "..", "config"))
        helper_batch_file = os.path.join(batch_file_dir, "run_elasticsearch.bat")

        # Log file setup
        log_file_dir = os.path.abspath(os.path.join(script_dir, "..", "logs"))
        log_file_path = os.path.join(log_file_dir, "elasticsearch_output.log")

        with open(log_file_path, 'w') as f:
            # Start the batch file using cmd /c start /B to run in the background
            command = f"cmd /c start /B {helper_batch_file}"
            cls.es_process = subprocess.Popen(
                command,
                stdout=f,
                stderr=subprocess.STDOUT,
                cwd=batch_file_dir,
                shell=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP  # Ensure the process is detached
            )

        # Save the PID to a file for later use
        pid_file = os.path.join(log_file_dir, "elasticsearch_pid.txt")
        with open(pid_file, 'w') as pidf:
            pidf.write(str(cls.es_process.pid))

        print(f"Elasticsearch process started, PID: {cls.es_process.pid}")

        # Initialize the progress window for loading Elasticsearch
        total_lines = 126  # Total lines expected in the log file when Elasticsearch is fully loaded
        progress_window = ProgressWindow(total_lines, title="Loading Elasticsearch", label_format="{:.0f}%", log_message="Expected log lines: {}")

        # Tail the log file and update progress bar
        cls.tail_log_file(log_file_path, total_lines, progress_window)

        # Check if Elasticsearch started successfully
        if cls.is_elasticsearch_running():
            print("Elasticsearch is running.")
        else:
            print("Elasticsearch did not start within the expected time.")
        progress_window.close()

    @classmethod
    def tail_log_file(cls, log_file_path, total_lines, progress_window):
        """Tail the log file and update the progress window."""
        with open(log_file_path, 'r') as log_file:
            log_file.seek(0, os.SEEK_END)  # Move to the end of the file
            while not cls.is_elasticsearch_running():
                line = log_file.readline()
                if line:
                    current_progress = (sum(1 for _ in open(log_file_path)) / total_lines) * 100
                    progress_window.update_progress(current_progress - progress_window.progress)
                else:
                    time.sleep(0.1)  # Sleep briefly to avoid busy waiting

    @classmethod
    def elastic_init_interaction(cls):
        if not cls.is_elasticsearch_running():
            print("Elasticsearch is not running.")
            if confirm_selection("Start Elasticsearch", "Elasticsearch is not currently running. Would you like to start it now?"):
                cls.start_elasticsearch()
            else:
                print("User elected to not start Elasticsearch service. The application may not function as intended.")
        else:
            print("Elasticsearch is already running.")