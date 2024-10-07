import tkinter as tk
from tkinter import ttk
import logging
from utilities.logging.logging_utilities import error_handler

logger = logging.getLogger(__name__)

class ProgressWindow:
    def __init__(self, total_items, title="Processing Files", label_format="{}/{}", log_message="Total items identified: {}"):
        logger.info("Initializing progress window.")
        logger.info(log_message.format(total_items))
        self.root = tk.Tk()
        self.root.title(title)
        self.root.attributes('-topmost', True)  # Make the window topmost

        self.total_items = total_items
        self.progress = 0
        self.label_format = label_format

        # Label to display the progress status
        self.label = tk.Label(self.root, text=self.label_format.format(0, self.total_items))
        self.label.pack()

        # Create the progress bar
        self.progressbar = ttk.Progressbar(self.root, length=400, mode='determinate', maximum=self.total_items)
        self.progressbar.pack()

        self.root.update()

    @error_handler
    def update_progress(self, increment=1):
        """Update the progress bar and label."""
        self.progress += increment
        self.progressbar['value'] = self.progress
        self.label.config(text=self.label_format.format(self.progress, self.total_items))
        self.root.update()

    @error_handler
    def close(self):
        """Close the progress window."""
        self.root.destroy()
