#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 27 15:31:51 2021

@author: root
"""

import sys

sys.path.append("../client-api/")

import pprint
import glob
import os

from examples_base import parse_command_line_args
from pyelicit import elicit
from random import shuffle

NUM_REGISTERED_USERS = 0
NUM_ANONYMOUS_USERS = 10
NUM_AUTO_CREATED_USERS = 10

FontSize = '20'

## Stimuli URLs
#video_mp4_url = 'https://cdn.muse.ai/w/1d51a75d0e66f71ac1be9adabe7109a9675a1bf7e8639389569258c5d255b5d7/videos/video.mp4'
video_youtube_url = 'https://youtu.be/zr9leP_Dcm8'
video_mp4_url = '/application/Images/sample_640x360.mp4'

##
## MAIN
##

pp = pprint.PrettyPrinter(indent=4)

# get the elicit object to define the experiment
elicit_object = elicit.Elicit(parse_command_line_args())

# Double-check that we have the right user: we need to be admin to create a study
#user_admin = elicit_object.assert_investigator()
user_admin = elicit_object.assert_admin()

#
# Add a new Study Definition
#

# Define study
study_definition_description = dict(title='Movie task',
                                    description="""In this experiment we will test the perception of certain aspects of movies""",
                                    version=1,
                                    lock_question=1,
                                    enable_previous=1,
                                    allow_anonymous_users=(NUM_AUTO_CREATED_USERS > 0 or NUM_ANONYMOUS_USERS > 0),
                                    # allow taking the study without login
                                    max_auto_created_users=NUM_AUTO_CREATED_USERS,  # up to ten workerId created users
                                    show_in_study_list=False,  # show in the (public) study list for anonymous protocols
                                    footer_label="If you have any questions, you can email {{link|mailto:neuroccny@gmail.com|here}}",
                                    redirect_close_on_url='https://app.prolific.co',
                                    data="Put some data here, we don't really care about it.",
                                    principal_investigator_user_id=user_admin.id)

study_object = elicit_object.add_study(study=dict(study_definition=study_definition_description))

#
# Create a Protocol Definition
#

# Define protocol
protocol_definition_descriptiopn = dict(name='Movie task',
                                        definition_data="whatever you want here",
                                        summary="where",
                                        description='In this experiment we will ask about your impression of a short movie clip',
                                        active=True)

# Add protocol
protocol_object = elicit_object.add_protocol_definition(
    protocol_definition=dict(protocol_definition=protocol_definition_descriptiopn),
    study_definition_id=study_object.id)

#
# Add users to protocol
#

# Get a list of users who can participate in the study (the ones that have already registered in the system)
users = elicit_object.get_all_users()

# find registered users
study_participants = list(filter(lambda usr: usr.role == 'anonymous_user', users))

# add users to protocol
elicit_object.add_users_to_protocol(study_object, protocol_object, study_participants)

#
# Add Phase Definition for testing RadiobuttonGroup with stimuli
#
phases = []
trials = []

trials_stimuli = []

# Define phase
phase_definition_description = dict(
    phase_definition=dict(name='Video phase with questions', definition_data=dict(PhaseType='Video and questions')))

# Add phase
phase_object = elicit_object.add_phase_definition(phase_definition=phase_definition_description,
                                                  study_definition_id=study_object.id,
                                                  protocol_definition_id=protocol_object.id)
phases.append(phase_object)

#
# TRIAL 2: Video stimulus hack with hidden radiobutton group
#

# Trial definition col order
trial_definition_specification = dict(
    trial_definition=dict(name='Please watch the video below', definition_data=dict(TrialType='RadiobuttonGroup page')))

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
                                                    Header=dict(
                                                        HeaderLabel='{{center|Please watch the video below}}')))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id,
                                               trial_definition_id=trial_object.id)

## hacky way of getting stimuli only
component_definition = dict(name='RadioButtonGroup',
                            definition_data=dict(
                                Instruments=[dict(
                                    Instrument=dict(
                                        RadioButtonGroup=dict(
                                            Layout='column',
                                            ColumnWidthPercent='0',
                                            QuestionsPerRow='1',
                                            HeaderLabel='Please use the small play button to start',
                                            IsOptional='1',
                                            Items=dict(Item=[]))))],
                                Stimuli=[dict(
                                    Label='Hacky way of doing stimuli only',
                                    Type='video/mp4',
                                    IsPausable=True,
                                    IsOptional=False,
                                    URI=video_mp4_url)]))

component_object = elicit_object.add_component(component=dict(component=component_definition),
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id,
                                               trial_definition_id=trial_object.id)

#
# TRIAL 2: Video stimulus alone that doesn't work
#

# Trial definition col order
trial_definition_specification = dict(
    trial_definition=dict(name='Stimuli', definition_data=dict(TrialType='Video stimuli')))

trial_object = elicit_object.add_trial_definition(trial_definition=trial_definition_specification,
                                                  study_definition_id=study_object.id,
                                                  protocol_definition_id=protocol_object.id,
                                                  phase_definition_id=phase_object.id)
# save trial to later define trial orders
trials_stimuli.append(trial_object)

# Component definition: Header Label
component_definition_description = dict(name='HeaderLabel',
                                        definition_data=dict(
                                            Instruments=[dict(
                                                Instrument=dict(
                                                    Header=dict(
                                                        HeaderLabel='{{center|Please watch the video below}}')))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id,
                                               trial_definition_id=trial_object.id)

# Video 1
component_definition = dict(name='SoloTimulus',
                            definition_data=dict(
                                Stimuli=[dict(
                                    Label='',
                                    Type='video/mp4',
                                    Width='50',
                                    Height='50',
                                    IsPausable=True,
                                    IsOptional=False,
                                    URI=video_mp4_url
                                )]))

component_object = elicit_object.add_component(component=dict(component=component_definition),
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id,
                                               trial_definition_id=trial_object.id)

# %% Add a new Phase Order

phase_sequence_data = ",".join([str(phase_definition.id) for phase_definition in phases])

phase_order_specification = dict(phase_order=dict(sequence_data=phase_sequence_data,
                                                  user_id=user_admin.id))

phase_order_object = elicit_object.add_phase_order(phase_order=phase_order_specification,
                                                   study_definition_id=study_object.id,
                                                   protocol_definition_id=protocol_object.id)

# print some basic details about the experiment
print('Study id: ' + str(study_object.id))
print('Protocol id: ' + str(str(protocol_object.id)))
print('Phase ids: ', end='')
for phase_id in range(0, len(phases)):
    print(str(phases[phase_id].id) + ', ', end='')
print('')
print('Trial ids: ', end='')
for trial_id in range(0, len(trials)):
    print(str(trials[trial_id].id) + ', ', end='')
print('')

print('Added ' + str(len(study_participants)) + ' users to the protocol')
print('User ids: ', end='')
for user_id in range(0, len(study_participants)):
    print(str(study_participants[user_id].id) + ', ', end='')
print('')
# print(('https://elicit.compute.dtu.dk/api/v1/study_definitions/' + str(study_object.id) + '/protocol_definitions/' + str(protocol_object.id) + '/preview?phase_definition_id='  + str(phases[0].id) + '&trial_definition_id=' + str(trials[0].id)))

print('Study link: ', end='')
print(('https://elicit-experiment.com/studies/' + str(study_object.id) + '/protocols/' + str(protocol_object.id)))
