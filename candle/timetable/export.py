import csv
import io
import json
from datetime import datetime, timedelta, date, time
from xml.etree import ElementTree
from zoneinfo import ZoneInfo

from flask import make_response, abort, current_app
from icalendar import Calendar, Event

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
    if format == "ics":
        return _to_ics(layout)
    if format == "xml":
        return _to_xml(layout)
    if format == "txt":
        return _to_txt(layout)
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


def _to_txt(layout: Layout):
    rows = []

    for lesson in layout.get_lessons():
        row = [lesson.day_abbreviated, f"{lesson.start_formatted} - {lesson.end_formatted}",
               f"({lesson.rowspan} v.hod.)", lesson.room.name, lesson.type.name, lesson.subject.short_code,
               lesson.subject.name, lesson.get_note(), lesson.get_teachers_formatted()]
        rows.append("\t".join(row))

    response = make_response("\n".join(rows))
    response.mimetype = "text/plain"
    return response


def _to_ics(layout: Layout):
    cal = Calendar()
    cal.add('prodid', '-//Candle-NG//NONSGML candle.fmph.uniba.sk//')
    cal.add('version', '2.0')

    tz = ZoneInfo("Europe/Bratislava")
    semester_start: date = current_app.config["CANDLE_SEMESTER_START"]
    semester_end: date = current_app.config["CANDLE_SEMESTER_END"]
    semester = current_app.config["CANDLE_SEMESTER"]

    for lesson in layout.get_lessons():
        event = Event()
        event.add("uid", f"{semester}-{lesson.id_}@candle.fmph.uniba.sk")

        day = semester_start + timedelta(days=(lesson.day - semester_start.weekday()) % 7)
        start = datetime.combine(day, time(lesson.start // 60, lesson.start % 60), tz)
        end = datetime.combine(day, time(lesson.end // 60, lesson.end % 60), tz)

        event.add("dtstamp", start)
        event.add("dtstart", start)
        event.add("dtend", end)
        event.add("summary", lesson.subject.name)
        event.add("location", lesson.room.name)

        description = [lesson.type.name]
        if lesson.note:
            description.append(lesson.note)
        description.extend(["", lesson.get_teachers_formatted()])
        event.add("description", "\n".join(description))
        event.add("rrule", {"freq": "weekly", "until": semester_end})

        cal.add_component(event)

    response = make_response(cal.to_ical())
    response.mimetype = "text/calendar"
    return response


def _to_xml(layout: Layout):
    root = ElementTree.Element("timetable", version="1.0")

    for lesson in layout.get_lessons():
        lesson_elem = ElementTree.SubElement(root, "lesson", id=str(lesson.id_))
        elem = ElementTree.SubElement(lesson_elem, "type")
        elem.text = lesson.type.name

        elem = ElementTree.SubElement(lesson_elem, "room")
        elem.text = lesson.room.name

        elem = ElementTree.SubElement(lesson_elem, "subject", shortcode=lesson.subject.short_code)
        elem.text = lesson.subject.name

        elem = ElementTree.SubElement(lesson_elem, "day")
        elem.text = lesson.day_abbreviated

        elem = ElementTree.SubElement(lesson_elem, "start")
        elem.text = lesson.start_formatted

        elem = ElementTree.SubElement(lesson_elem, "end")
        elem.text = lesson.end_formatted

        for teacher in lesson.teachers:
            elem = ElementTree.SubElement(lesson_elem, "teacher")
            elem.text = teacher.short_name

        if lesson.note:
            elem = ElementTree.SubElement(lesson_elem, "note")
            elem.text = lesson.note

    response = make_response(ElementTree.tostring(root))
    response.mimetype = "application/xml"
    return response
