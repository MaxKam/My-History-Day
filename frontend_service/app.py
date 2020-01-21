import sys
sys.path.append("./rpc_classes")
sys.path.append("../protos")
sys.path.append("./protos")

import os
import json
import pickle
import redis
import google.oauth2.credentials
import google_auth_oauthlib.flow
import grpc
import get_events_pb2
import get_events_pb2_grpc
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from configparser import ConfigParser
from db_connect import db, User
from gtoken_validator import GTokenValidator


#Instantiate ConfigParser and point to config file
config = ConfigParser()
config.read("./config/app_config.ini")

#Set up Flask 
app = Flask(__name__)
app.secret_key = config.get("APP_SETTINGS", "secret_key")
app.config['SQLALCHEMY_DATABASE_URI'] = config.get("DB_SETTINGS", "database_uri")
app.config['DEBUG'] = config.get("APP_SETTINGS", "debug")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
APP_DOMAIN = config.get("APP_SETTINGS", "app_domain")
DEBUG_STATUS = config.get("APP_SETTINGS", "debug")

# This is used in dev. Ideally you would want your web server to serve static assets
app.config['static_url_path'] = './static'

#Google API settings
CLIENT_SECRETS_FILE = config.get("GOOGLE_API", "client_secrets_file")
SCOPES = config.get("GOOGLE_API", "scopes")
API_SERVICE_NAME = config.get("GOOGLE_API", "api_service_name")
API_VERSION = config.get("GOOGLE_API", "api_version")
MY_CLIENT_ID = config.get("GOOGLE_API", "client_id")
OAUTHLIB_INSECURE_TRANSPORT = config.get("GOOGLE_API", "oauthlib_insecure_transport")

#Hostname of the RPC server that fetches events Google's API
RPC_SERVER = config.get("APP_SETTINGS", "rpc_server")

#Connect flask-sqlalchemy to Flask app
with app.test_request_context():
  db.init_app(app)
  db.create_all()

#Set up Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#Instantiate token verifier class
gtoken_valid = GTokenValidator()

# Create Redis connection object
REDIS_URL = config.get("DB_SETTINGS", "redis_url")
REDIS_PORT = config.get("DB_SETTINGS", "redis_port")
REDIS_PASSWORD = config.get("DB_SETTINGS", "redis_password")

rcache = redis.Redis(
  host=REDIS_URL,
  port=REDIS_PORT,
  password=REDIS_PASSWORD)

@login_manager.user_loader
def user_loader(user_id):
  return User.query.get(user_id)

##### Routes #####
@app.route('/')
def index():
  return render_template('home.html', MY_CLIENT_ID=MY_CLIENT_ID)


@app.route('/login',methods=['GET', 'POST'])
def login():
  if request.method == 'GET':
    return render_template('login.html', MY_CLIENT_ID=MY_CLIENT_ID)
  if request.method == 'POST':
      token_result = gtoken_valid.check_token(request.form["idtoken"], MY_CLIENT_ID)

      if token_result == "Token from user not verified":
        flash("Unable to log you in. Please check your Google account")
        return url_for("index")

      #Get users unique Google ID
      userid = token_result['sub']

      registered_user = User.query.filter_by(google_id=userid).first()

      if registered_user is None:
        user_properties = {'google_id': str(userid), 'given_name': token_result['given_name'], 'family_name': token_result['family_name'] }
        create_user(user_properties)
        registered_user = User.query.filter_by(google_id=userid).first()

      login_user(registered_user, remember=True)
      return url_for('events')

@app.route('/events', methods=['GET', 'POST'])
@login_required
def events():
  if request.method == 'GET':
    if User.query.get(session['user_id']).google_credentials is None:
      return redirect('authorize')
    return render_template('events.html')
  if request.method == 'POST':
    registered_user = User.query.get(session['user_id'])
    credentials_dict = pickle.loads(registered_user.google_credentials)
    events_list = get_gcal_events(credentials_dict, API_SERVICE_NAME, API_VERSION,
    request.form['date'])
    if events_list == "No events":
      return "No events"
    else:
      return jsonify(events_list)


@app.route('/authorize')
def authorize():
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES)

  flow.redirect_uri = url_for('oauth2callback', _external=True)

  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

  # Store the state so the callback can verify the auth server response.
  session['state'] = state

  return redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = session['state']

  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
  flow.redirect_uri = url_for('oauth2callback', _external=True)

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = request.url
  flow.fetch_token(authorization_response=authorization_response)

  credentials_dict = credentials_to_dict(flow.credentials)
  # Get user from database to add the credentials to the googleCredentials column
  registered_user = User.query.get(session['user_id'])
  registered_user.google_credentials = pickle.dumps(credentials_dict)
  db.session.commit()

  return redirect(url_for('events'))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/sms-events', methods=['POST'])
@login_required
def sms_events():
  registered_user = User.query.get(session['user_id'])
  if 'sendSMS' in request.form and request.form['phoneNumber'] != "":
    registered_user.send_sms = True
    registered_user.users_phone = request.form['phoneNumber']
    db.session.commit()
  else:
    registered_user.send_sms = False
    registered_user.users_phone = None
    db.session.commit()
  return redirect(url_for('events'))


##### Helper Functions

def create_user(user_props):
  new_user = User(google_id=user_props['google_id'], first_name=user_props['given_name'], last_name=user_props['family_name'])
  db.session.add(new_user)
  db.session.commit()

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def get_gcal_events(credentials_dict, api_service_name, api_version, requested_date):
    with grpc.insecure_channel('%s:50051' % RPC_SERVER) as channel:
        stub = get_events_pb2_grpc.GCalendarEventsStub(channel)
        
        events_request = stub.GetEvents(get_events_pb2.EventsRequest(token=credentials_dict['token'],
        refresh_token=credentials_dict['refresh_token'],
        token_uri=credentials_dict['token_uri'],
        client_id=credentials_dict['client_id'],
        client_secret=credentials_dict['client_secret'],
        scopes=credentials_dict['scopes'],
        api_service_name=api_service_name,
        api_version=api_version,
        requested_date=requested_date
        ))
        
        events_list = {}
        for event in events_request:
          if event.event_title == "No events":
            return "No events"
          else:
            events_list[event.event_start_time] = event.event_title
        return events_list

def check_cache(key_name):
  cache_value = rcache.get(key_name)
  if cache_value != None:
    return cache_value
  else:
    return None

def set_cache(key_name, key_value):
  if key_name != '':
    status = rcache.set(key_name, key_value)
    if status == True:
      return True
    else:
      return False

  # When running locally, disable OAuthlib's HTTPs verification.
  # ACTION ITEM for developers:
  #     When running in production *do not* leave this option enabled.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = OAUTHLIB_INSECURE_TRANSPORT
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

# Specify a hostname that you have set as a valid redirect URI
# for your API project in the Google API Console. If using a port other than
# 80 or 443 for flask, for example port 5000 during dev, then you must add the
# port number as part of the redirect URI in the Google API Console. 
app.run(host='0.0.0.0', debug=DEBUG_STATUS)