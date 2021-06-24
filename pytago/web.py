import os

from flask import Flask, request
from pytago.core import python_to_go

app = Flask(__name__)


@app.route("/", methods=["POST"])
def index():
    py = (request.get_json() or {}).get("py")
    if not py:
        return "Bad request", 400
    return python_to_go(py, app.debug)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
