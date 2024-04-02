from flask import Flask, Response

app: Flask = Flask(__name__)

@app.route("/")
def hello_world() -> Response:
    return Response("<p>Hello, World!</p>")
