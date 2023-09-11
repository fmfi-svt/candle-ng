from sqlalchemy.ext.hybrid import hybrid_property

from candle import db
from candle.models import SchoolTimetable

teacher_lessons = db.Table(
    "teacher_lessons",
    db.Column("id", db.Integer, primary_key=True),
    db.Column("teacher_id", db.Integer, db.ForeignKey("teacher.id")),
    db.Column("lesson_id", db.Integer, db.ForeignKey("lesson.id")),
)


class Teacher(SchoolTimetable):
    id_ = db.Column("id", db.Integer, primary_key=True)
    given_name = db.Column(db.String(50), nullable=True)
    family_name = db.Column(db.String(50), nullable=False)
    iniciala = db.Column(db.String(50), nullable=True)
    oddelenie = db.Column(db.String(), nullable=True)
    katedra = db.Column(db.String(), nullable=True)
    external_id = db.Column(db.String(), nullable=True)
    login = db.Column(db.String(), nullable=True)
    slug = db.Column(db.String(), nullable=True)
    lessons = db.relationship(
        "Lesson",
        secondary=teacher_lessons,
        lazy="dynamic",
        backref=db.backref(
            "teachers", lazy="joined", order_by="asc(Teacher.family_name)"
        ),
    )

    def __repr__(self):
        return f"Teacher(id:'{self.id_}', :'{self.given_name} {self.family_name}' )"

    def __str__(self):
        return self.fullname

    @property
    def short_name(self):
        """E.g. for 'Andrej Blaho' return 'A. Blaho'"""
        if self.given_name is None or self.given_name.strip() == "":
            return self.family_name
        return self.given_name[0] + ". " + self.family_name

    @hybrid_property
    def fullname(self):
        return self.given_name + " " + self.family_name

    @hybrid_property  # we need it in SQL queries
    def fullname_reversed(self):
        return self.family_name + " " + self.given_name

    @property
    def timetable_name(self) -> str:
        return self.fullname

    @property
    def timetable_short_name(self) -> str:
        return self.short_name

    def to_dict(self):
        return {
            "id": self.id_,
            "given_name": self.given_name,
            "family_name": self.family_name,
            "department": self.katedra,
            "login": self.login,
            "slug": self.slug,
        }

    @property
    def url_id(self):
        if self.slug:
            return self.slug
        return self.id_
