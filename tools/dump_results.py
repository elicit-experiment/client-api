"""
Example for dumping the results of a study.
"""
import csv
import pprint
import json
import os
import collections
from datetime import datetime
import functools
import pandas as pd
from pyelicit import elicit
from pyelicit import command_line
from dump_time_series import convert_msgpack_to_ndjson, uncompress_datapoint, fetch_time_series
import shutil

##
## DEFAULT ARGUMENTS
##

arg_defaults = {
    "env_file": "<UPDATE THIS FOLDER>/prod.yaml",
    "study_id": 1294,
    "user_id": None, # all users
    "result_root_dir": "/tmp/results"
}


##
## HELPERS
##

ELICIT_API_DATEFMT='%Y-%m-%dT%H:%M:%S.%fZ'
RESULTS_OUTPUT_DATEFMT='%Y-%m-%d %H:%M:%S.%f%Z'
video_layout_fields = frozenset(['x','y', 'width', 'height', 'top', 'bottom', 'left'])

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
           (data_point.get('method') is not None) and \
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

command_line.init_parser({"env": (arg_defaults.get("env") or "prod")}) # Allow the script to be reentrant: start with a fresh parser every time,
command_line.parser.add_argument(
    '--study_id', default=arg_defaults["study_id"], help="The study ID to dump", type=int)
command_line.parser.add_argument(
    '--user_id', default=arg_defaults["user_id"], help="The user ID to dump", type=int)
command_line.parser.add_argument(
    '--user_name', default=None, help="The user name to dump")
command_line.parser.add_argument(
    '--result_root_dir', default=arg_defaults.get("result_root_dir") or "results", help="The root folder to dump to")
args = command_line.parse_command_line_args(arg_defaults)
pp.pprint(args)

el = elicit.Elicit(args)
client = el.client



def result_path_for(filename, user_id=None):
    path = os.path.join(args.result_root_dir, str(args.study_id))
    if user_id:
        path = os.path.join(path, f'user_{user_id}')
    os.path.isdir(path) or os.makedirs(path, exist_ok=True)
    return os.path.join(path, filename)


#
# Double-check that we have the right user
#

user = el.assert_creator()

study_results = el.find_study_results(study_definition_id=args.study_id)
print(study_results)
all_answers = []
raw_questions = dict()
all_video_events = []
all_video_layout_events = []
all_trial_results = []
all_experiment_results = []
all_url_parameters_infos = []
all_demographics = []
CUSTOM_PARAMETERS_NON_URL_FIELDS = []
all_datapoints = []
object_counts=dict(trial_results=0, data_points=0, experiments=0, study_results=0)
object_ids=dict(trial_results=[],data_points=[])


def face_landmark_summary(data_points):
    summary_data_points = []

    for summary in data_points:
        if summary['point_type'] == 'send_points_summary' and summary['kind'] == 'face_landmark':
            summary_data_points.append({
                'datetime': summary['datetime'],
                'queued': summary['value']['queued'],
                'posted': summary['value']['posted'],
                'acknowledged': summary['value']['acknowledged'],
                'posted_bytes': summary['value']['posted_bytes'],
                'posted_compressed_bytes': summary['value']['posted_compressed_bytes'],
                'acknowledged_bytes': summary['value']['acknowledged_bytes'],
                'acknowledged_compressed_bytes': summary['value']['acknowledged_compressed_bytes'],
            })

    return pd.DataFrame(summary_data_points)

def analyze_landmarker_summary(datapoints):
    """
    Analyzes and filters data points for specific 'point_type' values:
    'face_landmark_lifecycle_start' and 'face_landmark_lifecycle_end'.
    """

    start = list(
        filter(lambda dp: dp['point_type'] in ['face_landmark_lifecycle_start'],
               datapoints))
    end = list(
        filter(lambda dp: dp['point_type'] in ['face_landmark_lifecycle_stop'],
               datapoints))

    if len(start) != 1 or len(end) != 1:
        return

    time_range = end[0]['datetime'] - start[0]['datetime']

    print(f"\n\nFACE LANDMARK SUMMARY for user {user_id}\n\n")

    landmarker_configuration = start[0]['value']
    print(f"Landmarker configuration: {landmarker_configuration}\n")

    face_landmark_summary_df = face_landmark_summary(datapoints)
    if not face_landmark_summary_df.empty:
        print('Aggregate values for entire experiment')
        pp.pprint(face_landmark_summary_df.drop('datetime', axis=1).sum())
        print('\nRates/s')
        pp.pprint(face_landmark_summary_df.drop('datetime', axis=1).sum() / time_range)
        print("\n")

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
    video_events = filter(lambda x: is_video_event(x), data_points)
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
        fields = set(video_layout.keys())
        if fields.issuperset(video_layout_fields):
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
        else:
            print("Invalid video_layout event")
            print(video_layout)
    return video_layout_events, video_events_rows

def fetch_datapoints(trial_result, protocol_user_id, user_id):
    response_data_points = []
    page = 1
    while True:
        dps = el.find_data_points(study_result_id=study_result.id,
                                  trial_definition_id=trial_result.trial_definition_id,
                                  protocol_user_id=protocol_user_id,
                                  page_size=50, page=page)
        response_data_points += dps
        if len(dps) < 50:
            break
        page += 1

    if args.debug:
        print("Got %d datapoints for study result %d, trial result %d protocol user %d" % (
            len(response_data_points), study_result.id, trial_result.id, protocol_user_id))

    make_data_point_row = lambda x: ({
        "id": x['id'],
        "phase_definition_id": trial_result.phase_definition_id,
        "trial_definition_id": trial_result.trial_definition_id,
        "component_id": x['component_id'],
        "study_result_id": study_result.id,
        "experiment_id": experiment.id,
        "protocol_user_id": protocol_user_id,
        "user_id": user_id,
        "datetime": x['datetime'],
        "point_type": x['point_type'],
        "kind": x['kind'],
        "entity_type": x['entity_type'],
        "value": x['value'],
    })

    return list(map(make_data_point_row, response_data_points))

def process_trial_result(trial_result):
    global all_video_events, all_video_layout_events, all_answers, all_answers, all_demographics, all_datapoints
    response_data_points = fetch_datapoints(trial_result, trial_result.protocol_user_id, user_id)

    all_datapoints += response_data_points

    object_counts['data_points'] += len(response_data_points)
    object_ids['data_points'] += [r['id'] for r in response_data_points]

    trial_definition_data = json.loads(trial_result['trial_definition']['definition_data'])
    video_layout_events, video_events = extract_video_events(response_data_points)
    all_video_events += video_events
    all_video_layout_events += video_layout_events
    states = list(filter(lambda x: x['point_type'] == 'State', response_data_points))

    if 'TrialType' in trial_definition_data:
        trial_type = trial_definition_data['TrialType']

        if trial_type == 'Questions':
            print('EXTRACTING QUESTIONS')
            all_answers += extract_answers(states)
        if trial_type == 'Demographics':
            print('EXTRACTING DEMOGRAPHICS')
            all_demographics += extract_demographics(states)


print("\n\nSTUDY_RESULTS\n\n")

if args.debug:
    pp.pprint([with_dates(study_result) for study_result in study_results])
else:
    print(f"\tGot {len(study_results)} study results: #{[study_result.id for study_result in study_results]}")

object_counts['study_results'] = len(study_results)

for study_result in study_results:
    experiments = el.find_experiments(study_result_id=study_result.id)

    all_experiment_results += [[x['protocol_user']['user_id'],
                                x.started_at,
                                x.completed_at,
                                x.id] for x in experiments]

    print("\n\nEXPERIMENTS\n\n")

    if args.debug:
        pp.pprint([with_dates(experiment) for experiment in experiments])
    else:
        print(f"\tGot {len(experiments)} experiments for study result {study_result.id}")

    object_counts['experiments'] += len(experiments)

    for experiment in experiments:
        user_id = experiment['protocol_user']['user_id']
        user_name = experiment['protocol_user']['user']['username']

        if args.user_id and args.user_id != user_id:
            print("Skipping user %d (not %d)" % (user_id, args.user_id))
            continue

        custom_parameters_string = experiment['custom_parameters']
        if custom_parameters_string and custom_parameters_string.strip():
            custom_parameters = json.loads(custom_parameters_string)

            url_parameters = {key: value for key, value in custom_parameters.items() if key not in CUSTOM_PARAMETERS_NON_URL_FIELDS}
            url_parameters.update({user_id: user_id})
            all_url_parameters_infos += [url_parameters]

        protocol_user_id = experiment['protocol_user_id']
        stages = el.find_stages(study_result_id=study_result.id, experiment_id=experiment.id)
        print("\n\nSTAGES\n\n")
        if args.debug:
            print(stages)
        else:
            print(f"\tGot {len(stages)} stages for experiment {experiment.id}: #{[stage.id for stage in stages]}")

        trial_results = el.find_trial_results(study_result_id=study_result.id, experiment_id=experiment.id)

        video_layout = None

        all_trial_results += [[user_id,
                               x.started_at,
                               x.completed_at,
                               experiment.id,
                               x.phase_definition_id,
                               x.trial_definition_id] for x in trial_results]

        object_counts['trial_results'] += len(trial_results)
        object_ids['trial_results'] += [r.id for r in trial_results]

        print('PROCESSING TRIAL RESULTS:')
        for trial_result in trial_results:
            process_trial_result(trial_result)

        print("\n\nDATA POINTS\n\n")

        with open(result_path_for(f"{args.study_id}_{user_id}_datapoints.json", user_id), 'w') as outfile:
            user_datapoints = list(filter(lambda row: row['user_id'] == user_id, all_datapoints))
            list(map(lambda row: row.update({"datetime": row["datetime"].v.timestamp()}), user_datapoints))
            list(map(lambda row: row.update({"value": json.loads(row["value"])}) if row['value'].startswith('{"') else row, user_datapoints))
            json.dump(user_datapoints, outfile, indent=2)

            print(f"Wrote {len(user_datapoints)} datapoints for user {user_id} to {result_path_for('datapoints.json', user_id)}")

            analyze_landmarker_summary(user_datapoints)

        for stage_id in (stage.id for stage in stages):
            time_series = el.find_time_series(study_result_id=study_result.id, stage_id=stage_id)

            if len(time_series) < 1:
                print("No time series for stage %d (user %d)\n" % (stage_id, user_id))
                continue

            print(f"Got {len(time_series)} time series for stage {stage_id} (user {user_id}). {['%s (%s)' % (ts.id, ts.series_type) for ts in time_series]}\n")

            for time_series in time_series:
                url = time_series.file_url

                base_filename = result_path_for(f"{args.study_id}_{user_id}_", user_id=user_id)
                query_filename = base_filename + time_series.series_type + "." + time_series.file_type

                final_filename = fetch_time_series(url, time_series.file_type, base_filename=base_filename, filename=query_filename, authorization=el.auth_header(), verify=args.send_opt['verify'])

                # Move the file to the preferred naming convention.
                shutil.move(final_filename, query_filename)
                final_filename = query_filename

                if time_series.series_type == 'face_landmark':
                    print(f"Processing face landmark data for stage {stage_id} (user {user_id}) {time_series.file_type}")
                    if time_series.file_type == 'msgpack':
                        ndjson_filename = final_filename.replace('.msgpack', '.ndjson')

                        convert_msgpack_to_ndjson(final_filename, ndjson_filename)
                    else:
                        ndjson_filename = final_filename

                    with open(ndjson_filename, 'r') as ndjson_file:
                        try:
                            for line in ndjson_file:
                                stripped_line = line.strip()
                                if stripped_line == '':
                                    continue
                                try:
                                    data = json.loads(stripped_line)

                                    uncompressed_filename = final_filename.replace('face_landmark.json', 'face_landmark_uncompressed.json')
                                    with open(uncompressed_filename, 'a') as uncompressed_file:
                                        uncompressed_file.write(json.dumps(uncompress_datapoint(data)) + '\n')
                                except json.JSONDecodeError:
                                    print(f"Error: Line '{stripped_line}' is not valid JSON.")
                        except Exception as e:
                            print(f"Error maybe uncompressing file #{ndjson_filename}: {e}")

with open(result_path_for('video.csv'), 'w', newline='') as csvfile:
    videowriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    videowriter.writerow(
        ['user_id', 'datetime', 'event', 'experiment_id', 'phase_definition_id', 'trial_definition_id', 'component_id'])
    for video_event in all_video_events:
        videowriter.writerow(video_event)

with open(result_path_for('video_layouts.csv'), 'w', newline='') as csvfile:
    videowriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    header = ['x', 'y', 'width', 'height', 'top', 'right', 'bottom', 'left', 'datetime', 'user_id', 'experiment_id',
              'phase_definition_id', 'trial_definition_id', 'component_id']
    videowriter.writerow(header)
    for video_layout_event in all_video_layout_events:
        videowriter.writerow(video_layout_event)

with open(result_path_for('trial_events.csv'), 'w', newline='') as csvfile:
    videowriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    header = ['user_id', 'created_at', 'completed_at',
              'experiment_id', 'phase_definition_id', 'trial_definition_id']
    videowriter.writerow(header)
    for trial_event in all_trial_results:
        videowriter.writerow(trial_event)

with open(result_path_for('experiment_events.csv'), 'w', newline='') as csvfile:
    videowriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    header = ['user_id', 'started_at', 'completed_at',
              'experiment_id']
    videowriter.writerow(header)
    for experiment_event in all_experiment_results:
        videowriter.writerow(experiment_event)

with open(result_path_for('answer.csv'), 'w', newline='') as csvfile:
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

with open(result_path_for('url_parameters.csv'), 'w', newline='') as csvfile:
    url_parameter_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    header = ['user_id'] + CUSTOM_PARAMETERS_NON_URL_FIELDS
    url_parameter_writer.writerow(header)
    for url_parameters_record in all_url_parameters_infos:
        pp.pprint(url_parameters_record)
        url_parameter_writer.writerow(url_parameters_record)


with open(result_path_for('demographics.csv'), 'w', newline='') as csvfile:
    answerwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    header = ['user_id', 'user_name', 'answer_id', 'datetime', 'component_id']
    answerwriter.writerow(header)
    for answer in all_demographics:
        answerwriter.writerow(answer)


if len(all_datapoints) > 0:
    df = pd.DataFrame.from_records(all_datapoints)

    csv = df.to_csv(index=False)

    with open(result_path_for('datapoints.csv'), 'w', newline='') as csvfile:
        csvfile.write(csv)

else:
    pp.pprint('No datapoints')

pp.pprint(object_counts)
for object_type in object_ids.keys():
    pp.pprint('Duplicates for %s'%object_type)
    dupes = [item for item, count in collections.Counter(object_ids[object_type]).items() if count > 1]
    pp.pprint(dupes)

