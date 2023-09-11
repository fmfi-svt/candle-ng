from candle import db
from candle.models import SchoolTimetable

student_group_lessons = db.Table(
    "student_group_lessons",
    db.Column("student_group_id", db.Integer, db.ForeignKey("student_group.id")),
    db.Column("lesson_id", db.Integer, db.ForeignKey("lesson.id")),
)


class StudentGroup(SchoolTimetable):
    id_ = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    lessons = db.relationship("Lesson", secondary=student_group_lessons, lazy="dynamic")

    def __str__(self):
        return self.name

    @property
    def timetable_name(self) -> str:
        return f"Rozvh krúžku {self.name}"

    @property
    def timetable_short_name(self) -> str:
        return self.name

    def to_dict(self):
        return {
            "id": self.id_,
            "name": self.name,
        }
