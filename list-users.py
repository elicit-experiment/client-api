import xml.etree.cElementTree as ET
import json
from collections import defaultdict
import pprint
from pyswagger import App, Security
from pyswagger.contrib.client.requests import Client
from pyswagger.utils import jp_compose
import sys

pp = pprint.PrettyPrinter(indent=4)

public_client_id = 'admin_public'
public_client_secret = 'czZCaGRSa3F0MzpnWDFmQmF0M2JW'

app = App._create_('http://localhost:3000/apidocs/v1/swagger.json')
# init swagger client
client = Client(Security(app))

# a request to create a new pet
auth_request=dict(client_id=public_client_id,
                  client_secret=public_client_secret,
                  grant_type='password',
                  email='admin@elicit.com',
                  password='password') 
resp = client.request(app.op['getAuthToken'](auth_request=auth_request))

assert resp.status == 200

access_token = resp.data.access_token
auth = 'Bearer ' + access_token

resp = client.request(app.op['findUsers'](authorization=auth))

assert resp.status == 200

pp.pprint(resp.data)

registered_users = list(filter(lambda x: x.role == 'registered_user', resp.data))

pp.pprint(registered_users)