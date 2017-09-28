from pyswagger import App, Security
from pyswagger.contrib.client.requests import Client
from pyswagger.utils import jp_compose

public_client_id = 'admin_public'
public_client_secret = 'czZCaGRSa3F0MzpnWDFmQmF0M2JW'

# load Swagger resource file into App object
app = App._create_('http://localhost:3000/apidocs/v1/swagger.json')

auth = Security(app)
#auth.update_with('api_key', 'admin_public') # api key
#auth.update_with('petstore_auth', 'czZCaGRSa3F0MzpnWDFmQmF0M2JW') # oauth2

# init swagger client
client = Client(auth)

# a request to create a new pet
auth_request=dict(client_id=public_client_id, client_secret=public_client_secret, grant_type='password', email='foo5@bar.com', password='abcd12_') 
print(auth_request)
# making a request
resp = client.request(app.op['getAuthToken'](auth_request=auth_request))

# Status
assert resp.status == 200

access_token = resp.data.access_token

client._Client__s.headers['Authorization'] = 'Bearer ' + access_token

resp = client.request(app.op['findStudyDefinitions']())

# Status
assert resp.status == 200

print(resp.data)

new_study = dict(study_definition=dict(title='Newly created from Python', principal_investigator_user_id=0))
resp = client.request(app.op['addStudy'](study=new_study))

assert resp.status == 201

print(resp.data)


