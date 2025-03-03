# CS 121 - Assignment 3 (M1)
# Group 23
# Catherine Fajardo, Yaqub Hasan, Kyle Jung, Noban Tahir

import time
import os
import json
import pickle
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning, XMLParsedAsHTMLWarning
import warnings
import nltk
import re
import nltk
from nltk.stem import PorterStemmer

# Download necessary NLTK data
nltk.download('punkt', quiet=True)

# Set up Porter Stemmer
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

def insert_posting(token_dict, token, doc_id, token_freq, tagged) -> dict:
    """Insert a posting tuple (doc_id, token freq, tagged) into a token dictionary."""
    if token not in token_dict:
        token_dict[token] = []
    token_dict[token].append((doc_id, token_freq, tagged))
    return token_dict

def merge_dict(dict_a, dict_b):
    """Merge two token dictionaries."""
     # We copy dict_a so we don't change the original, then add in dict_b's postings without sorting.
    merged_dict = dict_a.copy()
    for token, postings in dict_b.items():
        if token not in merged_dict:
            merged_dict[token] = []
        merged_dict[token] += postings
    return merged_dict

# ------------------------------------------------------
# File I/O for Pickle
# ------------------------------------------------------
def save_pickle(data, filename):
    """Save data to a pickle file."""
    with open(filename, 'wb') as f:
        pickle.dump(data, f)
    print(f"Data saved to {filename}")

def load_pickle(filename):
    """Load and return data from a pickle file."""
    if not os.path.exists(filename):
        print(f"Pickle file '{filename}' does not exist. Returning empty dictionary.")
        return {}
    with open(filename, 'rb') as f:
        data = pickle.load(f)
    print(f"Data loaded from {filename}")
    return data

# ------------------------------------------------------
# HTML Parsing & Tokenization
# ------------------------------------------------------
def parse_html(content):
    """Use BeautifulSoup with 'lxml' to extract plain text from HTML."""
    soup = BeautifulSoup(content, 'lxml')
    return soup.get_text(separator=" ")

def tokenize(text):
    """
    Tokenize text using a regex approach
    
    Ignoring tokens < 3 chars or containing 'http'/'www',
    then apply Porter stemming.
    """
    # Capture alphanumeric sequences only, in lowercase
    raw_tokens = re.findall(r'[a-zA-Z0-9]+', text.lower())
    filtered_tokens = []
    
    for tok in raw_tokens:
        # Ignore tokens shorter than 3 chars
        if len(tok) < 3:
            continue
        # Skip anything that looks like a link
        if "http" in tok or "www" in tok:
            continue
        # Stem the token using PorterStemmer
        stemmed = ps.stem(tok)
        filtered_tokens.append(stemmed)
    return filtered_tokens

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

# ------------------------------------------------------
# Path Retrieval
# ------------------------------------------------------
def retrieve_paths():
    """retrieves list of all file paths within directory of developer/dev"""
    
    # get paths for current directory and dev folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path_dev = os.path.join(current_dir, "developer", "DEV")
    
    if not os.path.exists(path_dev):
        print(f"Error: directory '{path_dev}' does not exist.")
        return []
    
    # Return a list of JSON file paths
    return [
        os.path.join(base, page)
        for base, _, docs in os.walk(path_dev)
        for page in docs if page.endswith(".json")]

# ------------------------------------------------------
# Index Building
# ------------------------------------------------------
def build_index():
    """
    Build the inverted index from all JSON files, dumping partial indexes exactly 3 times:
    1) After processing ~1/3 of the documents
    2) After processing ~2/3 of the documents
    3) After processing all documents
    """
    global doc_count, token_count
    
    # Retrieve all JSON file paths from the "developer/DEV" folder
    paths = retrieve_paths()
    total_files = len(paths)
    
    # If no files are found, print a message and return
    if total_files == 0:
        print("No JSON files found.")
        return 0
    
    # Determine the cut-off points for dumping partial indexes:
    # dump1 is at 1/3 of the total files, dump2 is at 2/3 of the total files
    dump1 = total_files // 3
    dump2 = (total_files * 2) // 3
    
    # This dictionary will hold our in-memory index until we dump it
    index = {}
    # Keep track of how many partial indexes we've saved so far
    partial_count = 0
    
    # Loop over each file path, using enumerate to track the index (i)
    for i, doc_path in enumerate(paths):
        try:
            # Attempt to open and load the JSON file
            with open(doc_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            # If there's an error reading the file, print a message and skip
            print(f"Error reading {doc_path}: {e}")
            continue
        
        # Increment the global document counter
        doc_count += 1
        
        # Extract the "content" field; skip if it's empty or just whitespace
        html_content = data.get('content', "")
        if not html_content.strip():
            continue
        
        # Get the document's URL or fallback to its file path
        doc_id = data.get('url', doc_path)
        # Convert the HTML content to plain text
        text_content = parse_html(html_content)
        
        # Tokenize the text content (regex-based, no stopword removal)
        tokens = tokenize(text_content)
        
        # If tokenization yields no tokens, skip this file
        if not tokens:
            continue
        
         # List of HTML tags that mark 'important' words
        tag_list = ['title', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'b']
        important_tokens = create_tagged_set(html_content, tag_list)
        
        # Build a frequency dictionary for tokens in this document
        freq_dict = {}
        for t in tokens:
            freq_dict[t] = freq_dict.get(t, 0) + 1
        
        # If the frequency dictionary is empty, skip
        if not freq_dict:
            continue
        
        # Insert each token posting into our index, noting if it's "important"
        for token, freq in freq_dict.items():
            is_important = (token in important_tokens)
            insert_posting(index, token, doc_id, freq, is_important)
            # Increment the global token postings counter
            token_count += 1
        
        # Check if we've reached one of our partial dumping milestones
        if (i + 1) == dump1 or (i + 1) == dump2 or (i + 1) == total_files:
            # Sort the index by token alphabetically before dumping
            sorted_index = dict(sorted(index.items(), key=lambda x: x[0]))
            # Save this partial index to a pickle file
            save_pickle(sorted_index, f"partial_index_{partial_count}.pkl")
            # Clear the index to start fresh for the next batch and increment the partial index count
            index.clear()
            partial_count += 1
    
    # Return how many partial indexes were saved
    return partial_count

# ------------------------------------------------------
# Merge Partial Indexes
# ------------------------------------------------------
def merge_partial_indexes():
    """
    Merge all partial indexes (partial_index_*.pkl) into a final index file named 'final_index.pkl'.
    """
    # Find all files that match the naming pattern for partial indexes
    pkl_files = [f for f in os.listdir() if f.startswith("partial_index_") and f.endswith(".pkl")]
    # Sort them by their numeric suffix (e.g., partial_index_0.pkl, partial_index_1.pkl, etc.)
    pkl_files.sort(key=lambda x: int(x.split("_")[-1].split(".")[0]))
    
    final_index = {}
    # Load each partial index, merge into 'final_index', then remove the partial file
    for pf in pkl_files:
        data = load_pickle(pf)
        final_index = merge_dict(final_index, data)
        os.remove(pf)
    
    # Sort the final index by token before saving
    final_index = dict(sorted(final_index.items(), key=lambda x: x[0]))
    save_pickle(final_index, "final_index.pkl")
    print(f"Final index saved as 'final_index.pkl' with {len(final_index)} unique tokens.")
    return final_index

# ------------------------------------------------------
# Boolean AND Search
# ------------------------------------------------------
def boolean_search(query, index):
    """Perform a Boolean AND search on the final index for the given query."""
    # Convert the query string into tokens
    query_tokens = tokenize(query)
    result_set = None
    
    # For each token, get the set of doc_ids and intersect them
    for token in query_tokens:
        postings = index.get(token, [])
        doc_ids = {doc_id for doc_id, freq, imp in postings}
        
        # If it's the first token, initialize result_set;
        # otherwise, intersect with existing results
        if result_set is None:
            result_set = doc_ids
        else:
            result_set = result_set.intersection(doc_ids)
    
    # Return an empty set if result_set is None
    return result_set or set()

def main():
    # Measure how long the indexing process takes
    final_index = False
    if not os.path.exists("final_index.pkl"):
        start_time = time.time()
        
        partial_count = build_index()
        print("Total documents processed:", total_docs())
        print("Total token postings inserted:", total_tokens())
        print(f"{partial_count} partial index files have been saved.")
        
        final_index = merge_partial_indexes()
        
        end_time = time.time()
        print(f"Indexing and merging took {end_time - start_time:.2f} seconds.\n")
    
    if not final_index:
        final_index = pickle.load(open("final_index.pkl", "rb"))
        
    # Now prompt for queries and measure each query's time
    print("Enter queries (Boolean AND). Type 'exit' to quit.\n")
    while True:
        user_input = input("Query: ").strip()
        if user_input.lower() == 'exit':
            break
        if not user_input:
            continue
        
        query_start = time.time()
        results = boolean_search(user_input, final_index)
        query_end = time.time()
        
        print(f"Found {len(results)} results. (Query took {query_end - query_start:.4f} seconds.)")
        for doc_id in list(results)[:5]:
            print("  ", doc_id)

if __name__ == "__main__":
    main()