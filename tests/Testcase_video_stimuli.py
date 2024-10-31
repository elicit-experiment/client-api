# -*- coding: utf-8 -*-
"""
Example testing the video player
"""

import sys
sys.path.append("../")

import pprint

from examples_base import parse_command_line_args
from pyelicit import elicit
from random import shuffle

experiment_URL = 'https://elicit-experiment.com'

##
## MAIN
##

NUM_ANONYMOUS_USERS = 10
NUM_REGISTERED_USERS = 0

pp = pprint.PrettyPrinter(indent=4)

# get the elicit object to define the experiment
elicit_object = elicit.Elicit(parse_command_line_args())


# Double-check that we have the right user: we need to be investigator or admin to create a study
user_investigator = elicit_object.assert_investigator()

#
# Add a new Study Definition
#

# Define study
study_definition_description = dict(title='Video player test',
                        description="""This is a test of the video player""",
                        version=1,
                        lock_question=1,
                        enable_previous=1,
                        allow_anonymous_users=True,  # allow taking the study without login
                        show_in_study_list=False,  # show in the (public) study list for anonymous protocols
                        footer_label="If you have any questions, you can email {{link|mailto:neuroccny@gmail.com|here}}",
                        redirect_close_on_url=experiment_URL + "/participant",
                        data="Put some data here, we don't really care about it.",
                        principal_investigator_user_id=user_investigator.id)


study_object = elicit_object.add_study(study=dict(study_definition=study_definition_description))

#
# Create a Protocol Definition
#

# Define protocol
protocol_definition_description = dict(name='This protocol tests the video player',
                                       definition_data="whatever you want here",
                                       summary="This is a test of the video player",
                                       description='This is a test of the video player',
                                       active=True)

# Add protocol
protocol_object = elicit_object.add_protocol_definition(protocol_definition=dict(protocol_definition=protocol_definition_description),
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


#%% Trial 1: 2 videos on the same page

# Trial definition
trial_definition_specification = dict(trial_definition=dict(name='Multi-video page', definition_data=dict(TrialType='Video page')))
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
                                                                Header=dict(HeaderLabel='{{center|This is a test of multi videos per page}}')))]))

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
                                            Label='This video is pausable (smol)',
                                            Type='video/youtube',
                                            Width='50',
                                            Height='50',
                                            IsPausable=True,
                                            URI=butterfly_video_url)]))

component_object = elicit_object.add_component(component=dict(component=video_component_definition),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)

#Video 2
butterfly_video_url = 'https://youtu.be/zr9leP_Dcm8'
video_component_definition = dict(name='This video is NOT pausable',
                            definition_data=dict(
                                    Stimuli=[dict(
                                            Label='This video is NOT pausable',
                                            Type='video/youtube',
                                            IsPausable=False,
                                            URI=butterfly_video_url)]))

component_object = elicit_object.add_component(component=dict(component=video_component_definition),
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

#%% Trial 2: Single pausable video

# Trial definition
trial_definition_specification = dict(trial_definition=dict(name='Pausable video page', definition_data=dict(TrialType='Video page')))
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
                                                                Header=dict(HeaderLabel='{{center|Pausable video page}}')))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)


# Define video component (pausable)
butterfly_video_url = 'https://youtu.be/zr9leP_Dcm8'
video_component_definition = dict(name='This video is pausable',
                            definition_data=dict(
                                    Stimuli=[dict(
                                            Label='This video is pausable',
                                            Type='video/youtube',
                                            IsPausable=True,
                                            URI=butterfly_video_url)]))

#add video component to trial
component_object = elicit_object.add_component(component=dict(component=video_component_definition),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)


def video_test(test_name, video_label, video_params):
    #
    # Trial definition
    trial_definition_specification = dict(
        trial_definition=dict(name=test_name, definition_data=dict(TrialType='Video page')))
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
                                                            HeaderLabel="{{center|%s}}"%test_name)))]))
    # Component addition: add the component to the trial
    elicit_object.add_component(component=dict(component=header_component_definition),
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id,
                                               trial_definition_id=trial_object.id)
    # Define video component
    butterfly_video_url = 'https://youtu.be/zr9leP_Dcm8'
    stimulus = dict(
                                              Label=video_label,
                                              Type='video/youtube',
                                              URI=butterfly_video_url);
    stimulus.update(video_params)
    video_component_definition = dict(name=video_label,
                                      definition_data=dict(
                                          Stimuli=[stimulus]))
    print('WUT')
    print(video_component_definition)
    elicit_object.add_component(component=dict(component=video_component_definition),
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id,
                                               trial_definition_id=trial_object.id)


#
#%% Trial 3: Single non pausable video
video_test(test_name='Non-Pausable video page', video_label='This video is NOT pausable', video_params=dict(IsPausable=False))

#
#%% Trial 4: Single replayable video
video_test(test_name='Replayable video page', video_label='This video is replayable', video_params=dict(IsReplayable=True))

#
#%% Trial 5: Single optional video
video_test(test_name='Optional video page', video_label='This video is optional', video_params=dict(IsOptional=True))

#%% Trial 6: Single optional video
video_test(test_name='NOT Optional video page', video_label='This video is optional', video_params=dict(IsOptional=False))
#

#%% Trial 7: Single replayable (2X) video
video_test(test_name='Replayable video page', video_label='This video is replayable (2 times)', video_params=dict(IsReplayable=True, MaxReplayCount=2))

#%% Trial 6: Single optional video
video_test(test_name='Optional video page', video_label='This video is optional', video_params=dict(IsOptional=False))

#
#%% Trial 7: Single replayable (2X) video
video_test(test_name='Replayable video page', video_label='This video is replayable (2 times)', video_params=dict(IsReplayable=True, MaxReplayCount=2))

#%% Trial 8: End of experiment page

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

print('Added ' + str(len(study_participants)) + ' users to the protocol')
print('User ids: ', end='')
for user_id in range(0, len(study_participants)):
    print(str(study_participants[user_id].id) + ', ', end='')
print('')

print('Study link: ', end='')
print((experiment_URL + '/studies/' + str(study_object.id) + '/protocols/'  + str(protocol_object.id)))