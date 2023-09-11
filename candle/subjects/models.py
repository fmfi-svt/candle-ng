from candle import db
from candle.models import SchoolTimetable


class Subject(SchoolTimetable):
    id_ = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    short_code = db.Column(db.String(20), nullable=False)
    credit_value = db.Column(db.Integer, nullable=False)
    rozsah = db.Column(db.String(30), nullable=True)
    external_id = db.Column(db.String(30), nullable=True)
    lessons = db.relationship('Lesson', backref='subject', lazy='dynamic')

    def __repr__(self):
        return f"Subject(id:'{self.id_}', name:'{self.name}' )"

    def __str__(self):
        if self.short_code:
            return f"{self.short_code} - {self.name}"
        return self.name

    def to_dict(self) -> dict:
        """
        Returns the Subject as dict for JSON rendering.
        """
        return {
            "id": self.id_,
            "name": self.name,
            "shortcode": self.short_code,
            "code": self.code,
        }

    @property
    def timetable_name(self) -> str:
        return self.name

    @property
    def url_id(self):
        if self.short_code:
            return self.short_code
        return self.id_
