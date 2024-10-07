import json
import logging
import re
from sklearn.decomposition import NMF  # Non-negative Matrix Factorization
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from sklearn.feature_extraction.text import TfidfVectorizer

from utilities import Keywords

logger = logging.getLogger(__name__)

# Function to identify and retain unique subjects from a list by removing duplicates.
def unique_subjects(subject_list):
    """
    Remove duplicates from the list of subjects and normalize the text.

    Parameters:
    subject_list (list of dicts): A list of dictionaries containing 'text' and 'label' keys.

    Returns:
    list: A list of unique subject dictionaries.
    """
    seen = set()  # Initialize an empty set to keep track of seen subjects
    unique_subjects = []  # Initialize a list to store unique subjects
    for subject in subject_list:
        # Clean the text by removing "None" strings, trimming spaces, and converting to lower case

        cleaned_text = subject['text'].replace("None", "").strip().lower()
        
        # Remove special characters, keeping only alphanumeric and spaces
        cleaned_text = re.sub(r'[^a-z0-9 ]', '', cleaned_text)
        
        # Replace multiple spaces with a single space
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        # Create a tuple of the cleaned text and its label for uniqueness checking
        subject_tuple = (cleaned_text, subject['label'])
        
        # Add the subject to the list if it's not already seen
        if subject_tuple not in seen and cleaned_text:
            updated_subject = {'text': cleaned_text, 'label': subject['label']}
            unique_subjects.append(updated_subject)
            seen.add(subject_tuple)
            
    return unique_subjects  # Return the list of unique subjects

# Function to extract topics from text using NMF topic modeling.
def extract_topics(text, num_topics=5, top_n=5):
    """
    Extract topics from a text using NMF (Non-negative Matrix Factorization).

    Parameters:
    text (str): The text to analyze.
    num_topics (int): The number of topics to extract.
    top_n (int): The number of top words to consider for each topic.

    Returns:
    list: A list of extracted topics.
    """
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 3))
    X = vectorizer.fit_transform(text)
    
    model = NMF(n_components=num_topics, random_state=42)
    model.fit(X)
    
    feature_names = vectorizer.get_feature_names_out()
    topics = [feature_names[i] for topic_idx, topic in enumerate(model.components_)
              for i in topic.argsort()[:-top_n - 1:-1]]
    
    # Post-processing to filter out unwanted patterns from topics
    topics = list(set(topic for topic in topics
                      if not re.match(r'^\d+$', topic) and
                      not re.match(r'\b\d{1,2}[a-zA-Z]{1,3}\s?\w{1,5}\s?\d{1,5}\s?\d{1,5}\b', topic) and
                      len(topic) > 2 and topic not in ENGLISH_STOP_WORDS))
    
    return topics

# Function to normalize MGRS (Military Grid Reference System) strings by removing spaces.
def normalize_mgrs(mgrs_str):
    """
    Normalize an MGRS string by removing all spaces.

    Parameters:
    mgrs_str (str): The MGRS string to normalize.

    Returns:
    str: The normalized MGRS string.
    """
    return mgrs_str.replace(" ", "")

# # Function to extract the highest classification and any caveats from a body of text using regex.
# def extract_classification_and_caveats(text):
#     """
#     Extract classification and caveats from a given text using regular expressions.

#     Parameters:
#     text (str): The text from which to extract classifications and caveats.

#     Returns:
#     tuple: A tuple containing the highest classification and a list of caveats.
#     """
#     classifications_priority = ['none_found', 'Classification', 'U', 'C', 'S']
#     highest_classification = "none_found"
#     caveats = "none_found"

#     classification_pattern = r'\((U|C|S|Classification)(?://([\w,]+))?\)'
#     matches = re.findall(classification_pattern, text)

#     if matches:
#         caveats_set = set()
#         for match in matches:
#             classification, caveat_str = match
#             if classification in classifications_priority:
#                 if classifications_priority.index(classification) > classifications_priority.index(highest_classification):
#                     highest_classification = classification
#             if caveat_str:
#                 caveats_set.update(caveat_str.split(','))

#         caveats = list(caveats_set) if caveats_set else caveats
    
#     return highest_classification, caveats

def extract_classification_and_caveats(text):
    """
    Extract classification and caveats from a given text using regular expressions.

    Parameters:
    text (str): The text from which to extract classifications and caveats.

    Returns:
    tuple: A tuple containing the highest classification and a list of caveats.
    """
    classifications_priority = ['none_found', 'Classification', 'U', 'C', 'S']
    highest_classification = "none_found"
    caveats = "none_found"

    # Improved regex pattern to capture classification and caveats
    classification_pattern = r'\((U|C|S|Classification)(?:\/\/([\w,]+))?\)'
    matches = re.findall(classification_pattern, text)

    logger.info(f"Matches found: {matches}")

    if matches:
        caveats_set = set()
        for match in matches:
            classification, caveat_str = match
            if classification in classifications_priority:
                if classifications_priority.index(classification) > classifications_priority.index(highest_classification):
                    highest_classification = classification
            if caveat_str:
                caveats_set.update(caveat_str.split(','))

        caveats = list(caveats_set) if caveats_set else caveats

    logger.info(f"Final highest classification: {highest_classification}, caveats: {caveats}")

    return highest_classification, caveats

# Function to extract keywords from a given text, based on a predefined list of keywords.
def extract_keywords(text):
    """
    Extract keywords from the text that match a predefined list of keywords.

    Parameters:
    text (str): The text to search for keywords.

    Returns:
    list: A list of found keywords.
    """
    keywords_list = Keywords.keywords_list

    found_keywords = set()
    text_lower = text.lower()
    for keyword in keywords_list:
        if keyword.lower() in text_lower:
            found_keywords.add(keyword)
    return list(found_keywords)

# Function to filter out unwanted text patterns, such as MGRS coordinates and numbers.
def filter_text(text):
    """
    Remove unwanted text patterns from a string, such as MGRS-like strings and purely numeric strings.

    Parameters:
    text (str): The text to filter.

    Returns:
    str: The filtered text.
    """
    # Regex to match MGRS-like patterns 
    text = re.sub(r'\b\d{1,2}[A-Za-z]{1,3}(?:\s+[A-Za-z]{1,2})?\s*\d+\s*\d+\b', '', text)
    # Remove purely numeric strings
    text = re.sub(r'\b\d+\b', '', text)

    # Remove the word "MGRS"
    text = re.sub(r'\bMGRS\b', '', text)

    return text

# Function to clean and normalize timeframes from a list, standardizing them for consistency.
def clean_timeframes(timeframes_list):
    """
    Clean and normalize the timeframes from a list of strings.

    This function matches various timeframe formats and normalizes them into a standardized lowercase
    string without spaces. It maps them back to a human-readable format, which is then returned as a list
    or a single string "none" if no valid timeframes are found.

    Parameters:
    timeframes_list (list): A list of timeframe strings.

    Returns:
    list or str: A cleaned list of timeframes or the string "none" if no valid timeframes are found.
    """
    logger.info("\t\tAttempting to clean timeframes.")
    clean_timeframes = {}  # Using a dictionary to map normalized to original timeframes
    for timeframe in timeframes_list:
        # Match various timeframe formats and normalize
        if re.match(r'(\d{1,4}[-/]\d{1,2}[-/]\d{1,4})|(\d{1,2}:\d{1,2})|(next|last)?\s?\d+\s?(days?|months?|years?|hours?|minutes?)|(january|february|march|april|may|june|july|august|september|october|november|december)\s?\d{1,4}|(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', timeframe, re.IGNORECASE):
            normalized_timeframe = re.sub(r'\s+', '', timeframe).lower()  # Normalize the timeframe
            clean_timeframes[normalized_timeframe] = timeframe.capitalize().strip()  # Map normalized to original
    
    cleaned = list(clean_timeframes.values())  # Retrieve the human-readable versions
    
    return ','.join(cleaned) if cleaned else "none"  # Return the cleaned timeframes as a comma-separated string or "none"

# Function to remove duplicate location entries from a list, ensuring each location is unique.
def remove_duplicate_locations(locations_list):
    """
    Remove duplicate entries from a list of location strings.

    This function uses a set to ensure that only unique location strings are kept. The resulting set
    is then converted back into a comma-separated string.

    Parameters:
    locations_list (list): A list of location strings.

    Returns:
    str: A string of unique, comma-separated location names.
    """
    logger.info("\t\tAttempting to remove duplicate locations.")
    unique_locations = set(locations_list)  # Remove duplicates by converting the list to a set
    return ','.join(unique_locations)  # Convert the set back to a comma-separated string

# Function to filter and clean individual topic entries from a list, removing unwanted characters or words.
def filter_individual_topics(topics):
    """
    Filter individual topics to remove unwanted characters or words.

    This function applies a text filtering process to each topic in a list, ensuring that only relevant and
    cleaned topics are returned.

    Parameters:
    topics (list): A list of topic strings.

    Returns:
    list: A list of filtered topic strings.
    """
    logger.info("\t\tAttempting to filter topics.")
    filtered_topics = []  # Initialize an empty list for filtered topics
    for topic in topics:
        filtered_topic = filter_text(topic)  # Apply text filtering
        if filtered_topic:  # Only add non-empty, filtered topics to the list
            filtered_topics.append(filtered_topic)
    return filtered_topics  # Return the list of filtered topics