"""
Sample server.

"""

from flask import Flask

app = Flask(__name__)


@app.route("/")
def king_mufasa():
    """
    Landing page.

    :return:
    """

    return "<p>A True King Searches for What He Can Give!</p> <p> Mufasa(c)</p>"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
