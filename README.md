
# NLP Web Search Engine

A Python-based search engine that processes a collection of cached web pages, builds an inverted index using natural language processing techniques, and provides both terminal and web-based search interfaces.

## Features

-   **Efficient Text Processing**: Uses NLTK for tokenization and Porter Stemmer for stemming
-   **Advanced Indexing**: Creates compressed inverted indexes with tf-idf scoring
-   **Partial Indexing**: Implements memory-efficient index construction for large datasets
-   **Binary Search**: Custom BinarySearch class for efficient retrieval from disk
-   **Dual Interface**: Both command-line and web-based search interfaces
-   **Smart Ranking**: Enhanced scoring for terms in important HTML tags
-   **High Performance**: Search response times in single-digit milliseconds
-   **HTML Content Analysis**: Uses BeautifulSoup to parse and extract meaningful content

## Project Structure

### Core Components

-   **m1.py**: Main module for index building, merging, and terminal searching
-   **website.py**: Flask web application providing browser-based interface
-   **binary_search.py**: Implements the BinarySearch class for efficient storage/retrieval
-   **tools.py**: Helper utilities (timers, formatting, etc.)

### Data Structures

-   Inverted index mapping: tokens → document postings with frequencies
-   Document mappings: URL ↔ docID for efficient reference
-   tf-idf scores: Pre-calculated for ranking relevance
-   Binary file storage: Compressed representation of indexes

## Implementation Details

### Indexing Process

1.  Parse JSON files containing cached web pages
2.  Extract and process HTML content using BeautifulSoup
3.  Tokenize text and apply stemming using NLTK's Porter Stemmer
4.  Create partial indexes when memory threshold is reached
5.  Merge partial indexes into final compressed binary format
6.  Calculate and store tf-idf scores for ranking

### Ranking Algorithm

-   Basic ranking uses tf-idf scoring
-   Additional weight given to tokens found in important HTML tags:
    -   `title`,  `h1`-`h6`, and  `b`  elements
-   Search results sorted by relevance score

### Performance Optimizations

-   Stem caching to avoid redundant stemming
-   Partial indexing to manage memory usage
-   Binary file storage for efficient disk usage
-   Struct library for fast binary file operations

## Installation

1.  Ensure you have Python 3.x installed
2.  Install dependencies:
    
    ```
    pip install flask bs4 nltk
    
    ```
    
3.  Place your web page collection in the  `developer/DEV`  directory
4.  Run either  `m1.py`  or  `website.py`  to build the index (first run only)

## Usage

### Web Interface

1.  Start the web server:
    
    ```
    python website.py
    
    ```
    
2.  Open your browser and navigate to  [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
3.  Enter your search query and click "Search"
4.  View results showing URLs, relevance scores, and search statistics

### Command Line Interface

1.  Uncomment the main function in m1.py
2.  Run the search engine in terminal mode:
    
    ```
    python m1.py
    
    ```
    
3.  Follow the prompts to enter search queries
4.  Type 'quit' to exit

## Search Algorithm

1.  Parse and tokenize the search query using the same process as indexing
2.  Retrieve postings for each query term from the inverted index
3.  Calculate combined relevance scores using tf-idf values
4.  Sort results by score and return the top matches
5.  For multi-word queries, documents containing all terms are prioritized

## Directory Structure

The search engine expects web content in the following structure:

```
project_root/
├── m1.py, website.py, etc.
└── developer/
    └── DEV/
        └── [numbered folders]/
            └── [json files]

```

----------

_This search engine was developed as a project to demonstrate information retrieval and NLP techniques in Python._
