import multiprocessing
import os

import psutil


def calculate_dynamic_batch_size(target_memory_usage=0.2, max_batch_size=50):
    """
    Dynamically calculate batch size based on available system resources.

    Args:
        target_memory_usage (float): The percentage of memory to use for the batch. Default is 20% (0.2).
        max_batch_size (int): The maximum allowed batch size to avoid overwhelming the system.

    Returns:
        int: The calculated batch size.
    """
    # Number of CPU cores available
    num_cores = multiprocessing.cpu_count()

    # Get the available memory in bytes
    memory_info = psutil.virtual_memory()
    available_memory = memory_info.available  # Available memory in bytes
    target_memory = available_memory * target_memory_usage

    # Estimate an average memory usage per file (in bytes)
    # This is a rough estimate, adjust based on testing
    avg_memory_per_file = 50 * 1024 * 1024  # Assuming 50MB per file

    # Calculate memory-limited batch size
    memory_based_batch_size = max(1, int(target_memory / avg_memory_per_file))

    # Take the minimum of CPU cores or memory-based batch size
    calculated_batch_size = min(num_cores, memory_based_batch_size, max_batch_size)

    # Ensure the batch size is at least 1
    return max(1, calculated_batch_size)


def get_available_resources():
    """
    Get current system resource information such as CPU and memory.

    Returns:
        dict: Dictionary containing available CPU cores and memory information.
    """
    num_cores = multiprocessing.cpu_count()
    memory_info = psutil.virtual_memory()

    return {
        "num_cores": num_cores,
        "available_memory": memory_info.available,
        "total_memory": memory_info.total,
    }
