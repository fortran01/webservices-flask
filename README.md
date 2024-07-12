# webservices-flask

This project demonstrates various Flask web services, including Stripe payment processing, webhook handling, long polling, SSE, websockets, and more.

## Features

- **Stripe Payment Processing**: A synchronous service that creates Stripe charges.
- **Stripe Webhook Handling**: Receives and processes Stripe webhook events.
- **Long Polling**: Implements long polling to simulate real-time data fetching.
- **Server-Sent Events (SSE)**: Implements Server-Sent Events to push data to the client.
- **WebSockets**: Implements WebSockets to push data to the client.
- **Task Queue**: Demonstrates how to use a task queue to process long-running tasks asynchronously.
- **CORs**: Implements CORs to allow cross-origin requests.

## Endpoints

- **Stripe Payment Processing**: `POST /api/create_charge`
- **Stripe Webhook Handling**: `POST /api/webhook`
- **Long Polling**: `GET /api/poll` and the home page at `GET /`
- **Server-Sent Events (SSE)**: `GET /api/sse`
- **Task Queue**: `GET /api/fetch-github-data`

## Simple Frontend Demos

- /login.html - A simple login page that sets a secure cookie with the username and redirects to the client page.
- /client.html - A client-side application that fetches and displays blog posts, and allows deletion of posts with CORS support.
- /task.html - A client-side application that fetches GitHub data using a task queue.
- /charge.html - A client-side application that creates a Stripe charge.
- /index.html - A client-side application that demonstrates Stripe payment processing with real-time updates via WebSockets.

## Setup

- Clone the repository
- Create a virtual environment:

```bash
python3 -m venv venv
```

- Install dependencies:
  
```bash
pip install -r requirements.txt
```

## Running the Services

Activate the virtual environment:

```bash
. ./venv/bin/activate
```

Start the Flask server for a specific service:

```bash
flask --app [app_name] run
```

Replace `[app_name]` with `sync`, `webhook`, or `longpoll` depending on the service you want to run.

## Configuration

The project uses different configurations based on the Flask environment (`development`, `testing`, `production`). Configurations are defined in `config.py`.
