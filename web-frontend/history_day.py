from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from configparser import ConfigParser
from db_connect import db, User

import os
import json
import google.oauth2.credentials
import google_auth_oauthlib.flow

config = ConfigParser()
config.read("../config/app_config.txt")


app = Flask(__name__)
app.secret_key = config.get("APP_SETTINGS", "secret_key")
app.config['SQLALCHEMY_DATABASE_URI'] = config.get("DB_SETTINGS", "database_uri")

#Google API settings
CLIENT_SECRETS_FILE = config.get("GOOGLE_API", "client_secrets_file")
SCOPES = config.get("GOOGLE_API", "scopes")
API_SERVICE_NAME = config.get("GOOGLE_API", "api_service_name")
API_VERSION = config.get("GOOGLE_API", "api_version")
MY_CLIENT_ID = config.get("GOOGLE_API", "client_id")


db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except:
        return None

@app.route('/')
def index():
  return render_template('home.html', MY_CLIENT_ID=MY_CLIENT_ID)

@app.route('/login',methods=['POST'])
def login():
  from google.oauth2 import id_token
  from google.auth.transport import requests

  token = request.form["idtoken"]

  idinfo = id_token.verify_oauth2_token(token, requests.Request(), MY_CLIENT_ID)

  if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
        raise ValueError('Wrong issuer.')

  #Store users unique Google ID for easier access
  userid = idinfo['sub']

  registered_user = User.query.filter_by(googleID=userid).first()

  if registered_user is None:
    user_properties = {'google_id': str(userid), 'given_name': idinfo['given_name'], 'family_name': idinfo['family_name'] }
    create_user(user_properties)
    registered_user = User.query.filter_by(googleID=userid).first()

  login_user(registered_user)
  return redirect(request.args.get('next') or redirect(url_for('events'))

@app.route('/events')
@login_required
def events():
  return render_template('events.html', MY_CLIENT_ID=MY_CLIENT_ID)




def create_user(user_props):
  new_user = User(googleID=user_props['google_id'], firstName=user_props['given_name'], lastName=user_props['family_name'])
  db.session.add(new_user)
  db.session.commit()

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification.
  # ACTION ITEM for developers:
  #     When running in production *do not* leave this option enabled.
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

  # Specify a hostname and port that are set as a valid redirect URI
  # for your API project in the Google API Console.
  app.run('localhost', 8080, debug=False)