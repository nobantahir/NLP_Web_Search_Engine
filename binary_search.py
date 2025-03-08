import struct
import pickle
import os
from nltk.stem import PorterStemmer

class BinarySearch:
    def __init__(self, pickle_index):
        self.pickle_index = pickle_index # The final_index.pkl file which contains the dictionary object created in M1.
        self.dat_file = 'inverted_index.dat' # The local disk file to store our inverted index.
        self.search_dict = 'search_dict.pkl' # File for loading index_of_index in memory .
        self.index_of_index = None # Dict storing disk locations for tokens.
        self.initialize()


    def initialize(self):
        """Checks if the dat file or search dict files exist to load, otherwise creates them."""
        if os.path.exists(self.dat_file) and os.path.exists(self.search_dict):
            self.load_index_of_index()
        elif self.pickle_index:
            self.file_setup()
        else:
            raise Exception("File system corrupted. Search will not function.")


    def file_setup(self):
        """Creates the inverted_index.dat and search_dict.pkl files."""
        with open(self.pickle_index, 'rb') as f:
            data = pickle.load(f)
        self.dict_to_dat(data)
        self.index_of_index = self.create_index_of_index()
        self.save_index_of_index()

    
    def dict_to_dat(self, data):
        """Takes dictionary object and writes it to a .dat file using the struct library.
           
           Key: string
           -> encoded to bytes using utf-8

           Value: python object
           -> encoded to bytes using pickle

           struct.pack(format, value1, value2, ...)
           
           format: str 
           -> specify how to pack (encode) bytes
           -> !: network (big-endian). is version safe and reads left to right maintaining order.
           -> I: unsigned int of 4 bytes. capable of storing up to 2^32 different values which is a safe upper limit.
           ->    creates: b'\x00\x00\x00\x00'

           value: int
           -> specify how many bytes are needed to store data
           -> updates b'\x00\x00\x00\x00' with hexadeximal number of how many bytes to read to capture data
        """
        with open(self.dat_file, 'wb') as f:
            for key, value in data.items():
                key_bytes = key.encode('utf-8')
                value_bytes = pickle.dumps(value)
                f.write(struct.pack('!I', len(key_bytes)))
                f.write(key_bytes) # Write binary representation of key
                f.write(struct.pack('!I', len(value_bytes)))
                f.write(value_bytes) # Write binary representation of value


    def create_index_of_index(self):
        """Reads inverted_index.dat and unpacks the struct data to create an in memory index_of_index
           and a pickle file to save the dictionary object for future use.
           
           While Loop Logic:
           1. Check where in the file we are using pos.
           2. Try to read length of key from struct.
           3. If length of key, EOF and break.
           4. Parse length of key and store key content (after decoding from binary) into variable.
           5. Read length of value from struct.
           6. Move pointer using seek by length of value to reach start of next key.
           7. Store key:value pair of token:dat_position in dict.
        """
        index_of_index = {}
        with open(self.dat_file, 'rb') as f:
            while True:
                pos = f.tell() # Find where in the dat file we are
                key_length_data = f.read(4) # Read the 4 byte "value"
                if not key_length_data: # Reached EOF
                    break
                key_length = struct.unpack('!I', key_length_data)[0] # Parse the length to read key
                key = f.read(key_length).decode('utf-8') # Read length and decode key
                value_length = struct.unpack('!I', f.read(4))[0] # Read 4 byte "value" then parse value
                f.seek(value_length, os.SEEK_CUR) # Move to end of the values portion of key:value pair
                index_of_index[key] = pos # Store location of key
        return index_of_index

    def get_item(self, key):
        """Retrieve the value from the .dat file using the index_of_index to find disk location."""
        with open(self.dat_file, 'rb') as f:
            f.seek(self.index_of_index[key])
            key_length = struct.unpack('!I', f.read(4))[0]
            f.seek(key_length, os.SEEK_CUR)
            value_length = struct.unpack('!I', f.read(4))[0]
            value_bytes = f.read(value_length)
            return pickle.loads(value_bytes)

    def save_index_of_index(self):
        """Save the index_of_index dict to a pickle file."""
        with open(self.search_dict, 'wb') as f:
            pickle.dump(self.index_of_index, f)

    def load_index_of_index(self):
        """Load the index_of_index from a pickle file to a dict."""
        with open(self.search_dict, 'rb') as f:
            self.index_of_index = pickle.load(f)

    @staticmethod
    def stem_term(term):
        """Stem a term using PorterStemmer."""
        ps = PorterStemmer()
        return ps.stem(term.lower())

    def single_search(self, term, result_count):
        """Search for a stemmed term and return the top X results.
           
           If not in index, return empty list. 

           Get the posting list from the key:value pair and then adjust the scores.
           If important -> add ten to frequency.

           Sort by frequency and return specified count of results in descending order.
        """
        stemmed_term = self.stem_term(term)
        if stemmed_term in self.index_of_index:
            result = self.get_item(stemmed_term)
            adjusted_result = [(doc_id, freq + (10 if important else 0), important) for doc_id, freq, important in result]
            sorted_result = sorted(adjusted_result, key=lambda x: x[1], reverse=True)
            return sorted_result[:result_count]
        return []
