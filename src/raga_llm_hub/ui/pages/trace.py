from flask import Blueprint, abort, render_template, request
from jinja2 import TemplateNotFound
from datetime import datetime

from ..helpers import group_by_data_point_id


def trace_page_creator(context: dict):
    trace_page = Blueprint("trace_page", __name__, template_folder="templates")

    @trace_page.route("/trace/<data_point_id>")
    def page(data_point_id):
        results = context.get("results")
        result = list(
            filter(
                lambda x: x.get("data_point_id") == data_point_id,
                group_by_data_point_id(results),
            )
        )[0]
        if result is None:
            abort(404)

        result = {
            "Trace": result.get("test_run_id"),
            "prompt": result.get("prompt", result.get("input")),
            "response": result.get("response"),
            "Ground Truth": result.get("expected_response"),
            "context": result.get("context"),
            "test_name": result.get("test_name"),
            "data_point_id": data_point_id,
            "dynamic": result.get("dynamic"),
        }
        try:
            return render_template(
                "trace.html", result=result, tests=result.get("dynamic")
            )
        except TemplateNotFound:
            abort(404)

    return trace_page
