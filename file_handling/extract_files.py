from .directory_traversal import traverse_directory


def extract_files_from_directory(root_dir):
    file_dict = traverse_directory(root_dir)
    return file_dict
