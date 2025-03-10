# CS 121 - Assignment 3 (M1)
# Group 23
# Catherine Fajardo, Yaqub Hasan, Kyle Jung, Noban Tahir

import json
import nltk
import os
import pickle
import re
import time
import warnings
import zlib
from binary_search import BinarySearch
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning, XMLParsedAsHTMLWarning
from collections import Counter
from nltk.stem import PorterStemmer
from tools import timer, print_returns, count_calls
from math import log

# Download necessary NLTK data
nltk.download('punkt', quiet=True)

# Set up the Porter Stemmer
ps = PorterStemmer()
# Create global for BinarySearch
bs = None

# Ignore warnings for content resembling URLs or XML parsed as HTML
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# -----------------------------------------------------------------------------
# Global variables
# -----------------------------------------------------------------------------
doc_count = 0        # Number of documents processed
token_count = 0      # Number of token postings inserted
current_file = 0     # Tracks which file is currently being processed
total_files = 0      # Stores the total number of files to process
doc2id = {}          # Maps a document URL -> integer docID
doc2url = {}         # Maps an integer docID -> the original document URL
next_doc_id = 0      # Keeps track of the next available integer docID

stem_cache = {}      # Cache for token -> stem (avoids re-stemming the same token)
MAX_POSTINGS = 200_000  # If postings exceed this, we do a partial dump

INDEX_READY = False      # Will be set to True once the index is loaded/built
final_index = {}         # Our final in-memory index

idf = {}                 # Dict for token:num of docs

# -----------------------------------------------------------------------------
# Utility
# -----------------------------------------------------------------------------
def total_docs():
    """Return the total number of documents processed."""
    return doc_count

def total_tokens():
    """Return the total number of token postings inserted."""
    return token_count

# -----------------------------------------------------------------------------
# Insert posting
# -----------------------------------------------------------------------------
def insert_posting(token_dict, token, doc_id_int, token_freq, is_important=False, len_tokens=0):
    """Insert a posting tuple (doc_id, token freq, is_important) into a token dictionary."""
    if token not in token_dict:
        token_dict[token] = []
    token_dict[token].append((doc_id_int, token_freq, is_important, len_tokens))
    return token_dict

# -----------------------------------------------------------------------------
# Scoring Calculations
# -----------------------------------------------------------------------------
def calc_tf(token_freq, token_total, token):
    """Calculate the term frequency (tf) of a document and a given token."""
    return (token_freq / token_count)

def calc_idf(token):
    """Calculate the inverse document frequency (idf) of a document and given token."""
    global idf
    temp_doc_num = idf.get(token, None)
    max_doc = 55243

    if temp_doc_num:
        return log((max_doc/temp_doc_num), 10)
    else:
        return None

def calc_tf_idf(token, token_freq, token_total, doc_freq):
    """Calculate the tf-idf score of a document and a given token."""
    tf_score = calc_tf(token_freq, token_total, token)
    idf_score = calc_idf(doc_freq)
    # tf-idf = (1+log(tf)) * log(idf_score)
    return ((1+log(tf_score, 10)) * (log(idf_score, 10)))


# -----------------------------------------------------------------------------
# Merge two dictionaries
# -----------------------------------------------------------------------------
def merge_dict(dict_a, dict_b):
    """Merge two token dictionaries."""
    merged_dict = dict_a.copy()
    for token, postings in dict_b.items():
        if token not in merged_dict:
            merged_dict[token] = []
        merged_dict[token] += postings
    return merged_dict

# -----------------------------------------------------------------------------
# Compressed Pickle I/O
# -----------------------------------------------------------------------------
def save_pickle(data, filename):
    """Save data to a compressed pickle file using zlib."""
    pickled_data = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
    compressed_data = zlib.compress(pickled_data, level=6)
    with open(filename, 'wb') as f:
        f.write(compressed_data)

def load_pickle(filename):
    """Load data from a compressed pickle file using zlib."""
    if not os.path.exists(filename):
        print(f"Pickle file '{filename}' does not exist. Returning empty dictionary.")
        return {}
    with open(filename, 'rb') as f:
        compressed_data = f.read()
    pickled_data = zlib.decompress(compressed_data)
    data = pickle.loads(pickled_data)
    print(f"Data loaded from {filename}")
    return data

# -----------------------------------------------------------------------------
# doc_id mapping
# -----------------------------------------------------------------------------
def get_doc_id_int(doc_url):
    """
    Returns an integer docID for a given doc_url.
    If it's a new URL, it assigns the next available integer docID
    and updates the doc2id/doc2url mappings.
    """
    global next_doc_id
    if doc_url not in doc2id:
        doc2id[doc_url] = next_doc_id
        doc2url[next_doc_id] = doc_url
        next_doc_id += 1
    return doc2id[doc_url]

# -----------------------------------------------------------------------------
# HTML Parsing & Tokenization
# -----------------------------------------------------------------------------
def parse_html(content):
    """Use BeautifulSoup with 'lxml' to extract plain text from HTML."""
    soup = BeautifulSoup(content, 'lxml')
    return soup.get_text(separator=" ")

#@count_calls
def tokenize(text):
    """
    Tokenize text using a regex approach, ignoring tokens < 3 chars
    or containing 'http'/'www', then apply Porter stemming.
    """
    raw_tokens = re.findall(r'[a-zA-Z0-9]+', text.lower())
    filtered_tokens = []

    for tok in raw_tokens:
        # Skip tokens shorter than 3 chars
        if len(tok) < 2:
            continue
        # Skip anything that looks like a link
        if "http" in tok or "www" in tok:
            continue
        # (Optional) skip tokens that contain digits
        if any(ch.isdigit() for ch in tok):
            continue

        # Use caching to avoid re-stemming the same token
        if tok in stem_cache:
            stemmed = stem_cache[tok]
        else:
            stemmed = ps.stem(tok)
            stem_cache[tok] = stemmed

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

# -----------------------------------------------------------------------------
# Path Retrieval
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# Build Index
# -----------------------------------------------------------------------------
def build_index():
    """
    Build the inverted index from all JSON files, dumping partial indexes
    exactly 3 times (1/3, 2/3, and end). Also does dynamic partial dumps
    if the index grows too large (MAX_POSTINGS).

    This function also tracks progress by updating 'current_file'
    (which file we're on) and 'total_files' (total number of files).
    """
    global doc_count, token_count, current_file, total_files

    # Retrieve all JSON file paths from the "developer/DEV" folder
    paths = retrieve_paths()
    total_files = len(paths)  # Set total number of files for progress tracking
    
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
        # Update the global 'current_file' so we know how many files have been processed
        current_file = i + 1

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

        url_field = data.get('url', doc_path)
        
        # Get the document's URL or fallback to its file path
        doc_id_int = get_doc_id_int(url_field)
        # Convert the HTML content to plain text
        text_content = parse_html(html_content)
        
        # Tokenize the text content (regex-based, no stopword removal)
        tokens = tokenize(text_content)
        
        # If tokenization has no tokens, skip this file
        if not tokens:
            continue

        # List of HTML tags that mark 'important' words
        tag_list = ['title', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'b']
        important_tokens = create_tagged_set(html_content, tag_list)

        # Build a frequency dictionary for tokens in this document
        freq_dict = Counter(tokens)
        if not freq_dict:
            continue

        # Insert each token into our index
        for token, freq in freq_dict.items():
            is_important = (token in important_tokens)
            insert_posting(index, token, doc_id_int, freq, is_important, len(tokens))
            # Increment the global token postings counter
            token_count += 1

        # Check if index is too large -> dynamic partial dump
        total_postings = sum(len(v) for v in index.values())
        if total_postings > MAX_POSTINGS:
            sorted_index = dict(sorted(index.items(), key=lambda x: x[0]))
            save_pickle(sorted_index, f"partial_index_{partial_count}.pkl")
            index.clear()
            partial_count += 1

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

# -----------------------------------------------------------------------------
# Merge Partial Indexes
# -----------------------------------------------------------------------------
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


# -----------------------------------------------------------------------------
# Index Initialization
# -----------------------------------------------------------------------------
def initialize_index():
    """
    Builds or loads the index and doc2url mapping once. Sets INDEX_READY to True
    when everything is loaded. If final_index.pkl already exists, it just loads it.
    Otherwise, it calls build_index() and merge_partial_indexes().
    """
    global final_index, doc2url, INDEX_READY

    if os.path.exists("final_index.pkl"):
        print("Loading Index.")
        # Load existing index
        final_index_loaded = load_pickle("final_index.pkl")
        final_index.update(final_index_loaded)
        # Load doc2url mapping if it exists
        if os.path.exists("doc2url.pkl"):
            doc2url_map = load_pickle("doc2url.pkl")
            doc2url.update(doc2url_map)
        INDEX_READY = True
    else:
        print("Building Index.")
        # Build index from scratch
        start_time = time.time()
        partial_count = build_index()
        print("Total documents processed:", total_docs())
        print("Total token postings inserted:", total_tokens())
        print(f"{partial_count} partial index files have been saved.")

        final_merged = merge_partial_indexes()
        final_index.update(final_merged)
        end_time = time.time()
        print(f"Indexing and merging took {end_time - start_time:.2f} seconds.\n")

        # Save doc2url
        save_pickle(doc2url, "doc2url.pkl")
        INDEX_READY = True
    
    temp_index = load_pickle("final_index.pkl")
    
    global idf
    for key, value in temp_index.items():
        idf[key] = len(value)

    global bs
    bs = BinarySearch("final_index.pkl")
    return bs

# -----------------------------------------------------------------------------
# Posting Combinations
# -----------------------------------------------------------------------------
def merge_postings(lst1, lst2):
    """Takes two lists of postings, intersects them and adds freq for shared doc_id."""
    merged_list = []

    i, j = 0, 0
    while i < len(lst1) and j < len(lst2):
        if lst1[i][0] < lst2[j][0]:
            i += 1
        elif lst1[i][0] > lst2[j][0]:
            j += 1
        else:
            merged_list.append((lst1[i][0], lst1[i][1] + lst2[j][1])) # When doc_id matches, add freq and put in list of common
            i += 1
            j += 1

    return merged_list


def merge_by_smallest_lst(lsts):
    """Merge all posting lists in order from smallest to largest.
       after merging all, return list sorted by freq.
    """
    # If lsts is empty, we have no results
    if not lsts:
        print("Found 0 results.")
        return []

    if len(lsts) == 1:
        print(f"Found {len(lsts[0])} results.")
        return sorted(lsts[0], key=lambda x: x[1], reverse=True)

    if len(lsts) == 2:
        merged = merge_postings(lsts[0], lsts[1])
        print(f"Found {len(merged)} results.")
        return sorted(merged, key=lambda x: x[1], reverse=True)
    
    # Otherwise, we have 3+ lists
    lsts.sort(key=len)
    result = lsts[0]
    for i in range(1, len(lsts)):
        result = merge_postings(result, lsts[i])
    print(f"Found {len(result)} results.")

    return sorted(result, key=lambda x: x[1], reverse=True)

# -----------------------------------------------------------------------------
# Search Functionality
# -----------------------------------------------------------------------------
def search_loop(bs):
    """Interactive search method that prompts for queries and displays results."""
    print("Enter your search queries or type 'quit' to exit.")
    print()

    while True:
        search_query = input("Enter a search term (or 'quit' to exit): ")
        if search_query.lower() == 'quit':
            break

        search_tokens = tokenize(search_query)
        result_list = []

        start_time = time.time()
        for item in search_tokens:
            temp = bs.single_search(item)
            tf_idf = []
            for post in temp:
                lst_post = list(post)
                if calc_idf(item):
                    lst_post[1] *= calc_idf(item)
                tup_post = tuple(lst_post)
                tf_idf.append(tup_post)
            result_list.append(tf_idf)
        merged_results = merge_by_smallest_lst(result_list)
        end_time = time.time()

        # Calculate the execution time in milliseconds
        execution_time_ms = (end_time - start_time) * 1000

        # If no results, just print nothing and continue
        if not merged_results:
            print(f"Search completed in {execution_time_ms:.2f} ms\n")
            continue

        # Otherwise, proceed with printing top results
        final_results = merged_results[:10]

        # Safely compute alignment only if final_results is not empty
        longest_url = max(len(doc2url[item[0]]) for item in final_results)
        longest_freq = max(len(str(item[1])) for item in final_results)
        width = longest_url + longest_freq + 15

        for i, item in enumerate(final_results, 1):
            url = doc2url[item[0]]
            freq = item[1]
            print(f"{i:2}. {url:<{width - longest_freq - 7}}{freq:>{longest_freq}}")
        
        # Print the execution time
        print(f"Search completed in {execution_time_ms:.2f} ms\n")

def bin_search(search_query):
    """Boolean single search operation but using the bs object."""
    global bs
    search_tokens = tokenize(search_query)
    
    # If there are no valid tokens, return empty results right away
    if not search_tokens:
        return []
    
    result_list = []
    for item in search_tokens:
        temp = bs.single_search(item)
        tf_idf = []
        for post in temp:
            lst_post = list(post)
            if calc_idf(item):
                lst_post[1] *= calc_idf(item)
            tup_post = tuple(lst_post)
            tf_idf.append(tup_post)
        result_list.append(tf_idf)
    
    # If for some reason all tokens yield no postings, return empty
    if not result_list:
        return []
    
    merged_results = merge_by_smallest_lst(result_list)
    return merged_results

# -----------------------------------------------------------------------------
# Main - Command Line Version
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("Initializing Index.")
    bs = initialize_index()
    search_loop(bs)
