from flask_sqlalchemy.query import Query

from candle.subjects.models import Subject


def search_subjects(query: str|None) -> Query:
    subjects = Subject.query.order_by(Subject.short_code)
    if query:
        subjects = subjects.filter(Subject.name.ilike(f"%{query}%") | Subject.short_code.ilike(f"%{query}%"))
    return subjects


def get_subject(slug: str) -> Subject:
    return Subject.query.filter((Subject.short_code == slug) | (Subject.id_ == slug)).first_or_404()
