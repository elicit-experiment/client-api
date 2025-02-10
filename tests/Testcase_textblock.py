"""
Testcase for headers
"""

import pprint
import sys
import csv
import json

from random import shuffle

from pyelicit.command_line import parse_command_line_args
from pyelicit import elicit

study_url = 'https://elicit-experiment.com/studies/'

##
## MAIN
##

pp = pprint.PrettyPrinter(indent=4)

# get the elicit object to define the experiment
elicit_object = elicit.Elicit(parse_command_line_args())

# Double-check that we have the right user: we need to be admin to create a study
user_investigator = elicit_object.assert_investigator()

#
# Add a new Study Definition
#

# Define study
study_definition_description = dict(title='TextBlock test',
                                    description="""This study tests the TextBlock component""",
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
protocol_definition_descriptiopn = dict(name='TextBlock test',
                                        definition_data="whatever you want here",
                                        summary="This summary will be shown on the webpage? \n This is a test to show off all the capabilities of Elicit",
                                        description='This is a detailed account of what the experiment will inbolve. \n All the components and functionality of Elicit will be displayed here',
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

# only define a single phase for this experiment
phases = [phase_object]

trials = []


#%% Trial 1: Welcome slide

# Trial definition
trial_definition_specification = dict(trial_definition=dict(name='Justified TextBlock', definition_data=dict(TrialType='TextBlock page')))
trial_object = elicit_object.add_trial_definition(trial_definition=trial_definition_specification,
                                                  study_definition_id=study_object.id,
                                                  protocol_definition_id=protocol_object.id,
                                                  phase_definition_id=phase_object.id)
# save trial to later define trial orders
trials.append(trial_object)

# Component definition: Text Block
component_definition_description = dict(name='TextBlock',
                                        definition_data=dict(Layout=dict(Type='column',
                                                                         ColumnWidthPercent=['30', '70']),
                                                             Instruments=[dict(
                                                                    Instrument=dict(
                                                                        TextBlock=dict(
                                                                            Text=("{{center|Some centered text here}}{{n}}{{n}}{{n}}" + 
                                                                                  "{{right|{{b|Some right justified bold text after some next lines}}}}{{n}}{{n}}{{n}}" + 
                                                                                  "{{left|{{b|Some left justified bold text after some next lines}}}}{{n}}{{n}}{{n}}"  +                                                            
                                                                                  "{{center|{{b|Some centered bold text after some next lines}}}}{{n}}{{n}}{{n}}" 
                                                                                  ))))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id,
                                               trial_definition_id=trial_object.id)

#%% Trial 2
trial_definition_specification = dict(trial_definition=dict(name='Multiformat TextBlock', definition_data=dict(TrialType='TextBlock page')))
trial_object = elicit_object.add_trial_definition(trial_definition=trial_definition_specification,
                                                  study_definition_id=study_object.id,
                                                  protocol_definition_id=protocol_object.id,
                                                  phase_definition_id=phase_object.id)
# save trial to later define trial orders
trials.append(trial_object)


component_definition_description = dict(name='TextBlock',
                                        definition_data=dict(Layout=dict(Type='column',
                                                                         ColumnWidthPercent=['30', '70']),
                                                            Instruments=[dict(
                                                                    Instrument=dict(
                                                                        TextBlock=dict(
                                                                            Text=("{{mark|Neutral}}{{n}}" + 
                                                                                  "{{style|color: red;font-size: 20px;|Red with fontsize 20}}{{n}}" +
                                                                                  "{{style|color: green;font-size: 100px;|Green with fontsize 100}}{{n}}" +
                                                                                  "Subscript{{sub|Subscript}}{{n}}" +
                                                                                  "Superscript{{super|Superscript}}{{n}}" +
                                                                                  "{{b|Bold}}{{n}}" +
                                                                                  "{{i|Italic}}{{n}}" +
                                                                                  "Different colors: {{color|red|Red}}, {{color|blue|Blue}}, {{color|yellow|Yellow}}{{n}}" +
                                                                                  "{{link|http://www.google.com|Link}}{{n}}"
                                                                                  ))))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id,
                                               trial_definition_id=trial_object.id)



trial_definition_specification = dict(trial_definition=dict(name='Image TextBlock', definition_data=dict(TrialType='TextBlock page')))
trial_object = elicit_object.add_trial_definition(trial_definition=trial_definition_specification,
                                                  study_definition_id=study_object.id,
                                                  protocol_definition_id=protocol_object.id,
                                                  phase_definition_id=phase_object.id)
# save trial to later define trial orders
trials.append(trial_object)

component_definition_description = dict(name='TextBlock',
                                        definition_data=dict(Layout=dict(Type='column',
                                                                         ColumnWidthPercent=['30', '70']),
                                                            Instruments=[dict(
                                                                    Instrument=dict(
                                                                        TextBlock=dict(
                                                                            Text=("{{style|color: black;font-size: 50px;|Large centered 800x400 google image}}{{n}}{{n}}" +
                                                                                  "{{image|https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png|800|400|center}}{{n}}{{n}}" +
                                                                                  "{{style|color: black;font-size: 40px;|Smaller left 400x200 google image}}{{n}}{{n}}" +
                                                                                  "{{image|https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png|400|200|left}}{{n}}{{n}}" +
                                                                                  "{{style|color: black;font-size: 30px;|Smaller left 200x100 google image}}{{n}}{{n}}" +
                                                                                  "{{image|https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png|200|100|right}}{{n}}{{n}}"
                                                                                  ))))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id,
                                               trial_definition_id=trial_object.id)

#%% Trial 3: End of experiment page
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
                                                    Header=dict(
                                                        HeaderLabel='{{center|Thank you for your participation}}')))]))

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
                                                  user_id=user_investigator.id))

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

print('Study link: ', end='')
print((study_url + str(study_object.id) + '/protocols/'  + str(protocol_object.id)))

