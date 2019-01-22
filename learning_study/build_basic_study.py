"""
Example for dumping the results of a study.
"""

import pprint

import sys
import csv
import json

from examples_base import *
from pyelicit import elicit

##
## MAIN
##

pp = pprint.PrettyPrinter(indent=4)

args = parse_command_line_args()

el = elicit.Elicit(args)

#
# Double-check that we have the right user: we need to be admin to create a study
#

user = el.assert_admin()

#
# Get list of users who will use the study
#

users = el.get_all_users()

study_participants = list(filter(lambda usr: usr.role == 'registered_user', users))

#
# Add a new Study Definition
#
study_definition = dict(title='Learning Study - WebGazer',
                        description="""Study of learning, using eye gaze tracking from WebGazer 
                        This version calibrates on the video page""",
                        version=1,
                        lock_question=1,
                        enable_previous=1,
                        allow_anonymous_users=True,  # allow taking the study without login
                        show_in_study_list=True,  # show in the (public) study list for anonymous protocols
                        footer_label="This is the footer of the study",
                        redirect_close_on_url=el.elicit_api.api_url + "/participant",
                        data="Put some data here, we don't really care about it.",
                        principal_investigator_user_id=user.id)
new_study = el.add_study(study=dict(study_definition=study_definition))

#
# Add a new Protocol Definition
#

new_protocol_definition = dict(name='Learning Study Protocol',
                               definition_data="whatever you want here",
                               summary="Video Learning",
                               description='A nice description',
                               active=True)
new_protocol = el.add_protocol_definition(protocol_definition=dict(protocol_definition=new_protocol_definition),
                                          study_definition_id=new_study.id)

#
# Add users to protocol
#

el.add_users_to_protocol(new_study, new_protocol, study_participants)

#
#
# Add Phase Definition

new_phase_definition = dict(phase_definition=dict(definition_data="foo"))

new_phase = el.add_phase_definition(phase_definition=new_phase_definition,
                                    study_definition_id=new_study.id,
                                    protocol_definition_id=new_protocol.id)
phase_definitions = [new_phase]

trials = []

#
# Add Trial Definitions with components
#

# WebGazer Configuration

new_trial_definition_config = dict(
    trial_definition=dict(definition_data=dict(type="NewComponent::WebGazerCalibrate")))
new_trial_definition = el.add_trial_definition(trial_definition=new_trial_definition_config,
                                               study_definition_id=new_study.id,
                                               protocol_definition_id=new_protocol.id,
                                               phase_definition_id=new_phase.id)
trials.append(new_trial_definition)

new_component_config = dict(name='Empty component',
                            definition_data=dict())
new_component = el.add_component(component=dict(component=dict(name='Empty component',
                                                               definition_data=dict())),
                                 study_definition_id=new_study.id,
                                 protocol_definition_id=new_protocol.id,
                                 phase_definition_id=new_phase.id,
                                 trial_definition_id=new_trial_definition.id)

# Video page

new_trial_definition_config = dict(trial_definition=dict(definition_data=dict()))
new_trial_definition = el.add_trial_definition(trial_definition=new_trial_definition_config,
                                               study_definition_id=new_study.id,
                                               protocol_definition_id=new_protocol.id,
                                               phase_definition_id=new_phase.id)
trials.append(new_trial_definition)

butterfly_video_url = 'https://youtu.be/zr9leP_Dcm8'
video_component_definition = dict(
    Stimuli=[dict(
        Label='Video Label',
        Type='video/youtube',
        IsPausable=False,
        URI=butterfly_video_url)])

new_component_config = dict(name='Video page component',
                            definition_data=video_component_definition)
new_component = el.add_component(component=dict(component=new_component_config),
                                 study_definition_id=new_study.id,
                                 protocol_definition_id=new_protocol.id,
                                 phase_definition_id=new_phase.id,
                                 trial_definition_id=new_trial_definition.id)

# Radio button page

new_trial_definition_config = dict(trial_definition=dict(definition_data=dict()))
new_trial_definition = el.add_trial_definition(trial_definition=new_trial_definition_config,
                                               study_definition_id=new_study.id,
                                               protocol_definition_id=new_protocol.id,
                                               phase_definition_id=new_phase.id)
trials.append(new_trial_definition)

component_definition = dict(
    Instruments=[dict(
        Instrument=dict(
            RadioButtonGroup=dict(
                AlignForStimuli='0',
                QuestionsPerRow=1,
                HeaderLabel='question label',
                # todo_permute these
                Items=dict(
                    Item=[
                        dict(
                            Id='0',
                            Label='answer 1',
                            Selected='0',
                            Correct=True),
                        dict(
                            Id='1',
                            Label='answer 2',
                            Selected='0',
                            Correct=False),
                        dict(
                            Id='2',
                            Label='answer 3',
                            Selected='0',
                            Correct=False),
                        dict(
                            Id='3',
                            Label='answer 4',
                            Selected='0',
                            Correct=False)]),
                MaxNoOfScalings='1',
                MinNoOfScalings='1')))])

new_component_config = dict(name='Radio button component',
                            definition_data=component_definition)
new_component = el.add_component(component=dict(component=new_component_config),
                                 study_definition_id=new_study.id,
                                 protocol_definition_id=new_protocol.id,
                                 phase_definition_id=new_phase.id,
                                 trial_definition_id=new_trial_definition.id)

# end of experiment page

new_trial_definition_config = dict(trial_definition=dict(definition_data='{}'))
new_trial_definition = el.add_trial_definition(trial_definition=new_trial_definition_config,
                                               study_definition_id=new_study.id,
                                               protocol_definition_id=new_protocol.id,
                                               phase_definition_id=new_phase.id)
trials.append(new_trial_definition)

label_component = dict(
    Instruments=[dict(
        Instrument=dict(
            Header=dict(
                HeaderLabel='Thank you')))]
)

new_component_config = dict(name='Label component',
                            definition_data=json.dumps(component_definition))
new_component = el.add_component(component=dict(component=new_component_config),
                                 study_definition_id=new_study.id,
                                 protocol_definition_id=new_protocol.id,
                                 phase_definition_id=new_phase.id,
                                 trial_definition_id=new_trial_definition.id)

eoe_component = dict(
    Instruments=[dict(
        Instrument=dict(
            EndOfExperiment=dict()))]
)

new_component_config = dict(name='End of experiment component',
                            definition_data=json.dumps(eoe_component))
new_component = el.add_component(component=dict(component=new_component_config),
                                 study_definition_id=new_study.id,
                                 protocol_definition_id=new_protocol.id,
                                 phase_definition_id=new_phase.id,
                                 trial_definition_id=new_trial_definition.id)

#
# Add a new Trial Orders
#

for study_participant in study_participants:
    new_trial_order_config = dict(trial_order=dict(sequence_data=",".join([str(trial.id) for trial in trials]),
                                                   user_id=study_participant.id))
    new_trial_order = el.add_trial_order(trial_order=new_trial_order_config,
                                         study_definition_id=new_study.id,
                                         protocol_definition_id=new_protocol.id,
                                         phase_definition_id=new_phase.id)

#
# Add a new Phase Order
#

phase_sequence_data = ",".join(
    [str(phase_definition.id) for phase_definition in phase_definitions])
new_phase_order_config = dict(phase_order=dict(sequence_data=phase_sequence_data,
                                               user_id=user.id))
new_phase_order = el.add_phase_order(phase_order=new_phase_order_config,
                                     study_definition_id=new_study.id,
                                     protocol_definition_id=new_protocol.id)
