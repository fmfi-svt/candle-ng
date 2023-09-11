from flask_sqlalchemy.query import Query

from candle.teachers.models import Teacher


def search_teachers(query: str|None) -> Query:
    teachers = Teacher.query.order_by(Teacher.family_name, Teacher.given_name)
    if query:
        teachers = teachers.filter(Teacher.fullname.ilike(f"%{query}%") | Teacher.fullname_reversed.ilike(f"%{query}%"))
    return teachers
