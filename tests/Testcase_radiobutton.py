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
from random import shuffle

from examples_base import parse_command_line_args
from pyelicit import elicit

##
## MAIN
##

butterfly_video_url = 'https://youtu.be/zr9leP_Dcm8'

NUM_REGISTERED_USERS = 0
NUM_ANONYMOUS_USERS = 10

pp = pprint.PrettyPrinter(indent=4)

# get the elicit object to define the experiment
elicit_object = elicit.Elicit(parse_command_line_args())


# Double-check that we have the right user: we need to be admin to create a study
user_investigator = elicit_object.assert_investigator()

#
# Add a new Study Definitionx
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
                        principal_investigator_user_id=user_investigator.id)


study_object = elicit_object.add_study(study=dict(study_definition=study_definition_description))

#
# Create a Protocol Definition
#

# Define protocol
protocol_definition_descriptiopn = dict(name='Radiobutton test',
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

#%% Trial 1: Radiobutton group

# Trial definition
trial_definition_specification = dict(trial_definition=dict(name='IsOptional test',definition_data=dict(TrialType='RadioButtonGroup page')))

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


# 5 answer options
component_definition = dict(name='RadioButtonGroup',
                            definition_data=dict(
                                            Layout=dict(Type='column',
                                                        ColumnWidthPercent=['30', '70']),
                                            Instruments=[dict(
                                                Instrument=dict(
                                                    RadioButtonGroup=dict(
                                                            IsOptional=True,
                                                            QuestionsPerRow=1,
                                                            HeaderLabel='IsOptional=True {{n}} (i.e. does not have to be answered to proceed)',                                                            
                                                            AnswerOnce=False,
                                                            MustAnswerCorrectly=False,
                                                            ShowFeedback=False,
                                                            ShowCorrectness=False,
                                                            Items=dict(
                                                                    Item=[dict(Id='1',Label='answer 1 Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco ',Selected='0',Correct=True),
                                                                          dict(Id='2',Label='answer 2',Selected='0',Correct=True),
                                                                          dict(Id='3',Label='answer 3',Selected='0',Correct=True),
                                                                          dict(Id='4',Label='answer 4 Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco ',Selected='0',Correct=True),
                                                                          dict(Id='5',Label='answer 5',Selected='0',Correct=True)]))))],
                                          Stimuli=[dict(
                                                        Label='butterflies',
                                                        Type='video/youtube',
                                                        IsPausable=False, 
                                                        IsOptional=True, 
                                                        IsReplayable=True, 
                                                        MaxReplayCount=2,
                                                        URI=butterfly_video_url)]))
                        
component_object = elicit_object.add_component(component=dict(component=component_definition),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)

# 5 answer options
component_definition = dict(name='RadioButtonGroup',
                            definition_data=dict(
                                            Layout=dict(Type='column',
                                                        ColumnWidthPercent=['30', '70']),
                                            Instruments=[dict(
                                                Instrument=dict(
                                                    RadioButtonGroup=dict(
                                                            IsOptional=False,
                                                            QuestionsPerRow=1,
                                                            HeaderLabel='IsOptional=False {{n}} (i.e. does not have to be answered to proceed)',                                                            
                                                            AnswerOnce=False,
                                                            MustAnswerCorrectly=False,
                                                            ShowFeedback=False,
                                                            ShowCorrectness=False,
                                                            Items=dict(
                                                                    Item=[dict(Id='1',Label='answer 1 Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco ',Selected='0',Correct=True),
                                                                          dict(Id='2',Label='answer 2',Selected='0',Correct=True),
                                                                          dict(Id='3',Label='answer 3',Selected='0',Correct=True),
                                                                          dict(Id='4',Label='answer 4 Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco ',Selected='0',Correct=True),
                                                                          dict(Id='5',Label='answer 5',Selected='0',Correct=True)]))))],
                                          Stimuli=[dict(
                                                        Label='butterflies',
                                                        Type='video/youtube',
                                                        IsPausable=False, 
                                                        IsOptional=True, 
                                                        IsReplayable=True, 
                                                        MaxReplayCount=2,
                                                        URI=butterfly_video_url)]))
                        
component_object = elicit_object.add_component(component=dict(component=component_definition),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)


monitor = dict(name='Monitor', definition_data=dict(
                                        Instruments=[dict(
                                               Instrument=dict(
                                                       Monitor=dict(
                                                           MouseTracking=True,
                                                           KeyboardTracking=True,
                                                           )))]))

elicit_object.add_component(component=dict(component=monitor),
                             study_definition_id=study_object.id,
                             protocol_definition_id=protocol_object.id,
                             phase_definition_id=phase_object.id,
                             trial_definition_id=trial_object.id)

#%% Trial 2: Radiobutton group (audio)

component_definition_description = dict(name='RadioButtonGroup',
                            definition_data=dict(
                                    Layout=dict(Type='row'),
                                    Instruments=[dict(
                                            Instrument=dict(
                                                    RadioButtonGroup=dict(
                                                            HeaderLabel='Listen to this cool excerpt',
                                                            Items=dict(
                                                                   Item=[dict(Id='1',Label='yes',Selected='0'),
                                                                         dict(Id='2',Label='no',Selected='0')]))))],
                                    Stimuli=[dict(
                                            Label='Audio Excerpt',
                                            Type='audio/mpeg',
                                            IsPausable=True,
                                            URI="www.parralab.org/experiments/education/sound/01.Why_are_Stars_Shaped_like_Stars_excerpt_8_sec.wav")]))
                        
    
    # Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                                   study_definition_id=study_object.id,
                                                   protocol_definition_id=protocol_object.id,
                                                   phase_definition_id=phase_object.id,
                                                   trial_definition_id=trial_object.id)

#%% Trial 2: Radiobutton group (feedback)

# Trial definition
trial_definition_specification = dict(trial_definition=dict(name='feedback test', definition_data=dict(TrialType='RadiobuttonGroup page')))

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
                                                                Header=dict(HeaderLabel='{{center|This is a test of the RadiobuttonGroup feedback}}')))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)


# 13 answer options
component_definition = dict(name='RadioButtonGroup',
                            definition_data=dict(
                                            Layout=dict(Type='column',
                                                        ColumnWidthPercent=['30', '70']),
                                            Instruments=[dict(
                                                Instrument=dict(
                                                    RadioButtonGroup=dict(
                                                            HeaderLabel='AnswerOnce=True, MustAnswerCorrectly=False',
                                                            QuestionsPerRow='3',
                                                            IsOptional='0',
                                                            RandomizeOrder = False, # randomize the order of the Items
                                                            AnswerOnce = True, # allow the user to only answer once and then disable the instrument
                                                            MustAnswerCorrectly = False, # user can only progress if they answered correctly
                                                            ShowFeedback = False, # show feedback about the instrument
                                                            ShowCorrectness = False, # show which one was correct or incorrect
                                                            Items=dict(
                                                                    Item=[dict(Id='1',Label='answer 1',Selected='0',Correct=False,Feedback='No no no!'),
                                                                          dict(Id='2',Label='answer 2',Selected='0',Correct=False,Feedback='No no no!'),
                                                                          dict(Id='3',Label='answer 3',Selected='0',Correct=False,Feedback='No no no!'),
                                                                          dict(Id='4',Label='answer 4',Selected='0',Correct=False,Feedback='No no no!'),
                                                                          dict(Id='5',Label='answer 5',Selected='0',Correct=False,Feedback='No no no!'),
                                                                          dict(Id='6',Label='answer 6',Selected='0',Correct=False,Feedback='No no no!'),
                                                                          dict(Id='7',Label='answer 7',Selected='0',Correct=False,Feedback='No no no!'),
                                                                          dict(Id='8',Label='answer 8',Selected='0',Correct=True,Feedback='CORRECT!'),
                                                                          dict(Id='9',Label='answer 9',Selected='0',Correct=True,Feedback='CORRECT!'),
                                                                          dict(Id='10',Label='answer 10',Selected='0',Correct=True,Feedback='CORRECT!'),
                                                                          dict(Id='11',Label='answer 11',Selected='0',Correct=True,Feedback='CORRECT!'),
                                                                          dict(Id='12',Label='answer 12',Selected='0',Correct=True,Feedback='CORRECT!'),
                                                                          dict(Id='13',Label='answer 13',Selected='0',Correct=True,Feedback='CORRECT!')]))))],
                                          Stimuli=[]))
                        
component_object = elicit_object.add_component(component=dict(component=component_definition),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)

# 13 answer options
component_definition = dict(name='RadioButtonGroup',
                            definition_data=dict(
                                            Layout=dict(Type='column',
                                                        ColumnWidthPercent=['30', '70']),
                                            Instruments=[dict(
                                                Instrument=dict(
                                                    RadioButtonGroup=dict(
                                                            QuestionsPerRow='3',
                                                            HeaderLabel='MustAnswerCorrectly=True,ShowCorrectness=True,ShowFeedback=False',
                                                            IsOptional='0',
                                                            RandomizeOrder = False, # randomize the order of the Items
                                                            AnswerOnce = False,     # allow the user to only answer once and then disable the instrument
                                                            MustAnswerCorrectly = True, # user can only progress if they answered correctly
                                                            ShowFeedback = False,   # show feedback about the instrument
                                                            ShowCorrectness = True, # show which one was correct or incorrect
                                                            Items=dict(
                                                                    Item=[dict(Id='1',Label='answer 1',Selected='0',Correct=False,Feedback='No no no!'),
                                                                          dict(Id='2',Label='answer 2',Selected='0',Correct=True,Feedback='You know it!'),
                                                                          dict(Id='3',Label='answer 3',Selected='0',Correct=False,Feedback='No no no!!'),
                                                                          dict(Id='4',Label='answer 4',Selected='0',Correct=True,Feedback='You know it!'),
                                                                          dict(Id='5',Label='answer 5',Selected='0',Correct=False,Feedback='No no no!'),
                                                                          dict(Id='6',Label='answer 6',Selected='0',Correct=True,Feedback='You know it!'),
                                                                          dict(Id='7',Label='answer 7',Selected='0',Correct=False,Feedback='No no no!'),
                                                                          dict(Id='8',Label='answer 8',Selected='0',Correct=True,Feedback='You know it!'),
                                                                          dict(Id='9',Label='answer 9',Selected='0',Correct=False,Feedback='No no no!'),
                                                                          dict(Id='10',Label='answer 10',Selected='0',Correct=True,Feedback='You know it!'),
                                                                          dict(Id='11',Label='answer 11',Selected='0',Correct=False,Feedback='No no no!'),
                                                                          dict(Id='12',Label='answer 12',Selected='0',Correct=True,Feedback='You know it!'),
                                                                          dict(Id='13',Label='answer 13',Selected='0',Correct=True,Feedback='You know it!')]))))],
                                          Stimuli=[]))
                        
component_object = elicit_object.add_component(component=dict(component=component_definition),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)

# 13 answer options
component_definition = dict(name='RadioButtonGroup',
                            definition_data=dict(
                                            Layout=dict(Type='column',
                                                        ColumnWidthPercent=['30', '70']),
                                            Instruments=[dict(
                                                Instrument=dict(
                                                    RadioButtonGroup=dict(
                                                            HeaderLabel='AnswerOnce=False, MustAnswerCorrectly=False,ShowFeedback=True',
                                                            QuestionsPerRow='3',
                                                            IsOptional='0',
                                                            RandomizeOrder = False, # randomize the order of the Items
                                                            AnswerOnce = False, # allow the user to only answer once and then disable the instrument
                                                            MustAnswerCorrectly = False, # user can only progress if they answered correctly
                                                            ShowFeedback = True, # show feedback about the instrument
                                                            ShowCorrectness = False, # show which one was correct or incorrect
                                                            ColumnWidthPercent='30',
                                                            Layout='column',
                                                            Items=dict(
                                                                    Item=[dict(Id='1',Label='answer 1',Selected='0',Correct=False,Feedback='No no no!'),
                                                                          dict(Id='2',Label='answer 2',Selected='0',Correct=False,Feedback='No no no!'),
                                                                          dict(Id='3',Label='answer 3',Selected='0',Correct=False,Feedback='No no no!'),
                                                                          dict(Id='4',Label='answer 4',Selected='0',Correct=False,Feedback='No no no!'),
                                                                          dict(Id='5',Label='answer 5',Selected='0',Correct=False,Feedback='No no no!'),
                                                                          dict(Id='6',Label='answer 6',Selected='0',Correct=False,Feedback='No no no!'),
                                                                          dict(Id='7',Label='answer 7',Selected='0',Correct=False,Feedback='No no no!'),
                                                                          dict(Id='8',Label='answer 8',Selected='0',Correct=True,Feedback='CORRECT!'),
                                                                          dict(Id='9',Label='answer 9',Selected='0',Correct=True,Feedback='CORRECT!'),
                                                                          dict(Id='10',Label='answer 10',Selected='0',Correct=True,Feedback='CORRECT!'),
                                                                          dict(Id='11',Label='answer 11',Selected='0',Correct=True,Feedback='CORRECT!'),
                                                                          dict(Id='12',Label='answer 12',Selected='0',Correct=True,Feedback='CORRECT!'),
                                                                          dict(Id='13',Label='answer 13',Selected='0',Correct=True,Feedback='CORRECT!')]))))],
                                          Stimuli=[]))
                        
component_object = elicit_object.add_component(component=dict(component=component_definition),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)

#%% Trial 3
# Trial definition
trial_definition_specification = dict(trial_definition=dict(name='Options ordering and formatting', definition_data=dict(TrialType='RadiobuttonGroup page')))
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
                                            Layout=dict(Type='column',
                                                        ColumnWidthPercent=['30', '70']),
                                            Instruments=[dict(
                                                Instrument=dict(
                                                    RadioButtonGroup=dict(
                                                            QuestionsPerRow='3',
                                                            HeaderLabel='{{style|font-size: 100px;| {{b|What do you think of this image}}}}{{n}}{{n}}{{image|https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png|800|400|center}}',
                                                            IsOptional='0',
                                                            RandomizeOrder=False, # randomize the order of the Items
                                                            AnswerOnce=False, # allow the user to only answer once and then disable the instrument
                                                            MustAnswerCorrectly=False, # user can only progress if they answered correctly
                                                            ShowFeedback=False, # show feedback about the instrument
                                                            ShowCorrectness=False, # show which one was correct or incorrect
                                                            ColumnWidthPercent='30', # layout of the component
                                                            Layout='column', # layout of the component
                                                            Items=dict(
                                                                    Item=[dict(Id='1',Label='{{mark|Neutral}}',Selected='0',Correct=True),
                                                                          dict(Id='2',Label='{{style|color: red;font-size: 20px;|Super}}',Selected='0',Correct=True),
                                                                          dict(Id='3',Label='It{{sub|Neutral}}',Selected='0',Correct=True),
                                                                          dict(Id='4',Label='It{{super|Sleepy}}',Selected='0',Correct=True),
                                                                          dict(Id='5',Label='{{b|Something}}',Selected='0',Correct=True),
                                                                          dict(Id='6',Label='Multiline{{n}}{{b|Multiline}}{{n}}{{color|red|Multiline}}{{n}}{{color|blue|Multiline}}{{n}}{{color|yellow|Multiline}}',Selected='0',Correct=True), 
                                                                          dict(Id='7',Label='{{link|http://www.google.com|Link}}',Selected='0',Correct=True),
                                                                          dict(Id='8',Label='{{style|color: green;font-size: 20px;|Unpleasant is the options here}}{{n}}{{i|Negative}}{{n}} Bad',Selected='0',Correct=True)]))))],
                                          Stimuli=[]))
                        
component_object = elicit_object.add_component(component=dict(component=component_definition),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)


#%% Trial 3
# Trial definition
trial_definition_specification = dict(trial_definition=dict(name='Pre-selection', definition_data=dict(TrialType='RadiobuttonGroup page')))
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
                                                                Header=dict(HeaderLabel='{{center|Pre-selection}}')))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)


# with images and wierd options
component_definition = dict(name='RadioButtonGroup',
                            definition_data=dict(
                                            Layout=dict(Type='column',
                                                        ColumnWidthPercent=['30', '70']),
                                            Instruments=[dict(
                                                Instrument=dict(
                                                    RadioButtonGroup=dict(
                                                            QuestionsPerRow='3',
                                                            HeaderLabel='Pre selected options, IsOptional=False',
                                                            IsOptional=False,
                                                            RandomizeOrder=False,
                                                            MustAnswerCorrectly=False,
                                                            ShowFeedback=False,
                                                            ShowCorrectness=False,
                                                            ColumnWidthPercent='30',
                                                            Layout='column',
                                                            Items=dict(
                                                                    Item=[dict(Id='1',Label='answer 1 (pre)',Selected='1',Correct=True),
                                                                          dict(Id='2',Label='answer 2',Selected='0',Correct=True),
                                                                          dict(Id='3',Label='answer 3',Selected='0',Correct=True),
                                                                          dict(Id='4',Label='answer 4',Selected='0',Correct=True),
                                                                          dict(Id='5',Label='answer 5',Selected='0',Correct=True),
                                                                          dict(Id='6',Label='answer 6',Selected='0',Correct=True)]))))],
                                          Stimuli=[]))
                        
component_object = elicit_object.add_component(component=dict(component=component_definition),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)

component_definition = dict(name='RadioButtonGroup',
                            definition_data=dict(
                                Instruments=[dict(
                                    Instrument=dict(
                                        RadioButtonGroup=dict(
                                            QuestionsPerRow='3',
                                            HeaderLabel='Pre selected options, IsOptional=True',
                                            IsOptional=True,
                                            RandomizeOrder=False,
                                            MustAnswerCorrectly=False,
                                            ShowFeedback=False,
                                            ShowCorrectness=False,
                                            ColumnWidthPercent='30',
                                            Layout='column',
                                            Items=dict(
                                                Item=[dict(Id='1', Label='answer 1 (pre)', Selected='1', Correct=True),
                                                      dict(Id='2', Label='answer 2', Selected='0', Correct=True),
                                                      dict(Id='3', Label='answer 3', Selected='0', Correct=True),
                                                      dict(Id='4', Label='answer 4', Selected='0', Correct=True),
                                                      dict(Id='5', Label='answer 5', Selected='0', Correct=True),
                                                      dict(Id='6', Label='answer 6', Selected='0', Correct=True)]))))]))

component_object = elicit_object.add_component(component=dict(component=component_definition),
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id,
                                               trial_definition_id=trial_object.id)


#%% Trial 3
# Trial definition
trial_definition_specification = dict(trial_definition=dict(name='Random orders', definition_data=dict(TrialType='RadiobuttonGroup page')))
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
                                                                Header=dict(HeaderLabel='{{center|Random orders}}')))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)

# with images and wierd options
component_definition = dict(name='RadioButtonGroup',
                            definition_data=dict(
                                            Layout=dict(Type='column',
                                                        ColumnWidthPercent=['30', '70']),
                                            Instruments=[dict(
                                                Instrument=dict(
                                                    RadioButtonGroup=dict(
                                                            QuestionsPerRow='3',
                                                            HeaderLabel='This is a test of randomized order)',
                                                            IsOptional=False,
                                                            RandomizeOrder=True,
                                                            MustAnswerCorrectly=False,
                                                            ShowFeedback=False,
                                                            ShowCorrectness=False,
                                                            ColumnWidthPercent='30',
                                                            Layout='column',                                                            
                                                            Items=dict(
                                                                    Item=[dict(Id='1',Label='answer 1',Selected='0',Correct=True),
                                                                          dict(Id='2',Label='answer 2',Selected='0',Correct=True),
                                                                          dict(Id='3',Label='answer 3',Selected='0',Correct=True),
                                                                          dict(Id='4',Label='answer 4',Selected='0',Correct=True),
                                                                          dict(Id='5',Label='answer 5',Selected='0',Correct=True),
                                                                          dict(Id='6',Label='answer 6',Selected='0',Correct=True)]))))],
                                          Stimuli=[]))
                        
component_object = elicit_object.add_component(component=dict(component=component_definition),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)



component_definition = dict(name='RadioButtonGroup',
                            definition_data=dict(
                                            Layout=dict(Type='column',
                                                        ColumnWidthPercent=['30', '70']),
                                            Instruments=[dict(
                                                Instrument=dict(
                                                    RadioButtonGroup=dict(
                                                            QuestionsPerRow='3',
                                                            HeaderLabel='This is a test of randomized order (pre-selected)))',
                                                            IsOptional=False,
                                                            RandomizeOrder=True,
                                                            MustAnswerCorrectly=False,
                                                            ShowFeedback=False,
                                                            ShowCorrectness=False,
                                                            ColumnWidthPercent='30',
                                                            Layout='column',
                                                            Items=dict(
                                                                    Item=[dict(Id='0',Label='answer 0'      ,Selected='0',Correct=True),
                                                                          dict(Id='1',Label='answer 1'      ,Selected='0',Correct=True),
                                                                          dict(Id='2',Label='answer 2 (pre)',Selected='1',Correct=True),
                                                                          dict(Id='3',Label='answer 3'      ,Selected='0',Correct=True),
                                                                          dict(Id='4',Label='answer 4'      ,Selected='0',Correct=True),
                                                                          dict(Id='5',Label='answer 5'      ,Selected='0',Correct=True)]))))],
                                          Stimuli=[]))
                        
component_object = elicit_object.add_component(component=dict(component=component_definition),
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
    #shuffle(trial_id)

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

# %% print some basic details about the experiment
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

print('Study link: ', end='')
print(('https://elicit-experiment.com/studies/' + str(study_object.id) + '/protocols/'  + str(protocol_object.id)))
