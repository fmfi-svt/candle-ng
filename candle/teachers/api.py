from flask import Blueprint, request

from candle.teachers.search import search_teachers, get_teacher

teachers = Blueprint('teachers', __name__, url_prefix='/teachers')


@teachers.route("/")
def listing():
    teachers = search_teachers(request.args.get("q"))
    return [t.to_dict() for t in teachers]


@teachers.route("/<slug>/")
def detail(slug):
    teacher = get_teacher(slug).to_dict()
    # TODO: add lessons
    return teacher
