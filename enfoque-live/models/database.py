from flask_sqlalchemy import SQLAlchemy
import datetime 

db = SQLAlchemy()

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(255), unique=True)
    name = db.Column(db.String(255), nullable=True)
    footprint = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(255), nullable=True)
    sold = db.Column(db.Boolean, nullable=True)
    banned = db.Column(db.Boolean, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())