import json
import uuid

import requests
from flask import Flask
from pyngrok import ngrok
from pyngrok.ngrok import PyngrokConfig

from .pages.index import index_page_creator
from .pages.trace import trace_page_creator
from .helpers import kill_ngrok, IN_COLAB
from waitress import serve
import os

PORT = os.getenv("RAGA_LLM_PORT", 5000)
FILENAME = "data.json"
TOKEN_URL = "https://raga-llm-store.s3.amazonaws.com/token/key.json"
DOMAIN = "ngrok.ragaai.ai"

auth_token = requests.get(TOKEN_URL).json().get("key")
pyngrok_config = PyngrokConfig(auth_token=auth_token)
session_id = str(uuid.uuid4())

app = Flask(__name__, static_url_path="")
app.register_blueprint(index_page_creator(FILENAME, session_id, pyngrok_config))
app.register_blueprint(trace_page_creator(FILENAME))

IS_LAUNCHED = False


def restart_ngrok(port):
    kill_ngrok(pyngrok_config)
    # Open a ngrok tunnel to the HTTP server
    return ngrok.connect(port, domain=DOMAIN, pyngrok_config=pyngrok_config).public_url


def get_public_url(port):
    if IN_COLAB:
        return restart_ngrok(port)
    else:
        return f"http://localhost:{port}"


def launch_app(results: list, port=PORT, *args, **kwargs):
    public_url = get_public_url(port)
    # Update any base URLs to use the public ngrok URL
    app.config["BASE_URL"] = public_url

    if IN_COLAB:
        public_url = f"{public_url}?id={session_id}"

    print(f"You can load the UI using {public_url}")

    with open(FILENAME, "w") as f:
        json.dump(results, f)

    global IS_LAUNCHED
    if not IS_LAUNCHED:
        from threading import Thread

        thread = Thread(target=lambda: serve(app, host="0.0.0.0", port=port))
        thread.start()
        if not IN_COLAB:
            thread.join()
        IS_LAUNCHED = True
    return


if __name__ == "__main__":
    results = []
    with open("results.json") as f:
        results = json.loads(f.read())

    launch_app(results)
