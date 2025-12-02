from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
from werkzeug.security import generate_password_hash, check_password_hash



db = SQLAlchemy()

#your classes here
class User(db.Model):
    """
    User model
    DailyWaldo - one to many
    WaldoFound - one to many
    Leaderboard - one to many
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    profile_image_url = db.Column(db.String, nullable=False)
    points = db.Column(db.Integer, default=0)
    admin = db.Column(db.Boolean, default=False)
    
    finds = db.relationship('WaldoFound')

    def __init__(self, **kwargs):
        """
        Initialize User object
        """
        self.username = kwargs.get("username", "")
        self.email = kwargs.get("email", "")
        self.password = kwargs.get("password")
        self.profile_image_url = kwargs.get("profile_image_url")
        self.points = 0
        self.admin = kwargs.get("admin", False)


    def set_password(self,password):
        """
        Sets the password for a user securely
        """
        self.password_hash = generate_password_hash(password)


    def check_password(self,password):
        """
        Checks the password for login securely
        """
        return check_password_hash(self.password_hash, password)
    

    def serialize(self):
        """
        Serialize User object
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'profile_image_url': self.profile_image_url,
            'points': self.points
        }
    

class DailyWaldo(db.Model):
    """
    DailyWaldo model - waldo for a specific day
    User - Many to One 
    WaldoHint - One to Many
    WaldoFind - One to Many
    """
    __tablename__ = 'daily_waldos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, unique=True, nullable=False, default=db.func.current_date())
    secret_code = db.Column(db.String, unique=True, nullable=False)
    
    hints = db.relationship('WaldoHint')
    found = db.relationship('WaldoFound')
    waldo_user = db.relationship('User', backref='daily_waldos')

    def __init__(self, **kwargs):
        """
        Initialize DailyWaldo object
        """
        self.user_id = kwargs.get("user_id", "")
        self.date = kwargs.get("date", None)
        self.secret_code = kwargs.get("secret_code")

    def serialize(self):
        """
        Serialize a Waldo object
        """
        return {
            'id': self.id,
            'waldo': self.waldo_user.username,
            'image': self.waldo_user.profile_image_url,
            'date': self.date.isoformat(),
            'hints': [hint.serialize() for hint in self.hints],
            'finders': len(self.found)
        }
    

class WaldoHint(db.Model):
    """
    WaldoHint Model - hints by waldo
    DailyWaldo - Many to One
    """
    __tablename__ = 'waldo_hints'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    daily_waldo_id = db.Column(db.Integer, db.ForeignKey('daily_waldos.id'), nullable=False)
    hint_text = db.Column(db.String, nullable=True)
    hint_image_url = db.Column(db.String, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, **kwargs):
        """
        Initialize WaldoHint object
        """
        self.daily_waldo_id = kwargs.get("daily_waldo_id", "")
        self.hint_text = kwargs.get("hint_text")
        self.hint_image_url = kwargs.get("hint_image_url")


    def serialize(self):
        """
        Serialize a WaldoHint object
        """
        return {
            'id': self.id,
            'text': self.hint_text,
            'image': self.hint_image_url,
            'time': self.timestamp.isoformat()
        }
    

class WaldoFound(db.Model):
    """
    WaldoFound Model - users that found waldo
    DailyWaldo - many to one
    User - many to one
    """
    __tablename__ = 'waldo_found'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    daily_waldo_id = db.Column(db.Integer, db.ForeignKey('daily_waldos.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    points_earned = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)

    user = db.relationship('User')

    __table_args__ = (db.UniqueConstraint("user_id", "daily_waldo_id", name="uix_user_waldo"),)

    def __init__(self, **kwargs):
        """
        Initialize WaldoFound object
        """
        self.daily_waldo_id = kwargs.get("daily_waldo_id", "")
        self.user_id = kwargs.get("user_id", "")
        self.points_earned = kwargs.get("points_earned", "")
        self.date = kwargs.get("date", None)

    def serialize(self):
        """
        Serialize a WaldoFound object
        """
        return {
            'id': self.id,
            'user': self.user.username,
            'points_earned': self.points_earned,
        }
    

class Leaderboard(db.Model):
    """
    Leaderboard Model - rankings/points for users
    """
    __tablename__ = 'leaderboard'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    total_points = db.Column(db.Integer, default=0, nullable=False)
    rank = db.Column(db.Integer, nullable=True)

    user = db.relationship('User', backref='leaderboard_entry')

    def serialize(self):
        return {
            'user_id': self.user_id,
            'username': self.user.username,
            'total_points': self.total_points,
            'rank': self.rank
        }