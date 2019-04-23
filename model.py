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
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(20))
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.utcnow)

    # job = db.relationship('Job', back_populates='user')

    # def __init__(self, username, password):
    #     self.username = username
    #     self.password = password
    

    # def __repr__(self):
    #     return f'<username: {self.username}>


class Job(db.Model):
    """ setup/schedule a job associated with a user """

    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    active = db.Column(db.Boolean, default=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    msg_txt = db.Column(db.String(160))
    frequency = db.Column(db.String, default='daily')
    time = db.Column(db.String, default='12:00')
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.utcnow)

    # user = db.relationship('User', back_populates='job')
    # events = db.relationship('Event', back_populates = 'job')

    user = db.relationship('User', backref=db.backref('jobs', order_by=id))
    events = db.relationship('Event', backref=db.backref('jobs', order_by=id))

    def __repr__(self):
        return f'<User Name: {self.user.username}, Job ID: {self.id}, Active: {self.active}>'


class Event(db.Model):
    """ run and log an instance of a job """

    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    msg_sid = db.Column(db.String(256))
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'))
    user_phone = db.Column(db.String(20))
    msg_type = db.Column(db.String(20))
    msg_body = db.Column(db.String(256), nullable=True)
    msg_status = db.Column(db.String(20), nullable=True)
    date_added = db.Column(db.Date(), default=datetime.now)
    date_updated = db.Column(db.DateTime(), default=datetime.utcnow)

    # job = db.relationship('Job', back_populates='events')

    def __repr__(self):
        return f'<Phone #: {self.user_phone}, Msg Text: {self.msg_body}>'


def connect_to_db(app):
    """Connect the database to app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///textstoself'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":

    from server import app
    connect_to_db(app)
    print("Connected to DB.")

    db.create_all()



    # melissa = User(username='Melissa', password=env.PASSWORD)
    # melissa_job = Job(user_id=1, active=True, phone=env.ADMIN_PHONE, msg_txt='What level anxiety were you at today?')

    # melissa_out = Event(msg_sid='SMc2b76fff5a4b4077b60454c7de369687',job_id=1, user_phone=env.ADMIN_PHONE, msg_type='outgoing', msg_body='What was your anxiety level today? Scale [1 - 10]', msg_status='queued')
    # melissa_in = Event(msg_sid='SMe78b674b4fc3477d3b2391707a11e94f',job_id=1, user_phone=env.ADMIN_PHONE, msg_type='incoming', msg_body='10', msg_status='received')
    # melissa_out1 = Event(msg_sid='SMc2b76fff5a4b4077b60454c7de369686',job_id=1, user_phone=env.ADMIN_PHONE, msg_type='outgoing', msg_body='What was your anxiety level today? Scale [1 - 10]', msg_status='queued', date_added='2019-04-13', date_updated='2019-04-13 02:43:30.877975')
    # melissa_in1 = Event(msg_sid='SMe78b674b4fc3477d3b2391707a11e94e',job_id=1, user_phone=env.ADMIN_PHONE, msg_type='incoming', msg_body='4', msg_status='received', date_added='2019-04-13', date_updated='2019-04-13 02:43:30.877975')
    # melissa_out2 = Event(msg_sid='SMc2b76fff5a4b4077b60454c7de369685',job_id=1, user_phone=env.ADMIN_PHONE, msg_type='outgoing', msg_body='What was your anxiety level today? Scale [1 - 10]', msg_status='queued', date_added='2019-04-14', date_updated='2019-04-14 02:43:30.877975')
    # melissa_in2 = Event(msg_sid='SMe78b674b4fc3477d3b2391707a11e94d',job_id=1, user_phone=env.ADMIN_PHONE, msg_type='incoming', msg_body='6', msg_status='received', date_added='2019-04-14', date_updated='2019-04-14 02:43:30.877975')
    # melissa_out3 = Event(msg_sid='SMc2b76fff5a4b4077b60454c7de369684',job_id=1, user_phone=env.ADMIN_PHONE, msg_type='outgoing', msg_body='What was your anxiety level today? Scale [1 - 10]', msg_status='queued', date_added='2019-04-15', date_updated='2019-04-15 02:43:30.877975')
    # melissa_in3 = Event(msg_sid='SMe78b674b4fc3477d3b2391707a11e94c',job_id=1, user_phone=env.ADMIN_PHONE, msg_type='incoming', msg_body='4', msg_status='received', date_added='2019-04-15', date_updated='2019-04-15 02:43:30.877975')

    # db.session.add(melissa)
    # db.session.add(melissa_job)
    # db.session.add(melissa_out)
    # db.session.add(melissa_in)
    # db.session.add(melissa_out1)
    # db.session.add(melissa_in1)
    # db.session.add(melissa_out2)
    # db.session.add(melissa_in2)
    # db.session.add(melissa_out3)
    # db.session.add(melissa_in3)
    # db.session.commit()





