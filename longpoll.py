from flask import Flask, jsonify, render_template_string, Response
import time
import os
from config import BaseConfig, ProdConfig, TestConfig
import random

app: Flask = Flask(__name__)

# Determine the environment and load the appropriate configuration
if os.getenv('FLASK_ENV') == 'production':
    app.config.from_object(ProdConfig)
elif os.getenv('FLASK_ENV') == 'testing':
    app.config.from_object(TestConfig)
else:
    app.config.from_object(BaseConfig)


def ensure_config_defaults() -> None:
    """
    Ensure all necessary configurations have a default value from BaseConfig
    if not explicitly set.
    """
    for attr in dir(BaseConfig):
        # Ignore private attributes
        if not attr.startswith("__"):
            app.config.setdefault(attr, getattr(BaseConfig, attr))


ensure_config_defaults()

INDEX_HTML: str = """
<!DOCTYPE html>
<html>
<head>
    <title>Long Polling Test on Synchronous Flask</title>
    <script src="//cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    <script>
        async function poll(url) {
            const startTime = new Date().getTime();
            document.getElementById('status').innerHTML +=
                '<br>Sent request from the browser at: ' +
                new Date(startTime).toLocaleTimeString();
            try {
                const response = await axios.get(url);
                const endTime = new Date().getTime();
                document.getElementById('status').innerHTML +=
                    '<br>Received response in the browser at: ' +
                    new Date(endTime).toLocaleTimeString();
                document.getElementById('status').innerHTML +=
                    '<br>Data: ' + JSON.stringify(response.data) + '<br>';
            } catch (error) {
                console.error('Error during polling:', error);
                document.getElementById('status').innerHTML +=
                    '<br>Error during polling.';
            }
        }

        function startPolling() {
            poll('/poll');
        }
    </script>
</head>
<body onload="startPolling()">
    <h2>Long Polling Test on Synchronous Flask</h2>
    <div id="status">Polling status:</div>
</body>
</html>
"""


@app.route("/")
def home() -> str:
    """
    Renders the home page.

    Returns:
        str: The HTML content of the home page.
    """
    return render_template_string(INDEX_HTML)


@app.route('/poll')
def poll() -> Response:
    """
    Handles long polling requests.

    Returns:
        Response: JSON response with data or timeout status.
    """
    time_start: float = time.time()
    print('Polling started at:', time.strftime('%Y-%m-%d %H:%M:%S',
          time.localtime(time_start)))
    data: dict = {}
    while not data:
        data = get_data()
        if time.time() - time_start > app.config['LONGPOLL_TIMEOUT']:
            return jsonify({'status': 'No new data'})
    print('Polling ended at:', time.strftime('%Y-%m-%d %H:%M:%S',
          time.localtime(time.time())))
    return jsonify(data)


def get_data() -> dict:
    """
    Simulates data retrieval with a random delay.

    Returns:
        dict: Retrieved data or an empty dict if no data is available.
    """
    processing_start: float = time.time()
    wait_time: int = random.randint(5, 10)  # Determine wait time
    time.sleep(wait_time)  # Simulate delay
    if random.random() > 0.1:  # 90% chance to return data
        processing_start_str = time.strftime('%Y-%m-%d %H:%M:%S',
                                             time.localtime(processing_start))
        processing_end_str = time.strftime('%Y-%m-%d %H:%M:%S',
                                           time.localtime(time.time()))
        return {
            'data': 'Sample data',
            'elapsed_time': wait_time,
            'processing_start': processing_start_str,
            'processing_end': processing_end_str
        }
    else:
        return {}
