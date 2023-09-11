from candle import db
from candle.models import SchoolTimetable


class Room(SchoolTimetable):
    id_ = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String(30), nullable=False)
    room_type_id = db.Column(db.Integer, db.ForeignKey('room_type.id'), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    lessons = db.relationship('Lesson', backref='room',
                              lazy='dynamic')  # 'lazy dynamic' allows us to work with lessons attribute like with query ( we can run order_by, etc)

    @property
    def prefix(self):
        # xMieRez is a special case:
        if 'xMieRez' in self.name:
            return "Ostatné"

        first_dash_position = self.name.find('-')
        if first_dash_position == -1:  # name doesn't contain '-'
            return self.name
        return self.name[0 : first_dash_position]

    def __repr__(self):
        return "<Room %r>" % self.name

    @property
    def timetable_name(self) -> str:
        return self.name

    def to_dict(self):
        return {
            "id": self.id_,
            "name": self.name,
            "capacity": self.capacity,
        }


class RoomType(db.Model):
    id_ = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    code = db.Column(db.String(1), nullable=False)
