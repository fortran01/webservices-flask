from flask import Flask, Response, stream_with_context, render_template_string
import time
from typing import Generator

app: Flask = Flask(__name__)

SSE_HTML: str = """
<!DOCTYPE html>
<html>
<head>
    <title>SSE Example</title>
    <script>
        if (!!window.EventSource) {
            var source;
            var reconnectAttempts = 0;
            var connect = function() {
                source = new EventSource('/events');

                source.onmessage = function(e) {
                    var dataDiv = document.getElementById('data');
                    dataDiv.innerHTML += e.data + '<br>';
                    // reset reconnect attempts on successful message
                    reconnectAttempts = 0;
                    var attemptsDiv = document.getElementById('reconnect-attempts');
                    attemptsDiv.innerHTML = 'Reconnect attempts: ' + reconnectAttempts;
                };

                source.onerror = function(error) {
                    console.error("EventSource failed:", error);
                    source.close();
                    reconnectAttempts++;
                    var attemptsDiv = document.getElementById('reconnect-attempts');
                    attemptsDiv.innerHTML = 'Reconnect attempts: ' + reconnectAttempts;
                    setTimeout(connect, 5000);
                };
            };
            connect();
        } else {
            console.log("Browser doesn't support SSE. Consider upgrading.");
        }
    </script>
</head>
<body>
    <h1>Server Sent Events (SSE) Example</h1>
    <div id="data"></div>
    <div id="reconnect-attempts">Reconnect attempts: 0</div>
</body>
</html>
"""


def event_stream() -> Generator[str, None, None]:
    """
    A generator function that simulates a delay and yields a count
    incrementally.

    Yields:
        str: A server-sent event formatted string containing the current count.
    """
    count: int = 0
    while True:
        time.sleep(1)  # Simulate a delay
        count += 1
        yield f"data: {{'count': {count}}}\n\n"


@app.route('/')
def index() -> str:
    """
    Renders the home page with SSE example.

    Returns:
        str: The HTML content of the SSE example page.
    """
    return render_template_string(SSE_HTML)


@app.route('/events')
def sse_request() -> Response:
    """
    Handles server-sent event requests by streaming the event_stream generator.

    Returns:
        Response: A Flask Response object configured for server-sent events.
    """
    return Response(
        stream_with_context(event_stream()),
        content_type='text/event-stream'
    )
