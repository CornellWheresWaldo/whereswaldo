from db import db, User, DailyWaldo, WaldoHint, WaldoFound, Leaderboard
from flask import Flask, request
import json
import secrets
import os

app = Flask(__name__)
db_filename = 'waldo.db'

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

db.init_app(app)
with app.app_context():
    db.create_all()

#success response
def success(data, code=200):
    return json.dumps(data), code


#error response
def failure(data, code=404):
    return json.dumps({"error": data}), code

#auth routes


#user routes


#waldo routes


#leaderboard routes


#admin routes