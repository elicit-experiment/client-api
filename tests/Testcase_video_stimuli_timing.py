# -*- coding: utf-8 -*-
"""
Example testing timing of the Video player
"""

import pprint
import sys
import csv
import json

from pyelicit.command_line import parse_command_line_args
from pyelicit import elicit
from random import shuffle

##
## MAIN
##

NUM_ANONYMOUS_USERS = 10
NUM_REGISTERED_USERS = 0

pp = pprint.PrettyPrinter(indent=4)

# get the elicit object to define the experiment
elicit_object = elicit.Elicit(parse_command_line_args())

# Double-check that we have the right user: we need to be admin to create a study
user_investigator = elicit_object.assert_investigator()

#
# Add a new Study Definition
#

# Define study
study_definition_description = dict(title='Video timing test',
                        description="""This is a test of the timing of the video player""",
                        version=1,
                        lock_question=1,
                        enable_previous=1,
                        allow_anonymous_users=True,  # allow taking the study without login
                        show_in_study_list=False,  # show in the (public) study list for anonymous protocols
                        footer_label="If you have any questions, you can email {{link|mailto:neuroccny@gmail.com|here}}",
                        redirect_close_on_url=elicit_object.elicit_api.api_url + "/participant",
                        data="Put some data here, we don't really care about it.",
                        principal_investigator_user_id=user_investigator.id)


study_object = elicit_object.add_study(study=dict(study_definition=study_definition_description))

#
# Create a Protocol Definition
#

# Define protocol
protocol_definition_descriptiopn = dict(name='Video timing test',
                               definition_data="whatever you want here",
                               summary="This is a test of the video player",
                               description='This is a test of the video player',
                               active=True)

# Add protocol
protocol_object = elicit_object.add_protocol_definition(protocol_definition=dict(protocol_definition=protocol_definition_descriptiopn),
                                          study_definition_id=study_object.id)


#
# Add users to protocol
#

# Get a list of users who can participate in the study (the ones that have already registered in the system)

study_participants = elicit_object.ensure_users(NUM_REGISTERED_USERS, NUM_ANONYMOUS_USERS)

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


#%% Trial 1: Short duration video

# Trial definition
trial_definition_specification = dict(trial_definition=dict(name='Short duration video', definition_data=dict(TrialType='Video page')))
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
                                                                Header=dict(HeaderLabel='{{center|Short duration video}}')))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)



# Video 1
butterfly_video_url = 'https://youtu.be/zr9leP_Dcm8'
video_component_definition = dict(name='This video is pausable',
                            definition_data=dict(
                                    Stimuli=[dict(
                                            Label='This video is pausable',
                                            Type='video/youtube',
                                            IsPausable=False,
                                            URI=butterfly_video_url)]))

component_object = elicit_object.add_component(component=dict(component=video_component_definition),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)

#%% Trial 2: Long duration video

# Trial definition
trial_definition_specification = dict(trial_definition=dict(name='Long duration video', definition_data=dict(TrialType='Video page')))
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
                                                                Header=dict(HeaderLabel='{{center|Long duration video}}')))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)



# Video 1
stars_video_url = 'https://youtu.be/soTEnpcn0ig'
video_component_definition = dict(name='This video is pausable',
                            definition_data=dict(
                                    Stimuli=[dict(
                                            Label='This video is pausable',
                                            Type='video/youtube',
                                            IsPausable=False,
                                            URI=stars_video_url)]))

component_object = elicit_object.add_component(component=dict(component=video_component_definition),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)

#%% Trial 5: End of experiment page

# Trial definition
trial_definition_specification = dict(trial_definition=dict(name='End of experiment', definition_data=dict(TrialType='EOE')))
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
    
    # Trial order addition
    trial_order_object = elicit_object.add_trial_order(trial_order=trial_order_specification_user,
                                                       study_definition_id=study_object.id,
                                                       protocol_definition_id=protocol_object.id,
                                                       phase_definition_id=phase_object.id)
#trail_orders for anonymous users
for anonymous_participant in range(0,10):
    trial_order_specification_anonymous = dict(trial_order=dict(sequence_data=",".join([str(trial.id) for trial in trials])))
    
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