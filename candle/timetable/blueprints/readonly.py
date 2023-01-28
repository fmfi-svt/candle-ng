from typing import Callable

from flask import Blueprint

from candle.models import SchoolTimetable
from candle.timetable.export import export_timetable_as
from candle.timetable.render import render_timetable


def register_timetable_routes(bp: Blueprint, getter: Callable[[str], SchoolTimetable]):
    @bp.route('/<slug>')
    def show_timetable(slug):
        """Shows a timetable."""
        obj = getter(slug)
        return render_timetable(obj.timetable_name, obj.lessons, editable=False)

    @bp.route('/<slug>.<format>')
    def export_timetable(slug, format):
        """Exports a timetable."""
        obj = getter(slug)
        return export_timetable_as(format, obj.lessons)
