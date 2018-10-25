from google.oauth2 import id_token
from google.auth.transport import requests

class GTokenValidator(object):

    def check_token(self, users_token, client_id):
        token = users_token

        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), client_id)

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError("Wrong issuer")
            else:
                return idinfo
        except:
            return "Token from user not verified"
