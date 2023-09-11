from typing import Callable

from flask import Blueprint, jsonify, url_for
from flask_login import login_required

from candle.models import SchoolTimetable
from candle.timetable.export import export_timetable_as
from candle.timetable.render import render_timetable
from candle.timetable.utils import duplicate_timetable


def register_timetable_routes(bp: Blueprint, getter: Callable[[str], SchoolTimetable]):
    @bp.route("/<slug>/")
    def show_timetable(slug):
        """Shows a timetable."""
        obj = getter(slug)
        return render_timetable(
            title=obj.timetable_name, lessons=obj.lessons, editable=False
        )

    @bp.route("/<slug>.<format>")
    def export_timetable(slug, format):
        """Exports a timetable."""
        obj = getter(slug)
        return export_timetable_as(format, obj.lessons)

    @login_required
    @bp.route("/<slug>/duplicate/", methods=["POST"])
    def duplicate(slug):
        new_timetable_id = duplicate_timetable(getter(slug))
        return jsonify(
            {"next_url": url_for("my_timetable.show_timetable", id_=new_timetable_id)}
        )
