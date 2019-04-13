import os
import env
from flask import Flask
from twilio.twiml.messaging_response import MessagingResponse

# The session object makes use of a secret key.
app = Flask(__name__)
app.config.from_object(__name__)


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

    from_number = request.values.get('From')


if __name__ == "__main__":
    app.run(debug=True)