import sys
import os
from datetime import datetime
from flask import Flask
from twilio.rest import Client
from flask_sqlalchemy import SQLAlchemy
import env

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///textstoself'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = env.SECRET_KEY

db = SQLAlchemy(app)


class User(db.Model):
    """ create a user """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True,)
    password = db.Column(db.String(20), unique=True,)
    phone = db.Column(db.String(20), unique=True)
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.utcnow)

    job = db.relationship('Job', back_populates='user')
    data_points = db.relationship('Event', back_populates='user')

    def __init__(self, username, password, phone=None):
        self.username = username
        self.password = password
        self.phone = phone

    def __repr__(self):
        return f'<username: {self.username}, phone: {self.phone}>'


class Job(db.Model):
    """ create/schedule a job associated with a user """

    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    active = db.Column(db.Boolean, default=False)
    msg_txt = db.Column(db.String(160))
    frequency = db.Column(db.String, default='day')
    time = db.Column(db.String, default='12:00')
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.utcnow)

    user = db.relationship('User', back_populates='job')
    events = db.relationship('Event', back_populates = 'job')

    def __repr__(self):
        return f'<User Name: {self.user.username}, Job ID: {self.id}, Active: {self.active}>'


class Event(db.Model):
    """ log of  sent messages """

    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'))
    type = db.Column(db.String(10))
    phone_num = db.Column(db.String(20), db.ForeignKey('users.phone'), unique=True)
    msg_txt = db.Column(db.String(80), nullable=True)
    date_added = db.Column(db.DateTime(), default=datetime.utcnow)

    user = db.relationship('User', back_populates='data_points')
    job = db.relationship('Job', back_populates='events')

    def __init__(self, job_id):
        self.job_id = job_id
        self.type = type
        self.phone_num = phone_num
        self.msg_txt = msg_txt

    def __repr__(self):
        return f'<User Name: {self.users.username}, Phone #: {self.phone_num}, Msg Text: {self.msg_txt}>'


    def send_sms(message, to_phone=env.ADMIN_PHONE):
        message = CLIENT.messages.create(
            from_=env.FROM_PHONE,
            to=to_phone,
            body=message,
        )
        return message.sid


if __name__ == '__main__':


    db.drop_all()
    db.create_all()

    melissa = User(username=env.USERNAME, phone=env.ADMIN_PHONE, password=env.PASSWORD)
    melissa_job = Job(user_id=1, active=False, msg_txt=env.MSG)

    db.session.add(melissa)
    db.session.add(melissa_job)
    db.session.commit()








