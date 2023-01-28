'''
Project: Candle (New Generation): Candle rewrite from PHP to Python.
Author: Daniel Grohol, FMFI UK
'''

from typing import Dict
from flask import render_template, Blueprint

from candle.models import StudentGroup
from candle.timetable.blueprints.readonly import register_timetable_routes

student_group = Blueprint('student_group',
                          __name__,
                          template_folder='templates', url_prefix='/kruzky')


@student_group.route('')
def list_student_groups():
    """Show all student groups."""
    groups_list = StudentGroup.query.order_by(StudentGroup.name).all()
    student_groups_dict = get_student_groups_sorted_by_first_letter(groups_list)
    title = "Rozvrhy krúžkov"
    return render_template('student_group/list_student_groups.html', student_groups_dict=student_groups_dict,
                           title=title, web_header=title)


def get_group(group_url_id: str) -> StudentGroup:
    if group_url_id.isnumeric():
        student_group = StudentGroup.query.filter_by(id_=group_url_id).first_or_404()
    else:
        student_group = StudentGroup.query.filter_by(name=group_url_id).first_or_404()
    return student_group


register_timetable_routes(student_group, get_group)


def get_student_groups_sorted_by_first_letter(student_groups) -> Dict:
    """Return student-groups in a dictionary sorted by the first letter."""
    result_dict = {}
    for group in student_groups:
        first_letter = group.name[0]
        if first_letter not in result_dict:
            result_dict[first_letter] = []
        result_dict[first_letter].append(group)
    return result_dict
