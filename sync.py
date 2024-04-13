"""
sync.py: A synchronous version of the charge service using the Stripe API.
"""

import os
import requests
from flask import Flask, jsonify, request, render_template, Response
from datetime import datetime, timedelta
from config import BaseConfig, ProdConfig, TestConfig
from typing import Tuple, Union

app: Flask = Flask(__name__)

# Determine the environment and load the appropriate configuration
if os.getenv('FLASK_ENV') == 'production':
    app.config.from_object(ProdConfig)
elif os.getenv('FLASK_ENV') == 'testing':
    app.config.from_object(TestConfig)
else:
    app.config.from_object(BaseConfig)


class Charge:
    """
    Represents a charge in the context of the Stripe API.

    Attributes:
        id (str): Unique identifier for the charge.
        amount (int): Amount of the charge.
        currency (str): Currency of the charge.
        status (str): Status of the charge.
    """

    def __init__(self, id: str, amount: int, currency: str,
                 status: str) -> None:
        """
        Initializes a new Charge instance.

        Parameters:
            id (str): Unique identifier for the charge.
            amount (int): Amount of the charge.
            currency (str): Currency of the charge.
            status (str): Status of the charge.
        """
        self.id: str = id
        self.amount: int = amount
        self.currency: str = currency
        self.status: str = status


@app.route('/')
def index() -> str:
    """
    Renders the main page of the application.

    Returns:
        str: HTML content of the main page.
    """
    return render_template('charge.html')


@app.route('/api/create_charge', methods=['POST'])
def create_charge() -> Tuple[Response, int]:
    """
    Creates a Stripe charge, returning details and latency.

    Returns:
        Tuple[Response, int]: Returns JSON (charge or error) and status code.
    """
    start: datetime = datetime.now()
    data: dict = request.get_json()
    token: str = data['token']
    amount: int = data['amount']
    currency: str = data['currency']
    # Get the Stripe API key from the environment variable
    stripe_api_key: Union[str, None] = os.getenv('STRIPE_API_KEY')

    if stripe_api_key is None:
        return jsonify(error="Stripe API key not found"), 500

    try:
        response: requests.Response = requests.post(
            'https://api.stripe.com/v1/charges',
            auth=(stripe_api_key, ''),
            data={
                'source': token,
                'amount': amount,
                'currency': currency
            },
            timeout=app.config['REQUEST_TIMEOUT']
        )
        response.raise_for_status()  # Raises stored HTTPError, if one occurred
    except requests.exceptions.RequestException as err:
        error_message = "Failed to create charge: An internal error occurred."
        if err.response is not None and 'error' in err.response.json():
            error_json = err.response.json().get('error')
            error_message = error_json.get('message', error_message)
        return jsonify(error=error_message), 500

    data: dict = response.json()
    charge: Charge = Charge(
        id=data['id'],
        amount=data['amount'],
        currency=data['currency'],
        status=data['status']
    )

    latency: timedelta = datetime.now() - start

    return jsonify(id=charge.id, latency=latency.total_seconds()), 200


if __name__ == '__main__':
    app.run()
