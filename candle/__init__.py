"""
Project: Candle (New Generation): Candle rewrite from PHP to Python.
Author: Daniel Grohol
"""

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from candle.config import Config

login_manager = LoginManager()  # keeps session data
login_manager.login_view = "auth.login"
# login_manager.login_message_category = 'info'
# ^ flash message category (not yet implemented)

# We need CSRF protection for our AJAX calls.
# More info: https://stackoverflow.com/questions/31888316/how-to-use-flask-wtforms-csrf-protection-with-ajax
csrf = CSRFProtect()
db = SQLAlchemy()
debug_toolbar = DebugToolbarExtension()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.config.from_object(config_class)

    init_extensions(app)
    register_blueprints(app)
    return app


def register_blueprints(app):
    from candle.api import create_api
    from candle.auth.auth import auth
    from candle.common.frontend import common
    from candle.groups.frontend import groups
    from candle.my_timetable.my_timetable import my_timetable
    from candle.panel.panel import panel
    from candle.rooms.frontend import rooms
    from candle.search.search import search
    from candle.subjects.frontend import subjects
    from candle.teachers.frontend import teachers
    from candle.timetable.timetable import timetable

    app.register_blueprint(auth)
    app.register_blueprint(timetable)
    app.register_blueprint(my_timetable)
    app.register_blueprint(panel)
    app.register_blueprint(search)

    api = create_api()
    app.register_blueprint(api)

    app.register_blueprint(common)
    app.register_blueprint(rooms)
    app.register_blueprint(groups)
    app.register_blueprint(subjects)
    app.register_blueprint(teachers)


def init_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    debug_toolbar.init_app(app)

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.add_extension("jinja2.ext.loopcontrols")
    app.jinja_env.add_extension("jinja2.ext.do")
