import os
import requests
from flask import Flask, jsonify, request, render_template
from datetime import datetime

app = Flask(__name__)

class Charge:
    def __init__(self, id: str, amount: int, currency: str, status: str):
        self.id = id
        self.amount = amount
        self.currency = currency
        self.status = status
        
@app.route('/')
def index():
    return render_template('charge.html')

@app.route('/create_charge', methods=['POST'])
def create_charge():
    start = datetime.now()

    data = request.get_json()
    token = data['token']
    amount = data['amount']
    currency = data['currency']
    print(amount)
    print(currency)

    try:
        response = requests.post(
            'https://api.stripe.com/v1/charges',
            auth=('sk_test_51P0xYPDCswokx5t0NuOCsGpcYv3HE7yOZ7fcjnPskO4uo1BcvWTqttBoUBnWjj5wXVmeJdHVOTfoZeQEKEGzg98300mEppeWg2', ''),
            data={
                'source': token,
                'amount': amount,
                'currency': currency
            },
            timeout=5
        )
        print(response.json())
        response.raise_for_status()  # Raises stored HTTPError, if one occurred
    except requests.exceptions.RequestException as err:
        # Handle timeouts, connection errors, etc.
        return jsonify(error=str(err)), 500

    data = response.json()
    charge = Charge(
        id=data['id'],
        amount=data['amount'],
        currency=data['currency'],
        status=data['status']
    )

    latency = datetime.now() - start

    print(f"Returning charge ID: {charge.id} with latency: {latency.total_seconds()} seconds")
    return jsonify(id=charge.__dict__['id'], latency=latency.total_seconds())
  
if __name__ == '__main__':
    app.run()
