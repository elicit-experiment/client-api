"""
Example for dumping the results of a study.
"""

import pprint
import csv
import json
import pdb
from random import shuffle

from examples_base import *
from pyelicit import elicit

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
    'Stars2': 'https://youtu.be/soTEnpcn0ig',
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
trial_names = []

study_description = "This study proceeds as follows:\n"

demographics_questions = [
    dict(
        Instruments=[dict(
            Instrument=dict(Header=dict(HeaderLabel='Questions about you')))]),
    dict(
        Instruments=[dict(
            Instrument=dict(
                Freetext=dict(
                    BoxHeight=None,
                    BoxWidth=None,
                    Label="Mechanical Turk ID",
                    LabelPosition='left',
                    Resizable=None,
                    Validation='.+')))]),
    dict(
        Instruments=[dict(
            Instrument=dict(
                RadioButtonGroup=dict(
                    AlignForStimuli='0',
                    QuestionsPerRow=1,
                    HeaderLabel='Sex',
                    Items=dict(
                        Item=[
                            dict(
                                Id='M',
                                Label='Male',
                                Selected='0',
                                Correct=False),
                            dict(
                                Id='F',
                                Label='Female',
                                Selected='0',
                                Correct=False)]),
                    MaxNoOfScalings='1',
                    MinNoOfScalings='1')))]),
    dict(
        Instruments=[dict(
            Instrument=dict(
                RadioButtonGroup=dict(
                    AlignForStimuli='0',
                    QuestionsPerRow=1,
                    HeaderLabel="What's the highest level of education you've attained?",
                    Items=dict(
                        Item=[
                            dict(
                                Id='Primary',
                                Label='Below High School',
                                Selected='0',
                                Correct=False),
                            dict(
                                Id='HS',
                                Label='High school',
                                Selected='0',
                                Correct=False),
                            dict(
                                Id='B',
                                Label="Bachelor's Degree",
                                Selected='0',
                                Correct=False),
                            dict(
                                Id='M',
                                Label="Master's Degree",
                                Selected='0',
                                Correct=False),
                            dict(
                                Id='P',
                                Label="PhD",
                                Selected='0',
                                Correct=False)
                        ]),
                    MaxNoOfScalings='1',
                    MinNoOfScalings='1')))]),
    dict(
        Instruments=[dict(
            Instrument=dict(
                RadioButtonGroup=dict(
                    AlignForStimuli='0',
                    QuestionsPerRow=1,
                    HeaderLabel="What device are you using for this survey?",
                    Items=dict(
                        Item=[
                            dict(
                                Id='Phone',
                                Label='Smartphone',
                                Selected='0',
                                Correct=False),
                            dict(
                                Id='Tablet',
                                Label='Tablet',
                                Selected='0',
                                Correct=False),
                            dict(
                                Id='Laptop',
                                Label="Laptop Computer",
                                Selected='0',
                                Correct=False),
                            dict(
                                Id='Desktop',
                                Label="Desktop Computer",
                                Selected='0',
                                Correct=False),
                        ]),
                    MaxNoOfScalings='1',
                    MinNoOfScalings='1')))]),
    dict(
        Instruments=[dict(
            Instrument=dict(
                RadioButtonGroup=dict(
                    AlignForStimuli='0',
                    QuestionsPerRow=1,
                    HeaderLabel="What size is your display?",
                    Items=dict(
                        Item=[
                            dict(
                                Id='S',
                                Label='< 6 inches (15cm)',
                                Selected='0',
                                Correct=False),
                            dict(
                                Id='M',
                                Label='6 to 12.9 inches (15cm - 33cm)',
                                Selected='0',
                                Correct=False),
                            dict(
                                Id='L',
                                Label="13 to 15 inches (33cm - 38cm)",
                                Selected='0',
                                Correct=False),
                            dict(
                                Id='XL',
                                Label="larger than 15 inches (38cm)",
                                Selected='0',
                                Correct=False),
                        ]),
                    MaxNoOfScalings='1',
                    MinNoOfScalings='1')))]),
]

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

    trial_components += [demographics_questions]
    trial_names += ['Demographics']
    trial_definition_data += [dict(TrialType='Demographics')]
    study_description += "First you'll answer some questions about yourself.<br/>"

    trial_components.append([None])
    trial_names += ['Webcam Calibration']
    trial_definition_data.append(dict(TrialType='Calibration', type="NewComponent::WebGazerCalibrate", MaxNoOfAttempts='2', MinCalibrationAccuracyPct='80'))
    study_description += "Then, you'll calibrate your gaze to the webcam of your computer.<br/>"

    trial_components += pre_questions[-5:]
    trial_names += [("Pre-question %d"%(i+1)) for i in range(5)]
    trial_definition_data += [dict(TrialType='Questions') for i in range(len(pre_questions))]
    study_description += "Then you'll answer some questions.<br/>"

    trial_components.append([yt_video])
    trial_names += ['Video']
    trial_definition_data.append(dict(TrialType='Video'))
    study_description += "Then you'll watch a cool video.<br/>"

    trial_components += post_questions[-5:]
    trial_names += [("Post-question %d"%(i+1)) for i in range(5)]
    trial_definition_data += [dict(TrialType='Questions') for _ in range(len(post_questions))]
    study_description += "Then another set of questions to answer.<br/>"

    trial_names += ['End of Experiment']
    trial_components += [[
        dict(
            Instruments=[dict(
                Instrument=dict(
                    Header=dict(
                        HeaderLabel='{{center|Thank {{b|you}}}}')))]
        ),
        dict(
            Instruments=[dict(
                Instrument=dict(
                    EndOfExperiment=dict()))]
        )
    ]]
    trial_definition_data += [dict()]

    study_description += "Then, done!.\n"

# print(trial_components)

# trial_components = [[yt_video],[video],[question]]

# exit()
# quit()

args = parse_command_line_args()

el = elicit.Elicit(args)

#
# Double-check that we have the right user: we need to be admin to create a study
#

user = el.assert_admin()

#
# Get list of users who will use the study
#
NUM_AUTO_CREATED_USERS=10
NUM_ANONYMOUS_USERS=5
NUM_REGISTERED_USERS=5
study_participants = el.ensure_users(NUM_REGISTERED_USERS, NUM_ANONYMOUS_USERS)

#
# Add a new Study Definition
#
study_definition = dict(title='Learning Study - WebGazer',
                        description="""Study of learning, using eye gaze tracking from WebGazer 
                        This version calibrates on the video page""",
                        version=1,
                        lock_question=1,
                        enable_previous=1,
                        allow_anonymous_users=(NUM_AUTO_CREATED_USERS>0 or NUM_ANONYMOUS_USERS>0),  # allow taking the study without login
                        show_in_study_list=True,  # show in the (public) study list for anonymous protocols
                        max_auto_created_users=NUM_AUTO_CREATED_USERS, # up to ten workerId created users
                        max_concurrent_users=1, # NYI
                        footer_label="This is the footer of the study",
                        redirect_close_on_url=el.elicit_api.api_url + "/participant",
                        data="Put some data here, we don't really care about it.",
                        principal_investigator_user_id=user.id)
new_study = el.add_study(study=dict(study_definition=study_definition))

#
# Add a new Protocol Definition
#
new_protocol_definition_data = dict( instructionsHtml = "<h3>instructions</h3>" )
new_protocol_definition = dict(name='Learning Study Protocol',
                               definition_data=new_protocol_definition_data,
                               summary="Video Learning",
                               description=study_description,
                               active=True)
new_protocol = el.add_protocol_definition(protocol_definition=dict(protocol_definition=new_protocol_definition),
                                          study_definition_id=new_study.id)

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

    new_phase_definition = dict(phase_definition=dict(definition_data=dict(),
                                                      trial_ordering='RandomWithoutReplacement'))

    new_phase = el.add_phase_definition(phase_definition=new_phase_definition,
                                        study_definition_id=new_study.id,
                                        protocol_definition_id=new_protocol.id)
    phase_definitions = [new_phase]

    trials = []

    for trial_idx in range(len(trial_components)):
        #
        # Add a new Trial Definition
        #

        def_data = trial_definition_data[trial_idx]
        new_trial_definition_config = dict(trial_definition=dict(name=trial_names[trial_idx], definition_data=def_data))
        pp.pprint(new_trial_definition_config)
        new_trial_definition = el.add_trial_definition(trial_definition=new_trial_definition_config,
                                                       study_definition_id=new_study.id,
                                                       protocol_definition_id=new_protocol.id,
                                                       phase_definition_id=new_phase.id)
        new_trial_definition.definition_data = def_data
        trials.append(new_trial_definition)

        #
        # Add a new Component
        #

        for idx, component_definition in enumerate(trial_components[trial_idx]):
            if not component_definition:
                continue
            new_component_config = dict(name='Newly created component definition from Python',
                                        definition_data=component_definition)
            new_component = el.add_component(component=dict(component=new_component_config),
                                             study_definition_id=new_study.id,
                                             protocol_definition_id=new_protocol.id,
                                             phase_definition_id=new_phase.id,
                                             trial_definition_id=new_trial_definition.id)

            if 'TrialType' in trial_definition_data[trial_idx] and trial_definition_data[trial_idx]['TrialType'] == 'Questions':
                if 'Instruments' in component_definition:
                    if 'RadioButtonGroup' in component_definition['Instruments'][0]['Instrument']:
                        radio = component_definition['Instruments'][0]['Instrument']['RadioButtonGroup']
                        answer_key[new_component.id] = dict(question=radio['HeaderLabel'],
                                                            items=radio['Items'])

    #
    # Add a new Trial Orders
    #

    for study_participant in study_participants:
        # generate randomized sequence
        questions = []
        seq = []
        for trial in trials:
            type = trial.definition_data['TrialType']
            if (type == 'Questions'):
                questions += [trial]
            else:
                if len(questions) > 0:
                    shuffle(questions)
                    seq += [x.id for x in questions]
                seq += [trial.id]

        pp.pprint(seq)

        # fixed sequence
        #sequence = ",".join([str(trial.id) for trial in trials])

        # randomized sequence
        sequence = ",".join(str(seq))

        # user_id = nil, so the TrialOrder can be chosen by anonymous users
        new_trial_order_config = dict(trial_order=dict(sequence_data=sequence))

        # user_id is fixed
        # new_trial_order_config = dict(trial_order=dict(sequence_data=sequence,
        #                                               user_id=study_participant.id))

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

answer_key_json = json.dumps(answer_key, indent=4)
print(answer_key_json)
with open('questions.json', 'w') as outfile:
    json.dump(answer_key, outfile)
