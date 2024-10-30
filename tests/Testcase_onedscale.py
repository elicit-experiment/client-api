# -*- coding: utf-8 -*-
"""
Example testing the OneDScale
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

## URLs
audio_url = "https://www.mfiles.co.uk/mp3-downloads/franz-liszt-liebestraum-3-easy-piano.mp3"
study_url = 'https://elicit-experiment.com/studies/'

##
## MAIN
##


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
study_definition_description = dict(title='OneDScale test',
                        description="""This is a test of the LikertScale component""",
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
protocol_definition_descriptiopn = dict(name='OneDScale test',
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
study_participants = elicit_object.ensure_users(0, NUM_ANONYMOUS_USERS)


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


#%% Trial 1: LikertScale

# Trial definition
trial_definition_specification = dict(trial_definition=dict(name='AlignForStimuli test', definition_data=dict(TrialType='OneDScale')))

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
                                                                Header=dict(HeaderLabel='{{center|This is a test of a OneDScale instrument}}')))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)

component_definition_description=dict(name='OneDScale',
                                         Instruments=[dict(
                                                  Instrument=dict(
                                                           OneDScale=dict(
                                                                    Layout='column',
                                                                    ColumnWidthPercent='30',
                                                                    HeaderLabel='No position with stimuli',
                                                                    Position=None,                                             
                                                                    X1AxisLabel='Label for X1 axis',
                                                                    X1AxisTicks=dict(
                                                                            X1AxisTick=[dict(Label='First x1 tick',Position='-0.5'),
                                                                                        dict(Label='Second x1 tick', Position='0.0'),
                                                                                        dict(Label='Third x1 tick', Position='0.5')]),
                                                                    X2AxisLabel='Label for X2 axis',
                                                                    X2AxisTicks=dict(
                                                                            X2AxisTick=[dict(Label='First x2 tick', Position='-1.0'),
                                                                                        dict(Label='Second x2 tick', Position='0.0'),
                                                                                        dict(Label='Third x2 tick', Position='1.0')]),
                                                                    Y1AxisLabel='Label for Y1 axis',
                                                                    Y1AxisTicks=dict(
                                                                            Y1AxisTick=dict(Label='Only y1 tick',Position='0.5')),
                                                                    Y2AxisLabel='Label for Y2 axis',
                                                                    Y2AxisTicks=dict(
                                                                             Y2AxisTick=dict(Label='Only y2 tick',Position='-0.5')))))],
                                        Stimuli=[dict(
                                                Label='This is my stimuli Label',
                                                Type='audio/mpeg',
                                                isOptional='0',
                                                isPausable='1',
                                                noPlays='1',
                                                URI=audio_url)])

component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)



component_definition_description=dict(name='OneDScale',
                                         Instruments=[dict(
                                                  Instrument=dict(
                                                           OneDScale=dict(
                                                                    Layout='column',
                                                                    ColumnWidthPercent='30',
                                                                    HeaderLabel='No stimuli (AlignForStimuli=0)',
                                                                    Position=None,                                             
                                                                    X1AxisLabel='Label for X1 axis',
                                                                    X1AxisTicks=dict(
                                                                            X1AxisTick=[dict(Label='First x1 tick',Position='-0.5'),
                                                                                        dict(Label='Second x1 tick', Position='0.0'),
                                                                                        dict(Label='Third x1 tick', Position='0.5')]),
                                                                    X2AxisLabel='Label for X2 axis',
                                                                    X2AxisTicks=dict(
                                                                            X2AxisTick=[dict(Label='First x2 tick', Position='-1.0'),
                                                                                        dict(Label='Second x2 tick', Position='0.0'),
                                                                                        dict(Label='Third x2 tick', Position='1.0')]),
                                                                    Y1AxisLabel='Label for Y1 axis',
                                                                    Y1AxisTicks=dict(
                                                                            Y1AxisTick=dict(Label='Only y1 tick',Position='0.5')),
                                                                    Y2AxisLabel='Label for Y2 axis',
                                                                    Y2AxisTicks=dict(
                                                                             Y2AxisTick=dict(Label='Only y2 tick',Position='-0.5')))))])

component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)


component_definition_description=dict(name='OneDScale',
                                         Instruments=[dict(
                                                  Instrument=dict(
                                                           OneDScale=dict(
                                                                    Layout='column',
                                                                    ColumnWidthPercent='30',
                                                                    HeaderLabel='No stimuli (AlignForStimuli=1)',
                                                                    Position=None,                                             
                                                                    X1AxisLabel='Label for X1 axis',
                                                                    X1AxisTicks=dict(
                                                                            X1AxisTick=[dict(Label='First x1 tick',Position='-0.5'),
                                                                                        dict(Label='Second x1 tick', Position='0.0'),
                                                                                        dict(Label='Third x1 tick', Position='0.5')]),
                                                                    X2AxisLabel='Label for X2 axis',
                                                                    X2AxisTicks=dict(
                                                                            X2AxisTick=[dict(Label='First x2 tick', Position='-1.0'),
                                                                                        dict(Label='Second x2 tick', Position='0.0'),
                                                                                        dict(Label='Third x2 tick', Position='1.0')]),
                                                                    Y1AxisLabel='Label for Y1 axis',
                                                                    Y1AxisTicks=dict(
                                                                            Y1AxisTick=dict(Label='Only y1 tick',Position='0.5')),
                                                                    Y2AxisLabel='Label for Y2 axis',
                                                                    Y2AxisTicks=dict(
                                                                             Y2AxisTick=dict(Label='Only y2 tick',Position='-0.5')))))])

component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)

component_definition_description=dict(name='OneDScale',
                                         Instruments=[dict(
                                                  Instrument=dict(
                                                           OneDScale=dict(
                                                                    Layout='column',
                                                                    ColumnWidthPercent='30',
                                                                    HeaderLabel='No stimuli (position=-0.5)',
                                                                    Position='-0.5',                                             
                                                                    X1AxisLabel='Label for X1 axis',
                                                                    X1AxisTicks=dict(
                                                                            X1AxisTick=[dict(Label='First x1 tick',Position='-0.5'),
                                                                                        dict(Label='Second x1 tick', Position='0.0'),
                                                                                        dict(Label='Third x1 tick', Position='0.5')]),
                                                                    X2AxisLabel='Label for X2 axis',
                                                                    X2AxisTicks=dict(
                                                                            X2AxisTick=[dict(Label='First x2 tick', Position='-1.0'),
                                                                                        dict(Label='Second x2 tick', Position='0.0'),
                                                                                        dict(Label='Third x2 tick', Position='1.0')]),
                                                                    Y1AxisLabel='Label for Y1 axis',
                                                                    Y1AxisTicks=dict(
                                                                            Y1AxisTick=dict(Label='Only y1 tick',Position='0.5')),
                                                                    Y2AxisLabel='Label for Y2 axis',
                                                                    Y2AxisTicks=dict(
                                                                             Y2AxisTick=dict(Label='Only y2 tick',Position='-0.5')))))])

component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)

#%%  Trial 3: End of experiment page
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

print('Added ' + str(len(study_participants)) + ' users to the protocol')
print('User ids: ', end='')
for user_id in range(0, len(study_participants)):
    print(str(study_participants[user_id].id) + ', ', end='')
print('')

print('Study link: ', end='')
print((study_url + str(study_object.id) + '/protocols/'  + str(protocol_object.id)))