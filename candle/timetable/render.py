from flask import render_template
from flask_login import current_user

from candle.models import Lesson, Subject
from candle.timetable.layout import Layout


def render_timetable(title, lessons, editable=True, **kwargs):
    lessons = lessons.join(Subject).order_by(Lesson.day, Lesson.start, Subject.name).all()
    t = Layout(lessons)

    if current_user.is_authenticated:
        my_timetables = current_user.timetables
    else:
        my_timetables = None
    return render_template('timetable/timetable.html', title=title,
                           web_header=title, timetable=t,
                           my_timetables=my_timetables,
                           show_welcome=False,
                           editable=editable, **kwargs)
