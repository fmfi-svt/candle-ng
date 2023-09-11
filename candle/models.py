'''
Project: Candle (New Generation): Candle rewrite from PHP to Python.
Author: Daniel Grohol, FMFI UK
'''

from typing import Union

from flask_login import UserMixin

from candle import db, login_manager
from candle.timetable.layout import Layout


class SchoolTimetable(db.Model):
    """Abstract class for Room, Student-Group and Teacher."""
    __abstract__ = True

    @property
    def url_id(self) -> Union[str, int]:
        if '.' in self.name or '_' in self.name:     # TODO add more problematic characters if necessary
            return self.id_
        return self.name

    @property
    def timetable_name(self) -> str:
        raise NotImplementedError()

    @property
    def timetable_short_name(self) -> str:
        return self.timetable_name

    @property
    def lessons(self):
        raise NotImplementedError()


class Lesson(db.Model):
    id_ = db.Column('id', db.Integer, primary_key=True)
    day = db.Column(db.Integer, nullable=False)
    start = db.Column(db.Integer, nullable=False)
    end = db.Column(db.Integer, nullable=False)
    lesson_type_id = db.Column(db.Integer, db.ForeignKey('lesson_type.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    external_id = db.Column(db.Integer, nullable=True)
    note = db.Column(db.VARCHAR, nullable=True)

    def __repr__(self):
        return f"Lesson(id:'{self.id_}', room_id:'{self.room_id}' )"

    @property
    def day_abbreviated(self) -> str:
        """Returns abbreviation of the day of the week."""
        days = ['Po', 'Ut', 'St', 'Št', 'Pi']
        return days[self.day]

    @property
    def start_formatted(self):
        return Layout.minutes_2_time(self.start)

    @property
    def end_formatted(self):
        return Layout.minutes_2_time(self.end)

    @property
    def breaktime(self) -> int:
        hours_count = self.rowspan
        return int(Layout.get_shortest_breaktime() * hours_count)

    @property
    def rowspan(self) -> int:
        """Return how many rows takes lesson in the timetable."""
        return (self.end - self.start) // Layout.get_shortest_lesson()

    def get_teachers_formatted(self) -> str:
        """ Return teachers separated by commas.
        E.g.: "A. Blaho, D. Bezáková, A. Hrušecká"
        """
        return ', '.join([t.short_name for t in self.teachers])

    def get_note(self) -> str:
        return self.note if self.note else ""


    def to_dict(self) -> dict:
        """
        Returns the Lesson as dict for JSON rendering.
        """

        return {
            "id": self.id_,
            "day": self.day_abbreviated,
            "start": self.start_formatted,
            "end": self.end_formatted,
            "type": self.type.code,
            "room": self.room.name,
            "subject": self.subject.to_dict(),
            "teachers": [t.short_name for t in self.teachers],
            "note": self.get_note(),
        }

class LessonType(db.Model):
    id_ = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    code = db.Column(db.String(1), nullable=False)
    lessons = db.relationship('Lesson', backref='type', lazy=True)

    def __repr__(self):
        return self.name


user_timetable_lessons = db.Table('user_timetable_lessons',
                                  db.Column('id', db.Integer(), primary_key=True),
                                  db.Column('user_timetable_id', db.Integer, db.ForeignKey('user_timetable.id')),
                                  db.Column('lesson_id', db.Integer, db.ForeignKey('lesson.id')),
                                  db.Column('highlighted', db.Boolean, default=False))


class UserTimetable(db.Model):
    id_ = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    published = db.Column(db.Integer, default=0)
    slug = db.Column(db.String(30))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    lessons = db.relationship('Lesson',
                              secondary=user_timetable_lessons,
                              backref=db.backref('user_timetable', lazy='joined'),
                              lazy='dynamic')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True)
    timetables = db.relationship('UserTimetable', backref='owner', lazy='dynamic')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


######################################################
# TODO:
@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'
