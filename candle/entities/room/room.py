'''
Project: Candle (New Generation): Candle rewrite from PHP to Python.
Author: Daniel Grohol, FMFI UK
'''

from flask import render_template, Blueprint
from candle.models import Room
from typing import Dict

from candle.timetable.blueprints.readonly import register_timetable_routes

room = Blueprint('room',
                 __name__,
                 template_folder='templates', url_prefix="/miestnosti")


@room.route('')
def list_rooms():
    """Show all rooms."""
    rooms_list = Room.query.order_by(Room.name).all()
    rooms_dict = get_rooms_sorted_by_dashes(rooms_list)  # rooms are in the dictionary sorted by prefix
    title = "Rozvrhy miestností"
    return render_template('room/list_rooms.html', rooms_dict=rooms_dict, title=title,
                           web_header=title)


def get_room(room_url_id: str) -> Room:
    if room_url_id.isnumeric():
        return Room.query.filter_by(id_=room_url_id).first_or_404()
    return Room.query.filter_by(name=room_url_id).first_or_404()


register_timetable_routes(room, get_room)


def get_rooms_sorted_by_dashes(rooms_lst) -> Dict:
    """
    Return OrderedDict that contains rooms sorted by categories.

    The key in the OrderedDict is always the room prefix and the values are rooms (objects of model Room)
     (For example'F1-108' has prefix 'F1').

    :parameter rooms_lst: The list of the Room model objects.
    :return OrderedDict (dict of str: list), where key is the prefix and the value is a list of Rooms.
    """
    d = {}
    for room in rooms_lst:
        url_id = room.url_id
        if url_id == " ":   # we have one room with empty name (" ")
            continue
        prefix = room.prefix

        # insert data into dictionary:
        if prefix not in d:
            d[prefix] = []
        d[prefix].append(room)
    return d
