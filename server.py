import sys
import os
import env
from flask import Flask, request, redirect
from twilio import twiml
from twilio.rest import Client
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from twilio.twiml.messaging_response import MessagingResponse
from model import connect_to_db, db, User, Job, Event


app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = env.SECRET_KEY


# senders = {
#     # "+123456789101": "Melissa",
#     "os.environ[env.ADMIN_PHONE]": "Melissa",
# }

# @app.route('/user/<int:id>')
# def user_page(id):
#     """show user page/info"""

#     user = User.query.get(id)
#     return render_template('user_page.html',user=user)

CLIENT = Client(env.TWILIO_ACCOUNT_SID, env.TWILIO_AUTH_TOKEN)

@app.route('/outgoing', methods=['GET', 'POST'])
def send_sms():
    message = CLIENT.messages.create(
        from_=env.FROM_PHONE,
        to=env.ADMIN_PHONE,
        body=env.MSG,
    )

    msg_type = 'outbound'
    user_phone = request.values.get('to')
    msg_txt = request.values.get('body')
    msg_sid = request.values.get('sid')
    status = request.values.get('status')

    new_prompt = Event(msg_type=msg_type,
        user_phone=user_phone,
        msg_txt=msg_txt,
        msg_sid=msg_sid,
        status=status
    )

    db.session.add(new_prompt)
    db.commit()

    print('SMS Sent')

    return 0


@app.route("/incoming", methods=['GET', 'POST'])
def receive_reply():
    """Respond to incoming messages with a friendly SMS."""

    msg_type = 'inbound'
    user_phone = request.values.get('From')
    msg_txt = request.values.get('Body')
    msg_sid = request.values.get('MessageSid')
    status = request.values.get('SmsStatus')

    new_reply = Event(msg_type=msg_type,
        user_phone=user_phone,
        msg_txt=msg_txt,
        msg_sid=msg_sid,
        status=status
    )


    db.session.add(new_reply)
    db.commit()

    resp = MessagingResponse()
    resp.message("Your response has been logged.")

    print(resp)

    return str(resp)


if __name__ == "__main__":

    app.run(debug=True)

    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    DebugToolbarExtension(app)
    app.run(port=5000, host='0.0.0.0')

