import sys
import os
from datetime import datetime, date
from flask import Flask
from twilio.rest import Client
from flask_sqlalchemy import SQLAlchemy
import env


db = SQLAlchemy()


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
    """ setup/schedule a job associated with a user """

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
    """ run and log an instance of a job """

    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'))
    user_phone = db.Column(db.String(20), db.ForeignKey('users.phone'))
    msg_type = db.Column(db.String(20))
    msg_body = db.Column(db.String(80), nullable=True)
    msg_sid = db.Column(db.String(120), nullable=True)
    msg_status = db.Column(db.String(80), nullable=True)
    date_added = db.Column(db.Date(), default=datetime.now)
    date_updated = db.Column(db.DateTime(), default=datetime.utcnow)

    user = db.relationship('User', back_populates='data_points')
    job = db.relationship('Job', back_populates='events')

    # def __init__(self, job_id):
    #     self.job_id = job_id
    #     self.user_phone = user_phone
    #     self.msg_type = msg_type
    #     self.msg_txt = msg_txt
    #     self.msg_sid = msg_sid
    #     self.status = status
    #     self.err_cd = err_cd
    #     self.err_msg = err_msg

    def __repr__(self):
        return f'<User Name: {self.user.username}, Phone #: {self.phone_num}, Msg Text: {self.msg_txt}>'

def connect_to_db(app):
    """Connect the database to app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///textstoself'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":

    from server import app
    connect_to_db(app)
    print("Connected to DB.")


    db.drop_all()
    db.create_all()

    melissa = User(username=env.USERNAME, phone=env.ADMIN_PHONE, password=env.PASSWORD)
    melissa_job = Job(user_id=1, active=False, msg_txt=env.MSG)

    db.session.add(melissa)
    db.session.add(melissa_job)
    db.session.commit()





