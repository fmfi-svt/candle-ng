import re

from candle import db
from candle.models import SchoolTimetable, UserTimetable
from flask_login import current_user


def get_unique_name(name) -> str:
    """Ensure that this timetable will not have the same name as some other one.
    :param name: name for timetable
    :return: unique name for timetable
    """
    pattern = '^(.*) \(\d+\)$'
    match = re.match(pattern, name)
    # if the name is in the format "Name (x)", where x is a number:
    if match:
        name = match.group(1)  # get the name before parenthesis (without a number)
    # get the names of the current timetables:
    timetables_names = [t.name for t in current_user.timetables]
    if name not in timetables_names:
        return name

    # add "(index)" after the name, and try if it is unique:
    index = 2
    while True:
        new_name = f"{name} ({index})"
        if new_name not in timetables_names:
            return new_name
        index += 1


def duplicate_timetable(old_timetable: SchoolTimetable):
    """Create a new timetable as a duplicate of old one and return its id."""
    new_name = get_unique_name(old_timetable.timetable_short_name)
    new_t = UserTimetable(name=new_name, user_id=current_user.id)
    db.session.add(new_t)
    for lesson in old_timetable.lessons:
        new_t.lessons.append(lesson)
    db.session.commit()
    return new_t.id_

