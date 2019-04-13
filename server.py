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
app.secret_key = env.SECRET_KEY


senders = {
    # "+123456789101": "Melissa",
    "os.environ[env.ADMIN_PHONE]": "Melissa",
}

@app.route("/incoming", methods=['GET', 'POST'])
def sms_reply():
    """Respond to incoming messages with a friendly SMS."""
    # Start our response
    resp = MessagingResponse()

    # Add a message
    resp.message("Your response has been logged.")

    return str(resp)

    user_phone = request.values.get('From')


if __name__ == "__main__":
    app.run(debug=True)

    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)


    DebugToolbarExtension(app)
    app.run(port=5000, host='0.0.0.0')