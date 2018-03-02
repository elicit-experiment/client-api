"""
Example for dumping the results of a study.
"""

import pprint
#import pdprint

import sys
import json
import lorem    # generate boilerplate text to make sure the website renders correctly
import re

from examples_default import *

from http import HTTPStatus

##
## MAIN
##

pp = pprint.PrettyPrinter(indent=4)

#
# Load trial definitions
#
trial_definitions_file = 'likertscaletest.xml.py'
trial_components = load_trial_definitions(trial_definitions_file)


elicit = ElicitClientApi()

#
# Double-check that we have the right user
#

user = assert_admin(elicit.client, elicit.elicit_api)

#
# Get list of users who will use the study
#

users = elicit.get_all_users()

study_participants = list(filter(lambda user: user.role == 'registered_user', users))

#
# Add a new Study Definition
#
study_definition = dict(title='Newly created from Python: create_study_example.py',
                        description='Fun study created with Python ' + lorem.paragraph(),
                        version=1,
                        lock_question=1,
                        enable_previous=1,
                        footer_label="This is the footer of the study",
                        redirect_close_on_url=elicit.elicit_api.api_url+"/participant",
                        data="Put some data here, we don't really care about it.",
                        principal_investigator_user_id=user.id)
args = dict(study=dict(study_definition=study_definition))
new_study = elicit.add_obj("addStudy", args)

#
# Add a new Protocol Definition
#

new_protocol_definition = dict(name='Newly created protocol definition from Python',
                               definition_data="foo",
                               summary=lorem.sentence(),
                               description=lorem.paragraph(),
                               active=True)
args = dict(protocol_definition=dict(protocol_definition=new_protocol_definition),
            study_definition_id=new_study.id)
new_protocol = elicit.add_obj("addProtocolDefinition", args)


#
# Add users to protocol
#

elicit.add_users_to_protocol(new_study, new_protocol, study_participants)


# generate two phases for example
phase_definitions = []
for phase_idx in range(2):
      #
      # Add a new Phase Definition
      #

      new_phase_definition = dict(phase_definition=dict(definition_data="foo"))
      args = dict(phase_definition=new_phase_definition,
                  study_definition_id=new_study.id,
                  protocol_definition_id=new_protocol.id)

      new_phase = elicit.add_obj("addPhaseDefinition", args)
      phase_definitions = [new_phase]

      trials = []

      # generate two trials for example
      for trial_idx in range(len(trial_components)):
            #
            # Add a new Trial Definition
            #

            new_trial_definition = dict(trial_definition=dict(definition_data="foo"))
            args = dict(trial_definition=new_trial_definition,
                        study_definition_id=new_study.id,
                        protocol_definition_id=new_protocol.id,
                        phase_definition_id=new_phase.id)
            new_trial_definition=elicit.add_obj("addTrialDefinition", args)
            trials.append(new_trial_definition)

            #
            # Add a new Component
            #

            for idx, component_definition in enumerate(trial_components[trial_idx]):

                  new_component = dict(name='Newly created component definition from Python',
                                       definition_data=json.dumps(component_definition))
                  args=dict(component = dict(component = new_component),
                            study_definition_id = new_study.id,
                            protocol_definition_id = new_protocol.id,
                            phase_definition_id = new_phase.id,
                            trial_definition_id = new_trial_definition.id)
                  new_component=elicit.add_obj("addComponent", args)


      #
      # Add a new Trial Order
      #

      new_trial_order = dict(trial_order=dict(sequence_data=",".join([str(trial.id) for trial in trials]),
                                              user_id=study_participants[0].id))
      args=dict(trial_order=new_trial_order,
                study_definition_id=new_study.id,
                protocol_definition_id=new_protocol.id,
                phase_definition_id=new_phase.id)
      new_trial_order=elicit.add_obj("addTrialOrder", args)


#
# Add a new Phase Order
#

phase_sequence_data = ",".join(
    [str(phase_definition.id) for phase_definition in phase_definitions])
new_phase_order = dict(phase_order=dict(sequence_data=phase_sequence_data,
                                        user_id=user.id))
args = dict(phase_order=new_phase_order,
          study_definition_id=new_study.id,
          protocol_definition_id=new_protocol.id)
new_phase_order = elicit.add_obj("addPhaseOrder", args)





