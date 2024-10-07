import logging
import re

from data_processing.text_processing import unique_subjects, normalize_mgrs, extract_classification_and_caveats, extract_keywords, extract_topics
from initialization.init_app import AppInitialization

logger = logging.getLogger(__name__)

# Main function to extract various types of information from text using NLP and regex.
def extract_info(text):
    """
    Extract various types of information from text, such as classifications, topics, locations, and more.

    Parameters:
    text (str): The text from which to extract information.

    Returns:
    dict: A dictionary with keys for each information type and their corresponding extracted data.
    """
    
    # Process the text using the NLP model
    nlp = AppInitialization.nlp

    doc = nlp(text)

    # Initialize dictionary to hold extracted information
    info = {
        'highest_classification': None,
        'caveats': None,
        'locations': [],
        'timeframes': [],
        'subjects': [],
        'topics': [],
        'keywords': [],
        'MGRS': [],
        'full_text': text
    }
    
    # Define custom regex patterns for extracting specific types of timeframes
    time_patterns = [
        r'\b\d{1,4}([-/.])\d{1,2}\1\d{1,4}\b',  # Dates with various separators
        r'\b\d{1,2}:\d{1,2}(?::\d{1,2})?\s?(?:AM|PM)?\b',  # Times with optional seconds and AM/PM
        r'\b(next|last)?\s?\d+\s?(days?|months?|years?|hours?|minutes?|hrs?|mins?)\b',  # Relative times
        r'\b(jan\.?|feb\.?|mar\.?|apr\.?|may|jun\.?|jul\.?|aug\.?|sep\.?|oct\.?|nov\.?|dec\.?)\s?\d{1,4}\b',  # Month abbreviations
        r'\b(mon|tue|wed|thu|fri|sat|sun)day\b',  # Days of the week
        r'\b\d{1,2}(st|nd|rd|th)\s(of\s)?(january|february|march|april|may|june|july|august|september|october|november|december),?\s\d{1,4}\b',  # Complex date expressions
        r'\b\d{1,2}/\d{1,2}\b',  # Numeric month/day
        r'\b\d{1,2}-\d{1,2}-\d{2,4}\b'  # Numeric date with dashes
        # Add more patterns as necessary
    ]
    
    # Initialize an empty set to keep track of unique MGRS coordinates found in the text
    unique_mgrs = set()
    
    # Use regex to find all potential MGRS coordinates in the text
    mgrs_coords = re.findall(r'\b\d{1,2}[a-zA-Z]{1,3}\s?\w{1,5}\s?\d{1,5}\s?\d{1,5}\b', text)
    for coord in mgrs_coords:
        # Normalize MGRS coordinates by removing spaces
        normalized_coord = normalize_mgrs(coord)
        if normalized_coord not in unique_mgrs:
            unique_mgrs.add(normalized_coord)
            if len(normalized_coord) >= 15:
                info['MGRS'].append(normalized_coord)  # If the normalized coordinate meets length requirements, store it
            else:
                info['MGRS'].append(coord)  # Otherwise, store the original coordinate format
    
    # Iterate through the entities recognized by spaCy's NLP model
    for ent in doc.ents:
        # Check the type of entity and add to the corresponding list in the 'info' dictionary
        if ent.label_ == 'GPE':
            info['locations'].append(ent.text)
        elif ent.label_ in ['DATE', 'TIME']:
            info['timeframes'].append(ent.text)
        elif ent.label_ in ['ORG', 'PERSON', 'NORP', 'FAC', 'LOC', 'PRODUCT', 'EVENT', 'WORK_OF_ART', 'LAW', 'LANGUAGE']:
            # Create a dictionary for each subject with the text and label
            subject_dict = {'text': ent.text, 'label': ent.label_}
            info['subjects'].append(subject_dict)
    
    # Remove duplicate subjects from the list
    info['subjects'] = unique_subjects(info['subjects'])
 
    # Combine individual time patterns into one large regex pattern using non-capturing groups
    time_combined_pattern = '|'.join(f'(?:{pattern})' for pattern in time_patterns)
    
    # Find all matches for the combined time pattern in the text
    time_matches = re.finditer(time_combined_pattern, text, re.IGNORECASE)
    
    # Add each non-empty match to the final timeframes list
    for time_match in time_matches:
        non_empty_group = next(filter(None, time_match.groups('')), '')
        if non_empty_group:
            info['timeframes'].append(non_empty_group.strip())
    
    # Deduplicate timeframes by converting the list to a set and back to a list
    info['timeframes'] = list(set(info['timeframes']))
    logger.info(f"Extracted timeframes: {info['timeframes']}")
    
    # Extract the highest classification and any caveats from the text
    highest_classification, caveats = extract_classification_and_caveats(text)
    
    # Update the 'info' dictionary with the extracted classification and caveats
    info['highest_classification'] = highest_classification
    info['caveats'] = caveats
    logger.info(f"Extracted Classification: {info['highest_classification']}")
    logger.info(f"Extracted Caveats: {info['caveats']}")
    
    # Extract keywords from the text based on a predefined list
    info['keywords'] = extract_keywords(text)
    logger.info(f"Extracted Keywords: {info['keywords']}")
    
    # Suppress specific warnings during topic extraction
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        # Extract topics from the text
        topics = extract_topics([text])
        info['topics'] = topics

    # Return the filled 'info' dictionary
    return info