# -*- coding: utf-8 -*-
"""
Example testing the components with stimuli and instruments
"""

import pprint

from pyelicit.command_line import parse_command_line_args
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
# user_admin = elicit_object.assert_investigator()
user_admin = elicit_object.assert_investigator()

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
protocol_definition_description = dict(name='Components with stimuli and instruments',
                                       definition_data="whatever you want here",
                                       summary="This is a test of Components with stimuli and instruments",
                                       description='This is a test of Components with stimuli and instruments',
                                       active=True)

# Add protocol
protocol_object = elicit_object.add_protocol_definition(
    protocol_definition=dict(protocol_definition=protocol_definition_description),
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
    phase_definition=dict(name='LikertScale', definition_data=dict(PhaseType='LikertScale   ')))

# Add phase
phase_object = elicit_object.add_phase_definition(phase_definition=phase_definition_description,
                                                  study_definition_id=study_object.id,
                                                  protocol_definition_id=protocol_object.id)
phases.append(phase_object)


def make_trial(component_type, stimulus_type, layout, instrument_config=dict()):
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
            QuestionsPerRow=1 if component_type == 'CheckboxGroup' else '6')

    header_label = "This is a {0} with {1} stimuli ({2})".format(component_type, stimulus_type, layout)

    if component_type == 'LikertScale':
        component_parameters = dict(
            HeaderLabel=header_label,
            IsOptional='0',
            MinNoOfScalings='10',
            Items=dict(
                Item=[dict(Id='1', Label='good'),
                      dict(Id='2', Label='indifferent'),
                      dict(Id='3', Label='bad')]))

        component_parameters = {**component_parameters, **layout_parameters}
        instruments = [dict(
            Instrument=dict(
                LikertScale=component_parameters))]
    elif component_type == 'OneDScale':
        component_parameters = dict(
            HeaderLabel=header_label,
            IsOptional='0',
            Position='-0.3',
            X1AxisTicks=dict(
                X1AxisTick=[dict(dictId='1', Position='-1.0', Label='good'),
                            dict(Id='2', Position='0.0', Label='indifferent'),
                            dict(Id='3', Position='1.0', Label='bad')]),
            X2AxisTicks=dict(
                X2AxisTick=[dict(dictId='1', Position='-1.0', Label='red'),
                            dict(Id='2', Position='0.0', Label='green'),
                            dict(Id='3', Position='1.0', Label='blue')]),
            Y1AxisTicks=dict(
                Y1AxisTick=[dict(dictId='1', Position='-1.0', Label='top'),
                            dict(Id='2', Position='0.0', Label='middle'),
                            dict(Id='3', Position='1.0', Label='bottom')]),
            Y2AxisTicks=dict(
                Y2AxisTick=[dict(dictId='1', Position='0.0', Label='up'),
                            dict(Id='2', Position='0.0', Label='center'),
                            dict(Id='3', Position='1.0', Label='down')])
        )

        component_parameters = {**component_parameters, **layout_parameters}
        instruments = [dict(
            Instrument=dict(
                OneDScale=component_parameters))]
    elif component_type == 'OneDScaleT':
        component_parameters = dict(
            HeaderLabel=header_label,
            IsOptional='0',
            Position='-0.3',
            X1AxisTicks=dict(
                X1AxisTick=[dict(dictId='1', Position='-1.0', Label='good'),
                            dict(Id='2', Position='0.0', Label='indifferent'),
                            dict(Id='3', Position='1.0', Label='bad')]),
            X2AxisTicks=dict(
                X2AxisTick=[dict(dictId='1', Position='-1.0', Label='red'),
                            dict(Id='2', Position='0.0', Label='green'),
                            dict(Id='3', Position='1.0', Label='blue')]),
            Y1AxisTicks=dict(
                Y1AxisTick=[dict(dictId='1', Position='-1.0', Label='top'),
                            dict(Id='2', Position='0.0', Label='middle'),
                            dict(Id='3', Position='1.0', Label='bottom')]),
            Y2AxisTicks=dict(
                Y2AxisTick=[dict(dictId='1', Position='0.0', Label='up'),
                            dict(Id='2', Position='0.0', Label='center'),
                            dict(Id='3', Position='1.0', Label='down')])
        )

        component_parameters = {**component_parameters, **layout_parameters}
        instruments = [dict(
            Instrument=dict(
                OneDScaleT=component_parameters))]
    elif component_type == 'TwoDScale':
        component_parameters = dict(
            HeaderLabel=header_label,
            IsOptional='0',
            Position='-0.3',
            X1AxisTicks=dict(
                X1AxisTick=[dict(dictId='1', Position='-1.0', Label='good'),
                            dict(Id='2', Position='0.0', Label='indifferent'),
                            dict(Id='3', Position='1.0', Label='bad')]),
            X2AxisTicks=dict(
                X2AxisTick=[dict(dictId='1', Position='-1.0', Label='red'),
                            dict(Id='2', Position='0.0', Label='green'),
                            dict(Id='3', Position='1.0', Label='blue')]),
            Y1AxisTicks=dict(
                Y1AxisTick=[dict(dictId='1', Position='-1.0', Label='top'),
                            dict(Id='2', Position='0.0', Label='middle'),
                            dict(Id='3', Position='1.0', Label='bottom')]),
            Y2AxisTicks=dict(
                Y2AxisTick=[dict(dictId='1', Position='0.0', Label='up'),
                            dict(Id='2', Position='0.0', Label='center'),
                            dict(Id='3', Position='1.0', Label='down')])
        )

        component_parameters = {**component_parameters, **layout_parameters}
        instruments = [dict(
            Instrument=dict(
                TwoDScale=component_parameters))]
    elif component_type == 'TwoDScaleK':
        component_parameters = dict(
            HeaderLabel=header_label,
            IsOptional='0',
            Position='-0.3',
            X1AxisTicks=dict(
                X1AxisTick=[dict(dictId='1', Position='-1.0', Label='good'),
                            dict(Id='2', Position='0.0', Label='indifferent'),
                            dict(Id='3', Position='1.0', Label='bad')]),
            Y1AxisTicks=dict(
                Y1AxisTick=[dict(dictId='1', Position='-1.0', Label='top'),
                            dict(Id='2', Position='0.0', Label='middle'),
                            dict(Id='3', Position='1.0', Label='bottom')]),
            Items=dict(
                Item=[dict(Id='1', Label='good'),
                      dict(Id='2', Label='indifferent'),
                      dict(Id='3', Label='bad')])
        )

        component_parameters = {**component_parameters, **layout_parameters}
        instruments = [dict(
            Instrument=dict(
                TwoDKScaleDD=component_parameters))]
    elif component_type == 'TaggingA':
        component_parameters = dict(
            HeaderLabel=header_label,
            IsOptional='0',
            SelectionTagBoxLabel="SelectionTagBoxLabel",
            UserTagBoxLabel = "UserTagBoxLabel",
            TextField = "TextField",
        Position='-0.3',
            SelectionTags=dict(
                Item=[dict(dictId='1', Position='-1.0', Label='good'),
                            dict(Id='2', Position='0.0', Label='indifferent'),
                            dict(Id='3', Position='1.0', Label='bad')]),
            UserTags=dict(
                Item=[dict(dictId='1', Position='-1.0', Label='top'),
                            dict(Id='2', Position='0.0', Label='middle'),
                            dict(Id='3', Position='1.0', Label='bottom')]),
            Items=dict(
                Item=[dict(Id='1', Label='good'),
                      dict(Id='2', Label='indifferent'),
                      dict(Id='3', Label='bad')])
        )

        component_parameters = {**component_parameters, **layout_parameters}
        instruments = [dict(
            Instrument=dict(
                TaggingA=component_parameters))]
    elif component_type == 'TaggingB':
        component_parameters = dict(
            HeaderLabel=header_label,
            IsOptional='0',
            SelectionTagBoxLabel="SelectionTagBoxLabel",
            UserTagBoxLabel = "UserTagBoxLabel",
            TextField = "TextField",
        Position='-0.3',
            SelectionTags=dict(
                Item=[dict(dictId='1', Position='-1.0', Label='good'),
                            dict(Id='2', Position='0.0', Label='indifferent'),
                            dict(Id='3', Position='1.0', Label='bad')]),
            UserTags=dict(
                Item=[dict(dictId='1', Position='-1.0', Label='top'),
                            dict(Id='2', Position='0.0', Label='middle'),
                            dict(Id='3', Position='1.0', Label='bottom')]),
            Items=dict(
                Item=[dict(Id='1', Label='good'),
                      dict(Id='2', Label='indifferent'),
                      dict(Id='3', Label='bad')])
        )

        component_parameters = {**component_parameters, **layout_parameters}
        instruments = [dict(
            Instrument=dict(
                TaggingB=component_parameters))]

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
    definition_data = {**dict(Instruments=instruments), **stimuli}
    component_definition = dict(name=component_type,
                                definition_data=definition_data)

    component_object = elicit_object.add_component(component=dict(component=component_definition),
                                                   study_definition_id=study_object.id,
                                                   protocol_definition_id=protocol_object.id,
                                                   phase_definition_id=phase_object.id,
                                                   trial_definition_id=trial_object.id)


make_trial('LikertScale', None, 'row')
make_trial('LikertScale', None, 'column')
make_trial('LikertScale', 'video', 'row')
make_trial('LikertScale', 'video_youtube', 'row')
make_trial('LikertScale', 'audio', 'row')
make_trial('LikertScale', 'image', 'row')
make_trial('LikertScale', 'video', 'column')
make_trial('LikertScale', 'video_youtube', 'column')
make_trial('LikertScale', 'audio', 'column')
make_trial('LikertScale', 'image', 'column')

make_trial('OneDScale', None, 'row')
make_trial('OneDScale', None, 'column')
make_trial('OneDScale', 'video', 'row')
make_trial('OneDScale', 'video_youtube', 'row')
make_trial('OneDScale', 'audio', 'row')
make_trial('OneDScale', 'image', 'row')
make_trial('OneDScale', 'video', 'column')
make_trial('OneDScale', 'video_youtube', 'column')
make_trial('OneDScale', 'audio', 'column')
make_trial('OneDScale', 'image', 'column')

make_trial('OneDScaleT', None, 'row')
make_trial('OneDScaleT', None, 'column')
make_trial('OneDScaleT', 'video', 'row')
make_trial('OneDScaleT', 'video_youtube', 'row')
make_trial('OneDScaleT', 'audio', 'row')
make_trial('OneDScaleT', 'image', 'row')
make_trial('OneDScaleT', 'video', 'column')
make_trial('OneDScaleT', 'video_youtube', 'column')
make_trial('OneDScaleT', 'audio', 'column')
make_trial('OneDScaleT', 'image', 'column')

"""
make_trial('TwoDScaleK', None, 'row')
make_trial('TwoDScaleK', None, 'column')
make_trial('TwoDScaleK', 'video', 'row')
make_trial('TwoDScaleK', 'video_youtube', 'row')
make_trial('TwoDScaleK', 'audio', 'row')
make_trial('TwoDScaleK', 'image', 'row')
make_trial('TwoDScaleK', 'video', 'column')
make_trial('TwoDScaleK', 'video_youtube', 'column')
make_trial('TwoDScaleK', 'audio', 'column')
make_trial('TwoDScaleK', 'image', 'column')

make_trial('TaggingA', None, 'row')
make_trial('TaggingA', None, 'column')
make_trial('TaggingA', 'video', 'row')
make_trial('TaggingA', 'video_youtube', 'row')
make_trial('TaggingA', 'audio', 'row')
make_trial('TaggingA', 'image', 'row')
make_trial('TaggingA', 'video', 'column')
make_trial('TaggingA', 'video_youtube', 'column')
make_trial('TaggingA', 'audio', 'column')
make_trial('TaggingA', 'image', 'column')


make_trial('TaggingB', None, 'row')
make_trial('TaggingB', None, 'column')
make_trial('TaggingB', 'video', 'row')
make_trial('TaggingB', 'video_youtube', 'row')
make_trial('TaggingB', 'audio', 'row')
make_trial('TaggingB', 'image', 'row')
make_trial('TaggingB', 'video', 'column')
make_trial('TaggingB', 'video_youtube', 'column')
make_trial('TaggingB', 'audio', 'column')
make_trial('TaggingB', 'image', 'column')

make_trial('TwoDScale', None, 'row')
make_trial('TwoDScale', None, 'column')
make_trial('TwoDScale', 'video', 'row')
make_trial('TwoDScale', 'video_youtube', 'row')
make_trial('TwoDScale', 'audio', 'row')
make_trial('TwoDScale', 'image', 'row')
make_trial('TwoDScale', 'video', 'column')
make_trial('TwoDScale', 'video_youtube', 'column')
make_trial('TwoDScale', 'audio', 'column')
make_trial('TwoDScale', 'image', 'column')

"""


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
