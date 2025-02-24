# CS 121 - Assignment 3 (M1)
# Group 23
# Catherine Fajardo, Yaqub Hasan, Kyle Jung, Noban Tahir

import os

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

def insert_posting(token_dict, token, doc_id, token_freq) -> dict:
    """Insert a posting tuple (doc_id, token freq) into a token dictionary."""
    # {token: [(doc_id: word freq), (doc_id:word_freq)]
    if not(token in token_dict):
        token_dict[token] = []
    token_dict[token].append((doc_id, token_freq))
    token_dict[token].sort()
    
    return token_dict

def merge_dict(dict_a, dict_b)->dict:
    """Merge two token dicts."""
    merged_dict = dict_a

    # get all tokens from second dict
    for token, postlist in dict_b.items():
        if not (token in merged_dict):
            merged_dict[token] = []
        # combine lists
        merged_dict[token] = merged_dict[token] + postlist
        merged_dict[token].sort
    
    return merged_dict

def retrievePaths():
    """retrieves list of all file paths within directory of developer/dev"""

    # get paths for current directory and dev folder
    currentDir = os.path.dirname(os.path.abspath(__file__))
    pathDev = os.path.join(currentDir, "developer", "DEV")
    
    # error check wrong dir
    if not os.path.exists(pathDev):
        print(f"error: dir '{pathDev}' does not exist.")
        return list()

    # iterate through subfolders
    webpages = list()
    for base, _, docs in os.walk(pathDev):
        for page in docs:
            if page.endswith(".json"):
                webpages.append(os.path.join(base, page))
    
    return webpages

if __name__ == "__main__":
    # parsing developer directory with os module
    json_paths = retrievePaths()

    # test req #2
    print(json_paths)

