import os
import sys
import pathlib
import json

#from flask import Flask
import connexion
from connexion import FlaskApp

from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

class DatabaseConfiguration(object):
    """ Class to store DB configuration """
    def __init__(self,
                driver=f"{os.getenv('DB_DRIVER')}",     # export variables when not dockerized
                db=f"{os.getenv('DB_NAME')}",           #
                user=f"{os.getenv('DB_USER')}",         #
                password=f"{os.getenv('DB_PASSWORD')}", #
                host=f"{os.getenv('DB_HOST')}",         # "localhost" or "db", when dockerized
                echo=False
                ):
        """ Load configuration """
        self.driver = driver
        self.db = db
        self.user = user
        self.password = password
        self.host = host
        self.echo = echo

    def __repr__(self) -> str:
        """ Returns a representation for the instance,
        excluding password """
        return f"{type(self).__name__}(driver={self.driver},db={self.db},user={self.user},host={self.host})"

    def __uri__(self) -> str:
        """ Returns a representation for the instance,
        to be used in db methods """
        return f"{self.driver}://{self.user}:{self.password}@\{self.host}/{self.db}"


""" DatabaseConfiguration instance """
db_config = DatabaseConfiguration()


""" Start and configure Conex App """
#Resolve parent directory as basedir
basedir = pathlib.Path(__file__).parent.resolve()

#app = Flask(__name__)
api = connexion.FlaskApp(__name__)
app = api.app

app.config["SQLALCHEMY_DATABASE_URI"] = db_config.__uri__()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#app.config["STATIC_FOLDER"] = f"{os.getenv('APP_FOLDER')}/project/static"
app.config["STATIC_FOLDER"] = f"{basedir}/static"
app.config['SECRET_KEY'] = f"{os.getenv('SECRET_KEY')}"


""" Start SQLAlchemy and Marshmallow App's """
db = SQLAlchemy(app)
ma = Marshmallow(app)