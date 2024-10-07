import logging
import os
from datetime import datetime

class DevLogger:
    _instance = None


    def __new__(cls, log_dir="../../logs", log_file="dev_trace.log"):
        current_time = datetime.now()

        if cls._instance is None :
            cls._instance = super(DevLogger, cls).__new__(cls)
            cls._last_initialized = current_time  # Update the time of initialization

            # Initialize the logger
            cls._instance.logger = logging.getLogger("dev_trace")
            cls._instance.logger.setLevel(logging.DEBUG)

            if not cls._instance.logger.hasHandlers():  # Ensure no duplicate handlers
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)

                log_path = os.path.join(log_dir, log_file)
                file_handler = logging.FileHandler(log_path)
                file_handler.setLevel(logging.DEBUG)

                formatter = logging.Formatter('%(message)s')
                file_handler.setFormatter(formatter)

                cls._instance.logger.addHandler(file_handler)

        return cls._instance

    def get_logger(self):
        return self.logger
