# -*- coding: utf-8 -*-
"""
Example testing the radiobuttons
"""

import sys
sys.path.append("../../client-api/")

import pprint
import sys
import csv
import json

sys.path.append("../")

import pprint

from examples_base import parse_command_line_args
from pyelicit import elicit
from random import shuffle

##
## MAIN
##

NUM_REGISTERED_USERS = 0
NUM_ANONYMOUS_USERS = 10

pp = pprint.PrettyPrinter(indent=4)

# get the elicit object to define the experiment
elicit_object = elicit.Elicit(parse_command_line_args())


# Double-check that we have the right user: we need to be admin to create a study
user_investigator = elicit_object.assert_investigator()

#
# Add a new Study Definition
#

# Define study
study_definition_description = dict(title='CheckboxGroup test',
                        description="""This is a test of the CheckboxGroup component""",
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
protocol_definition_description = dict(name='CheckboxGroup test',
                                       definition_data="whatever you want here",
                                       summary="This is a test of the RadiobuttonGroup component",
                                       description='This is a test of the RadiobuttonGroup component',
                                       active=True)

# Add protocol
protocol_object = elicit_object.add_protocol_definition(protocol_definition=dict(protocol_definition=protocol_definition_description),
                                                        study_definition_id=study_object.id)

#
# Add users to protocol
#

# Get a list of users who can participate in the study
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


#%% Trial 1: CheckboxGroup group

# Trial definition
trial_definition_specification = dict(trial_definition=dict(name='Min/Max NoOfSelections test', definition_data=dict(TrialType='CheckboxGroup page')))

trial_object = elicit_object.add_trial_definition(trial_definition=trial_definition_specification,
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id)

# save trial to later define trial orders
trials.append(trial_object)

# Component definition: CheckboxGroup
component_definition_description = dict(name='CheckboxGroup',
                                        definition_data=dict(
    Instruments=[dict(
        Instrument=dict(
            CheckBoxGroup=dict(
                AlignForStimuli='0',
                HeaderLabel='checkboxgroup (MinNoOfSelections=0)',
                MaxNoOfSelections='1',
                MinNoOfSelections='0',
                RandomizeOrder=False,
                Items=dict(
                    Item=[
                          dict(Id='0',Label='yes',Selected='0'),
                          dict(Id='1',Label='no',Selected='0'), 
                          dict(Id='2',Label='dont know',Selected='0')]))))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id,
                                               trial_definition_id=trial_object.id)


# Component definition: CheckboxGroup
component_definition_description = dict(name='CheckboxGroup',
                                        definition_data=dict(
                                                    Instruments=[dict(
                                                        Instrument=dict(
                                                            CheckBoxGroup=dict(
                                                                AlignForStimuli='0',
                                                                HeaderLabel='checkboxgroup (pre selected options, [1 3 5])',
                                                                MaxNoOfSelections='2',
                                                                MinNoOfSelections='0',
                                                                RandomizeOrder=False,
                                                                ShowFeedback=False,
                                                                ShowCorrectness=True,
                                                                FeedbackCorrect='',
                                                                FeedbackIncorrect='',
                                                                Items=dict(
                                                                    Item=[
                                                                          dict(Id='0',Label='yes',Selected='1',Correct=False),
                                                                          dict(Id='1',Label='no',Selected='0',Correct=True),
                                                                          dict(Id='2',Label='dont know',Selected='1',Correct=True),
                                                                          dict(Id='3',Label='kinda',Selected='0',Correct=False),
                                                                          dict(Id='4',Label='a little',Selected='1', Correct=False)]))))]))


component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id,
                                               trial_definition_id=trial_object.id)

#%% Trial 2: CheckboxGroup group (feedback)

# Trial definition
trial_definition_specification = dict(trial_definition=dict(name='Feedback', definition_data=dict(TrialType='CheckboxGroup page')))

trial_object = elicit_object.add_trial_definition(trial_definition=trial_definition_specification,
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id)

# save trial to later define trial orders
trials.append(trial_object)

# Component definition: CheckboxGroup
component_definition_description = dict(name='CheckboxGroup',
                                        definition_data=dict(
    Instruments=[dict(
        Instrument=dict(
            CheckBoxGroup=dict(
                AlignForStimuli='0',
                HeaderLabel='checkboxgroup (MinNoOfSelections=0)',
                MaxNoOfSelections='1',
                MinNoOfSelections='0',
                RandomizeOrder=False,
                Items=dict(
                    Item=[
                          dict(Id='0',Label='yes',Selected='0'),
                          dict(Id='1',Label='no',Selected='0'), 
                          dict(Id='2',Label='dont know',Selected='0')]))))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id,
                                               trial_definition_id=trial_object.id)


# Component definition: CheckboxGroup
component_definition_description = dict(name='CheckboxGroup',
                                        definition_data=dict(
                                                    Instruments=[dict(
                                                        Instrument=dict(
                                                            CheckBoxGroup=dict(
                                                                HeaderLabel='checkboxgroup w. feedback',
                                                                MaxNoOfSelections='2',
                                                                MinNoOfSelections='0',
                                                                RandomizeOrder=False,
                                                                ShowFeedback=True,
                                                                ShowCorrectness=True,
                                                                FeedbackCorrect='Good job',
                                                                FeedbackIncorrect='bad job',
                                                                Items=dict(
                                                                    Item=[
                                                                          dict(Id='0',Label='yes',Correct=False, Feedback="Not Right"),
                                                                          dict(Id='1',Label='no',Correct=True, Feedback="Right"),
                                                                          dict(Id='2',Label='dont know',Correct=True, Feedback="Right"),
                                                                          dict(Id='3',Label='kinda',Correct=False, Feedback="Not Right"),
                                                                          dict(Id='4',Label='a little', Correct=False, Feedback="Not Right")]))))]))



# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id,
                                               trial_definition_id=trial_object.id)


component_definition_description = dict(name='CheckboxGroup',
                                    definition_data=dict(
                                        Instruments=[dict(
                                            Instrument=dict(
                                                CheckBoxGroup=dict(
                                                    HeaderLabel='checkboxgroup {{n}} (AlignForStimuli=1,minSelect=2,maxSelect=10)',
                                                    MaxNoOfSelections=10,
                                                    MinNoOfSelections=2,
                                                    RandomizeOrder=False,
                                                    FeedbackCorrect='Good job',
                                                    FeedbackIncorrect='bad job',
                                                    Layout='column',
                                                    ColumnWidthPercent='30',
                                                    Items=dict(
                                                        Item=[
                                                            dict(Id='0',Label='bla1',Selected='0'),
                                                            dict(Id='1',Label='bla12',Selected='0'),
                                                            dict(Id='2',Label='bla123',Selected='0'),
                                                            dict(Id='3',Label='bla1234',Selected='0'),
                                                            dict(Id='4',Label='bla12345',Selected='0'),
                                                            dict(Id='5',Label='bla123456',Selected='0'),
                                                            dict(Id='6',Label='bla1234567',Selected='0'),
                                                            dict(Id='7',Label='bla12345678',Selected='0'),
                                                            dict(Id='8',Label='bla123456789',Selected='0'),
                                                            dict(Id='9',Label='bla1234567890',Selected='0'),
                                                            dict(Id='10',Label='blablabla',Selected='0'),
                                                            dict(Id='11',Label='blablablabla',Selected='0'),
                                                            dict(Id='12',Label='blablablabla',Selected='0'),
                                                            dict(Id='13',Label='blablablabla',Selected='0'),
                                                            dict(Id='14',Label='blablablabla',Selected='0'),
                                                            dict(Id='15',Label='This is some really long text which should test the wrapping of the content in this box and i could go on and on',Selected='0'),
                                                            dict(Id='16',Label='This is some really long text which should test the wrapping of the content in this box and i could go on and on',Selected='0'),
                                                            dict(Id='17',Label='This is some really long text which should test the wrapping of the content in this box and i could go on and on',Selected='0'),
                                                            dict(Id='18',Label='{{b|bold bla}}',Selected='0'),
                                                            dict(Id='19',Label='{{i|italic bla}}',Selected='0'),
                                                            dict(Id='20',Label='{{style|color: red;font-size: 20px;|Red large bla}}',Selected='0'),
                                                            dict(Id='21',Label='{{link|http://www.google.com|Link}}',Selected='0'),
                                                            dict(Id='22',Label='this should be flush{{n}}this should be flush{{n}}this should be flush',Selected='0'),
                                                            dict(Id='23',Label='{{image|https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png|68|23|center}}',Selected='0'),
                                                            dict(Id='24',Label='{{image|https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png|68|23|center}}',Selected='0'),
                                                            dict(Id='25',Label='{{image|https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png|68|23|center}}',Selected='0')
                                                            ]))))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id,
                                               trial_definition_id=trial_object.id)

component_definition_description = dict(name='CheckboxGroup',
                                    definition_data=dict(
                                        Instruments=[dict(
                                            Instrument=dict(
                                                CheckBoxGroup=dict(
                                                    AlignForStimuli='1',
                                                    HeaderLabel='checkboxgroup {{n}} (AlignForStimuli=1,minSelect=2,maxSelect=3)',
                                                    MaxNoOfSelections=3,
                                                    MinNoOfSelections=2,
                                                    RandomizeOrder=False,
                                                    FeedbackCorrect='Good job',
                                                    FeedbackIncorrect='bad job',
                                                    Items=dict(
                                                        Item=[
                                                            dict(Id='0',Label='bla1',Selected='0'),
                                                            dict(Id='1',Label='bla12',Selected='0'),
                                                            dict(Id='2',Label='bla123',Selected='0'),
                                                            dict(Id='3',Label='bla1234',Selected='0'),
                                                            dict(Id='4',Label='bla12345',Selected='0'),
                                                            dict(Id='5',Label='bla123456',Selected='0'),
                                                            dict(Id='6',Label='bla1234567',Selected='0'),
                                                            dict(Id='7',Label='bla12345678',Selected='0'),
                                                            dict(Id='8',Label='bla123456789',Selected='0'),
                                                            dict(Id='9',Label='bla1234567890',Selected='0'),
                                                            dict(Id='10',Label='blablabla',Selected='0'),
                                                            dict(Id='11',Label='blablablabla',Selected='0'),
                                                            dict(Id='12',Label='blablablabla',Selected='0'),
                                                            dict(Id='13',Label='blablablabla',Selected='0'),
                                                            dict(Id='14',Label='blablablabla',Selected='0'),
                                                            dict(Id='15',Label='This is some really long text which should test the wrapping of the content in this box and i could go on and on',Selected='0'),
                                                            dict(Id='16',Label='This is some really long text which should test the wrapping of the content in this box and i could go on and on',Selected='0'),
                                                            dict(Id='17',Label='This is some really long text which should test the wrapping of the content in this box and i could go on and on',Selected='0'),
                                                            dict(Id='18',Label='{{b|bold bla}}',Selected='0'),
                                                            dict(Id='19',Label='{{i|italic bla}}',Selected='0'),
                                                            dict(Id='20',Label='{{style|color: red;font-size: 20px;|Red large bla}}',Selected='0'),
                                                            dict(Id='21',Label='{{link|http://www.google.com|Link}}',Selected='0'),
                                                            dict(Id='22',Label='this should be flush{{n}}this should be flush{{n}}this should be flush',Selected='0'),
                                                            dict(Id='23',Label='{{image|https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png|68|23|center}}',Selected='0'),
                                                            dict(Id='24',Label='{{image|https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png|68|23|center}}',Selected='0'),
                                                            dict(Id='25',Label='{{image|https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png|68|23|center}}',Selected='0')
                                                            ]))))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id,
                                               trial_definition_id=trial_object.id)
#%%  Trial 2: End of experiment page
#
# Trial definition
trial_definition_specification =  dict(trial_definition=dict(name='End of experiment', definition_data=dict(TrialType='EOE')))
trial_object_eoe = elicit_object.add_trial_definition(trial_definition=trial_definition_specification,
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id)

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
                                 trial_definition_id=trial_object_eoe.id)



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
                                               trial_definition_id=trial_object_eoe.id)

#%% Add Trial Orders to the study
#trail_orders for anonymous users
for anonymous_participant in range(0,NUM_ANONYMOUS_USERS):
    trial_id = [int(trial.id) for trial in trials]
    shuffle(trial_id)
    trial_id.append(trial_object_eoe.id)

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
print(('https://elicit-experiment.com/studies/' + str(study_object.id) + '/protocols/'  + str(protocol_object.id)))
