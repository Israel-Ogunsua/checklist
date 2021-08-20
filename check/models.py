from datetime import time
from enum import unique
from check import app, login_manager
from flask_login import UserMixin
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(70), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable = False, unique= True)
    password = db.Column(db.String(225), nullable = False)
    posts = db.relationship('Post', backref='author', lazy=True)
    archives = db.relationship('Archive', backref='author', lazy=True)

    def __repr__(self):
        return f'User({self.username},{self.email}, {self.password},{self.posts} )'


class Post(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500),nullable = False)
    discription = db.Column(db.String(2550))
    Duetime = db.Column(db.String(1000))
    timePosted = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(1000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'User({self.title},{self.discription}, {self.status}, {self.Duetime},{self.user_id})'

class Archive(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    title  = title = db.Column(db.String(1000))
    discription = db.Column(db.String(2550))
    archived_id= db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'User({self.title},{self.discription})'

