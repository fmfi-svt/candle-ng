"""
Project: Candle (New Generation): Candle rewrite from PHP to Python.
Author: Daniel Grohol, FMFI UK
"""

from functools import wraps

from flask import Blueprint, current_app, flash, redirect, request, url_for
from flask_login import login_user, logout_user

from candle import db
from candle.models import User

auth = Blueprint("auth", __name__)


def require_remote_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_app.config["DEBUG"]:
            request.environ.setdefault("REMOTE_USER", "svttest")
        else:
            if request.environ.get("REMOTE_USER") is None:
                flash("User not logged in", "error")
                return redirect(url_for("common.home"))
        return func(*args, **kwargs)

    return wrapper


@auth.route("/prihlasit")
@require_remote_user
def login():
    ais_login = request.environ.get("REMOTE_USER")
    user = User.query.filter_by(login=ais_login).first()
    if not user:
        # vytvori takeho uzivatela v DB:
        user = User(login=ais_login)
        db.session.add(user)
        db.session.commit()
        # flash('Prihlasenie bolo neuspesne.')

    login_user(user, remember=True)
    return redirect(url_for("common.home"))


@auth.route("/odhlasit")
@require_remote_user
def logout():
    logout_user()
    return redirect(url_for("common.home"))
