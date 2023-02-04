'''
Project: Candle (New Generation): Candle rewrite from PHP to Python.
Author: Daniel Grohol, FMFI UK
'''

from flask import Blueprint, render_template

from typing import Dict
from candle.models import Teacher, Subject
from candle.entities.helpers import string_starts_with_ch
import unidecode

from candle.timetable.blueprints.readonly import register_timetable_routes

subject = Blueprint('subject',
                    __name__,
                    template_folder='templates', url_prefix='/predmety')


@subject.route('')
def list_teachers():
    """Show all teachers in the list."""
    subject_list = Subject.query.order_by(Subject.short_code).all()
    title = "Zoznam predmetov"
    return render_template('subject/list.html', subjects=subject_list, title=title,
                           web_header=title)


def get_subject(slug: str) -> Subject:
    return Subject.query.filter(Subject.short_code == slug).first_or_404()


register_timetable_routes(subject, get_subject)
