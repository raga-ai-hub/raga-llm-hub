import json
import logging
import sys

from flask import Flask

from .helpers import killport
from .pages.index import index_page_creator
from .pages.trace import trace_page_creator

PORT = 8888


def launch_app(results: list):
    try:
        killport(PORT)
    except:
        pass
    logging.getLogger("werkzeug").setLevel(logging.WARN)
    cli = sys.modules["flask.cli"]
    cli.show_server_banner = lambda *x: None
    app = Flask(__name__, static_url_path="")

    app.register_blueprint(index_page_creator({"results": results}))
    app.register_blueprint(trace_page_creator({"results": results}))
    print(f"raga-llm-hub:ui running on: http://127.0.0.1:{PORT}")
    app.run(host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    results = []
    with open("results.json") as f:
        results = json.loads(f.read())
