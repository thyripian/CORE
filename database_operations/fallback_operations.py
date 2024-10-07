import logging
import pandas as pd
from collections import OrderedDict
from utilities.configurations.database_config import DatabaseConfig
from utilities.logging.logging_utilities import error_handler
from .base_database import BaseDatabase

logger = logging.getLogger(__name__)

class CSVFailsafe(BaseDatabase):

    @error_handler
    def check_exists(self, hash_value):
            df = DatabaseConfig.all_info_df
            if df is not None or len(df) > 0:
                if "SHA256_hash" in df.columns:
                    return hash_value in df['SHA256_hash'].values
            else:
                pass
                    

    @error_handler
    def save_data(self, info):
        # Prepare and append information to a CSV file as the final fallback
        logger.info("\n\t\t>>> Trying to store to DataFrame for CSV fallback <<<\n")
        logger.info(f"Current length of all_info_df: {len(DatabaseConfig.all_info_df)}")
        if 'images' in info.keys():
             del info['images']
        ordered_info = OrderedDict(SHA256_hash=info['file_hash'])
        ordered_info.update(info)

        # Convert the dictionary to a DataFrame with a single row
        info_df = pd.DataFrame([ordered_info])

        # Get the existing DataFrame from the DatabaseConfig class
        all_info_df = DatabaseConfig.get_fallback_dataframe()

        # Use concat to add the new row to the existing DataFrame
        if all_info_df is not None:
            all_info_df = pd.concat([all_info_df, info_df], ignore_index=True)
        else:
            all_info_df = info_df

        # Update the class variable in DatabaseConfig with the new concatenated DataFrame
        DatabaseConfig.all_info_df = all_info_df
        logger.info(f"New length of all_info_df: {len(DatabaseConfig.all_info_df)}")

        logger.info("\t\tStored to DataFrame for CSV fallback.")

    @error_handler
    def delete_data():
         pass