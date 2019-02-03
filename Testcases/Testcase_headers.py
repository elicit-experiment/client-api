"""
Testcase for headers
"""

import sys
sys.path.append("../")

import pprint
import sys
import csv
import json

from examples_base import parse_command_line_args
from pyelicit import elicit
from random import shuffle

##
## MAIN
##

pp = pprint.PrettyPrinter(indent=4)

# get the elicit object to define the experiment
elicit_object = elicit.Elicit(parse_command_line_args())


# Double-check that we have the right user: we need to be admin to create a study
user_admin = elicit_object.assert_admin()

#
# Add a new Study Definition
#

# Define study
study_definition_description = dict(title='Headers test',
                        description="""This study attempts to display basic functionalities of the Elicit framework""",
                        version=1,
                        lock_question=1,
                        enable_previous=1,
                        allow_anonymous_users=True,  # allow taking the study without login
                        show_in_study_list=True,  # show in the (public) study list for anonymous protocols
                        footer_label="If you have any questions, you can email {{link|mailto:neuroccny@gmail.com|here}}",
                        redirect_close_on_url=elicit_object.elicit_api.api_url + "/participant",
                        data="Put some data here, we don't really care about it.",
                        principal_investigator_user_id=user_admin.id)


study_object = elicit_object.add_study(study=dict(study_definition=study_definition_description))

#
# Create a Protocol Definition
#

# Define protocol
protocol_definition_descriptiopn = dict(name='Headers test',
                               definition_data="whatever you want here",
                               summary="This summary will be shown on the webpage? \n This is a test to show off all the capabilities of Elicit",
                               description='This is a detailed account of what the experiment will inbolve. \n All the components and functionality of Elicit will be displayed here',
                               active=True)

# Add protocol
protocol_object = elicit_object.add_protocol_definition(protocol_definition=dict(protocol_definition=protocol_definition_descriptiopn),
                                          study_definition_id=study_object.id)


#
# Add users to protocol
#

# Get a list of users who can participate in the study (the ones that have already registered in the system)
users = elicit_object.get_all_users()

# find registered users
study_participants = list(filter(lambda usr: usr.role == 'registered_user', users))

# add users to protocol
elicit_object.add_users_to_protocol(study_object, protocol_object, study_participants)

#
# Add Phase Definition
#

# Define phase
phase_definition_description = dict(phase_definition=dict(definition_data="First phase of the experiment"))

# Add phase
phase_object = elicit_object.add_phase_definition(phase_definition=phase_definition_description,
                                    study_definition_id=study_object.id,
                                    protocol_definition_id=protocol_object.id)

#only define a single phase for this experiment
phases = [phase_object]

trials = []



#%% Trial 1: Welcome slide


# Trial definition
trial_definition_specification = dict(trial_definition=dict(definition_data='Welcome page'))
trial_object = elicit_object.add_trial_definition(trial_definition=trial_definition_specification,
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id)
# save trial to later define trial orders
trials.append(trial_object)



# Component definition: Header Label
component_definition_description = dict(name='HeaderLabel',
                                        definition_data=dict(
                                                Instruments=[dict(
                                                        Instrument=dict(
                                                                Header=dict(HeaderLabel='{{center|Welcome to this experiment}}')))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)



#%% Trial 2: Demographic slide


# Trial definition
trial_definition_specification =  dict(trial_definition=dict(name='Demographics page', definition_data=dict(TrialType='Demographics')))
trial_object = elicit_object.add_trial_definition(trial_definition=trial_definition_specification,
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id)

# save trial to later define trial orders
trials.append(trial_object)

# Component definition: Header Label
component_definition_description = dict(name='HeaderLabel',
                                        definition_data=dict(
                                                Instruments=[dict(
                                                        Instrument=dict(
                                                                Header=dict(HeaderLabel='{{center|Demographics}}')))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)



#%% Trial 3: End of experiment page

# Trial definition
trial_definition_specification =  dict(trial_definition=dict(name='End of experiment', definition_data=dict(TrialType='EOE')))
trial_object = elicit_object.add_trial_definition(trial_definition=trial_definition_specification,
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id)

# save trial to later define trial orders
trials.append(trial_object)


# Component definition: Header Label
component_definition_description = dict(name='HeaderLabel',
                            definition_data=dict(
                                    Instruments=[dict(
                                            Instrument=dict(
                                                    Header=dict(HeaderLabel='{{center|Thank you for your participation}}')))]))

# Component addition: add the component to the trial
new_component = elicit_object.add_component(component=dict(component=component_definition_description),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)



component_definition_description = dict(name='End of experiment',
                            definition_data=dict(
                                    Instruments=[dict(
                                            Instrument=dict(
                                                    EndOfExperiment=dict()))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id,
                                               trial_definition_id=trial_object.id)

#%% Add Trial Orders to the study

#trail_orders for specific users
for study_participant in study_participants:
    trial_order_specification_user = dict(trial_order=dict(sequence_data=",".join([str(trial.id) for trial in trials]),user_id=study_participant.id))
    print(trial_order_specification_user)
    
    # Trial order addition
    trial_order_object = elicit_object.add_trial_order(trial_order=trial_order_specification_user,
                                                       study_definition_id=study_object.id,
                                                       protocol_definition_id=protocol_object.id,
                                                       phase_definition_id=phase_object.id)
#trail_orders for anonymous users
for anonymous_participant in range(0,10):
    trial_id = [int(trial.id) for trial in trials]
    shuffle(trial_id)

    trial_order_specification_anonymous = dict(trial_order=dict(sequence_data=",".join(map(str,trial_id))))
    print(trial_order_specification_anonymous)
    
    # Trial order addition
    trial_order_object = elicit_object.add_trial_order(trial_order=trial_order_specification_anonymous,
                                                       study_definition_id=study_object.id,
                                                       protocol_definition_id=protocol_object.id,
                                                       phase_definition_id=phase_object.id)
    


#%% Add a new Phase Order
phase_sequence_data = ",".join([str(phase_definition.id) for phase_definition in phases])

phase_order_specification = dict(phase_order=dict(sequence_data=phase_sequence_data,
                                               user_id=user_admin.id))

phase_order_object = elicit_object.add_phase_order(phase_order=phase_order_specification,
                                     study_definition_id=study_object.id,
                                     protocol_definition_id=protocol_object.id)

# print some basic details about the experiment
print('Study id: ' + str(study_object.id))
print('Protocol id: ' + str(str(protocol_object.id)))
print('Phase ids: ' , end='')
for phase_id in range(0, len(phases)):
    print(str(phases[phase_id].id) + ', ', end='')
print('')
print('Trial ids: ' , end='')
for trial_id in range(0, len(trials)):
    print(str(trials[trial_id].id) + ', ', end='')
print('')    

print('Added ' + str(len(study_participants)) + ' users to the protocol')
print('User ids: ', end='')
for user_id in range(0, len(study_participants)):
    print(str(study_participants[user_id].id) + ', ', end='')
print('')
#print(('https://elicit.compute.dtu.dk/api/v1/study_definitions/' + str(study_object.id) + '/protocol_definitions/' + str(protocol_object.id) + '/preview?phase_definition_id='  + str(phases[0].id) + '&trial_definition_id=' + str(trials[0].id)))    

print('Study link: ', end='')
print(('https://elicit.compute.dtu.dk/studies/' + str(study_object.id) + '/protocols/'  + str(protocol_object.id)))




