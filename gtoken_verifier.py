from google.oauth2 import id_token
from google.auth.transport import requests

class GTokenVerify(object):

    def check_token(self, users_token, client_id):
        token = users_token

        idinfo = id_token.verify_oauth2_token(token, requests.Request(), client_id)

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            return ValueError("Wrong issuer")
        else:
            return idinfo
