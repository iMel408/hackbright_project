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

from twilio.twiml.messaging_response import Body, Message, Redirect, MessagingResponse

# response = MessagingResponse()
# message = Message()
# message.body('Hello World!')
# response.append(message)
# response.redirect('https://demo.twilio.com/welcome/sms/')

# print(response)

app = Flask(__name__)
# app.config.from_object(__name__)
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

    new_prompt = Event(msg_type='outbound',
        user_phone=message.to,
        msg_body=message.body,
        msg_sid=message.sid,
        msg_status=message.status
    )

    print('user_phone', message.to,
        'msg_body', message.body,
        'msg_sid', message.sid,
        'msg_status', message.status)


        db.session.add(new_prompt)
    db.session.commit()

    print(new_prompt)
    print(message.to)



@app.route("/incoming", methods=['GET', 'POST'])
def receive_reply():
    """Respond to incoming messages with a friendly SMS."""

    msg_type = 'inbound'
    user_phone = request.values.get('From')
    msg_body = request.values.get('Body')
    msg_sid = request.values.get('MessageSid')
    msg_status = request.values.get('SmsStatus')

    new_reply = Event(msg_type=msg_type,
        user_phone=user_phone,
        msg_body=msg_body,
        msg_sid=msg_sid,
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

