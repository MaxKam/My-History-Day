from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from configparser import ConfigParser

import os
import google.oauth2.credentials
import google_auth_oauthlib.flow

config = ConfigParser()
config.read("./config/app_config.txt")


app = Flask(__name__)
app.secret_key = config.get("APP_SETTINGS", "secret_key")
app.config['SQLALCHEMY_DATABASE_URI'] = config.get("DB_SETTINGS", "database_uri")


@app.route('/')
def index():
  return print_index_table()


if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification.
  # ACTION ITEM for developers:
  #     When running in production *do not* leave this option enabled.
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

  # Specify a hostname and port that are set as a valid redirect URI
  # for your API project in the Google API Console.
  app.run('localhost', 8080, debug=False)