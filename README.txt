----------------
Project Overview
----------------
This project implements a simple search engine in Python. It reads a collection of JSON files containing HTML content, builds an inverted index, and then provides two ways to search:
1. A terminal-based interface through m1.py.
2. A web-based interface through website.py using Flask.

-----
Files
-----
1. m1.py
   - Main module that builds the index, merges partial indexes, and provides functions for searching in the terminal or for other files to import.

2. website.py
   - A Flask web application that uses m1.py to perform searches in a browser-based interface.

3. binary_search.py
   - Contains the BinarySearch class for storing and retrieving postings from disk.

4. tools.py
   - Helper functions (timers, printing, etc.).

5. README.txt
   - Explains how to run and use the project.

6. TEST.txt
   - Contains the test queries used to evaluate the engine, plus notes on any improvements made.

---------------------
1. Building the Index
---------------------
1. Make sure you have all dependencies installed:
   - Python 3.x
   - pip install flask bs4 nltk (and any other libraries needed).

2. Whenever you run either m1.py or website.py, the code will:
   - Check if a final_index.pkl file exists.
   - If not, it processes all JSON files in developer/DEV, creates partial indexes, merges them into final_index.pkl, and also creates doc2url.pkl (mapping docIDs to URLs).
   - If final_index.pkl already exists, it simply loads the index.

--------------------------------------
2. Starting the Search Interface (Web)
--------------------------------------
1. Run website.py:
   - Open your terminal and type: python website.py
   - You will see messages like:
     About to initialize index...
     Loading Index.
     ...
     Flask server running at http://127.0.0.1:5000/

2. Open a Web Browser:
   - Go to http://127.0.0.1:5000/
   - You will see the home page with a search box.

3. Perform a Search:
   - Type a query into the search field and click Search.
   - The results page shows:
     - The total number of results found.
     - The top 10 results.
     - The time it took to perform the search (in milliseconds).
     - A table of URLs and their frequencies.

4. Navigation:
   - The “A23 Search Engine” text at the top is a clickable link that takes you back to the home page.
   - There is also a “Go Back” button on the results page, allowing you to return to the previous search query (if any).

5. Empty Queries:
   - If you click Search without entering anything, the page will simply take you back to the home page.

-------------------------------------------------
3. Performing a Search in the Terminal (Optional)
-------------------------------------------------
1. Run m1.py in interactive mode:
   - Uncomment the main in m1.py
   - Open your terminal and type: python m1.py
   - It will automatically check or build the index if needed, then prompt:
     Enter a search term (or 'quit' to exit):

2. Type a query:
   - Type a query and press Enter.
   - The script prints how many results were found and lists them with frequencies.

3. Exit:
   - Type quit to stop the terminal search loop.
