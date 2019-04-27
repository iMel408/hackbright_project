import env
from flask import Flask, render_template, request, redirect, flash, session
from twilio.rest import Client
from twilio.twiml.messaging_response import Body, Message, Redirect, MessagingResponse
from model import connect_to_db, db, User, Job, Event
from tasks import make_celery
from datetime import timedelta, datetime
from werkzeug.security import check_password_hash,generate_password_hash
import logging

# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
# logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = env.SECRET_KEY

app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379',
    CELERYBEAT_SCHEDULE={
        'run_every_hour': {
            'task': 'server.run_jobs',
            'schedule': timedelta(seconds=60*60)
        },
    }
)

celery = make_celery(app)

@celery.task()
def run_jobs():
    """send sms messages due for current hour"""

    with app.app_context():
        db.init_app(app)

        now = datetime.now()
        print("Current Hour:", now.hour)
        jobs_due = Job.query.filter_by(time=str(now.hour) + ':00').all() #TODO filter out inactive after testing is done

        # jobs_due = session.query(Job).filter_by(time=str(now.hour)+':00').options(joinedload('*')).all()

        print(jobs_due)
 
        for job in jobs_due:

            print("User:", job.user.username, "User Phone:", job.phone, "User Msg:", job.msg_txt, "Status:", job.active)

            if job.active:

                job_id = job.id
                to = job.phone
                body = job.msg_txt

                send_sms(to, body, job_id)
                # print(to, body, job_id)
                print("Sending:",job.phone, job.msg_txt, job.id)
                # send_sms(job.phone, job.msg_txt, job.id)

        db.session.commit()


CLIENT = Client(env.TWILIO_ACCOUNT_SID, env.TWILIO_AUTH_TOKEN)


@app.route('/outgoing', methods=['GET', 'POST'])
def send_sms(to, body, job_id, from_=env.FROM_PHONE):
    """create sms event"""

    message = CLIENT.messages.create(
        to=to,
        from_=from_,
        body=body
    )

    msg_type = 'outbound'
    job_id = job_id
    msg_sid = message.sid
    user_phone = message.to
    body = message.body
    msg_body = body.replace('Sent from your Twilio trial account - ', '')
    msg_status = message.status

    new_event = Event(
                        msg_type=msg_type,
                        job_id=job_id,
                        msg_sid=msg_sid,
                        user_phone=user_phone,
                        msg_body=msg_body,
                        msg_status=msg_status
                    )

    db.session.add(new_event)


@app.route("/incoming", methods=['GET', 'POST'])
def receive_reply():
    """Respond to incoming messages with a friendly SMS."""

    job = Job.query.filter_by(phone=request.values.get('From')).first()

    msg_type = 'inbound'
    job_id = job.id
    msg_sid = request.values.get('MessageSid')
    user_phone = request.values.get('From')
    msg_body = request.values.get('Body')
    msg_status = request.values.get('SmsStatus')

    new_reply = Event(
                        msg_type=msg_type,
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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET'])
def reg_form():
    return render_template('register.html')


@app.route('/register', methods=['GET', 'POST'])
def reg_process():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        error = None

        if User.query.filter_by(username=username).first() is not None:
            error = 'This username already exists!'

        if error is None:

            new_user = User(username=username, password=generate_password_hash(password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()

            flash(f'User {username} added.')
            return redirect('/login')

        flash(error)

    return render_template('register.html')


@app.route('/login', methods=['GET'])
def login_form():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_process():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        error = None
        user = User.query.filter_by(username=username).first()

        if user is None:
            error = 'Incorrect Username'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect Password'

        if error is None:
            session.clear()
            session['id'] = user.id
            flash('Logged In')
            return redirect(f'/user/{user.id}')

        flash(error)

    return render_template('login.html')



@app.route('/logout')
def logout():

    session.clear()
    flash('Logged out')

    return redirect('/')


@app.route('/user/<int:id>')
def user_page(id):
    """show user page/info"""

    user = User.query.get(id)

    job = Job.query.filter_by(user=user).first()

    if job:
        events = Event.query.filter_by(job_id=job.id, msg_type='inbound').all()

        return render_template('user.html', user=user, job=job, events=events)

    return render_template('user.html', user=user)


# def test_func():
#     # query the db
#     usrs = User.query.all()

#     # commit the session
#     db.session.commit()
#     # iterate through people accessing name to see if sql is emitted
#     for user in users:
#         print(f'User is {user.username}')

#     db.session.rollback()


if __name__ == "__main__":
    app.debug = True

    connect_to_db(app)

    # DebugToolbarExtension(app)

    app.run(host='0.0.0.0')
