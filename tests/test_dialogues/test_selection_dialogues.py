import pytest
from unittest import mock
from utilities.dialogues.selection_dialogues import (
    show_info_dialog,
    select_folder,
    select_file,
    confirm_selection
)

@pytest.fixture
def mock_tk():
    with mock.patch("utilities.dialogues.selection_dialogues.tk.Tk") as MockTk:
        yield MockTk.return_value

def test_show_info_dialog(mock_tk):
    with mock.patch("utilities.dialogues.selection_dialogues.messagebox.showinfo") as mock_showinfo:
        show_info_dialog("Test Title", "Test Message")
        mock_tk.withdraw.assert_called_once()
        mock_tk.attributes.assert_called_with('-topmost', True)
        mock_showinfo.assert_called_with("Test Title", "Test Message")
        mock_tk.destroy.assert_called_once()

def test_select_folder(mock_tk):
    with mock.patch("utilities.dialogues.selection_dialogues.filedialog.askdirectory") as mock_askdirectory:
        with mock.patch("utilities.dialogues.selection_dialogues.show_info_dialog") as mock_show_info_dialog:
            mock_askdirectory.return_value = "/path/to/folder"
            folder = select_folder()
            mock_show_info_dialog.assert_called_with("Folder Selection", "Please use the next window to select the folder you want to process.")
            mock_tk.withdraw.assert_called()
            mock_tk.attributes.assert_called_with('-topmost', True)
            mock_askdirectory.assert_called_with(title="Select Folder to Process")
            mock_tk.destroy.assert_called()
            assert folder == "/path/to/folder"

def test_select_file(mock_tk):
    with mock.patch("utilities.dialogues.selection_dialogues.filedialog.askopenfilename") as mock_askopenfilename:
        with mock.patch("utilities.dialogues.selection_dialogues.show_info_dialog") as mock_show_info_dialog:
            mock_askopenfilename.return_value = "/path/to/file"
            file = select_file()
            mock_show_info_dialog.assert_called_with("File Selection", "Please use the next window to select the configuration file you want to use.")
            mock_tk.withdraw.assert_called()
            mock_tk.attributes.assert_called_with('-topmost', True)
            mock_askopenfilename.assert_called_with(title="Select Config File")
            mock_tk.destroy.assert_called()
            assert file == "/path/to/file"

def test_confirm_selection(mock_tk):
    with mock.patch("utilities.dialogues.selection_dialogues.messagebox.askyesno") as mock_askyesno:
        mock_askyesno.return_value = True
        result = confirm_selection("Confirm", "Are you sure?")
        mock_tk.withdraw.assert_called()
        mock_tk.attributes.assert_called_with('-topmost', True)
        mock_askyesno.assert_called_with("Confirm", "Are you sure?")
        mock_tk.destroy.assert_called()
        assert result is True
