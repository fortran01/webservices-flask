from flask import Flask, jsonify, request, render_template, Response, abort
from flask_socketio import SocketIO
import requests
import os
import stripe
from typing import Dict, Any, Tuple, Union
from datetime import datetime, timedelta

# Initialize Flask app and Flask-SocketIO
app: Flask = Flask(__name__)
socketio: SocketIO = SocketIO(app)

# Load configurations based on the environment
if os.getenv('FLASK_ENV') == 'production':
    app.config.from_object('config.ProdConfig')
elif os.getenv('FLASK_ENV') == 'testing':
    app.config.from_object('config.TestConfig')
else:
    app.config.from_object('config.BaseConfig')


@app.route('/')
def index() -> str:
    """
    Renders the index page of the application.

    Returns:
        str: The HTML content of the index page.
    """
    return render_template('index.html')


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
        self.id = id
        self.amount = amount
        self.currency = currency
        self.status = status


@app.route('/api/create_charge', methods=['POST'])
def create_charge() -> Tuple[Response, int]:
    """
    Creates a Stripe charge, returning details and latency.

    Returns:
        Tuple[Response, int]: Returns JSON (charge or error) and status code.
    """
    start: datetime = datetime.now()
    data: Dict[str, Any] = request.get_json()
    token: str = data['token']
    amount: int = data['amount']
    currency: str = data['currency']
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

    charge_data: Dict[str, Any] = response.json()
    charge: Charge = Charge(
        id=charge_data['id'],
        amount=charge_data['amount'],
        currency=charge_data['currency'],
        status=charge_data['status']
    )

    latency: timedelta = datetime.now() - start
    socketio.emit('charge_status', {
                  'status': 'pending', 'charge': charge_data, 'timestamp': datetime.now().isoformat()})

    return jsonify(id=charge.id, latency=latency.total_seconds()), 200


@app.route('/api/webhook', methods=['POST'])
def stripe_webhook() -> Tuple[str, int]:
    """
    Handles Stripe webhook events.

    Returns:
        Tuple[str, int]: A tuple containing the response message and the
        HTTP status code.
    """
    payload: str = request.get_data(as_text=True)
    sig_header: Union[str, None] = request.headers.get('Stripe-Signature')
    # Runtime checks validate types against runtime values.
    endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    if not isinstance(endpoint_secret, str):
        raise TypeError(
            "Expected a string for endpoint_secret, got None instead.")

    if sig_header is None or endpoint_secret is None:
        app.logger.error('Missing necessary headers or configuration.')
        abort(400)

    # Initialize event to an empty dict to ensure it's always bound
    event: Dict[str, Any] = {}
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Log invalid payload error
        app.logger.error(f'Invalid payload: {e}')
        abort(400)
    except stripe.error.SignatureVerificationError as e:  # type: ignore
        # Log invalid signature error
        app.logger.error(f'Invalid signature: {e}')
        abort(400)

    # Handle the event
    if event and event['type'] == 'payment_intent.succeeded':
        payment_intent: Dict[str, Any] = event['data']['object']
        socketio.emit('payment_intent', {
                      'status': 'succeeded', 'payment_intent': payment_intent, 'timestamp': datetime.now().isoformat()})
    elif event and event['type'] == 'charge.refunded':
        refund: Dict[str, Any] = event['data']['object']
        socketio.emit('charge_status', {
                      'status': 'refunded', 'refund': refund, 'timestamp': datetime.now().isoformat()})
    elif event and event['type'] == 'charge.succeeded':
        charge: Dict[str, Any] = event['data']['object']
        socketio.emit('charge_status', {
                      'status': 'succeeded', 'charge': charge, 'timestamp': datetime.now().isoformat()})
    else:
        app.logger.error(
            f'Unhandled event type: {event.get("type", "Unknown")}')
        abort(400)

    return 'Success', 200


if __name__ == '__main__':
    # use_reloader is set to True to automatically reload the server
    # when changes are made to the code for development purposes
    socketio.run(app, debug=True, use_reloader=True, log_output=True)
