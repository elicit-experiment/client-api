"""
Example for dumping the results of a study.
"""

import csv
import pprint
import json
import os
import cgi
import collections
from datetime import datetime
from functools import partial
import requests
from examples_base import *
import functools
from pyelicit import elicit
import pandas as pd

##
## HELPERS
##

ELICIT_API_DATEFMT='%Y-%m-%dT%H:%M:%S.%fZ'
RESULTS_OUTPUT_DATEFMT='%Y-%m-%d %H:%M:%S.%f%Z'


def parse_datetime(field, state):
    state[field] = datetime.strptime(state[field], ELICIT_API_DATEFMT)
    return state


def with_dates(o):
    o = (o.copy())
    for key in o:
        if key.endswith('_at') and o[key] is not None:
            o[key] = (o[key].v).strftime(RESULTS_OUTPUT_DATEFMT)
    return o


def is_video_event(data_point):
    return (data_point['point_type'] != 'State') and \
           (data_point['method'] != None) and \
           ((data_point['method'].find('audio') != -1) or (data_point['method'].find('video') != -1))


##
## MAIN
##

questions_filename = 'questionsx.json'
questions = dict()
if os.path.isfile(questions_filename):
    with open(questions_filename, 'r') as questionsfd:
        questions = json.load(questionsfd)

pp = pprint.PrettyPrinter(indent=4)

parser.add_argument(
    '--study_id', default=1, help="The study ID to dump", type=int)
parser.add_argument(
    '--user_id', default=None, help="The user ID to dump", type=int)
parser.add_argument(
    '--user_name', default=None, help="The user name to dump")
args = parse_command_line_args()

el = elicit.Elicit(args)
client = el.client

#
# Double-check that we have the right user
#

user = el.assert_admin()

study_results = el.find_study_results(study_definition_id=args.study_id)

all_answers = []
raw_questions = dict()
all_video_events = []
all_video_layout_events = []
all_trial_results = []
all_experiment_results = []
all_mturk_infos = []
all_demographics = []
MTURK_FIELDS = ['assignmentId', 'hitId', 'workerId']
all_datapoints = []
object_counts=dict(trial_results=0, data_points=0, experiments=0, study_results=0)
object_ids=dict(trial_results=[],data_points=[])

def fetch_answer(state):
    out = state.copy()
    value = out['value'] = json.loads(state['value'])
    if 'Id' in value:
        out['answer_id'] = value['Id']
    elif 'Text' in out['value']:
        out['answer_id'] = value['Text']
    else:
        out['answer_id'] = None
    return out


def extract_answers(states):
    global raw_questions

    states = map(fetch_answer, states)
    answers = list(
        map(lambda x: (user_id, user_name, x['answer_id'], x['datetime'], x['component_id']), states))
    for answer in answers:
        if not (answer[4] in raw_questions):
            component = el.get_component(component_id=answer[4])
            component_def = json.loads(component['definition_data'])
            component['parsed_definition_data'] = component_def
            is_radio_button = False
            if 'Instruments' in component_def:
                instrument = component_def['Instruments'][0]['Instrument']
                if 'RadioButtonGroup' in instrument:
                    raw_questions[answer[4]] = component
                    is_radio_button = True
            # if not is_radio_button:
            #    pp.pprint(answer)
    return answers


def extract_demographics(states):
    answer_states = map(fetch_answer, states)

    return list(map(lambda x: (user_id, user_name, x['answer_id'], x['datetime'], x['component_id']), answer_states))


def extract_video_events(data_points):
    video_events_rows = []
    video_layout_events = []
    video_events = filter(lambda x: is_video_event, data_points)
    video_events = list(video_events)
    make_video_event_row = lambda x: (user_id,
                                      x['datetime'],
                                      x['point_type'],
                                      experiment.id,
                                      trial_result.phase_definition_id,
                                      trial_result.trial_definition_id,
                                      x['component_id'])
    video_events_rows += map(make_video_event_row, video_events)
    layouts = list(filter(lambda x: x['point_type'] == 'Layout', data_points))
    if len(layouts) > 0:
        layout = layouts[0]
        video_layout = json.loads(layout['value'])
        video_layout_event = [video_layout['x'],
                              video_layout['y'],
                              video_layout['width'],
                              video_layout['height'],
                              video_layout['top'],
                              video_layout['right'],
                              video_layout['bottom'],
                              video_layout['left'],
                              layout['datetime'],
                              user_id,
                              experiment.id,
                              trial_result.phase_definition_id,
                              trial_result.trial_definition_id,
                              layout['component_id']]
        video_layout_events += [video_layout_event]
    return video_layout_events, video_events_rows


def process_trial_result(trial_result):
    global all_video_events, all_video_layout_events, all_answers, all_answers, all_demographics, all_datapoints
    data_points = el.find_data_points(study_result_id=study_result.id,
                                      trial_definition_id=trial_result.trial_definition_id,
                                      protocol_user_id=protocol_user_id,
                                      page_size=50)
    print("Got %d datapoints for study result %d, trial result %d protocol user %d" % (
        len(data_points), study_result.id, trial_result.id, protocol_user_id))

    #pp.pprint(list(data_points))

    make_data_point_row = lambda x: (user_id,
                                      x['datetime'],
                                      x['point_type'],
                                      experiment.id,
                                      trial_result.phase_definition_id,
                                      trial_result.trial_definition_id,
                                      x['component_id'])

    print("got %d datapoints"%(len(data_points)))
    all_datapoints += data_points

    object_counts['data_points'] += len(data_points)
    object_ids['data_points'] += [r.id for r in data_points]

    trial_definition_data = json.loads(trial_result['trial_definition']['definition_data'])
    #pp.pprint(trial_definition_data)
    video_layout_events, video_events = extract_video_events(data_points)
    all_video_events += video_events
    all_video_layout_events += video_layout_events
    states = list(filter(lambda x: x['point_type'] == 'State', data_points))

    if 'TrialType' in trial_definition_data:
        trial_type = trial_definition_data['TrialType']
        print(trial_type)

        if trial_type == 'Questions':
            print('EXTRACTING QUESTIONS')
            all_answers += extract_answers(states)
        if trial_type == 'Demographics':
            print('EXTRACTING DEMOGRAPHICS')
            all_demographics += extract_demographics(states)


print("\n\nSTUDY_RESULTS\n\n")

pp.pprint([with_dates(study_result) for study_result in study_results])

object_counts['study_results'] = len(study_results)

for study_result in study_results:
    experiments = el.find_experiments(study_result_id=study_result.id)

    all_experiment_results += [[x['protocol_user']['user_id'],
                                x.started_at,
                                x.completed_at,
                                x.id] for x in experiments]

    print("\n\nEXPERIMENTS\n\n")

    pp.pprint([with_dates(experiment) for experiment in experiments])

    object_counts['experiments'] += len(experiments)

    for experiment in experiments:
        user_id = experiment['protocol_user']['user_id']
        user_name = experiment['protocol_user']['user']['username']

        if args.user_id and args.user_id != user_id:
            continue

        custom_parameters = experiment['custom_parameters']
        if custom_parameters and custom_parameters.strip():
            mturk_info = json.loads(custom_parameters)
            missing = [i for i in MTURK_FIELDS if not i in mturk_info.keys()]
            if len(missing) == 0:
                row = [user_id] + [mturk_info[field] for field in MTURK_FIELDS]
                all_mturk_infos += [row]

        protocol_user_id = experiment['protocol_user_id']
        stages = el.find_stages(study_result_id=study_result.id, experiment_id=experiment.id)

        trial_results = el.find_trial_results(study_result_id=study_result.id, experiment_id=experiment.id)

        video_layout = None

        # pp.pprint(trial_results)

        all_trial_results += [[user_id,
                               x.started_at,
                               x.completed_at,
                               experiment.id,
                               x.phase_definition_id,
                               x.trial_definition_id] for x in trial_results]

        object_counts['trial_results'] += len(trial_results)
        object_ids['trial_results'] += [r.id for r in trial_results]

        for trial_result in trial_results:
            process_trial_result(trial_result)

        for stage_id in (stage.id for stage in stages):
            time_series = el.find_time_series(study_result_id=study_result.id, stage_id=stage_id)

            if len(time_series) < 1:
                print("No time series for stage %d (user %d)\n" % (stage_id, user_id))
                continue

            time_series = time_series[0]

            # url = elicit.api_url + "/api/v1/study_results/time_series/%d/content"%(time_series["id"])
            url = el.api_url() + json.loads(time_series.file.replace("'", '"'))['url']

            headers = {
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/tab-separated-values',
                'Authorization': el.auth_header(),
            }
            with requests.get(url, headers=headers, stream=True, verify=args.send_opt['verify']) as r:
                content_disposition = r.headers.get('Content-Disposition')
                query_filename = ("user_%d_" % user_id) + os.path.basename(url)
                if content_disposition:
                    value, params = cgi.parse_header(content_disposition)
                    query_filename = ("user_%d_" % user_id) + params['filename']
                with open(query_filename, 'wb') as fd:
                    for chunk in r.iter_content(chunk_size=128):
                        fd.write(chunk)

with open('video.csv', 'w', newline='') as csvfile:
    videowriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    videowriter.writerow(
        ['user_id', 'datetime', 'event', 'experiment_id', 'phase_definition_id', 'trial_definition_id', 'component_id'])
    for video_event in all_video_events:
        videowriter.writerow(video_event)

with open('video_layouts.csv', 'w', newline='') as csvfile:
    videowriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    header = ['x', 'y', 'width', 'height', 'top', 'right', 'bottom', 'left', 'datetime', 'user_id', 'experiment_id',
              'phase_definition_id', 'trial_definition_id', 'component_id']
    videowriter.writerow(header)
    for video_layout_event in all_video_layout_events:
        videowriter.writerow(video_layout_event)

with open('trial_events.csv', 'w', newline='') as csvfile:
    videowriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    header = ['user_id', 'created_at', 'completed_at',
              'experiment_id', 'phase_definition_id', 'trial_definition_id']
    videowriter.writerow(header)
    for trial_event in all_trial_results:
        videowriter.writerow(trial_event)

with open('experiment_events.csv', 'w', newline='') as csvfile:
    videowriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    header = ['user_id', 'started_at', 'completed_at',
              'experiment_id']
    videowriter.writerow(header)
    for experiment_event in all_experiment_results:
        videowriter.writerow(experiment_event)

with open('answer.csv', 'w', newline='') as csvfile:
    answerwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    header = ['user_id', 'user_name', 'answer_id', 'datetime', 'component_id', 'question', 'correct']
    for answer_idx in range(0, 4):
        header += [("answer%d" % answer_idx)]
        header += [("answer%d_id" % answer_idx)]
    answerwriter.writerow(header)
    for answer in all_answers:
        id = answer[2]
        if id is None:
            continue
        question = 'unknown'
        correct = False
        component_id = answer[4]
        component_id_s = str(component_id)
        if component_id_s in questions:
            items = questions[component_id_s]['items']['Item']
            question = questions[component_id_s]['question']
            answered_option = next((x for x in items if x['Id'] == str(id)))
            correct = answered_option['Correct']
            answers = functools.reduce(lambda a, b: a + b, [[x['Label'], x['Id']] for x in items])
        elif component_id in raw_questions:
            component = raw_questions[component_id]
            component_def = component['parsed_definition_data']
            radio_button_def = component_def['Instruments'][0]['Instrument']['RadioButtonGroup']
            items = radio_button_def['Items']['Item']
            question = radio_button_def['HeaderLabel']
            answered_option = next((x for x in items if x['Id'] == str(id)))
            correct = answered_option['Correct']
            answers = functools.reduce(lambda a, b: a + b, [[x['Label'], x['Id']] for x in items])

        answerwriter.writerow(answer + (question, correct) + tuple(answers))

with open('mturk.csv', 'w', newline='') as csvfile:
    videowriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    header = ['user_id'] + MTURK_FIELDS
    videowriter.writerow(header)
    for mturk_record in all_mturk_infos:
        pp.pprint(mturk_record)
        videowriter.writerow(mturk_record)


with open('demographics.csv', 'w', newline='') as csvfile:
    answerwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    header = ['user_id', 'user_name', 'answer_id', 'datetime', 'component_id']
    answerwriter.writerow(header)
    for answer in all_demographics:
        answerwriter.writerow(answer)


df = pd.DataFrame.from_records(all_datapoints)

csv = df[['datetime', 'phase_definition_id', 'trial_definition_id', 'component_id', 'entity_type', 'kind', 'method', 'point_type', 'component_name', 'value']].to_csv(index=False)
#print(df[['datetime', 'phase_definition_id', 'trial_definition_id', 'component_id', 'entity_type', 'kind', 'method', 'point_type', 'component_name', 'value']])

with open('datapoints.csv', 'w', newline='') as csvfile:
    csvfile.write(csv)

pp.pprint(object_counts)
#pp.pprint(object_ids)
for object_type in object_ids.keys():
    pp.pprint('Duplicates for %s'%object_type)
    dupes = [item for item, count in collections.Counter(object_ids[object_type]).items() if count > 1]
    pp.pprint(dupes)

