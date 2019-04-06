import os
from env import LOGIN, PASSWORD
from flask import Flask
from twilio.twiml.messaging_response import MessagingResponse

# The session object makes use of a secret key.
app = Flask(__name__)
app.config.from_object(__name__)


senders = {
    # "+123456789101": "Melissa",
    os.environ['ADMIN']: "Admin",
}

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    """Respond to incoming messages with a friendly SMS."""
    # Start our response
    resp = MessagingResponse()

    # Add a message
    resp.message("Thanks! [Melissa - testing response to incoming SMS.]")

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)