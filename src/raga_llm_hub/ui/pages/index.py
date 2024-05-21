import json
import math
from threading import Thread

from flask import Blueprint, abort, render_template, request
from jinja2 import TemplateNotFound
from pyngrok import ngrok
from pyngrok.ngrok import PyngrokConfig

from ..helpers import (
    get_test_for_test_run_id,
    get_test_name_for_test_run_id,
    group_by_data_point_id,
    kill_ngrok,
    IN_COLAB,
)


def index_page_creator(
    fileName: str, session_id: str, pyngrok_config: PyngrokConfig
) -> Blueprint:
    index_page = Blueprint("index_page", __name__, template_folder="templates")

    @index_page.route("/")
    def page():
        if IN_COLAB:
            if request.args.get("id") != session_id:
                abort(404)

        f = open(fileName)
        results = json.load(f)

        # region pagination related code
        page = request.args.get("page", 0, int)
        size = request.args.get("size", len(results), int)
        offset = page * size
        total_pages = 0 if len(results) == 0 else math.ceil(len(results) / size)
        target_results = results[offset : offset + size]
        # endregion

        groups = group_by_test_run_id(target_results)
        if IN_COLAB:
            # kill tunnel
            thread = Thread(target=kill_ngrok, args=[pyngrok_config])
            thread.start()

        try:
            return render_template(
                "index.html",
                target_results=json.dumps(group_by_data_point_id(target_results)),
                total_elements=len(target_results),
                total_pages=total_pages,
                current_page=page,
                uniq_tests=groups,
                count_of_key=count_of_key_creator("is_passed"),
                get_test_for_test_run_id=get_test_for_test_run_id,
                get_test_name_for_test_run_id=get_test_name_for_test_run_id,
                max=max,
                min=min,
            )
        except TemplateNotFound:
            abort(404)

    return index_page


def group_by_test_run_id(results: list):
    groups = {}
    for result in results:
        test_run_id = result.get("test_run_id")
        if test_run_id not in groups:
            groups[test_run_id] = []
        groups[test_run_id].append(result)
    return groups


def count_of_key_creator(key: str):
    def count_of_key(arr: list, value):
        count = 0
        for a in arr:
            if a.get(key) == value:
                count += 1
        return count

    return count_of_key
