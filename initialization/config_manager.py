import logging
from utilities.configurations.configs import AppConfig

logger = logging.getLogger(__name__)

class ConfigManager:
    @staticmethod
    def get_config(section):
        """
        Get configuration data for a specified section from AppConfig.
        
        Args:
            section (str): Section name in the configuration data.
        
        Returns:
            dict: Configuration data for the specified section, or an empty dictionary if not found.
        """
        return AppConfig.system_config.get(section, {})

    @staticmethod
    def get_user_config(section):
        """
        Get user-specific configuration data for a specified section from AppConfig.
        
        Args:
            section (str): Section name in the user configuration data.
        
        Returns:
            dict: User configuration data for the specified section, or an empty dictionary if not found.
        """
        return AppConfig.user_config.get(section, {})
