import logging
import os
import tkinter as tk
from tkinter import filedialog, messagebox

logger = logging.getLogger(__name__)


def show_info_dialog(title, message):
    """
    Display an informational dialog to the user.

    :param title: The title of the dialog window.
    :param message: The informational message to display.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main Tk window
    root.attributes("-topmost", True)  # Make the window topmost
    messagebox.showinfo(title, message)
    root.destroy()  # Destroy the Tk window after showing the message


# def select_folder(prompt="Select Folder to Process"):
#     """
#     Opens a dialog for the user to select a folder.

#     :param prompt: The title of the dialog window.
#     :return: The path to the selected folder.
#     """
#     show_info_dialog("Folder Selection", "Please use the next window to select the folder you want to process.")
#     root = tk.Tk()
#     root.withdraw()  # Hide the main Tk window
#     root.attributes('-topmost', True)  # Make the window topmost
#     folder_selected = filedialog.askdirectory(title=prompt)
#     root.destroy()  # Destroy the Tk window after selection
#     logger.info(f'Selected folder: {folder_selected}')
#     return folder_selected


def select_folder(prompt="Select Folder to Process"):
    """
    Opens a dialog for the user to select a folder.

    :param prompt: The title of the dialog window.
    :return: The path to the selected folder.
    """
    show_info_dialog(
        "Folder Selection",
        "Please use the next window to select the folder you want to process.",
    )

    root = tk.Tk()
    root.withdraw()  # Hide the main Tk window
    root.attributes("-topmost", True)  # Make the window topmost

    folder_selected = filedialog.askdirectory(title=prompt)
    logger.info(f"DIRECTORY: {folder_selected}")
    root.destroy()  # Destroy the Tk window after selection

    if not folder_selected:
        logger.warning("No folder was selected.")
        return None

    # Normalize the path to ensure it's in the correct format
    folder_selected = os.path.normpath(folder_selected)
    folder_selected = folder_selected.replace("\\", "\\\\")

    # Log the path with delimiters to check for hidden characters
    logger.info(f"Selected folder: >{folder_selected}<")

    # Verify the folder exists
    if not os.path.exists(folder_selected):
        logger.error(f"Directory does not exist: {folder_selected}")
        return None

    return folder_selected


def select_file(prompt="Select Config File"):
    """
    Opens a dialog for the user to select a file.

    :param prompt: The title of the dialog window.
    :return: The path to the selected file.
    """
    show_info_dialog(
        "File Selection",
        "Please use the next window to select the configuration file you want to use.",
    )
    root = tk.Tk()
    root.withdraw()  # Hide the main Tk window
    root.attributes("-topmost", True)  # Make the window topmost
    file_selected = filedialog.askopenfilename(title=prompt)
    root.destroy()  # Destroy the Tk window after selection
    logger.info(f"Selected file: {file_selected}")
    return file_selected


def confirm_selection(title, message):
    """
    Display a dialog asking the user to confirm a selection.

    :param title: The title of the confirmation dialog.
    :param message: The confirmation message to display.
    :return: True if the user confirms, False otherwise.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main Tk window
    root.attributes("-topmost", True)  # Make the window topmost
    result = messagebox.askyesno(title, message)  # Show a yes/no messagebox
    root.destroy()  # Destroy the Tk window after showing the dialog
    logger.info(f"Confirmation result: {result}")
    return result
