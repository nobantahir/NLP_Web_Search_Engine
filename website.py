# CS 121 - Assignment 3 (M1)
# Group 23
# Catherine Fajardo, Yaqub Hasan, Kyle Jung, Noban Tahir

import m1
import time
from flask import Flask, request, render_template_string
# -----------------------------------------------------------------------------
# Flask Application
# -----------------------------------------------------------------------------
app = Flask(__name__)
HTML_INDEX_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>A23 Search Engine</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: #f0f0f0;
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }
        header {
            background: #003366;
            color: #fff;
            padding: 1rem;
            text-align: center;
        }
        header h1 {
            margin: 0;
        }
        header h1 a {
            color: #fff;
            text-decoration: none;
        }
        header h1 a:hover {
            text-decoration: underline;
        }
        .spacer {
            flex: 1;
        }
        .container {
            max-width: 1000px;
            margin: 2rem auto;
            background: #fff;
            padding: 2rem;
            border-radius: 6px;
            box-shadow: 0 0 8px rgba(0,0,0,0.1);
        }
        .search-form {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        .search-form input[type="text"] {
            width: 70%;
            padding: 0.5rem;
            font-size: 1rem;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        .search-form button {
            padding: 0.6rem 1rem;
            font-size: 1rem;
            border: none;
            border-radius: 4px;
            background: #003366;
            color: #fff;
            cursor: pointer;
        }
        .search-form button:hover {
            background: #002244;
        }
        footer {
            background: #003366;
            color: #fff;
            padding: 1rem;
            text-align: center;
        }
    </style>
</head>
<body>
    <header>
        <h1><a href="/">A23 Search Engine</a></h1>
    </header>

    <div class="spacer">
      <div class="container">
        <h2>Welcome!</h2>
        <p>Enter your query below:</p>
        <form class="search-form" action="/search" method="get">
            <input type="text" name="q" placeholder="Enter your query" />
            <button type="submit">Search</button>
        </form>
      </div>
    </div>

    <footer></footer>
</body>
</html>
"""
HTML_RESULTS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Search Results</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f0f0f0;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }
        header {
            background: #003366;
            color: #fff;
            padding: 1rem;
            text-align: center;
        }
        header h1 {
            margin: 0;
        }
        header h1 a {
            color: #fff;
            text-decoration: none;
        }
        .container {
            max-width: 1000px;
            margin: 2rem auto;
            background: #fff;
            padding: 2rem;
            border-radius: 6px;
            box-shadow: 0 0 8px rgba(0,0,0,0.1);
        }
        .search-form {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        .search-form input[type="text"] {
            width: 70%;
            padding: 0.5rem;
            font-size: 1rem;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        .search-form button {
            padding: 0.6rem 1rem;
            font-size: 1rem;
            border: none;
            border-radius: 4px;
            background: #003366;
            color: #fff;
            cursor: pointer;
        }
        .search-form button:hover {
            background: #002244;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }
        th, td {
            border: 1px solid #ccc;
            padding: 0.6rem;
        }
        th {
            background: #eee;
            text-align: left;
        }
        td.url-col a {
            color: #003366;
            text-decoration: none;
            word-wrap: break-word;
        }
        td.freq-col {
            text-align: right;
            width: 80px;
        }
        .nav-links {
            margin-top: 1rem;
        }
        .nav-links button {
            color: #fff;
            background-color: #003366;
            border: 1px solid #003366;
            padding: 0.6rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1rem;
        }
        .nav-links button:hover {
            background-color: #002244;
            border-color: #002244;
        }
        footer {
            background: #003366;
            color: #fff;
            padding: 1rem;
            text-align: center;
        }
        .spacer {
            flex: 1;
        }
    </style>
</head>
<body>
    <header>
        <h1><a href="/">A23 Search Engine</a></h1>
    </header>

    <div class="spacer">
      <div class="container">
        <h2>Search Results for "{{query}}"</h2>

        <!-- A search bar so users can keep searching -->
        <form class="search-form" action="/search" method="get">
            <input type="text" name="q" placeholder="Enter your query" />
            <button type="submit">Search</button>
        </form>

        <!-- Show how many results were found and how long the query took (in ms) -->
        {% if count == 0 %}
            <p>No results found. (Query completed in {{elapsed}} ms.)</p>
        {% else %}
            <p>Your search returned {{count}} results in total. Displaying the top 10 below. (Query completed in {{elapsed}} ms.)</p>
        {% endif %}


        {% if results and results|length > 0 %}
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>URL</th>
                <th>Frequency</th>
              </tr>
            </thead>
            <tbody>
              {% for item in results %}
                <tr>
                    <td>{{ loop.index }}</td>  <!-- loop.index is 1-based -->
                    <td class="url-col"><a href="{{ item.url }}" target="_blank">{{ item.url }}</a></td>
                    <td class="freq-col">{{ item.freq }}</td>
                    </tr>
                {% endfor %}
            </tbody>
          </table>
        {% else %}
            <p></p>
        {% endif %}

        <!-- "Go Back" button -->
        <div class="nav-links">
          <button type="button" onclick="window.history.back()">Go Back</button>
        </div>
      </div>
    </div>

    <footer></footer>
</body>
</html>
"""

@app.route("/")
def index_page():
    """Route for the home page. Shows a simple search form."""
    if not m1.INDEX_READY:
        return "<h1>Index is still building or loading. Please refresh.</h1>"
    return render_template_string(HTML_INDEX_PAGE)

@app.route("/search")
def search():
    if not m1.INDEX_READY:
        return "<h1>Index is still building or loading. Please refresh.</h1>"

    query = request.args.get("q", "").strip()
    
    if not query:
        return render_template_string(HTML_INDEX_PAGE)

    start_time = time.time()
    # This is now a list of (doc_id, freq) pairs
    merged_results = m1.bin_search(query)
    end_time = time.time()

    # Convert time to milliseconds
    execution_time_ms = (end_time - start_time) * 1000
    elapsed_time = f"{execution_time_ms:.2f}"
    top_results = merged_results[:10]

    results_list = []
    for doc_id_int, freq in top_results:
        the_url = m1.doc2url.get(doc_id_int, "???")
        results_list.append({"doc_id": doc_id_int, "url": the_url, "freq": freq})

    return render_template_string(
        HTML_RESULTS_PAGE,
        query=query,
        count=len(merged_results),
        elapsed=elapsed_time,
        results=results_list
    )
@app.route("/debug-list")
def debug_list():
    import os
    files = os.listdir(".")
    return {"files_in_cwd": files}
if __name__ == "__main__":
    # Initialize the index before running the Flask server
    print("About to initialize index...")
    m1.initialize_index()
    print("Flask server running at http://127.0.0.1:5000/")
    app.run(debug=True, port=5000)
