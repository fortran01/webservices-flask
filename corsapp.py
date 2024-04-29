from flask import Flask, Response, Request, abort, jsonify, request
from typing import Dict

app: Flask = Flask(__name__)

POSTS: Dict[str, Dict[str, str]] = {
    '1': {'post': 'This is the first blog post.'},
    '2': {'post': 'This is the second blog post.'},
    '3': {'post': 'This is the third blog post.'}
}


def is_preflight(request: Request) -> bool:
    """
    Determine if the incoming request is a CORS preflight request by examining
    the method and headers.

    Args:
        request (Request): The Flask request object.

    Returns:
        bool: True if the request is a preflight request, otherwise False.
    """
    is_http_options: bool = request.method == 'OPTIONS'
    has_origin_header: bool = 'Origin' in request.headers
    has_request_method: bool = (
        'Access-Control-Request-Method' in request.headers
    )
    return is_http_options and has_origin_header and has_request_method


@app.after_request
def handle_cors(response: Response) -> Response:
    """
    Modify the response to include CORS headers and handle preflight requests
    appropriately.

    Args:
        response (Response): The Flask response object to be modified.

    Returns:
        Response: The modified response object with added CORS headers.
    """
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    if is_preflight(request):
        response.headers['Access-Control-Allow-Methods'] = 'GET, DELETE'
        response.headers['Access-Control-Allow-Headers'] = (
            'Timezone-Offset, Sample-Source'
        )
        response.headers['Access-Control-Max-Age'] = '120'
        response.headers['Access-Control-Expose-Headers'] = 'X-Powered-By'
        response.status_code = 204
    return response


@app.route('/api/posts', methods=['GET'])
def get_posts() -> Response:
    """
    Retrieve all blog posts and return them as a JSON response.

    Returns:
        Response: A JSON response containing all blog posts.
    """
    return jsonify(POSTS)


@app.route('/api/posts/<post_id>', methods=['DELETE'])
def delete_post(post_id: str) -> Response:
    """
    Delete a specific blog post by its ID if the requester is the owner.

    Args:
        post_id (str): The ID of the blog post to delete.

    Returns:
        Response: An appropriate response depending on the outcome
                  (success, not found, or forbidden).
    """
    if request.cookies.get('username') == 'owner':
        if post_id in POSTS:
            del POSTS[post_id]
            return Response(status=204)
        else:
            abort(404)
    else:
        return Response(status=403)


if __name__ == '__main__':
    SERVER_PORT: int = 9999
    app.run(host='127.0.0.1', port=SERVER_PORT)
