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

new_protocol_definition = dict(protocol_definition=dict(name='Newly created protocol definition from Python', definition_data="foo"))
resp = client.request(app.op['addProtocolDefinition'](authorization=auth, protocol_definition=new_protocol_definition, study_definition_id=new_study.id))

assert resp.status == 201


new_protocol_definition = resp.data

print(new_protocol_definition)

#
# Add a new Phase Definition
#

new_phase_definition = dict(phase_definition=dict(name='Newly created phase definition from Python', definition_data="foo"))
resp = client.request(app.op['addPhaseDefinition'](authorization=auth, phase_definition=new_phase_definition, study_definition_id=new_study.id, protocol_definition_id=new_protocol_definition.id))

assert resp.status == 201


new_phase_definition = resp.data

print(new_phase_definition)

#
# Add a new Phase Order
#

new_phase_order = dict(phase_order=dict(name='Newly created phase order from Python', sequence_data="0", user_id=0))
resp = client.request(app.op['addPhaseOrder'](authorization=auth, phase_order=new_phase_order, study_definition_id=new_study.id, protocol_definition_id=new_protocol_definition.id))

assert resp.status == 201

new_phase_order = resp.data

print(new_phase_order)

#
# Add a new Trial Definition
#

new_trial_definition = dict(trial_definition=dict(name='Newly created trial definition from Python', definition_data="foo"))
resp = client.request(app.op['addTrialDefinition'](authorization=auth, trial_definition=new_trial_definition, study_definition_id=new_study.id, protocol_definition_id=new_protocol_definition.id, phase_definition_id=new_phase_definition.id))

assert resp.status == 201

new_trial_definition = resp.data

print(new_trial_definition)

#
# Add a new Trial Order
#

new_trial_order = dict(trial_order=dict(name='Newly created trial order from Python', sequence_data="0", user_id="0"))
resp = client.request(app.op['addTrialOrder'](authorization=auth, trial_order=new_trial_order, study_definition_id=new_study.id, protocol_definition_id=new_protocol_definition.id, phase_definition_id=new_phase_definition.id))

assert resp.status == 201

new_trial_order = resp.data

print(new_trial_order)

#
# Add a new Component
#

new_component = dict(component=dict(name='Newly created component definition from Python', definition_data="foo"))
resp = client.request(app.op['addComponent'](authorization=auth, component=new_component, study_definition_id=new_study.id, protocol_definition_id=new_protocol_definition.id, phase_definition_id=new_phase_definition.id, trial_definition_id=new_trial_definition.id))

assert resp.status == 201


new_component = resp.data

print(new_component)


new_stimulus = dict(stimulus=dict(name='Newly created stimulus definition from Python', definition_data="foo"))
resp = client.request(app.op['addStimulus'](authorization=auth, stimulus=new_stimulus, study_definition_id=new_study.id, protocol_definition_id=new_protocol_definition.id, phase_definition_id=new_phase_definition.id, trial_definition_id=new_trial_definition.id))

assert resp.status == 201


new_component = resp.data

print(new_component)


#
# Delete Study Definition
#

resp = client.request(app.op['deleteStudyDefinition'](id=new_study.id))

assert resp.status == 204




