import logging
import json
import base64
from datetime import datetime, timezone

from data_processing.text_processing import clean_timeframes, remove_duplicate_locations, filter_individual_topics

logger = logging.getLogger(__name__)

# Prepare data for storage
def prepare_data(file_path, info, images, file_hash):
    logger.info("\t\tPreparing extracted data for storage.")

    classification = info.get('highest_classification', '')
    caveats = ''.join(info.get('caveats', []))
    
    logger.info(f"Precleaned timeframes: {info['timeframes']}")
    timeframes = clean_timeframes(info['timeframes'])
    logger.info(f"Cleaned timeframes: {timeframes}")
    
    locations = remove_duplicate_locations(info['locations'])
    # subjects_str = '|'.join([f"{subject['text']}:{subject['label']}" for subject in info['subjects']])
    subjects_str = '|'.join(f"{subject['text']}:{subject['label']}" for subject in info['subjects'])
    logger.info(f"SUBJECTS STR TYPE: {type(subjects_str)}")
    logger.info(f"SUBJECTS STR CONTENT: {subjects_str}")

    # subjects_str = '|'.join(info['subjects'])
    filtered_topics = filter_individual_topics(info['topics'])
    topics_str = '|'.join(filtered_topics)
    keywords_str = ','.join(info['keywords'])

    mgrs_str = json.dumps(info['MGRS']) if 'MGRS' in info else '[]'
    
    # Encode images as base64 to ensure they are JSON-serializable
    if images:
        images_data = base64.b64encode(images).decode('utf-8')
    else:
        images_data = None

    # Initialize dictionary to hold extracted information
    data = {
        'file_hash': file_hash,
        'highest_classification': classification,
        'caveats': caveats,
        'file_path': file_path,
        'locations': locations,
        'timeframes': timeframes,
        'subjects': subjects_str,
        'topics': topics_str,
        'keywords': keywords_str,
        'MGRS': mgrs_str,
        'images': images_data,  # Now base64-encoded string
        'full_text': info['full_text'],
        'processed_time': datetime.now(timezone.utc)
    }
    return data