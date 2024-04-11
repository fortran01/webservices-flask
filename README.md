# webservices-flask

This project demonstrates various Flask web services, including Stripe payment processing, webhook handling, and long polling.

## Features

- **Stripe Payment Processing**: A synchronous service that creates Stripe charges.
- **Stripe Webhook Handling**: Receives and processes Stripe webhook events.
- **Long Polling**: Implements long polling to simulate real-time data fetching.

## Setup

- Clone the repository
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

## Endpoints

- **Stripe Payment Processing**: `POST /create_charge`
- **Stripe Webhook Handling**: `POST /api/webhook`
- **Long Polling**: `GET /poll` and the home page at `GET /`
