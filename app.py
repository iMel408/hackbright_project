import sys
import os
import env
from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from twilio.twiml.messaging_response import MessagingResponse
from model import connect_to_db, db, User, Job, Task


app = Flask(__name__)
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///textstoself'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = env.SECRET_KEY


senders = {
    # "+123456789101": "Melissa",
    "os.environ[env.ADMIN_PHONE]": "Melissa",
}

@app.route("/incoming", methods=['GET', 'POST'])
def receive_reply():
    """Respond to incoming messages with a friendly SMS."""
    # Start our response
    resp = MessagingResponse()

    user_phone = request.values.get('From')
    msg_txt = request.values.get('Body')

    new_reply = Event(type='incoming', user_phone=user_phone, msg_txt=msg_txt)

    db.session.add(new_reply)
    db.commit()
        # Add a message
    resp.message("Your response has been logged.")

    return str(resp)




if __name__ == "__main__":
    app.run(debug=True)

    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)


    DebugToolbarExtension(app)
    app.run(port=5000, host='0.0.0.0')




    -------------


    import sys
import os
import env
from flask import Flask, render_template, request, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from twilio import twiml
from twilio.rest import Client
from twilio.twiml.messaging_response import Body, Message, Redirect, MessagingResponse
from model import connect_to_db, db, User, Job, Event
from jinja2 import StrictUndefined
from werkzeug.security import check_password_hash, generate_password_hash
# from chart import make_chart
from tasks import make_celery
from datetime import timedelta, datetime


app = Flask(__name__)
app.secret_key = env.SECRET_KEY

app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379',
    CELERYBEAT_SCHEDULE = {
        'run_every_min': {
            'task': 'server.run_jobs',
            'schedule': timedelta(seconds=60*60)
        },
    }
)

celery = make_celery(app)


@celery.task()
def run_jobs():
    """send sms messages due for current hour"""

    now = datetime.now()
    print(now.hour)
    tasks_due = Job.query.filter_by(time=str(now.hour)+':00').all()

    for task in tasks_due:
        print(task.phone,task.msg_txt)
        send_sms(to=task.phone, body=task.msg_txt, from_=env.FROM_PHONE)




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



@app.route('/logout')
def logout():

    del(session['id'])
    flash('Logged out')
    print(session)
    return redirect('/')


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
def send_sms(to, body, from_=env.FROM_PHONE):

    with app.app_context():
        db.init_app(app)

        message = CLIENT.messages.create(
            to=to,
            from_=from_,
            body=body
        )

        msg_type='outbound'
        job_id = '1'
        msg_sid=message.sid
        user_phone=message.to
        body=message.body
        msg_body=body.replace('Sent from your Twilio trial account - ','')
        msg_status=message.status

        log_event(msg_type, job_id, msg_sid, user_phone, msg_body, msg_status)

    return 0


def log_event(msg_type, job_id, msg_sid, user_phone, msg_body, msg_status):
    """insert event details into db"""

    new_event = Event(msg_type=msg_type,
        job_id=job_id,
        msg_sid=msg_sid,
        user_phone=user_phone,
        msg_body=msg_body,
        msg_status=msg_status
    )

    
    db.session.add(new_event)
    db.session.commit()

##########
        


@app.route("/incoming", methods=['GET', 'POST'])
def receive_reply():
    """Respond to incoming messages with a friendly SMS."""

    msg_type = 'inbound'
    job_id=1
    msg_sid = request.values.get('MessageSid')
    user_phone = request.values.get('From')
    msg_body = request.values.get('Body')
    msg_status = request.values.get('SmsStatus')

    new_reply = Event(msg_type=msg_type,
        job_id=job_id,
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

    # DebugToolbarExtension(app)

    app.run(host='0.0.0.0')

