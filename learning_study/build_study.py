"""
Example for dumping the results of a study.
"""

import pprint
# import pdprint

import sys
import csv
import json
import lorem  # generate boilerplate text to make sure the website renders correctly
import re

from examples_base import *

##
## MAIN
##

pp = pprint.PrettyPrinter(indent=4)

answer_key = dict()

#
# Load trial definitions
#

video = dict(
    Stimuli=[dict(
        Label='Music excerpt',
        Type='video/mp4',
        URI='http://localhost:3000/videos/01a_Why_are_Stars_Shaped.mp4')])

yt_video = dict(
    Stimuli=[dict(
        Label='Music excerpt',
        Type='video/youtube',
        URI='https://youtu.be/soTEnpcn0ig')])

yt_urls = {
    'Stars': 'https://youtu.be/zr9leP_Dcm8',
    'Stars2':'https://youtu.be/soTEnpcn0ig',
    'Lightbulbs': 'https://youtu.be/AK0fLfdTSWA',
    'Immune': 'https://youtu.be/CHTRmZiS1dU',
    'Internet': 'https://youtu.be/7jhFkqgCKDE',
    'Boys and Girls': 'https://youtu.be/7qcii8BScIc'
}

question_rows = []
with open('./learning_study/questions.csv') as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            # print(f'Column names are {", ".join(row)}')
            line_count += 1
        else:
            line_count += 1
            if row['Video_no'] == '1':
                for col in ['Video_no', 'Question_no', 'Trigger_value']:
                    row[col] = int(row[col])
                question_rows.append(row)
    print(f'Processed {line_count} lines.')

videos = list(set([r['Video_no'] for r in question_rows]))

trial_components = []
trial_definition_data = []

study_description="This study proceeds as follows:\n"

for video_no in videos:
    video_rows = [r for r in question_rows if r['Video_no'] == video_no]
    video_name = video_rows[0]['Video_name']
    yt_url = yt_urls[video_name]
    yt_video = dict(
        Stimuli=[dict(
            Label=video_name,
            Type='video/youtube',
            IsPausable=False,
            URI=yt_url)])
    pre_questions = []
    post_questions = []
    for video_row in video_rows:
        question = dict(
            Instruments=[dict(
                Instrument=dict(
                    RadioButtonGroup=dict(
                        AlignForStimuli='0',
                        QuestionsPerRow=1,
                        HeaderLabel=video_row['Question'],
                        # todo_permute these
                        Items=dict(
                            Item=[
                                dict(
                                    Id='0',
                                    Label=video_row['Correct'],
                                    Selected='0',
                                    Correct=True),
                                dict(
                                    Id='1',
                                    Label=video_row['Wrong_1'],
                                    Selected='0',
                                    Correct=False),
                                dict(
                                    Id='2',
                                    Label=video_row['Wrong_2'],
                                    Selected='0',
                                    Correct=False),
                                dict(
                                    Id='3',
                                    Label=video_row['Wrong_3'],
                                    Selected='0',
                                    Correct=False)]),
                        MaxNoOfScalings='1',
                        MinNoOfScalings='1')))])

        if video_row['Position'] == 'Pre':
            pre_questions.append([question])
        else:
            post_questions.append([question])

    print("%s: %d pre questions, %d post questions" % (video_name, len(pre_questions), len(post_questions)))

    trial_components.append([dict()])
    trial_definition_data.append('{ "type": "NewComponent::WebGazerCalibrate" }')
    study_description += "First, you'll calibrate your gaze to the webcam of your computer.\n"

    trial_components += pre_questions[-5:]
    trial_definition_data += ["{}" for _ in range(len(pre_questions))]
    study_description += "Then you'll answer some questions.\n"

    trial_components.append([yt_video])
    trial_definition_data.append("{}")
    study_description += "Then you'll watch a cool video.\n"

    trial_components += post_questions[-5:]
    trial_definition_data += ["{}" for _ in range(len(post_questions))]
    study_description += "Then another set of questions to answer.\n"

    trial_components += [ [
        dict(
            Instruments=[dict(
                Instrument=dict(
                    Header=dict(
                        HeaderLabel='Thank you')))]
        ),
        dict(
            Instruments=[dict(
                Instrument=dict(
                    EndOfExperiment=dict()))]
        )
    ] ]
    trial_definition_data += [ "{}" ]

    study_description += "Then, done!.\n"


# print(trial_components)

# trial_components = [[yt_video],[video],[question]]

# exit()
# quit()

args = parse_command_line_args()

el = elicit.Elicit(args)

#
# Double-check that we have the right user
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
                        footer_label="This is the footer of the study",
                        redirect_close_on_url=el.elicit_api.api_url + "/participant",
                        data="Put some data here, we don't really care about it.",
                        principal_investigator_user_id=user.id)
args = dict(study=dict(study_definition=study_definition))
new_study = el.add_obj("addStudy", args)

#
# Add a new Protocol Definition
#

new_protocol_definition = dict(name='Learning Study Protocol',
                               definition_data="foo",
                               summary="Video Learning",
                               description=study_description,
                               active=True)
args = dict(protocol_definition=dict(protocol_definition=new_protocol_definition),
            study_definition_id=new_study.id)
new_protocol = el.add_obj("addProtocolDefinition", args)

#
# Add users to protocol
#

el.add_users_to_protocol(new_study, new_protocol, study_participants)

# generate N phases for example
phase_definitions = []
for phase_idx in range(1):
    #
    # Add a new Phase Definition
    #

    new_phase_definition = dict(phase_definition=dict(definition_data="foo"))
    args = dict(phase_definition=new_phase_definition,
                study_definition_id=new_study.id,
                protocol_definition_id=new_protocol.id)

    new_phase = el.add_obj("addPhaseDefinition", args)
    phase_definitions = [new_phase]

    trials = []

    # generate two trials for example
    for trial_idx in range(len(trial_components)):
        #
        # Add a new Trial Definition
        #

        new_trial_definition = dict(trial_definition=dict(definition_data=trial_definition_data[trial_idx]))
        args = dict(trial_definition=new_trial_definition,
                    study_definition_id=new_study.id,
                    protocol_definition_id=new_protocol.id,
                    phase_definition_id=new_phase.id)
        new_trial_definition = el.add_obj("addTrialDefinition", args)
        trials.append(new_trial_definition)

        #
        # Add a new Component
        #

        for idx, component_definition in enumerate(trial_components[trial_idx]):
            new_component = dict(name='Newly created component definition from Python',
                                 definition_data=json.dumps(component_definition))
            args = dict(component=dict(component=new_component),
                        study_definition_id=new_study.id,
                        protocol_definition_id=new_protocol.id,
                        phase_definition_id=new_phase.id,
                        trial_definition_id=new_trial_definition.id)
            new_component = el.add_obj("addComponent", args)

            if 'Instruments' in component_definition:
                if 'RadioButtonGroup' in component_definition['Instruments'][0]['Instrument']:
                    radio = component_definition['Instruments'][0]['Instrument']['RadioButtonGroup']
                    answer_key[new_component.id] = dict(question = radio['HeaderLabel'],
                                                        items = radio['Items'])

    #
    # Add a new Trial Orders
    #

    for study_participant in study_participants:
        new_trial_order = dict(trial_order=dict(sequence_data=",".join([str(trial.id) for trial in trials]),
                                                user_id=study_participant.id))
        args = dict(trial_order=new_trial_order,
                    study_definition_id=new_study.id,
                    protocol_definition_id=new_protocol.id,
                    phase_definition_id=new_phase.id)
        new_trial_order = el.add_obj("addTrialOrder", args)

#
# Add a new Phase Order
#

phase_sequence_data = ",".join(
    [str(phase_definition.id) for phase_definition in phase_definitions])
new_phase_order = dict(phase_order=dict(sequence_data=phase_sequence_data,
                                        user_id=user.id))
args = dict(phase_order=new_phase_order,
            study_definition_id=new_study.id,
            protocol_definition_id=new_protocol.id)
new_phase_order = el.add_obj("addPhaseOrder", args)


answer_key_json = json.dumps(answer_key, indent=4)
print(answer_key_json)
with open('questions.json', 'w') as outfile:
    json.dump(answer_key, outfile)