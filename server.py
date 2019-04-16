import sys
import os
import env
from flask import Flask, render_template, request, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from twilio import twiml
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from model import connect_to_db, db, User, Job, Event
from jinja2 import StrictUndefined
from werkzeug.security import check_password_hash, generate_password_hash


from twilio.twiml.messaging_response import Body, Message, Redirect, MessagingResponse


app = Flask(__name__)
app.secret_key = env.SECRET_KEY


@app.route('/')
def index():

    return render_template('index.html')


@app.route('/register', methods=['GET'])
def reg_form():

    return render_template('register.html')


@app.route('/register', methods=['POST'])
def reg_process():

    username = request.form['username']
    password = request.form['password']

    new_user = User(username=username, password=password)

    db.session.add(new_user)
    db.session.commit()

    flash(f'User {username} added.')
    return redirect('/login')


@app.route('/login', methods=['GET'])
def login_form():

    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_process():

    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()

    if not user:
        flask("no such user")
        return redirect('/login')

    if user.password != password:
        flash('incorrect password')
        return redirect('/login')

    session['id'] = user.id

    flash('Logged In')
    return redirect(f'/user/{user.id}')


@app.route('/user/<int:id>')
def user_page(id):
    """show user page/info"""

    user = User.query.get(id)

    job = Job.query.filter_by(user=user).first()

    if job:
        events = Event.query.filter_by(job_id=job.id,msg_type='inbound').all()

        return render_template('user.html',user=user,job=job,events=events)

    return render_template('user.html',user=user)

CLIENT = Client(env.TWILIO_ACCOUNT_SID, env.TWILIO_AUTH_TOKEN)

@app.route('/outgoing', methods=['GET', 'POST'])
def send_sms(from_, to, body=env.MSG):

    with app.app_context():
        db.init_app(app)

        message = CLIENT.messages.create(
            from_=from_,
            to=to,
            body=body
        )

        msg_type='outbound',
        msg_sid=message.sid,
        user_phone=message.to,
        msg_body=message.body,
        msg_status=message.status

        new_prompt = Event(msg_type=msg_type,
            msg_sid=msg_sid,
            user_phone=user_phone,
            msg_body=msg_body,
            msg_status=msg_status
        )

        db.session.add(new_prompt)
        db.session.commit()

    return


@app.route("/incoming", methods=['GET', 'POST'])
def receive_reply():
    """Respond to incoming messages with a friendly SMS."""

    msg_type = 'inbound'
    msg_sid = request.values.get('MessageSid')
    user_phone = request.values.get('From')
    msg_body = request.values.get('Body')
    msg_status = request.values.get('SmsStatus')

    new_reply = Event(msg_type=msg_type,
        msg_sid=msg_sid,
        user_phone=user_phone,
        msg_body=msg_body,
        msg_status=msg_status
    )

    db.session.add(new_reply)
    db.session.commit()

    resp = MessagingResponse()
    resp.message("Your response has been logged.")

    print(resp)

    return str(resp)


if __name__ == "__main__":

    app.debug = True

    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run(host='0.0.0.0')

