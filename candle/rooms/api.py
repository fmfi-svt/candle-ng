from flask import Blueprint, request

from candle.rooms.search import get_room, search_rooms

rooms = Blueprint("rooms", __name__, url_prefix="/rooms")


@rooms.route("/")
def listing():
    rooms = search_rooms(request.args.get("q"))
    return [t.to_dict() for t in rooms]


@rooms.route("/<slug>/")
def detail(slug):
    room = get_room(slug).to_dict()
    # TODO: add lessons
    return room
