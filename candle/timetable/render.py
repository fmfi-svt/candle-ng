from flask import render_template
from flask_login import current_user
from sqlalchemy.orm import joinedload, contains_eager

from candle import db
from candle.models import Lesson, Subject, Room, LessonType
from candle.timetable.layout import Layout


def render_timetable(title, lessons, editable=True, **kwargs):
    lessons = lessons.join(Lesson.subject).options(joinedload(Lesson.room), joinedload(Lesson.type),
                                                   joinedload(Lesson.teachers),
                                                   contains_eager(Lesson.subject)).order_by(Lesson.day, Lesson.start,
                                                                                            Subject.name).all()
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
