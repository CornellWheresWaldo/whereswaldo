from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime


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
    points = db.Column(db.Integer, default=0)
    admin = db.Column(db.Boolean, default=False)
    
    finds = db.relationship('WaldoFound')


    def __init__(self, **kwargs):
        """
        Initialize User object
        """
        self.username = kwargs.get("username", "")
        self.email = kwargs.get("email", "")
        self.profile_image_url = kwargs.get("profile_image_url")
        self.points = 0


    def set_password(self,password):
        """
        Sets the password for a user securely
        """
        pass

    def check_password(self,password):
        """
        Checks the password for login securely
        """
        pass

    def serialize(self):
        """
        Serialize user object
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
    date = db.Column(db.Date, unique=True, nullable=False, default=date.today)
    secret_code = db.Column(db.String, unique=True, nullable=False)
    
    hints = db.relationship('WaldoHint')
    found = db.relationship('WaldoFound')
    waldo_user = db.relationship('User')

    def serialize(self):
        """
        Serialize a waldo object
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

    def serialize(self):
        """
        Serialize a waldohint object
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
    __tablename__ = 'waldo_finders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    daily_waldo_id = db.Column(db.Integer, db.ForeignKey('daily_waldos.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    points_earned = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)

    user = db.relationship('User')

    __table_args__ = db.UniqueConstraint("user_id", "date", name="uix_user_date")

    def serialize(self):
        """
        Serialize a waldofound object
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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_points = db.Column(db.Integer, default=0)
    rank = db.Column(db.Integer)

    user = db.relationship('Users')

    def serialize(self):
        """
        Serialize a leaderboard object
        """
        return {
            'user_id': self.user_id,
            'username': self.user.username,
            'total_points': self.total_points,
            'rank': self.rank
        }