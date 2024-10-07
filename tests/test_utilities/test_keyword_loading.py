import pytest
import os
import json
from unittest import mock
from utilities.keyword_loading import Keywords

# Fixture to mock the file system
@pytest.fixture
def mock_filesystem(tmp_path):
    # Create temporary keyword JSON files
    keyword_dir = tmp_path / "keywords"
    keyword_dir.mkdir()
    
    file_1 = keyword_dir / "keywords_1.json"
    file_2 = keyword_dir / "keywords_2.json"
    file_3 = keyword_dir / "other_file.json"
    
    file_1.write_text(json.dumps(["keyword1", "keyword2"]))
    file_2.write_text(json.dumps(["keyword3", "keyword4"]))
    file_3.write_text(json.dumps(["irrelevant"]))

    # Mock DatabaseConfig to return the temporary directory path
    with mock.patch('utilities.DatabaseConfig.set_keyword_dir', return_value=str(keyword_dir)):
        yield keyword_dir, file_1, file_2

def test_load_latest_keywords(mock_filesystem):
    keyword_dir, file_1, file_2 = mock_filesystem

    # Mock os.listdir to return the files in the keyword directory
    with mock.patch('os.listdir', return_value=[file_1.name, file_2.name]):
        # Mock os.path.getmtime to return the modification times of the files
        with mock.patch('os.path.getmtime') as mock_getmtime:
            mock_getmtime.side_effect = lambda x: {
                str(file_1): 100,
                str(file_2): 200
            }[str(x)]
            
            # Load the latest keywords
            result = Keywords.load_latest_keywords()
            
            # Assert that the latest keywords are loaded correctly
            assert result == ["keyword3", "keyword4"]
            assert Keywords.keywords_list == ["keyword3", "keyword4"]

