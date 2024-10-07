import os, sys
import logging
import json

print("ENTRY POINT CWD: ",os.getcwd())
# Set root directory to the root of the project (merlin directory)
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_dir) 

from initialization.init_app import AppInitialization

# Construct the absolute paths to the config files
sys_config_path = os.path.join(root_dir, 'config', 'sys_config.json')
settings_path = os.path.join(root_dir, 'config', 'settings.json')

print(f"SYS CONFIG: {sys_config_path}")
print(f"SETTINGS: {settings_path}")

def initialize_backend():
    """
    Initialize the application components like logging, configurations, and database connections.
    This is intended to be called when the React app starts to ensure the core backend components are initialized.
    """

    # Load settings and configurations
    try:
        with open(settings_path, 'r') as f:
            settings = json.load(f)

        # Initialize the application (sets up logging, database connections, etc.)
        AppInitialization.initialize_application(settings)

        # Log the successful initialization
        logger = logging.getLogger(__name__)
        logger.info("Application successfully initialized.")

    except Exception as e:
        print(f"Error during application initialization: {e}")
        logger = logging.getLogger(__name__)
        logger.error(f"Error during application initialization: {e}")

