"""
Bot Server

"""
from flask import Flask, request, jsonify, make_response
import json
import logging
from datetime import datetime, timezone

# Configure a basic logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)


class BotServer:
    """
    Flask based
    """

    def __init__(self):
        pass

    @staticmethod
    @app.route('/', methods=['GET'])
    def hello_world():
        return 'Server is running!', 200

    @staticmethod
    @app.route('/health-check', methods=['GET'])
    def health_check():
        return 'Server is running!', 200

    @staticmethod
    @app.route('/ticket', methods=['POST'])
    def handle_ticket():
        """
        Route to echo back the received JSON data

        :return:
        """

        try:
            content_type = request.content_type

            if content_type == 'application/json':
                data = request.json
            elif 'application/x-www-form-urlencoded' in content_type:
                data = request.form
            else:
                logger.warning(f"Received unsupported Content-Type: {content_type}")
                return jsonify(
                    {"error": "Content-Type must be application/json or application/x-www-form-urlencoded"}), 415

            if not data:
                logger.error("Received POST request with no data.")
                return jsonify({"error": "No data provided"}), 400

            # Log the received data
            timestamp = datetime.now(timezone.utc).isoformat()
            logger.info(f"Received ticket at {timestamp}: {json.dumps(data)}")

            # Create a response that echoes back the received data
            response_data = {
                "received_timestamp": timestamp,
                "echo": data
            }

            # Return the response as JSON
            return jsonify(response_data), 200

        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}")
            return jsonify({"error": "Internal Server Error"}), 500

    def start(self):
        """
        Start the server.
        :return:
        """
        app.run(host='0.0.0.0', port=8080, debug=True)


if __name__ == '__main__':
    # Running the Flask app
    # host='0.0.0.0' makes the server accessible from outside localhost
    # debug=True enables the debugger
    app.run(host='0.0.0.0', port=8080, debug=True)

