import os
import requests
from flask import Flask, jsonify, request, render_template
from datetime import datetime

app: Flask = Flask(__name__)

class Charge:
    def __init__(self, id: str, amount: int, currency: str, status: str) -> None:
        self.id: str = id
        self.amount: int = amount
        self.currency: str = currency
        self.status: str = status
        
@app.route('/')
def index() -> str:
    return render_template('charge.html')

@app.route('/create_charge', methods=['POST'])
def create_charge() -> tuple:
    start: datetime = datetime.now()

    data: dict = request.get_json()
    token: str = data['token']
    amount: int = data['amount']
    currency: str = data['currency']

    try:
        response: requests.Response = requests.post(
            'https://api.stripe.com/v1/charges',
            auth=('sk_test_51P0xYPDCswokx5t0NuOCsGpcYv3HE7yOZ7fcjnPskO4uo1BcvWTqttBoUBnWjj5wXVmeJdHVOTfoZeQEKEGzg98300mEppeWg2', ''),
            data={
                'source': token,
                'amount': amount,
                'currency': currency
            },
            timeout=5
        )
        response.raise_for_status()  # Raises stored HTTPError, if one occurred
    except requests.exceptions.RequestException as err:
        # Handle timeouts, connection errors, etc.
        return jsonify(error=str(err)), 500

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
