# -*- coding: utf-8 -*-
"""
Example testing the components with stimuli and instruments
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

## Stimuli URLs
audio_url = "https://www.mfiles.co.uk/mp3-downloads/franz-liszt-liebestraum-3-easy-piano.mp3"
video_url = 'https://youtu.be/zr9leP_Dcm8'
##

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
study_definition_description = dict(title='Components with stimuli and instruments',
                        description="""This is a test of Components with stimuli and instruments""",
                        version=1,
                        lock_question=1,
                        enable_previous=1,
                        allow_anonymous_users=True,  # allow taking the study without login
                        show_in_study_list=False,  # show in the (public) study list for anonymous protocols
                        footer_label="If you have any questions, you can email {{link|mailto:neuroccny@gmail.com|here}}",
                        redirect_close_on_url=elicit_object.elicit_api.api_url + "/participant",
                        data="Put some data here, we don't really care about it.",
                        principal_investigator_user_id=user_admin.id)


study_object = elicit_object.add_study(study=dict(study_definition=study_definition_description))

#
# Create a Protocol Definition
#

# Define protocol
protocol_definition_descriptiopn = dict(name='Components with stimuli and instruments',
                               definition_data="whatever you want here",
                               summary="This is a test of Components with stimuli and instruments",
                               description='This is a test of Components with stimuli and instruments',
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
# Add Phase Definition for testing RadiobuttonGroup with stimuli
#
phases = []
trials = []

#%% RadiobuttonGroup

# Define phase
phase_definition_description = dict(phase_definition=dict(name='RadiobuttonGroup', definition_data=dict(PhaseType='RadiobuttonGroup')))

# Add phase
phase_object = elicit_object.add_phase_definition(phase_definition=phase_definition_description,
                                    study_definition_id=study_object.id,
                                    protocol_definition_id=protocol_object.id)
phases.append(phase_object)

#
# Trial 1: Radiobutton group
#

# Trial definition
trial_definition_specification = dict(trial_definition=dict(name='RadiobuttonGroup with Video Stimuli', definition_data=dict(TrialType='RadiobuttonGroup page')))

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
                                                                Header=dict(HeaderLabel='{{center|RadiobuttonGroup with Video Stimuli}}')))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)


## 13 answer options
component_definition = dict(name='RadioButtonGroup',
                            definition_data=dict(
                                    Instruments=[dict(
                                            Instrument=dict(
                                                    RadioButtonGroup=dict(
                                                            AlignForStimuli='0',
                                                            QuestionsPerRow='1',
                                                            HeaderLabel='This is a RadioButtonGroup with video stimuli',
                                                            IsOptional='0',
                                                            Items=dict(
                                                                    Item=[dict(Id='1',Label='answer 1',Selected='0',Correct=True),
                                                                          dict(Id='2',Label='answer 2',Selected='0',Correct=True),
                                                                          dict(Id='3',Label='answer 3',Selected='0',Correct=True),
                                                                          dict(Id='4',Label='answer 4',Selected='0',Correct=True),
                                                                          dict(Id='5',Label='answer 5',Selected='0',Correct=True),
                                                                          dict(Id='6',Label='answer 6',Selected='0',Correct=True),
                                                                          dict(Id='7',Label='answer 7',Selected='0',Correct=True),
                                                                          dict(Id='8',Label='answer 8',Selected='0',Correct=True),
                                                                          dict(Id='9',Label='answer 9',Selected='0',Correct=True),
                                                                          dict(Id='10',Label='answer 10',Selected='0',Correct=True),
                                                                          dict(Id='11',Label='answer 11',Selected='0',Correct=True),
                                                                          dict(Id='12',Label='answer 12',Selected='0',Correct=True),
                                                                          dict(Id='13',Label='answer 13',Selected='0',Correct=True)]))))], 
                                    Stimuli=[dict(
                                            Label='This video is pausable',
                                            Type='video/youtube',
                                            IsPausable=True,
                                            URI=video_url)]))
                        
component_object = elicit_object.add_component(component=dict(component=component_definition),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)


trial_definition_specification = dict(trial_definition=dict(name='RadiobuttonGroup with Audio Stimuli', definition_data=dict(TrialType='RadiobuttonGroup page')))

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
                                                                Header=dict(HeaderLabel='{{center|RadiobuttonGroup with Audio Stimuli}}')))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)

# 2 answer options
component_definition = dict(name='RadioButtonGroup',
                            definition_data=dict(
                                    Instruments=[dict(
                                            Instrument=dict(
                                                    RadioButtonGroup=dict(
                                                            AlignForStimuli='1',
                                                            HeaderLabel='Have you adjusted the volume appropriately?',
                                                            Items=dict(
                                                                    Item=[dict(Id='1',Label='yes',Selected='0'),
                                                                          dict(Id='2',Label='no',Selected='0')]))))],
                                    Stimuli=[dict(
                                            Label='Audio Excerpt',
                                            Type='audio/mpeg',
                                            IsPausable=True,
                                            URI=audio_url)]))
                        
component_object = elicit_object.add_component(component=dict(component=component_definition),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)

#%% CheckBoxGroup

# Define phase
phase_definition_description = dict(phase_definition=dict(name='CheckBoxGroup', definition_data=dict(PhaseType='CheckBoxGroup')))

# Add phase
phase_object = elicit_object.add_phase_definition(phase_definition=phase_definition_description,
                                    study_definition_id=study_object.id,
                                    protocol_definition_id=protocol_object.id)
phases.append(phase_object)

#
# Trial 1: CheckBoxGroup
#

# Trial definition
trial_definition_specification = dict(trial_definition=dict(name='CheckBoxGroup with Video Stimuli', definition_data=dict(TrialType='CheckBoxGroup page')))

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
                                                                Header=dict(HeaderLabel='{{center|CheckBoxGroup with Video Stimuli}}')))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)


## 13 answer options
component_definition = dict(name='CheckBoxGroup',
                            definition_data=dict(
                                    Instruments=[dict(
                                            Instrument=dict(
                                                    RadioButtonGroup=dict(
                                                            AlignForStimuli='1',
                                                            QuestionsPerRow='1',
                                                            HeaderLabel='This is a CheckBoxGroup with video stimuli',
                                                            MaxNoOfSelections='10',
                                                            MinNoOfSelections='2',
                                                            Items=dict(
                                                                    Item=[dict(Id='1',Label='answer 1',Selected='0',Correct=True),
                                                                          dict(Id='2',Label='answer 2',Selected='0',Correct=True),
                                                                          dict(Id='3',Label='answer 3',Selected='0',Correct=True),
                                                                          dict(Id='4',Label='answer 4',Selected='0',Correct=True),
                                                                          dict(Id='5',Label='answer 5',Selected='0',Correct=True),
                                                                          dict(Id='6',Label='answer 6',Selected='0',Correct=True),
                                                                          dict(Id='7',Label='answer 7',Selected='0',Correct=True),
                                                                          dict(Id='8',Label='answer 8',Selected='0',Correct=True),
                                                                          dict(Id='9',Label='answer 9',Selected='0',Correct=True),
                                                                          dict(Id='10',Label='answer 10',Selected='0',Correct=True),
                                                                          dict(Id='11',Label='answer 11',Selected='0',Correct=True),
                                                                          dict(Id='12',Label='answer 12',Selected='0',Correct=True),
                                                                          dict(Id='13',Label='answer 13',Selected='0',Correct=True)]))))], 
                                    Stimuli=[dict(
                                            Label='This video is pausable',
                                            Type='video/youtube',
                                            IsPausable=True,
                                            URI=video_url)]))
                        
component_object = elicit_object.add_component(component=dict(component=component_definition),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)


trial_definition_specification = dict(trial_definition=dict(name='CheckBoxGroup with Audio Stimuli', definition_data=dict(TrialType='CheckBoxGroup page')))

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
                                                                Header=dict(HeaderLabel='{{center|CheckBoxGroup with Audio Stimuli}}')))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)

# 2 answer options
component_definition = dict(name='CheckBoxGroup',
                            definition_data=dict(
                                    Instruments=[dict(
                                            Instrument=dict(
                                                    CheckBoxGroup=dict(
                                                            AlignForStimuli='1',
                                                            HeaderLabel='Have you adjusted the volume appropriately?',
                                                            MaxNoOfSelections='2',
                                                            MinNoOfSelections='1',
                                                            Items=dict(
                                                                    Item=[dict(Id='1',Label='yes',Selected='0'),
                                                                          dict(Id='2',Label='no',Selected='0')]))))],
                                    Stimuli=[dict(
                                            Label='Audio Excerpt',
                                            Type='audio/mpeg',
                                            IsPausable=True,
                                            URI=audio_url)]))
                        
component_object = elicit_object.add_component(component=dict(component=component_definition),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)

#%% FreeText

# Define phase
phase_definition_description = dict(phase_definition=dict(name='FreeText', definition_data=dict(PhaseType='FreeText')))

# Add phase
phase_object = elicit_object.add_phase_definition(phase_definition=phase_definition_description,
                                    study_definition_id=study_object.id,
                                    protocol_definition_id=protocol_object.id)
phases.append(phase_object)

#
# Trial 1: CheckBoxGroup
#

# Trial definition
trial_definition_specification = dict(trial_definition=dict(name='FreeText with Video Stimuli', definition_data=dict(TrialType='FreeText page')))

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
                                                                Header=dict(HeaderLabel='{{center|FreeText with Video Stimuli}}')))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)

## FreeText video combo
component_definition = dict(name='FreeText with video',
                            definition_data=dict(
                                    Instruments=[dict(
                                            Instrument=dict(
                                                    Freetext=dict(
                                                            BoxHeight=None,
                                                            BoxWidth=None,
                                                            Label="Please write what you think about this video",
                                                            LabelPosition='top',
                                                            Resizable=None,
                                                            Validation='.+')))], 
                                    Stimuli=[dict(
                                            Label='This video is pausable',
                                            Type='video/youtube',
                                            IsPausable=True,
                                            URI=video_url)]))
                        
component_object = elicit_object.add_component(component=dict(component=component_definition),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)


trial_definition_specification = dict(trial_definition=dict(name='FreeText with Audio Stimuli', definition_data=dict(TrialType='FreeText page')))

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
                                                                Header=dict(HeaderLabel='{{center|CheckBoxGroup with Audio Stimuli}}')))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)

# 2 answer options
component_definition = dict(name='FreeText with audio',
                            definition_data=dict(
                                    Instruments=[dict(
                                            Instrument=dict(
                                                    Freetext=dict(
                                                            BoxHeight=None,
                                                            BoxWidth=None,
                                                            Label="Please write what you think about this excerpts",
                                                            LabelPosition='top',
                                                            Resizable=None,
                                                            Validation='.+')))],
                                    Stimuli=[dict(
                                            Label='Audio Excerpt',
                                            Type='audio/mpeg',
                                            IsPausable=True,
                                            URI=audio_url)]))
                        
component_object = elicit_object.add_component(component=dict(component=component_definition),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)

#%% End of experiment

# Define phase
phase_definition_description = dict(phase_definition=dict(name='EndOfExperiment', definition_data=dict(PhaseType='EndOfExperiment')))

# Add phase
phase_object = elicit_object.add_phase_definition(phase_definition=phase_definition_description,
                                    study_definition_id=study_object.id,
                                    protocol_definition_id=protocol_object.id)
phases.append(phase_object)



#
# Trial 5: End of experiment page
#
# Trial definition
trial_definition_specification = dict(trial_definition=dict(name='EndOfExperiment', definition_data=dict(TrialType='EndOfExperiment')))
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
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
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


