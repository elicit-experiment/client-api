"""
Elicit client module for Python
"""

import json
from collections import defaultdict
import pprint
from pyswagger import App, Security
from pyswagger.contrib.client.requests import Client
from pyswagger.utils import jp_compose
import sys


# HACK to work around self-signed SSL certs used in development
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context


class ElicitCreds:
  """
  Class defining credentials to communicate with the Elicit service
  """
  PUBLIC_CLIENT_ID = 'admin_public'
  PUBLIC_CLIENT_SECRET = 'czZCaGRSa3F0MzpnWDFmQmF0M2JW'
  ADMIN_USER = 'admin@elicit.dk'
  ADMIN_PASSWORD = 'password'

  def __init__(self, _admin_user = ADMIN_USER, _admin_password = ADMIN_PASSWORD, _public_client_id = PUBLIC_CLIENT_ID, _public_client_secret = PUBLIC_CLIENT_SECRET):
    """
    Initialize
    :param _admin_user: The (typically admin) user name
    :param _admin_password: The password
    :param _public_client_id: The OAuth Client ID
    :param _public_client_secret: The OAuth client secret
    :return: returns nothing
    """
    self.admin_user = _admin_user
    self.admin_password = _admin_password
    self.public_client_id = _public_client_id
    self.public_client_secret = _public_client_secret

class Elicit:
  PRODUCTION_URL = 'https://elicit.compute.dtu.dk'

  def __init__(self, creds = ElicitCreds(), api_url = PRODUCTION_URL):
    self.api_url = api_url
    self.app = App._create_(self.api_url + '/apidocs/v1/swagger.json')
    self.auth = Security(self.app)
    self.creds = creds

    # init swagger client
    self.client = Client(self.auth, send_opt=dict(verify=False)) # HACK to work around self-signed SSL certs used in development


  def login(self):
    """
    Login to Elicit using credentials specified in init
    :return: client with auth header added.
    """
    auth_request=dict(client_id=self.creds.public_client_id,
                      client_secret=self.creds.public_client_secret,
                      grant_type='password',
                      email=self.creds.admin_user,
                      password=self.creds.admin_password) 
    resp = self.client.request(self.app.op['getAuthToken'](auth_request=auth_request))

    assert resp.status == 200

    self.auth = resp.data
    self.auth_header = 'Bearer ' + self.auth.access_token
    self.client._Client__s.headers['Authorization'] = self.auth_header

    return self.client


  def __getitem__(self, op):
    return lambda **args: self.app.op[op](**( self.bind_auth(args) ) )

  def bind_auth(self, args):
    args.update(authorization = self.auth_header)
    return args
