# -*- coding: utf-8 -*-
"""
Example testing the components with stimuli and instruments
"""

import sys
import yaml
import os

sys.path.append("../")

import pprint

from pyelicit.command_line import parse_command_line_args, get_parser
from pyelicit import elicit
from random import shuffle

## Stimuli URLs
audio_url = "https://www.mfiles.co.uk/mp3-downloads/franz-liszt-liebestraum-3-easy-piano.mp3"
video_youtube_url = 'https://youtu.be/zr9leP_Dcm8'
video_mp4_url = 'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4'
test_image_url = 'https://dummyimage.com/750x550/996633/fff'

##

##
## MAIN
##

pp = pprint.PrettyPrinter(indent=4)

# get the elicit object to define the experiment
parser = get_parser()
parser.add_argument('--folder', type=str, default='generic')
args = parse_command_line_args()
elicit_object = elicit.Elicit(args)

# Double-check that we have the right user: we need to be admin to create a study
# user_admin = elicit_object.assert_investigator()
user_admin = elicit_object.assert_investigator()

#
# Add a new Study Definition
#

# Define study
with open(os.path.join(args.folder, 'study_definition.yaml'), 'r') as f:
    study_definition_description = yaml.safe_load(f)
    study_definition_description['principal_investigator_user_id'] = user_admin.id

with open(os.path.join(args.folder, 'protocol_definition.yaml'), 'r') as f:
    protocol_definition_description = yaml.safe_load(f)

with open(os.path.join(args.folder, 'phase_definition.yaml'), 'r') as f:
    phase_definition_description = yaml.safe_load(f)

# with open(os.path.join(args.folder, 'phase_definition.yaml'), 'w') as f:
#     yaml.dump(phase_definition_description, f, default_flow_style=False)
#     phase_definition_description = yaml.safe_load(f)

study_object = elicit_object.add_study(study=dict(study_definition=study_definition_description))
protocol_object = elicit_object.add_protocol_definition(
    protocol_definition=dict(protocol_definition=protocol_definition_description),
    study_definition_id=study_object.id)
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

# Define phase

# Add phase
phase_object = elicit_object.add_phase_definition(phase_definition=phase_definition_description,
                                                  study_definition_id=study_object.id,
                                                  protocol_definition_id=protocol_object.id)
phases.append(phase_object)

# load all the yaml files from args.folder
trial_dirs = [f.path for f in os.scandir(args.folder) if f.is_dir()]
for trial_dir in sorted(trial_dirs):
    with open("{}.yaml".format(trial_dir), 'r') as f:
        trial_definition = yaml.safe_load(f)
        print("{}.yaml".format(trial_dir))
        print(trial_definition)
        trial_object = elicit_object.add_trial_definition(trial_definition=trial_definition,
                                                          study_definition_id=study_object.id,
                                                          protocol_definition_id=protocol_object.id,
                                                          phase_definition_id=phase_object.id)
        # save trial to later define trial orders
        trials.append(trial_object)
    yaml_files = [f for f in sorted(os.listdir(trial_dir)) if f.endswith('.yaml') or f.endswith('.yml')]
    for yaml_file in yaml_files:
        with open(os.path.join(trial_dir, yaml_file), 'r') as f:
            component_definition = yaml.safe_load(f)
            component_definition = elicit_object.add_component(component=dict(component=component_definition),
                                                           study_definition_id=study_object.id,
                                                           protocol_definition_id=protocol_object.id,
                                                           phase_definition_id=phase_object.id,
                                                           trial_definition_id=trial_object.id)


# %% End of experiment

#
# Trial 5: End of experiment page
#
# Trial definition
trial_definition_specification = dict(
    trial_definition=dict(name='EndOfExperiment', definition_data=dict(TrialType='EndOfExperiment')))
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

# %% Add Trial Orders to the study

# trail_orders for specific users
for study_participant in study_participants:
    trial_order_specification_user = dict(
        trial_order=dict(sequence_data=",".join([str(trial.id) for trial in trials]), user_id=study_participant.id))
    print(trial_order_specification_user)

    # Trial order addition
    trial_order_object = elicit_object.add_trial_order(trial_order=trial_order_specification_user,
                                                       study_definition_id=study_object.id,
                                                       protocol_definition_id=protocol_object.id,
                                                       phase_definition_id=phase_object.id)
# trail_orders for anonymous users
for anonymous_participant in range(0, 10):
    trial_id = [int(trial.id) for trial in trials]
    shuffle(trial_id)

    trial_order_specification_anonymous = dict(trial_order=dict(sequence_data=",".join(map(str, trial_id))))
    print(trial_order_specification_anonymous)

    # Trial order addition
    trial_order_object = elicit_object.add_trial_order(trial_order=trial_order_specification_anonymous,
                                                       study_definition_id=study_object.id,
                                                       protocol_definition_id=protocol_object.id,
                                                       phase_definition_id=phase_object.id)

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

print('Study link: ', end='')
print(('https://elicit-experiment.com/studies/' + str(study_object.id) + '/protocols/' + str(protocol_object.id)))
