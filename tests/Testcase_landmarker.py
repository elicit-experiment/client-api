"""
Testcase for webcam eye tracking
"""

import sys

sys.path.append("../")

import pprint

from examples_base import parse_command_line_args
from pyelicit import elicit

##
## MAIN
##

pp = pprint.PrettyPrinter(indent=4)

# get the Elicit object to define the experiment
elicit_object = elicit.Elicit(parse_command_line_args())

# Double-check that we have the right user: we need to be admin to create a study
user_admin = elicit_object.assert_investigator()

#
# Add a new Study Definition
#

# Define study
study_definition_description = dict(title='Landmarker test',
                                    description="""This study tests the Landmarker trial component""",
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
protocol_definition_descriptiopn = dict(name='Landmarker test',
                                        definition_data="whatever you want here",
                                        summary="This summary will be shown on the webpage? \n This is a test to show off all the capabilities of Elicit",
                                        description='This tests the Landmarker trial plugin',
                                        active=True)

# Add protocol
protocol_object = elicit_object.add_protocol_definition(
    protocol_definition=dict(protocol_definition=protocol_definition_descriptiopn),
    study_definition_id=study_object.id)

#
# Add users to protocol
#

#
# Get list of users who will use the study
#
NUM_AUTO_CREATED_USERS = 10
NUM_ANONYMOUS_USERS = 5
NUM_REGISTERED_USERS = 5
study_participants = elicit_object.ensure_users(NUM_REGISTERED_USERS, NUM_ANONYMOUS_USERS)

pp.pprint(study_participants)

# add users to protocol
elicit_object.add_users_to_protocol(study_object, protocol_object, study_participants)

#
#%% Add Phase Definition
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

#%%
# Trial 1: Landmarker calibration
#


trial_definition_specification = dict(trial_definition=dict(name='Landmarker calibration',
                                                            definition_data=dict(
                                                                    TrialType='Calibration',
                                                                    type='NewComponent::FaceLandmark',
                                                                    MaxNoOfAttempts='2',
                                                                    MinCalibrationAccuracyPct='20'
                                                                    )))

trial_object = elicit_object.add_trial_definition(trial_definition=trial_definition_specification,
                                                  study_definition_id=study_object.id,
                                                  protocol_definition_id=protocol_object.id,
                                                  phase_definition_id=phase_object.id,
                                                  )

trials.append(trial_object)

#new_component_config = dict(name='Label component',
#                            definition_data=json.dumps(dict(MaxNoOfAttempts='2', MinCalibrationAccuracyPct='80')))
#new_component = elicit_object.add_component(component=dict(component=new_component_config),
#                                            study_definition_id=study_object.id,
#                                            protocol_definition_id=protocol_object.id,
#                                            phase_definition_id=phase_object.id,
#                                            trial_definition_id=trial_object.id)

#%% add a little butterfly video
#
# Trial definition
trial_definition_specification = dict(trial_definition=dict(name='butterflies', definition_data=dict(TrialType='Video page')))

trial_object = elicit_object.add_trial_definition(trial_definition=trial_definition_specification,
                                                  study_definition_id=study_object.id,
                                                  protocol_definition_id=protocol_object.id,
                                                  phase_definition_id=phase_object.id)
# save trial to later define trial orders
trials.append(trial_object)

# Component definition: Header Label
header_component_definition = dict(name='HeaderLabel',
                                        definition_data=dict(
                                            Instruments=[dict(
                                                Instrument=dict(
                                                    Header=dict(
                                                        HeaderLabel='{{center|butterflies}}')))]))
# Component addition: add the component to the trial
elicit_object.add_component(component=dict(component=header_component_definition),
                                           study_definition_id=study_object.id,
                                           protocol_definition_id=protocol_object.id,
                                           phase_definition_id=phase_object.id,
                                           trial_definition_id=trial_object.id)
# Define video component
butterfly_video_url = 'https://youtu.be/zr9leP_Dcm8'
stimulus = dict(
                                          Label='butterflies',
                                          Type='video/youtube',
                                          IsPausable=False, 
                                          IsOptional=True, 
                                          IsReplayable=True, 
                                          MaxReplayCount=2,
                                          URI=butterfly_video_url);

video_component_definition = dict(name='butterflies',
                                  definition_data=dict(
                                      Stimuli=[stimulus]))

elicit_object.add_component(component=dict(component=video_component_definition),
                                           study_definition_id=study_object.id,
                                           protocol_definition_id=protocol_object.id,
                                           phase_definition_id=phase_object.id,
                                           trial_definition_id=trial_object.id)    

monitor = dict(name='Monitor', definition_data=dict(Instruments=[dict(Instrument=dict(Monitor=dict()))]))
elicit_object.add_component(component=dict(component=monitor),
                             study_definition_id=study_object.id,
                             protocol_definition_id=protocol_object.id,
                             phase_definition_id=phase_object.id,
                             trial_definition_id=trial_object.id)

#%% add a little butterfly video
#
# Trial definition
trial_definition_specification = dict(trial_definition=dict(name='butterflies', definition_data=dict(TrialType='Video page')))

trial_object = elicit_object.add_trial_definition(trial_definition=trial_definition_specification,
                                                  study_definition_id=study_object.id,
                                                  protocol_definition_id=protocol_object.id,
                                                  phase_definition_id=phase_object.id)
# save trial to later define trial orders
trials.append(trial_object)

# Component definition: Header Label
header_component_definition = dict(name='HeaderLabel',
                                        definition_data=dict(
                                            Instruments=[dict(
                                                Instrument=dict(
                                                    Header=dict(
                                                        HeaderLabel='{{center|butterflies}}')))]))
# Component addition: add the component to the trial
elicit_object.add_component(component=dict(component=header_component_definition),
                                           study_definition_id=study_object.id,
                                           protocol_definition_id=protocol_object.id,
                                           phase_definition_id=phase_object.id,
                                           trial_definition_id=trial_object.id)
# Define video component
butterfly_video_url = 'https://youtu.be/zr9leP_Dcm8'
stimulus = dict(
                                          Label='butterflies',
                                          Type='video/youtube',
                                          IsPausable=False, 
                                          IsOptional=True, 
                                          IsReplayable=True, 
                                          MaxReplayCount=2,
                                          URI=butterfly_video_url)

video_component_definition = dict(name='butterflies',
                                  definition_data=dict(
                                      Stimuli=[stimulus]))

elicit_object.add_component(component=dict(component=video_component_definition),
                                           study_definition_id=study_object.id,
                                           protocol_definition_id=protocol_object.id,
                                           phase_definition_id=phase_object.id,
                                           trial_definition_id=trial_object.id)    
monitor = dict(name='Monitor', definition_data=dict(Instruments=[dict(Instrument=dict(Monitor=dict()))]))
elicit_object.add_component(component=dict(component=monitor),
                             study_definition_id=study_object.id,
                             protocol_definition_id=protocol_object.id,
                             phase_definition_id=phase_object.id,
                             trial_definition_id=trial_object.id)
#%% Trial 3: Radiobutton group

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


# Component definition: Monitor
component_definition_description = dict(name='Monitor', definition_data=dict(Instruments=[dict(Instrument=dict(Monitor=dict()))]))

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
                                                                    Item=[dict(Id='1',Label='answer 1 Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco ',Selected='0',Correct=True),
                                                                          dict(Id='2',Label='answer 2',Selected='0',Correct=True),
                                                                          dict(Id='3',Label='answer 3',Selected='0',Correct=True),
                                                                          dict(Id='4',Label='answer 4 Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco ',Selected='0',Correct=True),
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
                                                            HeaderLabel='options 1-7 false, options 8-13 true',
                                                            IsOptional='0',                                                            
                                                            MustAnswerCorrectly=False,
                                                            ShowFeedback=False,
                                                            ShowCorrectness=True,
                                                            Items=dict(
                                                                    Item=[dict(Id='1',Label='answer 1',Selected='0',Correct=False),
                                                                          dict(Id='2',Label='answer 2',Selected='0',Correct=False),
                                                                          dict(Id='3',Label='answer 3',Selected='0',Correct=False),
                                                                          dict(Id='4',Label='answer 4',Selected='0',Correct=False),
                                                                          dict(Id='5',Label='answer 5',Selected='0',Correct=False),
                                                                          dict(Id='6',Label='answer 6',Selected='0',Correct=False),
                                                                          dict(Id='7',Label='answer 7',Selected='0',Correct=False),
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
                                                            MustAnswerCorrectly=True,
                                                            ShowFeedback=True,
                                                            ShowCorrectness=True,
                                                            Items=dict(
                                                                    Item=[dict(Id='1',Label='answer 1',Selected='0',Correct=False,Feedback='No no no!'),
                                                                          dict(Id='2',Label='answer 2',Selected='0',Correct=True,Feedback='You know!'),
                                                                          dict(Id='3',Label='answer 3',Selected='0',Correct=True,Feedback='Yes this is the one.'),
                                                                          dict(Id='4',Label='answer 4',Selected='0',Correct=True,Feedback='Yes this is the one.'),
                                                                          dict(Id='5',Label='answer 5',Selected='0',Correct=True,Feedback='Yes this is the one.'),
                                                                          dict(Id='6',Label='answer 6',Selected='0',Correct=True,Feedback='Yes this is the one.'),
                                                                          dict(Id='7',Label='answer 7',Selected='0',Correct=True,Feedback='Yes this is the one.'),
                                                                          dict(Id='8',Label='answer 8',Selected='0',Correct=True,Feedback='Yes this is the one.'),
                                                                          dict(Id='9',Label='answer 9',Selected='0',Correct=True,Feedback='Yes this is the one.'),
                                                                          dict(Id='10',Label='answer 10',Selected='0',Correct=True,Feedback='Yes this is the one.'),
                                                                          dict(Id='11',Label='answer 11',Selected='0',Correct=True,Feedback='Yes this is the one.'),
                                                                          dict(Id='12',Label='answer 12',Selected='0',Correct=True,Feedback='Yes this is the one.'),
                                                                          dict(Id='13',Label='answer 13',Selected='0',Correct=True,Feedback='Yes this is the one.')]))))]))
                        
component_object = elicit_object.add_component(component=dict(component=component_definition),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)

#%% Trial 2: End of experiment page
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
#print(('https://elicit-experiment.com/api/v1/study_definitions/' + str(study_object.id) + '/protocol_definitions/' + str(protocol_object.id) + '/preview?phase_definition_id='  + str(phases[0].id) + '&trial_definition_id=' + str(trials[0].id)))    

print('Study link: ', end='')
print(('https://elicit-experiment.com/studies/' + str(study_object.id) + '/protocols/'  + str(protocol_object.id)))
