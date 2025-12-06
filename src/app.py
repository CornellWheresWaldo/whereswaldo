from db import db, User, DailyWaldo, WaldoHint, WaldoFound
from flask import Flask, request
import json
import secrets
import os
from datetime import date, datetime

app = Flask(__name__)
db_filename = 'waldo.db'

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

#initialize the database
db.init_app(app)
with app.app_context():
    db.create_all()

#success response
def success_response(data, code=200):
    return json.dumps(data), code

#error response
def failure_response(data, code=404):
    return json.dumps({"error": data}), code


#-------AUTH ROUTES-------
#creating/registering a user
@app.route("/auth/register/", methods=["POST"])
def create_user():
    body = json.loads(request.data)
    required = ["username", "email", "password", "profile_image_url"]
    if any(body.get(field) is None for field in required):
        return failure_response("Please provide all required fields", 400)
    new_user = User(username=body.get("username"), email=body.get("email"), profile_image_url=body.get("profile_image_url"))
    new_user.set_password(body.get("password"))
    db.session.add(new_user)
    db.session.commit()
    return success_response(new_user.serialize(), 201)

#verifies login credientials (email and password)
@app.route("/auth/login/", methods=['POST'])
def login():
    body = json.loads(request.data)
    email = body.get("email")
    password = body.get("password")
    if email is None or password is None:
        return failure_response("Please provide email and password", 400)
    user = User.query.filter_by(email=email).first()
    if user is None:
        return failure_response("User not found")
    if not user.check_password(password):
        return failure_response("Incorrect password", 403)
    return success_response(user.serialize(), 201)


#-------USER ROUTES-------
#retrieves all registered users
@app.route("/user/users/")
def get_users():
    users = []
    for user in User.query.all():
        users.append(user.serialize())
    return success_response({"users": users})

#retrieves a user by id
@app.route("/user/<int:user_id>/")
def get_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not Found")
    return success_response(user.serialize())


#-------WALDO ROUTES-------
#randomly selects daily waldo and creates the secret code
@app.route("/waldo/create/", methods=["POST"])
def choose_waldo():
    users = User.query.all()
    today = date.today()
    if not users:
        return failure_response("No users exist to choose from", 400)
    import random
    chosen_user = random.choice(users)
    import secrets
    secret_code = secrets.token_hex(4)
    new_waldo = DailyWaldo(user_id=chosen_user.id, date=today, secret_code=secret_code)
    db.session.add(new_waldo)
    db.session.commit()
    return success_response({'new_waldo':new_waldo.serialize()})

#retrieves today's waldo
@app.route("/waldo/today/")
def get_waldo():
    today = date.today()
    waldo = DailyWaldo.query.filter_by(date=today).first()
    if waldo is None:
        waldo = choose_waldo()
    return success_response(waldo.serialize())

#posts a user to WaldoFound if found waldo and updates points
@app.route("/waldo/found/", methods=["POST"])
def found_waldo():
    body = json.loads(request.data)
    user_id = body.get("user_id")
    secret_code = body.get("secret_code")
    if user_id is None or secret_code is None:
        return failure_response("Missing user_id or secret_code", 400)
    today = date.today()
    waldo = DailyWaldo.query.filter_by(date=today).first()
    if waldo is None:
        return failure_response("No Waldo selected today", 404)
    if waldo.secret_code != secret_code:
        return failure_response("Invalid code", 403)
    existing = WaldoFound.query.filter_by(user_id=user_id, date=today).first()
    if existing:
        return failure_response("Already found today", 409)
    created_at = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    now = datetime.utcnow()
    seconds = (now - created_at).total_seconds()
    total_points = 1200
    hours_passed = seconds // 3600
    points = total_points - (hours_passed * 50)
    points = max(points, 0)
    new_find = WaldoFound(
        daily_waldo_id = waldo.id,
        user_id = user_id,
        points_earned = points,
        date = today
    )
    db.session.add(new_find)
    user = User.query.get(user_id)
    user.points += points
    db.session.commit()
    return success_response({"points_awarded": points, "total_points": user.points})

#create waldo's hints
@app.route("/waldo/hints/", methods=["POST"])
def create_hint():
    body = json.loads(request.data)
    today = date.today()
    waldo = DailyWaldo.query.filter_by(date=today).first()
    if waldo is None:
        return failure_response("Waldo does not exist", 404)
    hint_text = body.get("hint_text")
    hint_image_url = body.get("hint_image_url")
    if hint_text is None and hint_image_url is None:
        return failure_response("Hint cannot be empty", 400)
    new_hint = WaldoHint(daily_waldo_id=waldo.id, hint_text=hint_text, hint_image_url=hint_image_url)
    db.session.add(new_hint)
    db.session.commit()
    return success_response(new_hint.serialize(), 201)

#get today's hints
@app.route("/waldo/hints/")
def get_hints():
    today = date.today()
    waldo = DailyWaldo.query.filter_by(date=today).first()
    if waldo is None:
        return failure_response("Waldo not found", 404)
    hints = []
    for hint in waldo.hints:
        hints.append(hint.serialize())
    return success_response({"hints": hints})

#get waldo's secret code - should only be called by admin
@app.route("/waldo/code/")
def get_secret_code():
    today = date.today()
    waldo = DailyWaldo.query.filter_by(date=today).first()
    if waldo is None:
        return failure_response("Waldo not found", 404)
    return success_response({"secret_code": waldo.secret_code})

#adds points to user's score
@app.route("/user/points/<int:id>/", methods=["POST"])
def add_user_points(id):
    body = json.loads(request.data)
    user = User.query.get(id)
    if user is None:
        return failure_response("User not found", 404)
    todays_points = body.get("points")
    if todays_points is None or type(todays_points) is not int:
        return failure_response("Invalid or missing 'points'", 400)
    user.points += todays_points
    db.session.commit()
    return success_response({"new_points": user.points})

#retrives all waldos found by a user
@app.route("/user/finds/<int:id>/")
def waldo_finds(id):
    waldos_found = WaldoFound.query.filter_by(user_id=id).all()
    return success_response({"finds":[waldo.serialize for waldo in waldos_found]})


#-------LEADERBOARD ROUTES-------
#get leaderboard - sorts users by points
@app.route("/leaderboard/")
def leaderboard():
    users = User.query.order_by(User.points.desc()).all()
    leaderboard_data = []
    rank = 1
    for user in users:
        leaderboard_data.append({
            "rank": rank,
            "user_id": user.id,
            "username": user.username,
            "points": user.points
        })
        rank += 1
    return success_response({"leaderboard": leaderboard_data})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
