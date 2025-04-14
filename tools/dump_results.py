"""
Example for dumping the results of a study.
"""
import pprint
from pyelicit import elicit
from pyelicit import command_line
from dump_utilities import with_dates
from result_path_generator import ResultPathGenerator
from result_collector import ResultCollector
import elicit_helpers as elicit_helper 

##
## DEFAULT ARGUMENTS
##

arg_defaults = {
    "study_id": 1424,
    "env": "prod",
    "user_id": None, # all users
    "result_root_dir": "../../results",
    "env_file": "../prod.yaml"
}


##
## HELPERS
##

def process(collector: ResultCollector, results_path_generator: ResultPathGenerator):
    study_results = el.find_study_results(study_definition_id=args.study_id)
    study_info = elicit_helper.ensure_study_info(el, args.study_id, results_path_generator)
    phase_definition = study_info['protocol_definitions'][0]['phase_definitions'][0]
    trial_definitions = {}
    for trial_def in phase_definition["trial_definitions"]:
        if 'id' in trial_def:
            trial_definitions[trial_def['id']] = trial_def

    collector.trial_definitions = trial_definitions
    print("\nSTUDY_RESULTS\n")
    if args.debug:
        pp.pprint([with_dates(study_result) for study_result in study_results])
    else:
        print(f"\tGot {len(study_results)} study results: #{[study_result.id for study_result in study_results]}")

    for study_result in study_results:
        experiments = el.find_experiments(study_result_id=study_result.id)

        print("\nEXPERIMENTS\n")

        if args.debug:
            pp.pprint([with_dates(experiment) for experiment in experiments])
        else:
            print(f"\tGot {len(experiments)} experiments for study result {study_result.id}")

        for experiment in experiments:
            user_id = experiment['protocol_user']['user_id']

            if args.user_id and args.user_id != user_id:
                print("Skipping user %d (not %d)" % (user_id, args.user_id))
                continue

            experiment_time_series = elicit_helper.fetch_all_time_series(el,args.study_id,study_result, experiment,result_path_generator)
            collector.add_experiment_event(experiment, experiment_time_series)

            trial_results = el.find_trial_results(study_result_id=study_result.id, experiment_id=experiment.id)

            collector.add_trial_results(experiment, trial_results, trial_definitions)

            user_datapoints = []
            for trial_result in trial_results:
                response_data_points = elicit_helper.fetch_datapoints(el,study_result, experiment, trial_result, trial_result.protocol_user_id, user_id)
                user_datapoints += response_data_points

                collector.add_data_points(experiment, trial_result, response_data_points)
                #print(f"        Got {len(response_data_points)} data points for trial {trial_result.id} (user {user_id})")

            #%% face_landmark datapoints
            datapoints_facelandmarker, user_datapoints = elicit_helper.parse_datapoints(user_datapoints, 'face_landmark')
            
            # track the events that are generated when landmarker data is sent
            landmarker_event_configuration, duration, summary_df = elicit_helper.analyze_landmarker_event_summary(datapoints_facelandmarker, user_id)
            collector.add_landmarker_event_configuration(user_id, landmarker_event_configuration, duration, summary_df)
            
            elicit_helper.dump_user_data_points(datapoints_facelandmarker, args.study_id, user_id,result_path_generator,'face_landmark')

            #%% mouse datapoints
            datapoints_mouse,user_datapoints = elicit_helper.parse_datapoints(user_datapoints, 'mouse')
            
            # track the events that are generated when mouse data is sent
            mouse_event_tracking_configuration, duration, summary_df = elicit_helper.analyze_mouse_tracking_event_summary(datapoints_mouse, user_id)
            collector.add_mouse_tracking_event_summary(user_id, mouse_event_tracking_configuration, duration, summary_df)
            
            elicit_helper.dump_user_data_points(datapoints_mouse, args.study_id, user_id,result_path_generator,'mouse')
            
            #%% instruments datapoints
            datapoints_instruments,user_datapoints = elicit_helper.parse_datapoints(user_datapoints, 'instruments')
            
            for answer in elicit_helper.synthesize_answers(datapoints_instruments, trial_definitions):
                collector.add_answer(answer)
            
            elicit_helper.dump_user_data_points(datapoints_instruments, args.study_id, user_id,result_path_generator,'instruments')
            
            #%% face landmarker calibration datapoints
            datapoints_face_landmark_calibration,user_datapoints = elicit_helper.parse_datapoints(user_datapoints, 'face_landmark_calibration')
            
            collector.add_landmarker_calibration_events(datapoints_face_landmark_calibration)
            
            #%% stimuli datapoints
            datapoints_face_stimulus,user_datapoints = elicit_helper.parse_datapoints(user_datapoints, 'stimulus')
            elicit_helper.dump_user_data_points(datapoints_face_stimulus, args.study_id, user_id,result_path_generator,'stimulus')

            #%% everything else
            elicit_helper.dump_user_data_points(user_datapoints, args.study_id, user_id,result_path_generator,'leftover')


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
