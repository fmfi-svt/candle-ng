from flask import Blueprint, render_template, request

from typing import Dict
from candle.utils import string_starts_with_ch
import unidecode

from candle.teachers.search import search_teachers, get_teacher
from candle.timetable.blueprints.readonly import register_timetable_routes

teachers = Blueprint('teachers', __name__, template_folder='templates', url_prefix='/teachers')


@teachers.route('/')
def listing():
    """Show all teachers in the list."""
    teachers_list = search_teachers(request.args.get("q"))
    teachers_dict = get_teachers_sorted_by_family_name(teachers_list)
    title = "Rozvrhy učiteľov"
    return render_template('teachers/listing.html', teachers_dict=teachers_dict, title=title,
                           web_header=title)


register_timetable_routes(teachers, get_teacher)


def get_teachers_sorted_by_family_name(teachers) -> Dict:
    """Return a dictionary that contains teachers sorted by the first letter of the family_name.

    input: list of objects of model Teacher sorted by the family_name
    output: dictionary (string: List[Teacher]), where the key is the first letter of family_name
    and values are objects of model Teacher
    """
    d = {}
    others = []  # special category
    for teacher in teachers:
        if teacher.family_name is None or teacher.family_name == '':
            continue

        first_letter = (teacher.family_name[0])
        if first_letter.isalpha() == False:  # some names starts with dot '.', or forwardslash '/', (etc.)
            others.append(teacher)
            continue
        first_letter = unidecode.unidecode(first_letter)  # get rid of diacritics  (Č change to C)
        if string_starts_with_ch(teacher.family_name):  # family_name that starts on a "CH" is a special category
            first_letter = 'Ch'
        if first_letter not in d:
            d[first_letter] = []
        d[first_letter].append(teacher)
    d['Ostatné'] = others

    return d
