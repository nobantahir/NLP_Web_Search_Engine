# global token dict
all_tokens = {}

# global doc_count, token count
# assumes we are partial indexing
doc_count = 0
token_count = 0

def total_docs():
    return global doc_count

def total_tokens():
    return global token_count

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