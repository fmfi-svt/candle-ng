from flask import Blueprint


def get_error_handler(code, message):
    def fn(error):
        return {"error": message}, code

    return fn


def create_api():
    api = Blueprint("api", __name__, url_prefix="/api")

    from candle.groups.api import groups
    from candle.rooms.api import rooms
    from candle.subjects.api import subjects
    from candle.teachers.api import teachers

    api.register_blueprint(teachers)
    api.register_blueprint(subjects)
    api.register_blueprint(rooms)
    api.register_blueprint(groups)

    api.register_error_handler(404, get_error_handler(404, "Not found."))
    api.register_error_handler(403, get_error_handler(403, "Forbidden."))
    api.register_error_handler(500, get_error_handler(500, "Server error."))

    return api
