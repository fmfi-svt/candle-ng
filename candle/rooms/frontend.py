from flask import Blueprint, render_template, request

from candle.rooms.search import search_rooms, get_rooms_sorted_by_dashes, get_room
from candle.timetable.blueprints.readonly import register_timetable_routes

rooms = Blueprint('rooms', __name__, url_prefix="/rooms", template_folder="templates")


@rooms.route("/")
def listing():
    room_list = search_rooms(request.args.get("q"))
    rooms_dict = get_rooms_sorted_by_dashes(room_list)  # rooms are in the dictionary sorted by prefix
    title = "Rozvrhy miestností"
    return render_template('rooms/listing.html', rooms_dict=rooms_dict, title=title,
                           web_header=title)


register_timetable_routes(rooms, get_room)
