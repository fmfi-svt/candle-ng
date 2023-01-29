'''
Project: Candle (New Generation): Candle rewrite from PHP to Python.
Author: Daniel Grohol, FMFI UK
'''

from typing import Set

from flask import Blueprint, request, url_for, jsonify, render_template
from flask_login import current_user, login_required

from candle import db
from candle.models import (
    UserTimetable,
    Lesson,
    Subject,
    user_timetable_lessons,
)
from candle.timetable.export import export_timetable_as
from candle.timetable.layout import Layout, TooManyColumnsError
from candle.timetable.render import render_timetable
from candle.timetable.utils import duplicate_timetable, get_unique_name

my_timetable = Blueprint('my_timetable',
                         __name__,
                         static_folder='static',
                         static_url_path='/my_timetable/static')


def get_timetable(id_):
    id_ = int(id_)
    return current_user.timetables.filter(UserTimetable.id_ == id_).first_or_404()


def get_highlighted_lesson_ids(user_timetable_id: int) -> Set[int]:
    highlighted_user_timetable_lessons = db.session.query(
        user_timetable_lessons,
    ).filter(
        user_timetable_lessons.c.user_timetable_id == user_timetable_id,
        user_timetable_lessons.c.highlighted == True
    ).all()
    return {
        item._mapping["lesson_id"]
        for item in highlighted_user_timetable_lessons
    }


@my_timetable.route('/moj-rozvrh/<id_>')
@login_required
def show_timetable(id_):
    ut = get_timetable(id_)

    return render_timetable(
        title=ut.name,
        lessons=ut.lessons,
        highlighted_lesson_ids=get_highlighted_lesson_ids(ut.id_),
        selected_timetable_key=int(id_),
        editable=True,
    )


@my_timetable.route('/moj-rozvrh', methods=['POST'])
@login_required
def new_timetable():
    """Create a new timetable"""
    name = request.form['name']
    name = get_unique_name(name)
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
@my_timetable.route("/moj-rozvrh/<id_>/duplicate", methods=['POST'])
def duplicate_my_timetable(id_):
    old_timetable = UserTimetable.query.get_or_404(id_)
    new_timetable_id = duplicate_timetable(old_timetable)
    return jsonify({'next_url': url_for("my_timetable.show_timetable", id_=new_timetable_id)})



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
    new_name = get_unique_name(new_name)
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


def render_only_timetable(ut: UserTimetable):
    t = Layout(
        lessons=ut.lessons.order_by(Lesson.day, Lesson.start).all(),
        highlighted_lesson_ids=get_highlighted_lesson_ids(ut.id_),
    )
    timetable_layout = render_template('timetable/timetable_content.html', timetable=t)
    timetable_list = render_template('timetable/list.html', timetable=t)

    return jsonify(
        {
            'succes': True,
            'layout_html': timetable_layout,
            'list_html': timetable_list,
        }
    )


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
        raise ValueError("Bad route format! There should be either 'add' or 'remove' action in the URL!")

    try:
        result = render_only_timetable(ut)
        db.session.commit()
        return result
    except TooManyColumnsError:
        return jsonify({'success': False})


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

    try:
        result = render_only_timetable(ut)
        db.session.commit()
        return result
    except TooManyColumnsError:
        return jsonify({'success': False})


@login_required
@my_timetable.route("/moj-rozvrh/<timetable_id>/edit-lessons/<action>", methods=['POST'])
def edit_lessons(timetable_id, action):
    """Highlight/unhighlight/delete lessons in timetable"""
    data = request.json
    ut = get_timetable(timetable_id)

    if action in ("highlight", "unhighlight"):
        highlighted = action == "highlight"
        update_highlighted_statement = user_timetable_lessons.update().where(
            user_timetable_lessons.c.user_timetable_id == timetable_id,
            user_timetable_lessons.c.lesson_id.in_(data["lesson_ids"])
        ).values(highlighted=highlighted)
        db.session.execute(update_highlighted_statement)
    elif action == "remove":
        lessons = ut.lessons.filter(Lesson.id_.in_(data["lesson_ids"]))
        for l in lessons:
            ut.lessons.remove(l)
    else:
        raise ValueError("Unknown action!")

    db.session.commit()
    return render_only_timetable(ut)
