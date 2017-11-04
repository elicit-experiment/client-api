"""
Example for dumping the results of a study.
"""

import pprint
import sys
import json
import pyelicit

##
## MAIN
##

pp = pprint.PrettyPrinter(indent=4)

#elicit = pyelicit.Elicit(pyelicit.ElicitCreds(), 'http://localhost:3000')
elicit = pyelicit.Elicit()

#
# Login admin user to get study results
#
client = elicit.login()

# Define and validate component definitions
component_definitions_json = [
'''{
  "Header": {
    "Inputs": {
      "HeaderLabel": "Freetext test"
    } 
  },
  "Freetext": {
    "Inputs": {
      "Instrument": {
        "BoxHeight": null, 
        "Resizable": null, 
        "BoxWidth": null, 
        "LabelPosition": "top", 
        "Label": "Only digits here (LabelPosition=top)", 
        "Validation": "^[0-9]+$"
      }
    }
  }
}
''','''\
{
  "Header": {
    "Inputs": {
      "HeaderLabel": "Thank you for your participation"
    }
  }
}\
''',
'{"EndOfExperiment": {}}',
]

component_definitions = map(lambda j: json.loads(j), component_definitions_json)

pp.pprint(component_definitions)

#
# Double-check that we have the right user
#
resp = client.request(elicit['getCurrentUser']())

assert resp.status == 200

print("Current User:")
pp.pprint(resp.data)

user = resp.data

assert(resp.data.role == 'admin') # must be admin!


#
# Get list of users who will use the study
#

resp = client.request(elicit['findUsers']())

assert resp.status == 200

registered_users = list(filter(lambda x: x.role == 'registered_user', resp.data))

#
# Add a new Study Definition
#
study_definition = dict(title='Newly created from Python',
                        description='Fun study created with Python',
                        version=1,
                        lock_question=1,
                        enable_previous=1,
                        no_of_trials=5,
                        footer_label="This is the footer of the study",
                        redirect_close_on_url=elicit.api_url+"/participant",
                        data="Put some data here, we don't really care about it.",
                        principal_investigator_user_id=user.id)
new_study = dict(study_definition=study_definition)
resp = client.request(elicit['addStudy'](study=new_study))
assert resp.status == 201


new_study = resp.data
print("\n\nCreated new study:\n")
pp.pprint(new_study)

#
# Add a new Protocol Definition
#

new_protocol_definition = dict(protocol_definition=dict(name='Newly created protocol definition from Python',
                                                        definition_data="foo",
                                                        active=True))
resp = client.request(elicit['addProtocolDefinition'](protocol_definition=new_protocol_definition,
                                                      study_definition_id=new_study.id))

assert resp.status == 201


new_protocol_definition = resp.data
print("\n\nCreated new protocol:\n")
pp.pprint(new_protocol_definition)


#
# Add user to protocol
#

for user in registered_users:
  pp.pprint(user)
  protocol_user = dict(protocol_user=dict(user_id=user.id,
                                          study_definition_id=new_study.id,
                                          protocol_definition_id=new_protocol_definition.id))
  resp = client.request(elicit['addProtocolUser'](
                                                  protocol_user=protocol_user,
                                                  study_definition_id=new_study.id,
                                                  protocol_definition_id=new_protocol_definition.id))

  assert resp.status == 201

#
# Add a new Phase Definition
#

new_phase_definition = dict(phase_definition=dict(definition_data="foo"))
resp = client.request(elicit['addPhaseDefinition'](phase_definition=new_phase_definition,
                                                   study_definition_id=new_study.id,
                                                   protocol_definition_id=new_protocol_definition.id))

assert resp.status == 201

new_phase_definition = resp.data
print("\n\nCreated new phase:\n")
pp.pprint(new_phase_definition)

#
# Add a new Phase Order
#

new_phase_order = dict(phase_order=dict(sequence_data="0",
                                        user_id=user.id))
resp = client.request(elicit['addPhaseOrder'](
                                              phase_order=new_phase_order,
                                              study_definition_id=new_study.id,
                                              protocol_definition_id=new_protocol_definition.id))
assert resp.status == 201

new_phase_order = resp.data
print("\n\nCreated new phase order:\n")
pp.pprint(new_phase_order)

#
# Add a new Trial Definition
#

new_trial_definition = dict(trial_definition=dict(definition_data="foo"))
resp = client.request(elicit['addTrialDefinition'](trial_definition=new_trial_definition,
                                                   study_definition_id=new_study.id,
                                                   protocol_definition_id=new_protocol_definition.id,
                                                   phase_definition_id=new_phase_definition.id))

assert resp.status == 201

new_trial_definition = resp.data
print("\n\nCreated new trial definition:\n")
pp.pprint(new_trial_definition)

trials = [new_trial_definition]

#
# Add a new Trial Order
#

new_trial_order = dict(trial_order=dict(sequence_data=",".join([str(x) for x in range(len(trials))]),
                                        user_id=user.id))
resp = client.request(elicit['addTrialOrder'](
                                              trial_order=new_trial_order,
                                              study_definition_id=new_study.id,
                                              protocol_definition_id=new_protocol_definition.id,
                                              phase_definition_id=new_phase_definition.id))

assert resp.status == 201

new_trial_order = resp.data
print("\n\nCreated new trial order:\n")
pp.pprint(new_trial_order)

#
# Add a new Component
#



for component_definition in component_definitions_json:

      new_component = dict(component=dict(name='Newly created component definition from Python',
                                          definition_data=component_definition))
      resp = client.request(elicit['addComponent'](component=new_component,
                                                   study_definition_id=new_study.id,
                                                   protocol_definition_id=new_protocol_definition.id,
                                                   phase_definition_id=new_phase_definition.id,
                                                   trial_definition_id=new_trial_definition.id))
      print("\n\nCreated new phase component:\n")
      assert resp.status == 201


      new_component = resp.data

      pp.pprint(new_component)


new_stimulus = dict(stimulus=dict(name='Newly created stimulus definition from Python', definition_data="foo"))
resp = client.request(elicit['addStimulus'](stimulus=new_stimulus, study_definition_id=new_study.id, protocol_definition_id=new_protocol_definition.id, phase_definition_id=new_phase_definition.id, trial_definition_id=new_trial_definition.id))
print("\n\nCreated new phase stimulus:\n")
assert resp.status == 201


new_component = resp.data

pp.pprint(new_component)


#
# Delete Study Definition
#

#resp = client.request(elicit['deleteStudyDefinition'](id=3))
#assert resp.status == 204




