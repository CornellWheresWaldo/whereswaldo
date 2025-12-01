from db import db, User, DailyWaldo, WaldoHint, WaldoFound, Leaderboard
from flask import Flask, request
from datetime import date
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

# generalized response formats
def success(data, code=200):
    return json.dumps(data), code

def failure(data, code=404):
    return json.dumps({"error": data}), code


# -- AUTH ROUTES ------------------------------------------------------


@app.route("/auth/register/", methods=["POST"])
def register_user():
    """
    Endpoint to register a new user with username, email, password, and profile image
    """
    body = json.loads(request.data)
    username = body.get("username")
    email = body.get("email")
    profile_image_url = body.get("profile_image_url")
    if username is None or email is None or profile_image_url is None:
        return failure("Missing Fields", 404)
    new_user = User(username, email)
    password = body.get("password")
    if password is None:
        return failure("Password is Missing", 404)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return success(new_user.serialize())


@app.route("/auth/login", methods=["POST"])
def login():
    """
    Endpoint to login using username and password
    """
    pass


@app.route("/auth/logout/", methods=["POST"])
def logout():
    """
    Endpoint to logout
    """
    pass


# -- USER ROUTES ------------------------------------------------------


@app.route("/user/<int:user_id>")
def get_user(user_id):
    """
    Endpoint for getting user by id
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure("User not Found")
    return success(user.serialize())


# -- WALDO ROUTES ------------------------------------------------------


@app.route("/waldo/today/")
def get_waldo():
    """
    Endpoint for getting today's Waldo
    """
    today = date.today()
    waldo = DailyWaldo.query.filter_by(date=today).first()
    if waldo is None:
        return failure("Waldo not Found", 404)
    return success(waldo.serialize())


@app.route("/waldo/hint/", methods=["POST"])
def post_hint():
    """
    Endpoint for inputting Waldo hints throughout the day
    """
    pass


@app.route("/waldo/code/")
def get_code():
    """
    Endpoint for getting code
    """
    pass


@app.route("/waldo/redeem/")
def found_waldo():
    """
    Endpoint for redeeming points for finding Waldo
    """
    pass


# -- LEADERBOARD ROUTES ------------------------------------------------------


@app.route("/leaderboard/")
def get_leaderboard():
    """
    Endpoint for getting the leaderboard
    """
    pass


# -- ADMIN ROUTES ------------------------------------------------------


@app.route("/admin/waldo/create/<int:waldo_id>/", methods=["POST"])
def choose_waldo(waldo_id):
    """
    Endpoint for choosing Waldo of the Day
    """
    pass


@app.route("/admin/waldo/users/")
def get_users():
    """
    Endpoint for getting all users
    """
    users = []
    for user in User.query.all():
        users.append(user.serialize())
    return success({"users": users})