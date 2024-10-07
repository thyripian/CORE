import pytest
from unittest import mock
from utilities.dialogues.progress_window import ProgressWindow

@pytest.fixture
def progress_window():
    with mock.patch("utilities.dialogues.progress_window.tk.Tk") as MockTk:
        with mock.patch("utilities.dialogues.progress_window.ttk.Progressbar") as MockProgressbar:
            with mock.patch("utilities.dialogues.progress_window.tk.Label") as MockLabel:
                root = MockTk.return_value
                progressbar = MockProgressbar.return_value
                label = MockLabel.return_value
                yield ProgressWindow(total_items=100), root, progressbar, label

def test_initialization(progress_window):
    progress_window_instance, root, progressbar, label = progress_window
    root.title.assert_called_with("Processing Files")
    root.attributes.assert_called_with('-topmost', True)
    assert progress_window_instance.total_items == 100
    assert progress_window_instance.progress == 0
    assert progress_window_instance.label_format == "{}/{}"
    label.pack.assert_called_once()
    progressbar.pack.assert_called_once()
    root.update.assert_called_once()

def test_update_progress(progress_window):
    progress_window_instance, root, progressbar, label = progress_window
    progress_window_instance.update_progress(10)
    assert progress_window_instance.progress == 10
    progressbar.__setitem__.assert_called_with('value', 10)
    label.config.assert_called_with(text="10/100")
    root.update.assert_called()

def test_close(progress_window):
    progress_window_instance, root, progressbar, label = progress_window
    progress_window_instance.close()
    root.destroy.assert_called_once()
