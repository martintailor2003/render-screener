from flask import Flask, render_template
import threading
import time
from main import select_top_pairs_with_highest_volatility, get_pairs

app = Flask(__name__)
cached_data = None

def background_task():
    global cached_data
    while True:
        print("Refreshing data...")
        pairs = get_pairs()
        top_pairs = select_top_pairs_with_highest_volatility(pairs)
        cached_data = top_pairs
        print("Data refreshed.")
        time.sleep(10)  # Sleep for 20 minutes (20 minutes * 60 seconds) --> 10m

@app.route('/')
def index():
    global cached_data
    if cached_data is None:
        # If data is not cached, start a new thread to run background task
        thread = threading.Thread(target=background_task)
        thread.start()
        return render_template('loading.html')  # Return a loading page
    else:
        return render_template('index.html', top_pairs=cached_data)  # Return index page with cached data

if __name__ == '__main__':
    app.run(debug=True)
