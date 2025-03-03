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
import sys

SYS_MEMORY_USAGE = 0
GLOBAL_DUMP = 1024000

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

def total_docs():
    return doc_count

def total_tokens():
    return token_count

def create_tagged_set(content, tag_types:list) -> set:
    """Given HTML content and a list of HTML tag types, return a set
        of the words under those tags."""
    tagged_set = set()
    html_content = BeautifulSoup(content, 'lxml')
    for tag in tag_types:
        # get all text pieces under a certain HTML tag
        tagged_lines = [text.get_text() for text in html_content.find_all(tag) if text]
        tagged_tokens = set()

        # tokenize each line and combine sets
        for line in tagged_lines:
            if line:
                temp_tokens = set(tokenize(line))
                tagged_tokens = tagged_tokens | temp_tokens

        tagged_set = tagged_set | tagged_tokens
        # union of 2 sets
        
    return tagged_set

def insert_posting(token_dict, token, doc_id, token_freq, tagged) -> dict:
    """Insert a posting tuple (doc_id, token freq, tagged) into a token dictionary."""
    if token not in token_dict:
        token_dict[token] = []
    token_dict[token].append((doc_id, token_freq, tagged))
    return token_dict

def merge_dict(dict_a, dict_b)->dict:
    """Merge two token dicts."""
    # We copy dict_a so we don't change the original, then add in dict_b's postings without sorting.
    merged_dict = dict_a.copy()
    for token, postlist in dict_b.items():
        if token not in merged_dict:
            merged_dict[token] = []
        merged_dict[token] += postlist
    return merged_dict

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

def mergePartialIndexes():
    """merges all partial index files into one final index and records it"""

    partialIndexes = list()
    final = dict()
    
    # get partial index files
    for file in os.listdir():
        if file.startswith("partial_index_") and file.endswith(".pkl"):
            partialIndexes.append(file)

    # Sort the partial indexes by number to merge in order
    partialIndexes.sort(key=lambda x: int(x.split("_")[-1].split(".")[0]))

    # load/merge every partial index
    for i, v in enumerate(partialIndexes):
        partialData = load_pickle(v)
        final = merge_dict(final, partialData)

        # remove partial file after merge
        os.remove(v)

    # save merged final index
    save_pickle(final, "final_index.pkl")
    print(f"Final index saved as 'final_index.pkl' with {len(final)} unique tokens")


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

def save_partial_index(index, partial_num):
    """Save a partial index to a pickle file named with its partial number without printing."""
    filename = f"partial_index_{partial_num}.pkl"
    with open(filename, 'wb') as f:
        pickle.dump(index, f)

def parse_html(content):
    """
    Use BeautifulSoup with the lxml parser to extract plain text from HTML content.
    """
    soup = BeautifulSoup(content, 'lxml')
    return soup.get_text(separator=" ")

def tokenize(text, remove_stopwords=False, use_stemming=True):
    """
    Tokenize text using nltk's word_tokenize.
    
    Parameters:
      - remove_stopwords: if True, remove tokens that are in the stop_words set.
      - use_stemming: if True, apply Porter stemming to each token.
    """
    tokens = word_tokenize(text.lower())
    
    if remove_stopwords and use_stemming:
        tokens = [ps.stem(token) for token in tokens if token not in stop_words]
        
    elif remove_stopwords:
        tokens = [token for token in tokens if token not in stop_words]
    
    elif use_stemming:
        tokens = [ps.stem(token) for token in tokens]

    return tokens

def build_index():
    """
    Build the inverted index from all JSON files in the specified folder.
    """
    global doc_count, token_count
    index = {}
    partial_count = 0
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

        # list of HTML tags that mark 'important' words
        tag_list = ['title', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'b']
        tagged_token_set = create_tagged_set(html_content, tag_list)
    
        # Tokenize with stemming enabled (stop words are kept)
        tokens = tokenize(plain_text, remove_stopwords=False, use_stemming=True)
        
        # Create a frequency dictionary for tokens in this document
        freq_dict = {}
        for token in tokens:
            freq_dict[token] = freq_dict.get(token, 0) + 1
        
        # Insert each token, its frequency, and importance bool into the index
        # default bool for 'important tokens' is False
        for token, freq in freq_dict.items():
            tag_bool = False 
            if token in tagged_token_set:
                tag_bool = True

            insert_posting(index, token, doc_id, freq, tag_bool)
            token_count += 1
        
        # Check if the index has reached or exceeded 8,192 postings
        global GLOBAL_DUMP

        if len(index.items()) > 100000:
            save_partial_index(index, partial_count)
            global SYS_MEMORY_USAGE
            SYS_MEMORY_USAGE += sys.getsizeof(index)
            index.clear()  # Clear the index for the next partial
            partial_count += 1
    
    # Save any remaining postings as a final partial index
    if index:
        save_partial_index(index, partial_count)
        partial_count += 1
    
    # For now we don't merge partial indexes since that will be implemented later by someone else.
    return partial_count  # Return the number of partial indexes saved
    
def main():
    
    # Build the inverted index and get the count of partial indexes saved.
    partial_count = build_index()
    
    
    # Merge partial indexes
    # print("\nMerging all partial indexes...")
    # mergePartialIndexes()
    # inverted_index = build_index()
    
    # Print basic statistics about the index
    print("Total documents processed:", total_docs())
    print("Total token postings inserted:", total_tokens())
    # print("Unique tokens in index:", len(inverted_index))
    print(f"{partial_count} partial index files have been saved.")
    print(f"Total memory usage {SYS_MEMORY_USAGE/1024} KBs.")
    
    # # ----- Pickle Part -----
    # # Save the index to a pickle file for persistence
    # pickle_filename = "inverted_index.pkl"
    # save_pickle(inverted_index, pickle_filename)
    
    # # Load the index back from the pickle file to verify it saved correctly
    # loaded_index = load_pickle(pickle_filename)
    # size_kb = get_pickle_size(pickle_filename)
    # print(f"Pickle file size: {size_kb:.2f} KB")

if __name__ == "__main__":
    main()