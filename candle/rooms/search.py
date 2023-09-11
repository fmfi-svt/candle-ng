from typing import Iterable

from flask_sqlalchemy.query import Query

from candle.rooms.models import Room


def search_rooms(query: str | None) -> Query:
    rooms = Room.query.order_by(Room.name)
    if query:
        rooms = rooms.filter(Room.name.ilike(f"%{query}%"))
    return rooms


def get_rooms_sorted_by_dashes(rooms: Iterable[Room]) -> dict[str, list[Room]]:
    """
    Return OrderedDict that contains rooms sorted by categories.

    The key in the OrderedDict is always the room prefix and the values are rooms
     (For example'F1-108' has prefix 'F1').

    :parameter rooms: The list of the Room model objects.
    :return OrderedDict (dict of str: list), where key is the prefix and the value
    is a list of Rooms.
    """
    d = {}
    for room in rooms:
        url_id = room.url_id
        if url_id == " ":  # we have one room with empty name (" ")
            continue
        prefix = room.prefix

        # insert data into dictionary:
        if prefix not in d:
            d[prefix] = []
        d[prefix].append(room)
    return d


def get_room(slug: str) -> Room:
    return Room.query.filter((Room.id_ == slug) | (Room.name == slug)).first_or_404()
