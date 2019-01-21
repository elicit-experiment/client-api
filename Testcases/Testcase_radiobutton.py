# -*- coding: utf-8 -*-
"""
Example testing the radiobuttons
"""

import sys
sys.path.append("../")

import pprint
import sys
import csv
import json

from examples_base import parse_command_line_args
from pyelicit import elicit

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
study_definition_description = dict(title='Radiobutton test',
                        description="""This is a test of the RadiobuttonGroup component""",
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
protocol_definition_descriptiopn = dict(name='This protocol tests the RadiobuttonGroup component',
                               definition_data="whatever you want here",
                               summary="This is a test of the RadiobuttonGroup component",
                               description='This is a test of the RadiobuttonGroup component',
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

#
# Trial 1: Radiobutton group
#

# Trial definition
trial_definition_specification = dict(trial_definition=dict(name='IsOptional test', definition_data=dict(TrialType='RadiobuttonGroup page')))

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
                                                                Header=dict(HeaderLabel='{{center|This is a test of a RadiobuttonGroup component}}')))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)


# 13 answer options
component_definition = dict(name='RadioButtonGroup',
                            definition_data=dict(
                                    Instruments=[dict(
                                            Instrument=dict(
                                                    RadioButtonGroup=dict(
                                                            AlignForStimuli='0',
                                                            QuestionsPerRow='1',
                                                            HeaderLabel='IsOptional=1 {{n}} (i.e. has to be answered to proceed)',
                                                            IsOptional='1',
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
                                                                          dict(Id='13',Label='answer 13',Selected='0',Correct=True)]))))]))
                        
component_object = elicit_object.add_component(component=dict(component=component_definition),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)


# 13 answer options
component_definition = dict(name='RadioButtonGroup',
                            definition_data=dict(
                                    Instruments=[dict(
                                            Instrument=dict(
                                                    RadioButtonGroup=dict(
                                                            AlignForStimuli='0',
                                                            QuestionsPerRow='3',
                                                            HeaderLabel='IsOptional=0 (i.e. does not have to be answered) {{n}} 3 options per row',
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
                                                                          dict(Id='13',Label='answer 13',Selected='0',Correct=True)]))))]))
                        
component_object = elicit_object.add_component(component=dict(component=component_definition),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)



# 13 answer options
component_definition = dict(name='RadioButtonGroup',
                            definition_data=dict(
                                    Instruments=[dict(
                                            Instrument=dict(
                                                    RadioButtonGroup=dict(
                                                            AlignForStimuli='0',
                                                            QuestionsPerRow='3',
                                                            HeaderLabel='IsOptional=1 {{n}} 3 options per row',
                                                            IsOptional='1',
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
                                                                          dict(Id='13',Label='answer 13',Selected='0',Correct=True)]))))]))
                        
component_object = elicit_object.add_component(component=dict(component=component_definition),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)





# Trial definition
trial_definition_specification = dict(trial_definition=dict(name='Options formatting', definition_data=dict(TrialType='RadiobuttonGroup page')))
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
                                                                Header=dict(HeaderLabel='{{center|This is a test of a RadiobuttonGroup with wierd options}}')))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)






# with images and wierd options
component_definition = dict(name='RadioButtonGroup',
                            definition_data=dict(
                                    Instruments=[dict(
                                            Instrument=dict(
                                                    RadioButtonGroup=dict(
                                                            AlignForStimuli='0',
                                                            QuestionsPerRow='3',
                                                            HeaderLabel='{{style|font-size: 100px;| {{b|What do you think of this image}}}}{{n}}{{n}}{{image|https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png|800|400|center}}',
                                                            IsOptional='0',
                                                            Items=dict(
                                                                    Item=[dict(Id='1',Label='{{mark|Neutral}}',Selected='0',Correct=True),
                                                                          dict(Id='2',Label='{{style|color: red;font-size: 20px;|Super}}',Selected='0',Correct=True),
                                                                          dict(Id='3',Label='It{{sub|Neutral}}',Selected='0',Correct=True),
                                                                          dict(Id='4',Label='It{{super|Sleepy}}',Selected='0',Correct=True),
                                                                          dict(Id='5',Label='{{b|Something}}',Selected='0',Correct=True),
                                                                          dict(Id='6',Label='Multiline{{n}}{{b|Multiline}}{{n}}{{color|red|Multiline}}{{n}}{{color|blue|Multiline}}{{n}}{{color|yellow|Multiline}}',Selected='0',Correct=True), 
                                                                          dict(Id='7',Label='{{link|http://www.google.com|Link}}',Selected='0',Correct=True),
                                                                          dict(Id='8',Label='{{style|color: green;font-size: 20px;|Unpleasant is the options here}}{{n}}{{i|Negative}}{{n}} Bad',Selected='0',Correct=True),
                                                                          ]))))]))
                        
component_object = elicit_object.add_component(component=dict(component=component_definition),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)




# Trial definition
trial_definition_specification = dict(trial_definition=dict(name='Pre-selection', definition_data=dict(TrialType='RadiobuttonGroup page')))
trial_object = elicit_object.add_trial_definition(trial_definition=trial_definition_specification,
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id)
# save trial to later define trial orders
trials.append(trial_object)


# with images and wierd options
component_definition = dict(name='RadioButtonGroup',
                            definition_data=dict(
                                    Instruments=[dict(
                                            Instrument=dict(
                                                    RadioButtonGroup=dict(
                                                            AlignForStimuli='0',
                                                            QuestionsPerRow='3',
                                                            HeaderLabel='This is a test of pre selected options {{n}}(first options should be selected)',
                                                            IsOptional='0',
                                                            Items=dict(
                                                                    Item=[dict(Id='1',Label='answer 1',Selected='1',Correct=True),
                                                                          dict(Id='2',Label='answer 2',Selected='0',Correct=True),
                                                                          dict(Id='3',Label='answer 3',Selected='0',Correct=True),
                                                                          dict(Id='4',Label='answer 4',Selected='0',Correct=True),
                                                                          dict(Id='5',Label='answer 5',Selected='0',Correct=True),
                                                                          dict(Id='6',Label='answer 6',Selected='0',Correct=True)]))))]))
                        
component_object = elicit_object.add_component(component=dict(component=component_definition),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)




#
# Trial 5: End of experiment page
#
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

#
# Add a Trial Orders to the study
#

# Define the trial orders
for study_participant in study_participants:
    trial_order_specification = dict(trial_order=dict(sequence_data=",".join([str(trial.id) for trial in trials]),
                                                   user_id=study_participant.id))

# Trial order addition
    trial_order_object = elicit_object.add_trial_order(trial_order=trial_order_specification,
                                         study_definition_id=study_object.id,
                                         protocol_definition_id=protocol_object.id,
                                         phase_definition_id=phase_object.id)

#
# Add a new Phase Order
#
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

