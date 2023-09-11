from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

from candle import db
from candle.models import UserTimetable
from flask_wtf.csrf import CSRFError

common = Blueprint('common', __name__, template_folder="templates",
                static_folder='static',
                static_url_path='/common/static')


@common.route('/')
def home():
    if current_user.is_authenticated:
        my_timetables = current_user.timetables
        # if the user doesn't have any timetable:
        if my_timetables.first() is None:
            # create a new one:
            ut = UserTimetable(name='Rozvrh', user_id=current_user.id)
            db.session.add(ut)
            db.session.commit()
        else:
            # select the latest one (with the highest id):
            ut = my_timetables.order_by(UserTimetable.id_)[-1]
        # redirect to user's timetable view:
        return redirect(url_for('my_timetable.show_timetable', id_=ut.id_) )
    else:  # user is logged out, show welcome-info:
        return render_template('timetable/timetable.html', title='Rozvrh', show_welcome=True)


@common.app_errorhandler(404)
def error_404(error):
    return render_template('errors/404.html'), 404


@common.app_errorhandler(403)
def error_403(error):
    return render_template('errors/403.html'), 403


@common.app_errorhandler(500)
def error_500(error):
    return render_template('errors/500.html'), 500


@common.app_errorhandler(CSRFError)
def csrf_error(reason):
    return render_template('errors/csrf_error.html', reason=reason.description), 400
