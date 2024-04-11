from flask import Flask, request, abort
import stripe
from typing import Any, Dict, Optional
import os
from typing import Tuple

app: Flask = Flask(__name__)

# Determine the environment and load the appropriate configuration
if os.getenv('FLASK_ENV') == 'production':
    app.config.from_object('config.ProdConfig')
elif os.getenv('FLASK_ENV') == 'testing':
    app.config.from_object('config.TestConfig')
else:
    app.config.from_object('config.BaseConfig')


@app.route('/api/webhook', methods=['POST'])
def stripe_webhook() -> Tuple[str, int]:
    """
    Handles incoming webhook events from Stripe.

    This function processes webhook events by verifying the event signature,
    parsing the event payload, and then handling the event if it is a
    recognized type. It supports 'payment_intent.succeeded' and
    'charge.refunded' event types.

    Returns:
        Tuple[str, int]: A tuple containing the response message and status
                         code.
    """
    payload: str = request.get_data(as_text=True)
    sig_header: Optional[str] = request.headers.get('Stripe-Signature')
    endpoint_secret: Optional[str] = os.getenv('STRIPE_WEBHOOK_SECRET')

    if sig_header is None or endpoint_secret is None:
        app.logger.error('Missing necessary headers or configuration.')
        abort(400)

    try:
        event: Dict[str, Any] = stripe.Webhook.construct_event(
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
    if event['type'] == 'payment_intent.succeeded':
        payment_intent: Dict[str, Any] = event['data']['object']
        handle_payment_success(payment_intent)
    elif event['type'] == 'charge.refunded':
        refund: Dict[str, Any] = event['data']['object']
        handle_refund(refund)
    else:
        app.logger.error(f'Unhandled event type: {event["type"]}')
        abort(400)

    return 'Success', 200


def handle_payment_success(payment_intent: Dict[str, Any]) -> None:
    """
    Handles successful payment intents.

    This function is called when a payment intent succeeds. It logs the
    success and contains a placeholder for further logic to handle
    successful payments.

    Args:
        payment_intent (Dict[str, Any]): The payment intent object from the
                                         Stripe event.
    """
    print('Payment was successful.')
    # logic to handle successful payment


def handle_refund(refund: Dict[str, Any]) -> None:
    """
    Handles refunded charges.

    This function is called when a charge is refunded. It logs the refund
    and contains a placeholder for further logic to handle refunds.

    Args:
        refund (Dict[str, Any]): The refund object from the Stripe event.
    """
    print('Refund processed.')
    # logic to handle refund


if __name__ == '__main__':
    app.run(port=4242)
