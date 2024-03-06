import json
import math

from flask import Blueprint, abort, render_template, request
from jinja2 import TemplateNotFound

from ..helpers import (
    get_test_for_test_run_id,
    get_test_name_for_test_run_id,
    group_by_data_point_id,
    pick_matching_keys_from_dict,
)


def index_page_creator(context: dict):
    index_page = Blueprint("index_page", __name__, template_folder="templates")

    @index_page.route("/")
    def page():
        results = context.get("results")

        # region pagination related code
        page = request.args.get("page", 0, int)
        size = request.args.get("size", len(results), int)
        offset = page * size
        total_pages = 0 if len(results) == 0 else math.ceil(len(results) / size)
        target_results = results[offset : offset + size]
        # endregion

        groups = group_by_test_run_id(target_results)
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
