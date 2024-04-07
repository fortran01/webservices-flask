"""
sync.py: A synchronous version of the charge service using the Stripe API.
"""

import os
import requests
from flask import Flask, jsonify, request, render_template
from datetime import datetime
from config import BaseConfig, ProdConfig, TestConfig

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
    A class to represent a charge.

    Attributes:
        id (str): The unique identifier for the charge.
        amount (int): The amount of the charge.
        currency (str): The currency of the charge.
        status (str): The status of the charge.
    """
    def __init__(self, id: str, amount: int, currency: str,
                 status: str) -> None:
        """
        Initializes a new instance of the Charge class.

        Parameters:
            id (str): The unique identifier for the charge.
            amount (int): The amount of the charge.
            currency (str): The currency of the charge.
            status (str): The status of the charge.
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
        str: The HTML content of the main page.
    """
    return render_template('charge.html')


@app.route('/create_charge', methods=['POST'])
def create_charge() -> tuple:
    """
    Creates a charge with Stripe API. Returns charge details and latency.

    Returns:
        tuple: JSON response with charge details, HTTP status code.
    """
    start: datetime = datetime.now()
    data: dict = request.get_json()
    token: str = data['token']
    amount: int = data['amount']
    currency: str = data['currency']
    # Get the Stripe API key from the environment variable
    stripe_api_key: str = os.getenv('STRIPE_API_KEY')

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
        if 'error' in err.response.json():
            error_message = err.response.json().get('error').get('message', '')
            return (jsonify(error=f"Failed to create charge: {error_message}"),
                    err.response.status_code)
        else:
            return (jsonify(error="Failed to create charge: An internal error "
                            "occurred"), 500)
    data: dict = response.json()
    charge: Charge = Charge(
        id=data['id'],
        amount=data['amount'],
        currency=data['currency'],
        status=data['status']
    )

    latency: datetime.timedelta = datetime.now() - start

    return jsonify(id=charge.__dict__['id'], latency=latency.total_seconds())


if __name__ == '__main__':
    app.run()
