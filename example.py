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

assert resp.status == 200


#
# Add access token 
#

access_token = resp.data.access_token
auth = 'Bearer ' + access_token
client._Client__s.headers['Authorization'] = auth

#
# Get the list of Study Definitions
#

resp = client.request(app.op['findStudyDefinitions'](authorization=auth))

assert resp.status == 200

print(resp.data)


#
# Get the list of Users
#

resp = client.request(app.op['findUsers'](authorization=auth))

assert resp.status == 200

print(resp.data)


#
# Add a new Study Definition
#

new_study = dict(study_definition=dict(title='Newly created from Python', principal_investigator_user_id=0))
resp = client.request(app.op['addStudy'](authorization=auth, study=new_study))

assert resp.status == 201


new_study = resp.data

print(new_study)

#
# Add a new Protocol Definition
#

new_protocol_definition = dict(protocol_definition=dict(name='Newly created from Python', definition_data="foo"))
resp = client.request(app.op['addProtocolDefinition'](authorization=auth, protocol_definition=new_protocol_definition, study_definition_id=new_study.id))

assert resp.status == 201


new_protocol_definition = resp.data

print(new_protocol_definition)

#
# Add a new Phase Definition
#

new_phase_definition = dict(phase_definition=dict(name='Newly created from Python', definition_data="foo"))
resp = client.request(app.op['addPhaseDefinition'](authorization=auth, phase_definition=new_phase_definition, study_definition_id=new_study.id, protocol_definition_id=new_protocol_definition.id))

assert resp.status == 201


new_phase_definition = resp.data

print(new_phase_definition)



#
# Delete Study Definition
#

resp = client.request(app.op['deleteStudyDefinition'](id=new_study.id))

assert resp.status == 204




