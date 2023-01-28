'''
Project: Candle (New Generation): Candle rewrite from PHP to Python.
Author: Daniel Grohol, FMFI UK
'''

import os
from datetime import date

from dotenv import load_dotenv


# load .env file where environment variables are stored:
basedir = os.path.abspath(os.path.dirname(__file__))
ENV_FILE_PATH = os.path.join(basedir, '../.env')
if os.path.exists(ENV_FILE_PATH) == False:
    raise FileNotFoundError('.env file is missing. Check README.md for the instructions how to create one.')
load_dotenv(ENV_FILE_PATH)


class Config:
    DEBUG = os.environ.get("FLASK_DEBUG", False)
    TESTING = False
    CSRF_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("""No SQLALCHEMY_DATABASE_URI set for Flask application. 
                            Check README.md for the instructions how to create .env file 
                            and store your SQLALCHEMY_DATABASE_URI there.""")

    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError("""No SECRET_KEY set for Flask application. 
                            Check README.md for the instructions how to create .env file
                            and store your SECRET_KEY there.""")

    # app.config['SQLALCHEMY_ECHO'] = True    # show queries, that runs "in background"
    # TODO: real values
    CANDLE_SEMESTER = "2022-2023-zima"
    CANDLE_SEMESTER_START = date(2022, 1, 5)
    CANDLE_SEMESTER_END = date(2022, 12, 31)


class ProductionConfig(Config):
    ...

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    DEBUG = True
