# CS 121 - Assignment 3 (M1)
# Group 23
# Catherine Fajardo, Yaqub Hasan, Kyle Jung, Noban Tahir

import os
import json
import pickle
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning, XMLParsedAsHTMLWarning
import warnings
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import time
from datetime import datetime, timedelta
import functools

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')

# Set up stop words and the Porter Stemmer
stop_words = set(stopwords.words('english'))
ps = PorterStemmer()

# Ignore warnings for content resembling URLs or XML parsed as HTML
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)


# global token dict
all_tokens = {}

# global doc_count, token count
# assumes we are partial indexing
# we don't need global since we are not modifying. we need to declare global in the func
# and return just the variable if we choose to modify it
doc_count = 0
token_count = 0

def format_dt():
    dt = datetime.now()
    return dt.strftime("%#I:%M:%S %p %Y-%m-%d") if os.name == 'nt' else dt.strftime("%-I:%M:%S %p %Y-%m-%d")

def format_exec_time(seconds):
    td = timedelta(seconds=seconds)
    minutes, seconds = divmod(td.seconds, 60)
    return f"{minutes:02d}:{seconds:05.2f}"

def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_dt = format_dt()
        print(f"Starting {func.__name__} at: {start_dt}")
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_dt = format_dt()
        print(f"Ending {func.__name__} at: {end_dt}")
        
        execution_time = end_time - start_time
        formatted_time = format_exec_time(execution_time)
        print(f"Total execution time for {func.__name__}: {formatted_time}")
        
        return result
    return wrapper

def print_returns(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned: {result}")
        return result
    return wrapper

def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.count += 1
        print(f"{func.__name__} calls: {wrapper.count}")
        return func(*args, **kwargs)
    wrapper.count = 0
    return wrapper

def total_docs():
    return doc_count

def total_tokens():
    return token_count

def insert_posting(token_dict, token, doc_id, token_freq) -> dict:
    """Insert a posting tuple (doc_id, token freq) into a token dictionary."""
    if token not in token_dict:
        token_dict[token] = []
    token_dict[token].append((doc_id, token_freq))
    return token_dict

@count_calls
def merge_dict(dict_a, dict_b)->dict:
    """Merge two token dicts."""
    # We copy dict_a so we don't change the original, then add in dict_b's postings without sorting.
    merged_dict = dict_a.copy()
    for token, postlist in dict_b.items():
        if token not in merged_dict:
            merged_dict[token] = []
        merged_dict[token] += postlist
    return merged_dict

@count_calls
def retrievePaths():
    """retrieves list of all file paths within directory of developer/dev"""

    # get paths for current directory and dev folder
    currentDir = os.path.dirname(os.path.abspath(__file__))
    pathDev = os.path.join(currentDir, "developer", "DEV")
    
    if not os.path.exists(pathDev):
        print(f"Error: directory '{pathDev}' does not exist.")
        return []
    
    # Return a list of JSON file paths
    return [os.path.join(base, page)
            for base, _, docs in os.walk(pathDev)
            for page in docs if page.endswith(".json")]

def save_pickle(data, filename):
    """
    Save the given data to a pickle file. This allows you to store and later reload your index.
    """
    with open(filename, 'wb') as f:
        pickle.dump(data, f)
    print(f"Data saved to {filename}")

def load_pickle(filename):
    """
    Load and return data from a pickle file. If the file doesn't exist, return an empty dictionary.
    """
    if not os.path.exists(filename):
        print(f"Pickle file {filename} does not exist. Returning empty dictionary.")
        return {}
    with open(filename, 'rb') as f:
        data = pickle.load(f)
    print(f"Data loaded from {filename}")
    return data

def update_pickle(new_data, filename):
    """
    Update the pickle file by merging existing data with new_data, then saving.
    """
    data = load_pickle(filename)
    data = merge_dict(data, new_data)
    save_pickle(data, filename)

def get_pickle_size(filename):
    """
    Return the size of the pickle file in kilobytes (KB).
    """
    if os.path.exists(filename):
        size_bytes = os.path.getsize(filename)
        return size_bytes / 1024.0
    else:
        print(f"Pickle file {filename} does not exist.")
        return 0

@count_calls
def parse_html(content):
    """
    Use BeautifulSoup with the lxml parser to extract plain text from HTML content.
    """
    soup = BeautifulSoup(content, 'lxml')
    return soup.get_text(separator=" ")

@count_calls
def tokenize(text, remove_stopwords=False, use_stemming=False):
    """
    Tokenize text using nltk's word_tokenize.
    
    Parameters:
      - remove_stopwords: if True, remove tokens that are in the stop_words set.
      - use_stemming: if True, apply Porter stemming to each token.
    """
    tokens = word_tokenize(text.lower())
    
    if remove_stopwords:
        tokens = [token for token in tokens if token not in stop_words]
    
    if use_stemming:
        tokens = [ps.stem(token) for token in tokens]
    
    return tokens

@timer
def build_index():
    """
    Build the inverted index from all JSON files in the specified folder.
    """
    global doc_count, token_count
    index = {}
    paths = retrievePaths()
    
    for doc_path in paths:
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading {doc_path}: {e}")
            continue
        
        doc_count += 1
        # Use the 'url' field as the document identifier, or fallback to the file path
        doc_id = data.get('url', doc_path)
        html_content = data.get('content', "")
        plain_text = parse_html(html_content)
        # Tokenize with stemming enabled (stop words are kept)
        tokens = tokenize(plain_text, remove_stopwords=False, use_stemming=False)
        
        # Create a frequency dictionary for tokens in this document
        freq_dict = {}
        for token in tokens:
            freq_dict[token] = freq_dict.get(token, 0) + 1
        
        # Insert each token and its frequency into the index
        for token, freq in freq_dict.items():
            insert_posting(index, token, doc_id, freq)
            token_count += 1
    
    return index


def main():
    # Build the inverted index from your dataset
    inverted_index = build_index()
    
    # Print basic statistics about the index
    print("Total documents processed:", total_docs())
    print("Total token postings inserted:", total_tokens())
    print("Unique tokens in index:", len(inverted_index))
    
    # ----- Pickle Part -----
    # Save the index to a pickle file for persistence
    pickle_filename = "inverted_index.pkl"
    save_pickle(inverted_index, pickle_filename)
    
    # Load the index back from the pickle file to verify it saved correctly
    loaded_index = load_pickle(pickle_filename)
    size_kb = get_pickle_size(pickle_filename)
    print(f"Pickle file size: {size_kb:.2f} KB")

if __name__ == "__main__":
    main()
