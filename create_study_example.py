"""
Example for dumping the results of a study.
"""

import pprint
import sys
import json
import pyelicit
import lorem

import examples_default

##
## MAIN
##

pp = pprint.PrettyPrinter(indent=4)

examples_default.parser.add_argument('--active', default=False, help="The study is active and visible to participants.")
args = examples_default.parse_command_line_args()
elicit = pyelicit.Elicit(pyelicit.ElicitCreds(), args.apiurl, examples_default.send_opt)

#
# Login admin user to get study results
#
client = elicit.login()

# Define and validate component definitions
component_definitions_json = [
      [
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
'''],[
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
'''],['''\
{
  "Header": {
    "Inputs": {
      "HeaderLabel": "Thank you for your participation"
    }
  }
}\
''',
'{"EndOfExperiment": {}}'],
]

for cd in component_definitions_json:
  component_definitions = map(lambda j: json.loads(j), cd)

  pp.pprint(component_definitions)

#
# Double-check that we have the right user
#

user = examples_default.assert_admin(client, elicit)

#
# Get list of users who will use the study
#

resp = client.request(elicit['findUsers']())

assert resp.status == 200

registered_users = list(filter(lambda x: x.role == 'registered_user', resp.data))

#
# Add a new Study Definition
#
study_definition = dict(title='Newly created from Python: create_study_example.py',
                        description='Fun study created with Python ' + lorem.paragraph(),
                        version=1,
                        lock_question=1,
                        enable_previous=1,
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
                                                        summary=lorem.sentence(),
                                                        description=lorem.paragraph(),
                                                        active=args.active))
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


phase_definitions = []

# generate two phases for example
for phase_idx in range(2):
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

      phase_definitions.append(new_phase_definition)

      trials = []

      # generate two trials for example
      for trial_idx in range(len(component_definitions_json)):
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

            trials.append(new_trial_definition)

            #
            # Add a new Component
            #

            for component_definition in component_definitions_json[trial_idx]:

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


      new_stimulus = resp.data

      pp.pprint(new_stimulus)

      #
      # Add a new Trial Order
      #

      new_trial_order = dict(trial_order=dict(sequence_data=",".join([str(trial.id) for trial in trials]),
                                              user_id=registered_users[0].id))
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
# Add a new Phase Order
#

new_phase_order = dict(phase_order=dict(sequence_data=",".join([str(phase_definition.id) for phase_definition in phase_definitions]),
                                        user_id=registered_users[0].id))
resp = client.request(elicit['addPhaseOrder'](
                                              phase_order=new_phase_order,
                                              study_definition_id=new_study.id,
                                              protocol_definition_id=new_protocol_definition.id))
assert resp.status == 201

new_phase_order = resp.data
print("\n\nCreated new phase order:\n")
pp.pprint(new_phase_order)




