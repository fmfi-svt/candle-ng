from flask import Blueprint, request

from candle.groups.search import get_group, search_groups

groups = Blueprint("groups", __name__, url_prefix="/groups")


@groups.route("/")
def listing():
    groups = search_groups(request.args.get("q"))
    return [t.to_dict() for t in groups]


@groups.route("/<slug>/")
def detail(slug):
    group = get_group(slug).to_dict()
    # TODO: add lessons
    return group
