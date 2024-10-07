from abc import ABC, abstractmethod

class BaseDatabase(ABC):
    @abstractmethod
    def check_exists(self, hash_value):
        """
        Check if a record exists in the database.
        """
        pass
    
    @abstractmethod
    def save_data(self, info):
        """
        Save data to the database.
        """
        pass

    @abstractmethod
    def delete_data(self, hash_value):
        """
        Delete data from the database.
        """
        pass