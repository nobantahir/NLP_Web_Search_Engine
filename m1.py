# CS 121 - Assignment 3 (M1)
# Group 23
# , Kyle Jung

import os

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
