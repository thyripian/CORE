import pytest
import logging
import base64
import json
from unittest import mock
from utilities.data_preparation import prepare_data

# Sample inputs
file_path = 'sample/path/file.txt'
info = {
    'highest_classification': 'Confidential',
    'caveats': ['For official use only'],
    'timeframes': ['2024-06-04', '2024-06-05'],
    'locations': ['Location1', 'Location2', 'Location1'],
    'subjects': [{'text': 'Subject1', 'label': 'Label1'}, {'text': 'Subject2', 'label': 'Label2'}],
    'topics': ['Topic1', 'Topic2', 'Topic1'],
    'keywords': ['Keyword1', 'Keyword2'],
    'MGRS': ['MGRS1', 'MGRS2'],
    'full_text': 'This is the full text of the document.'
}
images = b'test_image_data'
file_hash = 'abc123'

# Ensure the logger is correctly configured to capture log messages
@pytest.fixture(autouse=True)
def setup_logging():
    logging.basicConfig(level=logging.DEBUG)

def test_prepare_data(caplog):
    with caplog.at_level(logging.INFO):
        with mock.patch('data_processing.text_processing.clean_timeframes', return_value='2024-06-04,2024-06-05'), \
             mock.patch('data_processing.text_processing.remove_duplicate_locations', return_value='Location1,Location2'), \
             mock.patch('data_processing.text_processing.filter_text', side_effect=lambda x: f"Filtered_{x}"), \
             mock.patch('utilities.data_preparation.filter_individual_topics') as mock_filter_topics:

            mock_filter_topics.return_value = ["Filtered_Topic1", "Filtered_Topic2"]

            result = prepare_data(file_path, info, images, file_hash)

            # Ensure the mock was called
            mock_filter_topics.assert_called_once_with(['Topic1', 'Topic2', 'Topic1'])

            # Debug print for locations and topics
            print(f"result['locations']: {result['locations']}")
            print(f"result['timeframes']: {result['timeframes']}")
            print(f"result['topics']: {result['topics']}")

            # Verify the returned data dictionary
            assert result['file_hash'] == file_hash
            assert result['highest_classification'] == 'Confidential'
            assert result['caveats'] == 'For official use only'
            assert result['file_path'] == file_path
            assert set(result['locations'].split(',')) == {'Location1', 'Location2'}
            assert result['timeframes'] == '2024-06-04,2024-06-05'
            assert result['subjects'] == 'Subject1:Label1|Subject2:Label2'
            assert result['topics'] == 'Filtered_Topic1|Filtered_Topic2'
            assert result['keywords'] == 'Keyword1,Keyword2'
            assert result['MGRS'] == json.dumps(['MGRS1', 'MGRS2'])
            assert result['images'] == base64.b64encode(images).decode('utf-8')
            assert result['full_text'] == 'This is the full text of the document.'

            # Verify log messages
            assert any("Preparing extracted data for storage." in message for message in caplog.messages)
            assert any("Precleaned timeframes: ['2024-06-04', '2024-06-05']" in message for message in caplog.messages)
            assert any("Cleaned timeframes: 2024-06-04,2024-06-05" in message for message in caplog.messages)
            assert any("SUBJECTS STR TYPE: <class 'str'>" in message for message in caplog.messages)
            assert any("SUBJECTS STR CONTENT: Subject1:Label1|Subject2:Label2" in message for message in caplog.messages)