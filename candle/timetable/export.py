import csv
import io
import json

from flask import make_response, abort

from candle.models import Subject, Lesson
from candle.timetable.layout import Layout


def export_timetable(format, lessons):
    lessons = lessons.join(Subject).order_by(Lesson.day, Lesson.start, Subject.name).all()
    layout = Layout(lessons)

    if format == "csv":
        return _to_csv(layout)
    if format == "json":
        return _to_json(layout)
    if format == "list":
        return _to_list(layout)
    abort(404)


def _to_csv(layout: Layout):
    buffer = io.StringIO()
    w = csv.writer(buffer, delimiter=";")
    w.writerow(layout.get_list_headers())

    for lesson in layout.get_lessons():
        w.writerow([
            lesson.day_abbreviated, lesson.start_formatted, lesson.end_formatted, lesson.room.name,
            lesson.type, lesson.subject.short_code, lesson.subject.name,
            lesson.get_teachers_formatted(), lesson.get_note(),
        ])

    buffer.seek(0)
    response = make_response(buffer)
    response.mimetype = 'text/csv'
    return response


def _to_json(layout: Layout):
    data = []

    for lesson in layout.get_lessons():
        data.append(lesson.to_dict())

    response = make_response(json.dumps(data))
    response.mimetype = 'application/json'
    return response


def _to_list(layout: Layout):
    subjects = set()

    for lesson in layout.get_lessons():
        subjects.add(lesson.subject.short_code)

    response = make_response("\n".join(subjects))
    response.mimetype = "text/plain"
    return response
