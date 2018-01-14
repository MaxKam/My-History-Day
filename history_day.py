from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from configparser import ConfigParser
from db_connect import db, User
from gtoken_verifier import GTokenVerify

import os
import json
import google.oauth2.credentials
import google_auth_oauthlib.flow

#Instantiate ConfigParser and point to config file
config = ConfigParser()
config.read("./config/app_config.txt")

#Set up Flask 
app = Flask(__name__)
app.secret_key = config.get("APP_SETTINGS", "secret_key")
app.config['SQLALCHEMY_DATABASE_URI'] = config.get("DB_SETTINGS", "database_uri")

#Google API settings
CLIENT_SECRETS_FILE = config.get("GOOGLE_API", "client_secrets_file")
SCOPES = config.get("GOOGLE_API", "scopes")
API_SERVICE_NAME = config.get("GOOGLE_API", "api_service_name")
API_VERSION = config.get("GOOGLE_API", "api_version")
MY_CLIENT_ID = config.get("GOOGLE_API", "client_id")

#Connect flask-sqlalchemy to Flask app
db.init_app(app)

#Set up Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#Instantiate token verifier class
gtoken_verifiy = GTokenVerify()

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
      token_result = gtoken_verifiy.check_token(request.form["idtoken"], MY_CLIENT_ID)

      if token_result == "Token from user not verified":
        flash("Unable to log you in. Please check your Google account")
        return url_for("index")

      #Get users unique Google ID
      userid = token_result['sub']

      registered_user = User.query.filter_by(googleID=userid).first()

      if registered_user is None:
        user_properties = {'google_id': str(userid), 'given_name': token_result['given_name'], 'family_name': token_result['family_name'] }
        create_user(user_properties)
        registered_user = User.query.filter_by(googleID=userid).first()

      login_user(registered_user, remember=True)
      return url_for('events')


@app.route('/events')
@login_required
def events():
  return render_template('events.html', MY_CLIENT_ID=MY_CLIENT_ID)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')

##### Helper Functions

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