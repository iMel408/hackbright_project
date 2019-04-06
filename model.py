from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from env import LOGIN, PASSWORD, SECRET_KEY

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///textstoself'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True  # mute warnings
app.secret_key = SECRET_KEY


db = SQLAlchemy(app)


class User(db.Model):
    """ create a user """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    password = db.Column(db.String(20), unique=True, nullable=False)
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.utcnow)

    jobs = db.relationship('jobs', back_populates = 'user')

    def __repr__(self):
        return f'<username: {self.username}, phone: {self.phone}>'


class Job(db.Model):
    """ create/schedule a job associated with a user """

    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id'))
    active = db.Column(db.Boolean, default=False)
    msg_txt = db.Column(db.String(50), nullable=False)
    frequency = db.Column(db.String, nullable=False, default='day')
    run_time = db.Column(db.String, nullable=False, default='12:00')
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.utcnow)

    user = db.relationship('users', back_populates = 'jobs')
    events = db.relationships('sent', back_populates = 'jobs')


    def __repr__(self):
        return f'<username: {self.users.username}, job_id: {self.id}, active: {self.active}>'


class Sent(db.Model):

    __tablename__ = 'sent'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, ForeignKey('job.id'))
    date_added = db.Column(db.DateTime(), default=datetime.utcnow)

    job = db.relationship('jobs', back_populates = 'sent')
    reply = db.relationship('received', back_populates = 'sent')

    def __repr__(self):
        return f'<active: {self.active}, created: {self.created}>'


class Received():

    __tablename__: 'received'

    id = db.Column(db.Integer, primary_key=True)
    sent_id = db.Column(db.Integer, ForeignKey('sent_log.id'))
    msg_txt = db.Column(db.String(80), nullable=True)
    date_added = db.Column(db.DateTime(), default=datetime.utcnow)

    event = db.relationship('sent', back_populates = 'received')

    def __repr__(self):
        return f'<username: {users.username}, msg_txt: {self.msg_txt}>'



if __name__ == '__main__':


    db.drop_all()
    db.create_all()

    melissa = User(username=USERNAME, phone=ADMIN_PHONE, password=PASSWORD)

    db.session.add(melissa)
    db.session.commit()








