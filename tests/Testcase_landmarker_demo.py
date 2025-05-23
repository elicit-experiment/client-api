"""
Testcase for webcam eye tracking
"""

import pprint

from pyelicit.command_line import parse_command_line_args
from pyelicit import elicit
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

response = requests.get('https://api.elicit-experiment.com', verify=False)

butterfly_video_url = 'https://youtu.be/zr9leP_Dcm8'

##
## MAIN
##

pp = pprint.PrettyPrinter(indent=4)

arg_defaults = {
    "env": "prod",
    "env_file": "../prod.yaml",
}

# get the Elicit object to define the experiment
elicit_object = elicit.Elicit(parse_command_line_args(arg_defaults))

# Double-check that we have the right user: we need to be admin to create a study
user_admin = elicit_object.assert_creator()

#
# Add a new Study Definition
#

# Define study
study_definition_description = dict(title='Landmarker Demo',
                                    description="""This study demos the Landmarker""",
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
protocol_definition_description = dict(name='Landmarker test',
                                       definition_data="whatever you want here",
                                       summary="This summary will be shown on the webpage? \n This is a test to show off all the capabilities of Elicit",
                                       description='This tests the Landmarker trial plugin',
                                       active=True)

# Add protocol
protocol_object = elicit_object.add_protocol_definition(
    protocol_definition=dict(protocol_definition=protocol_definition_description),
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
study_participants = elicit_object.ensure_users(NUM_REGISTERED_USERS, NUM_ANONYMOUS_USERS, False)

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

#%% Trial 1: Welcome page and start Monitor component

# Trial definition
trial_definition_specification = dict(trial_definition=dict(name='Start with the Monitor component', definition_data=dict(TrialType='Video page')))

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
                                                        HeaderLabel='{{center|Welcome to this Facelandmarker test}}')))]))

# Component addition: add the component to the trial
elicit_object.add_component(component=dict(component=header_component_definition),
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

#%% Trial 2: Landmarker calibration
#

trial_definition_specification = dict(trial_definition=dict(name='Landmarker Demo',
                                                            definition_data=dict(
                                                                    TrialType='Facelandmarker Calibration',
                                                                    type='NewComponent::FaceLandmarkDemo',
                                                                    # number of faces expected in the interface
                                                                    NumberOfFaces=1,
                                                                    Landmarks=True,  # return Landmark data
                                                                    Blendshapes=True,  # return Blendshape data
                                                                    FaceTransformation=True, # indicate if the affine transform should be performed or not
                                                                    CalibrationDuration=5, # duration of face within view measured in seconds
                                                                    StripZCoordinates=True, # 
                                                                    # IncludeBlendshapes='eyeLookInRight,eyeLookInLeft',
                                                                    # IncludeLandmarks = '1,2,5,100,346',
                                                                    MaximumSendRateHz=35,
                                                                    )))

trial_object = elicit_object.add_trial_definition(trial_definition=trial_definition_specification,
                                                  study_definition_id=study_object.id,
                                                  protocol_definition_id=protocol_object.id,
                                                  phase_definition_id=phase_object.id,
                                                  )

trials.append(trial_object)

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

print('Study link: ', end='')
print(('https://elicit-experiment.com/studies/' + str(study_object.id) + '/protocols/'  + str(protocol_object.id)))
