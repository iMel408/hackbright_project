import configparser

config = configparser.ConfigParser()
config.read('env.conf')

SECRET_KEY = config['flask']['secret']

ACCOUNT_SID = config['twilio_api']['sid']
AUTH_TOKEN = config['twilio_api']['token']

TWILIO_PHONE = config['phones']['twilio']
ADMIN_PHONE = config['phones']['admin']

USERNAME = config['login']['username']
PASSWORD = config['login']['password']