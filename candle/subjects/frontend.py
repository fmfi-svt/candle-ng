from flask import Blueprint, render_template, request

from candle.subjects.models import Subject
from candle.subjects.search import search_subjects
from candle.timetable.blueprints.readonly import register_timetable_routes

subjects = Blueprint('subjects',
                     __name__,
                     template_folder='templates', url_prefix='/subjects')


@subjects.route("/")
def listing():
    """Show all teachers in the list."""
    subject_list = search_subjects(request.args.get("q"))
    title = "Zoznam predmetov"
    return render_template('subjects/listing.html', subjects=subject_list, title=title,
                           web_header=title)


def get_subject(slug: str) -> Subject:
    return Subject.query.filter(Subject.short_code == slug).first_or_404()


register_timetable_routes(subjects, get_subject)
