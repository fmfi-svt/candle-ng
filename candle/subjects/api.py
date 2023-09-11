from flask import Blueprint, request

from candle.subjects.search import search_subjects, get_subject

subjects = Blueprint('subjects', __name__, url_prefix='/subjects')


@subjects.route("/")
def listing():
    subjects = search_subjects(request.args.get("q"))
    return [s.to_dict() for s in subjects]


@subjects.route("/<slug>/")
def detail(slug):
    subject = get_subject(slug).to_dict()
    # TODO: add lessons
    return subject
