'''
Project: Candle (New Generation): Candle rewrite from PHP to Python.
Author: Daniel Grohol, FMFI UK
'''

from flask import Blueprint, request, url_for, jsonify, render_template, abort
from flask_login import current_user, login_required
import re
from candle import db
from candle.models import UserTimetable, Teacher, Room, StudentGroup, Lesson, Subject
from candle.timetable.export import export_timetable_as
from candle.timetable.layout import Layout, TooManyColumnsError
from candle.timetable.render import render_timetable

my_timetable = Blueprint('my_timetable',
                         __name__,
                         static_folder='static',
                         static_url_path='/my_timetable/static')


def get_timetable(id_):
    id_ = int(id_)
    return current_user.timetables.filter(UserTimetable.id_ == id_).first_or_404()

@my_timetable.route('/moj-rozvrh/<id_>')
@login_required
def show_timetable(id_):
    ut = get_timetable(id_)
    return render_timetable(ut.name, ut.lessons, selected_timetable_key=int(id_))


@my_timetable.route('/moj-rozvrh', methods=['POST'])
@login_required
def new_timetable():
    """Create a new timetable"""
    name = request.form['name']
    name = getUniqueName(name)
    ut = UserTimetable(name=name, user_id=current_user.id)
    db.session.add(ut)
    db.session.commit()
    return url_for("my_timetable.show_timetable", id_=ut.id_)


@my_timetable.route('/moj-rozvrh/<id_>.<format>')
@login_required
def export_my_timetable(id_, format):
    """Exports users timetable"""
    return export_timetable_as(format, get_timetable(id_).lessons)


@login_required
@my_timetable.route("/ucitelia/<teacher_slug>/duplicate", methods=['POST'])
def duplicate_teacher_timetable(teacher_slug):
    old_timetable = Teacher.query.filter_by(slug=teacher_slug).first_or_404()
    new_timetable_id = duplicate_timetable(old_timetable)
    return jsonify({'next_url': url_for("my_timetable.show_timetable", id_=new_timetable_id)})

@login_required
@my_timetable.route("/miestnosti/<room_url_id>/duplicate", methods=['POST'])
def duplicate_room_timetable(room_url_id):
    old_timetable = Room.query.filter_by(name=room_url_id).first_or_404()
    new_timetable_id = duplicate_timetable(old_timetable)
    return jsonify({'next_url': url_for("my_timetable.show_timetable", id_=new_timetable_id)})

@login_required
@my_timetable.route("/kruzky/<group_url_id>/duplicate", methods=['POST'])
def duplicate_student_group_timetable(group_url_id):
    old_timetable = StudentGroup.query.filter_by(name=group_url_id).first_or_404()
    new_timetable_id = duplicate_timetable(old_timetable)
    return jsonify({'next_url': url_for("my_timetable.show_timetable", id_=new_timetable_id)})

@login_required
@my_timetable.route("/moj-rozvrh/<id_>/duplicate", methods=['POST'])
def duplicate_my_timetable(id_):
    old_timetable = UserTimetable.query.get_or_404(id_)
    new_timetable_id = duplicate_timetable(old_timetable)
    return jsonify({'next_url': url_for("my_timetable.show_timetable", id_=new_timetable_id)})


def duplicate_timetable(old_timetable):
    """Create a new timetable as a duplicate of old one and return its id."""
    if isinstance(old_timetable, Teacher):
        old_name = old_timetable.short_name
    else:
        old_name = old_timetable.name
    new_name = getUniqueName(old_name)
    new_t = UserTimetable(name=new_name, user_id=current_user.id)
    db.session.add(new_t)
    for lesson in old_timetable.lessons:
        new_t.lessons.append(lesson)
    db.session.commit()
    return new_t.id_



def getUniqueName(name) -> str:
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


@login_required
@my_timetable.route("/moj-rozvrh/<id_>/delete", methods=['DELETE'])
def delete_timetable(id_):
    ut = get_timetable(id_)
    db.session.delete(ut)
    db.session.commit()

    # if there is no timetable left, create a new one:
    if len(list(current_user.timetables)) == 0:
        new_ut = UserTimetable(name="Rozvrh", user_id=current_user.id)
        db.session.add(new_ut)
        db.session.commit()
        timetable_to_show_id = new_ut.id_
    else:
        # id of last added timetable:
        timetable_to_show_id = current_user.timetables.order_by(UserTimetable.id_)[-1].id_
    return jsonify({'next_url': url_for("my_timetable.show_timetable", id_=timetable_to_show_id)})



@login_required
@my_timetable.route("/moj-rozvrh/<id_>/rename", methods=['PUT'])
def rename_timetable(id_):
    new_name = request.form['new_name']
    new_name = getUniqueName(new_name)
    ut = get_timetable(id_)
    ut.name = new_name
    db.session.commit()

    # render new parts of the webpage:
    tabs_html = render_template("timetable/tabs.html", my_timetables=current_user.timetables, selected_timetable_key=ut.id_, title=ut.name)
    web_header_html = f"<h1>{ut.name}</h1>"
    title_html = render_template('main/title.html', title=ut.name)

    return jsonify({'tabs_html': tabs_html,
                    'web_header_html': web_header_html,
                    'title': ut.name,
                    'title_html': title_html})



@login_required
@my_timetable.route('/moj-rozvrh/<timetable_id>/lesson/<lesson_id>/<action>', methods=['POST'])
def add_or_remove_lesson(timetable_id, lesson_id, action):
    """Add or remove lesson to/from the timetable."""
    ut = get_timetable(timetable_id)
    lesson = Lesson.query.get_or_404(lesson_id)

    if action == 'add':
        ut.lessons.append(lesson)
    elif action == 'remove':
        ut.lessons.remove(lesson)
    else:
        raise Exception("Bad route format! There should be either 'add' or 'remove' action in the URL!")
    db.session.commit()
    try:
        t = Layout(lessons=ut.lessons.order_by(Lesson.day, Lesson.start).all())
    except TooManyColumnsError:
        return jsonify({'success': False})

    timetable_layout = render_template('timetable/timetable_content.html', timetable=t)
    timetable_list = render_template('timetable/list.html', timetable=t)

    return jsonify({'success': True,
                    'layout_html': timetable_layout,
                    'list_html': timetable_list})


@login_required
@my_timetable.route('/moj-rozvrh/<timetable_id>/subject/<subject_id>/<action>', methods=['POST'])
def add_or_remove_subject(timetable_id, subject_id, action):
    """Add/Remove subject (with all lessons) to/from user's timetable. Return timetable templates (layout & list)."""
    ut = get_timetable(timetable_id)
    subject = Subject.query.get_or_404(subject_id)

    if action == 'add':
        for l in subject.lessons:
            if l not in ut.lessons:
                ut.lessons.append(l)
    elif action == 'remove':
        for l in subject.lessons:
            ut.lessons.remove(l)
    else:
        raise Exception("Bad route format! There should be either 'add' or 'remove' action in the URL!")
    db.session.commit()
    t = Layout(lessons=ut.lessons.order_by(Lesson.day, Lesson.start).all())

    timetable_layout = render_template('timetable/timetable_content.html', timetable=t)
    timetable_list = render_template('timetable/list.html', timetable=t)

    return jsonify({'layout_html': timetable_layout,
                    'list_html': timetable_list})
