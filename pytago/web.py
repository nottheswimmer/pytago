import os

from flask import Flask, request
from flask_cors import CORS
from pytago.core import python_to_go

app = Flask(__name__)
cors = CORS(app)


@app.route("/", methods=["POST"])
def index():
    py = (request.get_json() or {}).get("py")
    if not py:
        return "Bad request", 400
    try:
        go = python_to_go(py, app.debug)
        return go
    except SyntaxError as e:
        import traceback
        tb = traceback.format_exc()
        lines = []
        seen_unknown = False
        for line in tb.splitlines():
            if '<unknown>' in line:
                seen_unknown = True
            if seen_unknown:
                lines.append(line)
        return '\n'.join(lines) or str(e)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
