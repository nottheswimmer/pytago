import os

from flask import Flask, request
from flask_cors import CORS
from pytago.core import python_to_go

app = Flask(__name__)
cors = CORS(app)
html = None
port = os.environ.get("PORT", 8080)
print(f"localhost link: http://127.0.0.1:{port}")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        global html
        if html is None:
            try:
                # Local
                with open(os.path.join(app.instance_path.removesuffix("instance"), 'static', 'index.html')) as f:
                    html = f.read()
            except FileNotFoundError:
                # Docker
                with open(os.path.join(app.instance_path.removesuffix("instance"), 'pytago', 'static', 'index.html')) as f:
                    html = f.read()
        return html

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
    app.run(debug=True, host="0.0.0.0", port=int(port))
