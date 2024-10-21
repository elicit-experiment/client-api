# -*- coding: utf-8 -*-
"""
Example testing the components with stimuli and instruments
"""

import sys

sys.path.append("../")

import pprint

from examples_base import parse_command_line_args
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
elicit_object = elicit.Elicit(parse_command_line_args())

# Double-check that we have the right user: we need to be admin to create a study
user_admin = elicit_object.assert_investigator()
#user_admin = elicit_object.assert_admin()

#
# Add a new Study Definition
#

# Define study
study_definition_description = dict(title='Components with stimuli and instruments',
                                    description="""This is a test of Components with stimuli and instruments""",
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
protocol_definition_descriptiopn = dict(name='Components with stimuli and instruments',
                                        definition_data="whatever you want here",
                                        summary="This is a test of Components with stimuli and instruments",
                                        description='This is a test of Components with stimuli and instruments',
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
study_participants = list(filter(lambda usr: usr.role == 'anonymous_user', users))

# add users to protocol
elicit_object.add_users_to_protocol(study_object, protocol_object, study_participants)

#
# Add Phase Definition for testing RadiobuttonGroup with stimuli
#
phases = []
trials = []

# %% RadiobuttonGroup

# Define phase
phase_definition_description = dict(
    phase_definition=dict(name='RadiobuttonGroup', definition_data=dict(PhaseType='RadiobuttonGroup')))

# Add phase
phase_object = elicit_object.add_phase_definition(phase_definition=phase_definition_description,
                                                  study_definition_id=study_object.id,
                                                  protocol_definition_id=protocol_object.id)
phases.append(phase_object)


def make_trial(component_type, stimulus_type, layout, instrument_config = dict()):
    # Trial definition col order
    trial_definition_specification = dict(
        trial_definition=dict(name="{0} with {1} Stimuli ({2} layout)".format(component_type, stimulus_type, layout),
                              definition_data=dict(
                                  TrialType='RadiobuttonGroup page')))

    trial_object = elicit_object.add_trial_definition(trial_definition=trial_definition_specification,
                                                      study_definition_id=study_object.id,
                                                      protocol_definition_id=protocol_object.id,
                                                      phase_definition_id=phase_object.id)
    # save trial to later define trial orders
    trials.append(trial_object)

    # Component definition: Header Label
    header_label = "{{{{center|{0} with {1} Stimuli}}}}".format(component_type, stimulus_type)
    component_definition_description = dict(name='HeaderLabel',
                                            definition_data=dict(
                                                Instruments=[dict(
                                                    Instrument=dict(
                                                        Header=dict(
                                                            HeaderLabel=header_label)))]))

    # Component addition: add the component to the trial
    component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                                   study_definition_id=study_object.id,
                                                   protocol_definition_id=protocol_object.id,
                                                   phase_definition_id=phase_object.id,
                                                   trial_definition_id=trial_object.id)

    if layout == "column":
        layout_parameters = dict(
            # LAYOUT
            # Layout is 'column' or 'row'
            # ColumnWidthPercent is the precentage of the width the instrument takes; the stimulus is therefore 100-ColumnWidthPercent
            Layout='column',
            ColumnWidthPercent='30',
            QuestionsPerRow='1')
    else:
        layout_parameters = dict(
            # LAYOUT
            # Layout is 'column' or 'row'
            # ColumnWidthPercent is the precentage of the width the instrument takes; the stimulus is therefore 100-ColumnWidthPercent
            Layout='row',
            QuestionsPerRow= 1 if component_type == 'CheckboxGroup' else '6')

    header_label = "This is a {0} with {1} stimuli ({2})".format(component_type, stimulus_type, layout)

    if component_type == 'RadiobuttonGroup':
        component_parameters = dict(
            HeaderLabel=header_label,
            IsOptional='0',
            Items=dict(
                Item=[dict(Id='1', Label='answer 1', Selected='0', Correct=True),
                      dict(Id='2', Label='answer 2', Selected='0', Correct=True),
                      dict(Id='3', Label='answer 3', Selected='0', Correct=True),
                      dict(Id='4', Label='answer 4', Selected='0', Correct=True),
                      dict(Id='5', Label='answer 5', Selected='0', Correct=True),
                      dict(Id='6', Label='answer 6', Selected='0', Correct=True),
                      dict(Id='7', Label='answer 7', Selected='0', Correct=True),
                      dict(Id='8', Label='answer 8', Selected='0', Correct=True),
                      dict(Id='9', Label='answer 9', Selected='0', Correct=True),
                      dict(Id='10', Label='answer 10', Selected='0', Correct=True),
                      dict(Id='11', Label='answer 11', Selected='0', Correct=True),
                      dict(Id='12', Label='answer 12', Selected='0', Correct=True),
                      dict(Id='13', Label='answer 13', Selected='0',
                           Correct=True)]))

        component_parameters = {**component_parameters, **layout_parameters}
        instruments = [dict(
            Instrument=dict(
                RadioButtonGroup=component_parameters))]
    elif component_type == 'CheckboxGroup':
        component_parameters = dict(
            HeaderLabel='checkboxgroup',
            MaxNoOfSelections='1',
            MinNoOfSelections='1',
            RandomizeOrder=False,
            Items=dict(
                Item=[
                    dict(Id='0',
                         Label='yes lorem50 Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco ',
                         Selected='0'),
                    dict(Id='1',
                         Label='no Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco ',
                         Selected='0')]
            ))
        component_parameters = {**component_parameters, **layout_parameters}
        instruments = [dict(
            Instrument=dict(
                CheckBoxGroup=component_parameters))]
    elif component_type == 'Freetext':
        component_parameters = dict(
                                    HeaderLabel='freetext',
                                    BoxHeight=None,
                                    BoxWidth=None,
                                    Label="Please write what you think about this excerpts",
                                    LabelPosition='top',
                                    Resizable=None,
                                    Validation='.+')
        component_parameters = {**component_parameters, **layout_parameters, **instrument_config}
        instruments = [dict(Instrument=dict(Freetext=component_parameters))]

    if stimulus_type == 'video':
        stimulus = dict(Label='This video is pausable',
                        Type='video/mp4',
                        IsPausable=True,
                        IsOptional=True,
                        IsReplayable=True,
                        MaxReplayCount=2,
                        URI=video_mp4_url)
    elif stimulus_type == 'video_youtube':
        stimulus = dict(Label='This video is pausable',
                        Type='video/youtube',
                        IsPausable=True,
                        IsOptional=True,
                        IsReplayable=True,
                        MaxReplayCount=2,
                        URI=video_youtube_url)
    elif stimulus_type == 'audio':
        stimulus = dict(Label='Audio Excerpt',
                        Type='audio/mpeg',
                        IsPausable=True,
                        IsOptional=True,
                        IsReplayable=True,
                        MaxReplayCount=2,
                        URI=audio_url)
        
    elif stimulus_type == 'image':
        stimulus = dict(
            Label='This is a full size',
            Type='image',
            Width='100%',
            Height='100%',
            URI=test_image_url)
    else:
        stimulus = None

    ## 13 answer options
    stimuli = dict(Stimuli=[stimulus])
    definition_data = {**dict(Instruments=instruments),**stimuli}
    component_definition = dict(name=component_type,
                                definition_data=definition_data)

    component_object = elicit_object.add_component(component=dict(component=component_definition),
                                                   study_definition_id=study_object.id,
                                                   protocol_definition_id=protocol_object.id,
                                                   phase_definition_id=phase_object.id,
                                                   trial_definition_id=trial_object.id)
    
# %% RadiobuttonGroup
make_trial('RadiobuttonGroup', None, 'row')
make_trial('RadiobuttonGroup', None, 'column')
make_trial('RadiobuttonGroup', 'video', 'row')
make_trial('RadiobuttonGroup', 'video_youtube', 'row')
make_trial('RadiobuttonGroup', 'audio', 'row')
make_trial('RadiobuttonGroup', 'image', 'row')
make_trial('RadiobuttonGroup', 'video', 'column')
make_trial('RadiobuttonGroup', 'video_youtube', 'column')
make_trial('RadiobuttonGroup', 'audio', 'column')
make_trial('RadiobuttonGroup', 'image', 'column')

# %% CheckBoxGroup

make_trial('CheckboxGroup', None, 'row')
make_trial('CheckboxGroup', None, 'column')
make_trial('CheckboxGroup', 'video', 'row')
make_trial('CheckboxGroup', 'video_youtube', 'row')
make_trial('CheckboxGroup', 'audio', 'row')
make_trial('CheckboxGroup', 'image', 'row')
make_trial('CheckboxGroup', 'video', 'column')
make_trial('CheckboxGroup', 'video_youtube', 'column')
make_trial('CheckboxGroup', 'audio', 'column')
make_trial('CheckboxGroup', 'image', 'column')

# %% FreeText

make_trial('Freetext', None, 'row')
make_trial('Freetext', None, 'column')
make_trial('Freetext', 'video', 'row', dict(BoxWidth='10',BoxHeight='5',Resizeable=True))
make_trial('Freetext', 'video_youtube', 'row', dict(BoxWidth='20',BoxHeight='2',Resizeable=True))
make_trial('Freetext', 'audio', 'row')
make_trial('Freetext', 'image', 'row', dict(BoxWidth='10',BoxHeight='1',Resizeable=True))
make_trial('Freetext', 'video', 'column')
make_trial('Freetext', 'video_youtube', 'column')
make_trial('Freetext', 'audio', 'column')
make_trial('Freetext', 'image', 'column')

# %% End of experiment

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
