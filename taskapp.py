from flask import Flask, jsonify, Response
from celery_config import make_celery
from flask_socketio import SocketIO
import requests
import time
import logging
from typing import Dict, List, Any

app: Flask = Flask(__name__, static_url_path='', static_folder='static')

# Configure Celery with Redis as the broker and backend
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379/0',
    RESULT_BACKEND='redis://localhost:6379/0'
)

# Initialize Celery
celery = make_celery(app)

# Initialize Flask-SocketIO with Redis as the message queue
# This approach allows the celery task to emit events to the client
socketio = SocketIO(app, message_queue='redis://localhost:6379/0')

# Set up logging
logging.basicConfig(level=logging.INFO)


@celery.task(bind=True)
def fetch_and_process_data(self) -> List[Dict[str, Any]]:
    """
    Fetches data from GitHub API and processes it.

    This task retrieves the top 100 starred GitHub repositories, simulates a
    lengthy process, and extracts the name and star count from each. The
    processed data is then broadcast via SocketIO.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing the 'name' and
        'stars' of each repository.
    """
    logging.info("Starting to fetch data from GitHub API.")
    # GitHub API endpoint for top 100 starred repositories
    url: str = ("https://api.github.com/search/repositories"
                "?q=stars:>1&sort=stars&order=desc&per_page=100")
    response = requests.get(
        url, headers={'Accept': 'application/vnd.github.v3+json'})
    data: Dict[str, Any] = response.json()
    repositories: List[Dict[str, Any]] = data['items']
    logging.info(f"Fetched {len(repositories)} repositories.")

    # Simulate a long-running process
    logging.info("Simulating a long-running process...")
    time.sleep(5)  # Artificial delay of 5 seconds
    logging.info("Simulation complete.")

    # Extract names and stars from repositories
    processed_data: List[Dict[str, Any]] = [
        {'name': repo['name'], 'stars': repo['stargazers_count']}
        for repo in repositories
    ]
    logging.info(
        "Data processing complete. Data processed for all repositories.")

    # Emit processed data via SocketIO
    socketio.emit('data_processed', {'data': processed_data})
    socketio.emit('task_completed', {'message': 'Data processing completed'})

    return processed_data


@app.route('/api/fetch-github-data', methods=['GET'])
def fetch_github_data() -> Response:
    """
    Initiates the asynchronous task to fetch and process GitHub data.

    This endpoint triggers the 'fetch_and_process_data' task and returns the
    task ID and status.

    Returns:
        Response: JSON response containing the task ID and the status of the
        task initiation.
    """
    task = fetch_and_process_data.delay()
    return jsonify({'task_id': task.id, 'status': 'Fetching GitHub data'})
