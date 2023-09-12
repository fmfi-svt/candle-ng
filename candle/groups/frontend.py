from typing import Dict

from flask import Blueprint, render_template, request

from candle.groups.search import get_group, search_groups
from candle.timetable.blueprints.readonly import register_timetable_routes

groups = Blueprint(
    "groups", __name__, template_folder="templates", url_prefix="/groups"
)


@groups.route("/")
def listing():
    """Show all student groups."""
    groups_list = search_groups(request.args.get("q"))
    student_groups_dict = get_student_groups_sorted_by_first_letter(groups_list)
    title = "Rozvrhy krúžkov"
    return render_template(
        "groups/listing.html",
        student_groups_dict=student_groups_dict,
        title=title,
        web_header=title,
    )


register_timetable_routes(groups, get_group)


def get_student_groups_sorted_by_first_letter(student_groups) -> Dict:
    """Return student-groups in a dictionary sorted by the first letter."""
    result_dict = {}
    for group in student_groups:
        first_letter = group.name[0]
        if first_letter not in result_dict:
            result_dict[first_letter] = []
        result_dict[first_letter].append(group)
    return result_dict
