"""
Example for dumping the results of a study.
"""
import pprint
import json
import os
import collections
import pandas as pd
import pyswagger.primitives
import yaml
from pyelicit import elicit
from pyelicit import command_line
from dump_time_series import convert_msgpack_to_ndjson, uncompress_datapoint, fetch_time_series
import shutil
from study_definition_helpers import dump_study_definition
from dump_utilities import with_dates
from result_path_generator import ResultPathGenerator
from result_collector import ResultCollector

##
## DEFAULT ARGUMENTS
##

arg_defaults = {
    "study_id": 1309,
    "env": "prod",
    "user_id": None, # all users
    "result_root_dir": "/tmp/results"
}


##
## HELPERS
##

def debug_log(message):
    if args.debug:
        print(message)


def ensure_study_info(el, study_id, result_path_generator: ResultPathGenerator = None):
    filename = result_path_generator.result_path_for(f"study_{study_id}.yaml")
    if os.path.exists(filename):
        print(f"Using existing study info file {filename}")
        return yaml.safe_load(open(filename, 'r'))
    else:
        print(f"Generating study info file {filename}")
        study_info = dump_study_definition(elicit, el, study_id)
        with open(filename, 'w') as file:
            yaml.dump(json.loads(json.dumps(study_info)), file)
        return study_info


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

def analyze_landmarker_summary(datapoints, user_id):
    """
    Finds the landmarker summary datapoints and extracts them for analysis in order to provide a quick overview of the experiment.
    Analyzes and filters data points for specific 'point_type' values:
    'face_landmark_lifecycle_start' and 'face_landmark_lifecycle_end'.
    """

    start = list(
        filter(lambda dp: dp['point_type'] in ['face_landmark_lifecycle_start'],
               datapoints))
    end = list(
        filter(lambda dp: dp['point_type'] in ['face_landmark_lifecycle_stop'],
               datapoints))

    if len(start) != 1:
       return None, None, None

    print(f"\n\nFACE LANDMARK SUMMARY for user {user_id}\n\n")

    landmarker_configuration = start[0]['value']
    print(f"Landmarker configuration: {landmarker_configuration}\n")

    if len(end) != 1:
        return landmarker_configuration, None, None

    time_range = end[0]['datetime'] - start[0]['datetime']

    face_landmark_summary_df = face_landmark_summary(datapoints)
    if not face_landmark_summary_df.empty:
        print('Aggregate values for entire experiment')
        pp.pprint(face_landmark_summary_df.drop('datetime', axis=1).sum())
        print('\nRates count/s')
        pp.pprint(face_landmark_summary_df.drop('datetime', axis=1).sum() / time_range)
        print("\n")

    return landmarker_configuration, time_range, face_landmark_summary_df


def mouse_tracking_summary(data_points):
    summary_data_points = []

    for summary in data_points:
        if summary['point_type'] == 'send_points_summary' and summary['kind'] == 'mouse':
            summary_data_points.append({
                'datetime': summary['datetime'],
                'count': summary['value']['numPoints'],
            })

    return pd.DataFrame(summary_data_points)

def analyze_mouse_tracking_summary(datapoints, user_id):
    """
    Finds the mouse summary datapoints and extracts them for analysis in order to provide a quick overview of the experiment.
    """

    start = list(
        filter(lambda dp: dp['point_type'] in ['mouse_tracking_lifecycle_start'],
               datapoints))
    end = list(
        filter(lambda dp: dp['point_type'] in ['mouse_tracking_lifecycle_stop'],
               datapoints))

    if len(start) != 1:
       return None, None, None

    mouse_tracking_configuration = start[0]['value']
    print(f"\n\nMOUSE TRACKING SUMMARY for user {user_id}\n\n")

    print(f"Landmarker configuration: {mouse_tracking_configuration}\n")

    if len(end) != 1:
        return mouse_tracking_configuration, None, None

    duration = end[0]['datetime'] - start[0]['datetime']

    mouse_tracking_summary_df = mouse_tracking_summary(datapoints)
    if not mouse_tracking_summary_df.empty:
        print('Aggregate values for entire experiment')
        pp.pprint(mouse_tracking_summary_df.drop('datetime', axis=1).sum())
        print('\nRates count/s')
        pp.pprint(mouse_tracking_summary_df.drop('datetime', axis=1).sum() / duration)
        print("\n")

    return mouse_tracking_configuration, duration, mouse_tracking_summary_df

def fetch_datapoints(study_result: pyswagger.primitives.Model, experiment: dict, trial_result: dict, protocol_user_id: int, user_id: int) -> list[dict]:
    """
           Fetch datapoints for an experiment and trial result.

           Args:
               experiment (dict): Experiment data.
               trial_result (dict): Trial result data.
               protocol_user_id (int): ID of the protocol user.
               user_id (int): ID of the user.

           Returns:
               list[dict]: List of datapoints.
           """
    ...

    response_data_points = []
    page = 1
    page_size = 1000
    while True:
        dps = el.find_data_points(study_result_id=study_result.id,
                                  trial_definition_id=trial_result.trial_definition_id,
                                  protocol_user_id=protocol_user_id,
                                  page_size=page_size, page=page)
        response_data_points += dps
        if len(dps) < page_size:
            break
        page += 1

    debug_log(f"Got {len(response_data_points)} datapoints for study result {study_result.id}, trial result {trial_result.id} protocol user {protocol_user_id}")

    make_data_point_row = lambda data_point: ({
        "id": data_point.id,
        "phase_definition_id": trial_result.phase_definition_id,
        "trial_definition_id": trial_result.trial_definition_id,
        "component_id": data_point['component_id'],
        "study_result_id": study_result.id,
        "experiment_id": experiment.id,
        "protocol_user_id": protocol_user_id,
        "user_id": user_id,
        "datetime": data_point.datetime,
        "point_type": data_point.point_type,
        "kind": data_point.kind,
        "method": data_point.method,
        "entity_type": data_point.entity_type,
        "value": data_point.value,
    })

    # ids = [x.id for x in response_data_points]
    # duplicate_ids = [item for item, count in collections.Counter(ids).items() if count > 1]
    # pp.pprint(duplicate_ids)

    return list(map(make_data_point_row, response_data_points))

def synthesize_answers(datapoints: list[dict], trial_definitions: pyswagger.primitives.Model):
    """
    Synthesize answers from datapoints & trial/component definitions.

    This transforms the data points into a more convenient format for analysis by aligning the final state of each component with the render of that component and enriches
    the result with the labels to make the result easier for humans to understand.
    """

    answer_datapoints = list(
        filter(lambda row: row['point_type'] == 'State' or row['point_type'] == 'Render', datapoints))
    grouped_answer_datapoints = collections.defaultdict(list)
    for data_point in answer_datapoints:
        grouped_answer_datapoints[data_point['component_id']].append(data_point)
    answers = []
    for answer_component_id, answer_datapoints in grouped_answer_datapoints.items():
        render_answer_datapoints = list(filter(lambda row: row['point_type'] == 'Render', answer_datapoints))
        state_answer_datapoints = list(filter(lambda row: row['point_type'] == 'State', answer_datapoints))
        if len(render_answer_datapoints) == 0 or len(state_answer_datapoints) == 0:
            print(
                "WARN: Found answer datapoints for component %d without both Render and State datapoints" % answer_component_id)
            pp.pprint(render_answer_datapoints)
            pp.pprint(state_answer_datapoints)
        else:
            render_answer_datapoint = render_answer_datapoints[0]
            state_answer_datapoint = state_answer_datapoints[0]

            if isinstance(state_answer_datapoint['value'], dict):
                state_values = state_answer_datapoint['value']
            else:
                try:
                    state_values = json.loads(state_answer_datapoint['value'])
                except (json.JSONDecodeError, TypeError) as e:
                    print(f"Error decoding JSON from state_answer_datapoint['value']: {e} {state_answer_datapoint}")
                    state_values = {}
            if 'Id' not in state_values:
                continue

            answer_id = int(state_values['Id'])
            render_values = json.loads(render_answer_datapoint['value'])

            question = ''
            for component in trial_definitions[render_answer_datapoint['trial_definition_id']]['components']:
                if component['id'] == answer_component_id:
                    def_data = json.loads(component['definition_data'])['Instruments'][0]['Instrument']
                    question = next(iter(def_data.values()))['HeaderLabel']

            if answer_id >= len(render_values):
                print(
                    f"WARN: Found answer datapoint for component {answer_component_id} with Id {answer_id} but only {len(render_values)} Render datapoints")
                answer = 'none'
            else:
                answer = render_values[answer_id]['Label']

            state_answer_datapoint.update({
                "render_id": [render_value['Id'] for render_value in render_values],
                "render_label": [render_value['Label'] for render_value in render_values],
                "question": question,
                "answer_id": answer_id,
                "answer": answer,
            })

            answers.append(state_answer_datapoint)

    return answers

def fetch_all_time_series(study_result, experiment):
    user_id = experiment['protocol_user']['user_id']

    stages = el.find_stages(study_result_id=study_result.id, experiment_id=experiment.id)
    print("\n\nSTAGES\n\n")
    if args.debug:
        print(stages)
    else:
        print(f"\tGot {len(stages)} stages for experiment {experiment.id}: #{[stage.id for stage in stages]}")

    experiment_time_series = {}

    for stage_id in (stage.id for stage in stages):
        time_series = el.find_time_series(study_result_id=study_result.id, stage_id=stage_id)

        if len(time_series) < 1:
            print(f"       No time series for stage {stage_id} (user {user_id})\n")
            continue

        print(
            f"        Got {len(time_series)} time series for stage {stage_id} (user {user_id}). {['%s (%s)' % (ts.id, ts.series_type) for ts in time_series]}\n")

        for time_series in time_series:
            url = time_series.file_url

            base_filename = result_path_generator.result_path_for(f"{args.study_id}_{user_id}_", user_id=user_id)
            query_filename = base_filename + time_series.series_type + "." + time_series.file_type

            final_filename = fetch_time_series(url, time_series.file_type, base_filename=base_filename,
                                               filename=query_filename, authorization=el.auth_header(),
                                               verify=True)

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

                                uncompressed_filename = final_filename.replace('face_landmark.json',
                                                                               'face_landmark_uncompressed.json')
                                with open(uncompressed_filename, 'a') as uncompressed_file:
                                    uncompressed_file.write(json.dumps(uncompress_datapoint(data)) + '\n')
                                final_filename = uncompressed_filename
                            except json.JSONDecodeError:
                                print(f"Error: Line '{stripped_line}' is not valid JSON.")
                    except Exception as e:
                        print(f"Error maybe uncompressed file #{ndjson_filename}: {e}")

            experiment_time_series[time_series.series_type] = {
                "filename": final_filename,
            }

    return experiment_time_series

def analyze_and_dump_user_data_points(user_datapoints, user_id):
    """Dump json data points for a single user."""
    with open(result_path_generator.result_path_for(f"{args.study_id}_{user_id}_datapoints.json", user_id), 'w') as outfile:
        list(map(lambda row: row.update({"datetime": row["datetime"].v.timestamp()}), user_datapoints))
        list(map(lambda row: row.update({"value": json.loads(row["value"])}) if row['value'].startswith(
            '{"') else row, user_datapoints))
        json.dump(user_datapoints, outfile, indent=2)

        print(
            f"Wrote {len(user_datapoints)} datapoints for user {user_id} to {result_path_generator.result_path_for('datapoints.json', user_id)}")

        landmarker_configuration, duration, summary_df = analyze_landmarker_summary(user_datapoints, user_id)
        collector.add_landmarker_configuration(user_id, landmarker_configuration, duration, summary_df)

        mouse_tracking_configuration, duration, summary_df = analyze_mouse_tracking_summary(user_datapoints, user_id)
        collector.add_mouse_tracking_summary(user_id, mouse_tracking_configuration, duration, summary_df)


def process(collector: ResultCollector, results_path_generator: ResultPathGenerator):
    study_results = el.find_study_results(study_definition_id=args.study_id)
    study_info = ensure_study_info(el, args.study_id, results_path_generator)
    phase_definition = study_info['protocol_definitions'][0]['phase_definitions'][0]
    trial_definitions = {}
    for trial_def in phase_definition["trial_definitions"]:
        if 'id' in trial_def:
            trial_definitions[trial_def['id']] = trial_def

    print("\n\nSTUDY_RESULTS\n\n")
    if args.debug:
        pp.pprint([with_dates(study_result) for study_result in study_results])
    else:
        print(f"\tGot {len(study_results)} study results: #{[study_result.id for study_result in study_results]}")

    for study_result in study_results:
        experiments = el.find_experiments(study_result_id=study_result.id)

        print("\n\nEXPERIMENTS\n\n")

        if args.debug:
            pp.pprint([with_dates(experiment) for experiment in experiments])
        else:
            print(f"\tGot {len(experiments)} experiments for study result {study_result.id}")

        for experiment in experiments:
            experiment_time_series = fetch_all_time_series(study_result, experiment)
            collector.add_experiment_event(experiment, experiment_time_series)

            user_id = experiment['protocol_user']['user_id']

            if args.user_id and args.user_id != user_id:
                print("Skipping user %d (not %d)" % (user_id, args.user_id))
                continue

            trial_results = el.find_trial_results(study_result_id=study_result.id, experiment_id=experiment.id)

            collector.add_trial_results(experiment, trial_results, trial_definitions)

            user_datapoints = []
            for trial_result in trial_results:
                response_data_points = fetch_datapoints(study_result, experiment, trial_result, trial_result.protocol_user_id, user_id)
                user_datapoints += response_data_points

                collector.add_data_points(experiment, trial_result, response_data_points)
                print(f"        Got {len(response_data_points)} data points for trial {trial_result.id} (user {user_id})")

            analyze_and_dump_user_data_points(user_datapoints, user_id)
            for answer in synthesize_answers(user_datapoints, trial_definitions):
                collector.add_answer(answer)


##
## MAIN
##

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

#
# Double-check that we have the right user
#

user = el.assert_creator()

if __name__ == "__main__":
    print("\nExecution of dump_results.py script started...")

    result_path_generator = ResultPathGenerator(args.result_root_dir, args.study_id)
    collector = ResultCollector(result_path_generator)

    process(collector, result_path_generator)

    collector.emit()
    print("\nExecution completed. Results have been emitted.")
