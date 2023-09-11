from candle.groups.models import StudentGroup
from flask_sqlalchemy.query import Query


def search_groups(query: str|None) -> Query:
    groups = StudentGroup.query.order_by(StudentGroup.name)
    if query:
        groups = groups.filter(StudentGroup.name.ilike(f"%{query}%"))
    return groups

