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
HTML_NOT_READY_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>A23 Search Engine - Building Index</title>
    <meta http-equiv="refresh" content="3">
    <style>
        body {
            margin: 0; padding: 0;
            background: #f0f0f0;
            font-family: Arial, sans-serif;
            display: flex; flex-direction: column;
            min-height: 100vh;
        }
        header {
            background: #003366; color: #fff; padding: 1rem; text-align: center;
        }
        header h1 { margin: 0; }
        header h1 a { color: #fff; text-decoration: none; }
        header h1 a:hover { text-decoration: underline; }
        .container {
            max-width: 1000px;
            margin: 2rem auto;
            background: #fff;
            padding: 2rem;
            border-radius: 6px;
            box-shadow: 0 0 8px rgba(0,0,0,0.1);
            text-align: center;
        }
        .progress-wrapper {
            margin: 2rem auto;
            width: 80%;
            background: #ccc;
            border-radius: 10px;
            overflow: hidden;
            height: 30px;
        }
        .progress-bar {
            height: 100%;
            width: 0%;
            background: #003366;
            color: #fff;
            text-align: center;
            line-height: 30px;
            font-weight: bold;
        }
        footer {
            background: #003366;
            color: #fff;
            padding: 1rem;
            text-align: center;
            margin-top: auto;
        }
    </style>
</head>
<body>
    <header>
        <h1><a href="/">A23 Search Engine</a></h1>
    </header>
    <div class="container">
        <h2>Index is still building or loading</h2>
        <p>Please wait a moment while we process documents.</p>
        
        <!-- Progress Bar -->
        <div class="progress-wrapper">
            <div id="progress-bar" class="progress-bar">0%</div>
        </div>
        <p>This may take a few minutes depending on the dataset size.</p>
    </div>
    <footer></footer>

    <!-- Simple JS to poll progress endpoint -->
    <script>
    function updateProgress() {
      fetch("/progress")
        .then(response => response.json())
        .then(data => {
          const bar = document.getElementById("progress-bar");
          const pct = data.progress;
          bar.style.width = pct + "%";
          bar.textContent = pct + "%";

          // If progress < 100, keep polling every 2 seconds
          if (pct < 100) {
            setTimeout(updateProgress, 2000);
          } else {
            // Once it's 100%, auto-refresh the page after 15 seconds
            bar.textContent = "Indexing complete! Refreshing...";
            setTimeout(() => window.location.reload(), 15000);
          }
        })
        .catch(err => {
          console.error("Error fetching progress:", err);
        });
    }

    // Start polling on page load
    updateProgress();
    </script>
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
        td.score-col {
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
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              {% for item in results %}
                <tr>
                    <td>{{ loop.index }}</td>
                    <td class="url-col"><a href="{{ item.url }}" target="_blank">{{ item.url }}</a></td>
                    <td class="freq-col">{{"%.0f"|format(item.score * 100) }}</td>
                </tr>
              {% endfor %}
            </tbody>
          </table>
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
    """Route for the home page."""
    if not m1.INDEX_READY:
        return render_template_string(HTML_NOT_READY_PAGE)
    return render_template_string(HTML_INDEX_PAGE)

@app.route("/progress")
def progress():
    """Returns approximate indexing progress as a percentage."""
    if m1.total_files == 0:
        # Avoid division by zero if no files
        return {"progress": 0}

    # Calculate approximate percentage
    pct = int((m1.current_file / m1.total_files) * 100)
    return {"progress": pct}

@app.route("/search")
def search():
    """Route for handling search queries."""
    if not m1.INDEX_READY:
        return render_template_string(HTML_NOT_READY_PAGE)

    query = request.args.get("q", "").strip()
    if not query:
        return render_template_string(HTML_INDEX_PAGE)

    start_time = time.time()
    merged_results = m1.bin_search(query)
    end_time = time.time()

    execution_time_ms = (end_time - start_time) * 1000
    elapsed_time = f"{execution_time_ms:.2f}"
    top_results = merged_results[:10]

    results_list = []
    for doc_id_int, score in top_results:
        the_url = m1.doc2url.get(doc_id_int, "???")
        results_list.append({"doc_id": doc_id_int, "url": the_url, "score": score})

    return render_template_string(
        HTML_RESULTS_PAGE,
        query=query,
        count=len(merged_results),
        elapsed=elapsed_time,
        results=results_list
    )

def start_index_thread():
    """Start index building in a background thread."""
    import threading
    def run_index():
        print("Index building in background thread...")
        m1.initialize_index()
        print("Index is ready.")

    thread = threading.Thread(target=run_index)
    thread.start()

if __name__ == "__main__":
    print("Flask server running at http://127.0.0.1:5000/")
    start_index_thread()  # Begin building the index in the background
    app.run(debug=True, port=5000, use_reloader=False)