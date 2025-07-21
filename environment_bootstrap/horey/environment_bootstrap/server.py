from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

# Configure basic logging for the Flask app
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']) # Catches root path
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']) # Catches all paths and common HTTP methods
def print_headers(path):
    """
    Endpoint to print all received HTTP headers, request method, and path.
    """
    logger.info(f"Received {request.method} request to path: /{path} from IP: {request.remote_addr}")

    received_headers = {}
    for header_name, header_value in request.headers:
        received_headers[header_name] = header_value
        logger.info(f"  Header: {header_name}: {header_value}")

    # Optionally, print the raw request body for POST/PUT/PATCH requests
    request_body = None
    if request.method in ['POST', 'PUT', 'PATCH']:
        try:
            request_body = request.data.decode('utf-8', errors='ignore')
            logger.info(f"  Request Body (raw): {request_body}...")
        except Exception as e:
            logger.warning(f"Could not decode request body: {e}")
            request_body = "[Could not decode body]"

    response_data = {
        "message": "Headers and request details received successfully!",
        "request_method": request.method,
        "request_path": f"/{path}",
        "source_ip": request.remote_addr,
        "received_headers": received_headers,
        "received_body_preview": request_body if request_body else "[No body for this method or empty]"
    }

    return jsonify(response_data), 200


if __name__ == '__main__':
    # Run the Flask app in debug mode
    # host='0.0.0.0' makes it accessible from outside localhost (e.g., from other containers)
    # port=5000 is the default Flask port
    logger.info("Flask app starting. Listening for requests on http://0.0.0.0:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)