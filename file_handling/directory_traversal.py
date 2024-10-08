import logging
import os

logger = logging.getLogger(__name__)


def traverse_directory(directory_path):
    """
    Traverse a directory and its subdirectories to find files of specific extensions.

    Parameters:
    directory_path (str): The path to the directory to traverse.

    Returns:
    dict: A dictionary with file extensions as keys and lists of file paths as values.
    """
    file_dict = {"docx": [], "xlsx": [], "pptx": [], "pdf": []}

    logger.info(f"Starting directory traversal for: {directory_path}")

    if not os.path.exists(directory_path):
        logger.error(f"Directory does not exist: {directory_path}")
        return file_dict

    for root, dirs, files in os.walk(directory_path):
        logger.info(f"Inspecting directory: {root}")
        for file in files:
            full_path = os.path.join(root, file)
            ext = file.split(".")[-1].lower()  # Make sure to handle case sensitivity
            logger.info(f"Found file: {file} with extension: {ext}")
            if ext in file_dict:
                file_dict[ext].append(full_path)

    for k, v in file_dict.items():
        logger.info(f"Total {k.upper()} found: {len(v)}")

    return file_dict
