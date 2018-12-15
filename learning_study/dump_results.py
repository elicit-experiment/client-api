"""
Example for dumping the results of a study.
"""

import csv
import json
import os
import cgi
from datetime import datetime
from functools import partial
import requests
from examples_base import *

##
## HELPERS
##

def parse_datetime(field, state):
    state[field] = datetime.strptime(state[field], '%Y-%m-%dT%H:%M:%S.%fZ')
    return state


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

for study_result in study_results:
    experiments = el.find_experiments(study_result_id=study_result.id)

    for experiment in experiments:
        user_id = experiment['protocol_user']['user_id']
        user_name = experiment['protocol_user']['user']['username']

        protocol_user_id = experiment['protocol_user_id']
        stages = el.find_stages(study_result_id=study_result.id, experiment_id=experiment.id)

        trial_results = el.find_trial_results(study_result_id=study_result.id, experiment_id=experiment.id)

        video_layout = None

        for trial_result in trial_results:
            data_points = el.find_data_points(study_result_id=study_result.id,
                                              trial_definition_id=trial_result.trial_definition_id,
                                              protocol_user_id=protocol_user_id, page_size=50)

            print("Got %d datapoints for study result %d, trial result %d protocol user %d"%(len(data_points), study_result.id, trial_result.id, protocol_user_id))

            #pp.pprint(data_points)

            states = filter(lambda x: x['point_type'] == 'State', data_points)
            video_events = filter(lambda x: (x['point_type'] != 'State') and (x['method'] != None) and ((x['method'].find('audio') != -1) or (x['method'].find('video') != -1)), data_points)
            video_events = list(video_events)

            video_events = filter(partial(parse_datetime, 'datetime'), video_events)

            all_video_events += map(lambda x: (user_id, x['datetime'], x['point_type']), video_events)

            layouts = list(filter(lambda x: x['point_type'] == 'Layout', data_points))
            if len(layouts) > 0:
                video_layout = json.loads(layouts[0]['value'])
                user_id = layouts[0]['protocol_user']['user_id']
                layout_filename = ("user_%d_layout.json" % (user_id))
                with open(layout_filename, 'w') as fd:
                    fd.write(layouts[0]['value'])
            #pp.pprint(list(layouts))

            def fetch_answer(state):
                out = state.copy()
                out['value'] = json.loads(state['value'])
                if 'Id' in out['value']:
                    out['answer_id'] = out['value']['Id']
                else:
                    out['answer_id'] = None
                return out

            states = map(fetch_answer, states)

            answers = list (map(lambda x: (user_id, user_name, x['answer_id'], x['datetime'], x['component_id']), states))

            all_answers += answers

            for answer in answers:
                if not (answer[4] in raw_questions):
                    component = el.get_component(component_id = answer[4])
                    component_def = json.loads(component['definition_data'])
                    component['parsed_definition_data'] = component_def
                    is_radio_button = False
                    if 'Instruments' in component_def:
                        instrument = component_def['Instruments'][0]['Instrument']
                        if 'RadioButtonGroup' in instrument:
                            raw_questions[answer[4]] = component
                            is_radio_button = True
                    #if not is_radio_button:
                    #    pp.pprint(answer)

        pp.pprint(stages)
        for stage_id in (stage.id for stage in stages):
            time_series = el.find_time_series(study_result_id=study_result.id, stage_id=stage_id)

            if len(time_series) < 1:
                print("No time series for stage %d (user %d)\n"%(stage_id, user_id))
                continue

            time_series = time_series[0]

            #url = elicit.api_url + "/api/v1/study_results/time_series/%d/content"%(time_series["id"])
            url =  el.api_url() + json.loads(time_series.file.replace("'", '"'))['url']

            headers = {
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/tab-separated-values',
                'Authorization':  el.auth_header(),
            }
            with requests.get(url, headers=headers, stream=True, verify=args.send_opt['verify']) as r:
                content_disposition = r.headers.get('Content-Disposition')
                query_filename = ("user_%d_"%user_id)+os.path.basename(url)
                if content_disposition:
                    value, params = cgi.parse_header(content_disposition)
                    query_filename=("user_%d_"%user_id)+params['filename']
                with open(query_filename, 'wb') as fd:
                    for chunk in r.iter_content(chunk_size=128):
                        fd.write(chunk)




with open('video.csv', 'w', newline='') as csvfile:
    videowriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    videowriter.writerow(['user_id', 'datetime', 'event'])
    for video_event in all_video_events:
        videowriter.writerow(video_event)

with open('answer.csv', 'w', newline='') as csvfile:
    answerwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    answerwriter.writerow(['user_id', 'user_name', 'answer_id', 'datetime', 'component_id', 'question', 'correct'])
    for answer in all_answers:
        id = answer[2]
        if id == None:
            continue
        question = 'unknown'
        correct = False
        component_id = answer[4]
        component_id_s = str(component_id)
        if component_id_s in questions:
            item = questions[component_id_s]['items']['Item']
            question = questions[component_id_s]['question']
            answered_option = next((x for x in item if x['Id'] == str(id)))
            #print("FROM QUESTIONS %s"%component_id)
            #pp.pprint(answered_option)
            correct = answered_option['Correct']
        elif component_id in raw_questions:
            #print("FROM RAWQUESTIONS %s"%component_id)
            component = raw_questions[component_id]
            component_def = component['parsed_definition_data']
            radio_button_def = component_def['Instruments'][0]['Instrument']['RadioButtonGroup']
            items = radio_button_def['Items']['Item']
            question = radio_button_def['HeaderLabel']
            answered_option = next((x for x in items if x['Id'] == str(id)))
            correct = answered_option['Correct']

        answerwriter.writerow(answer + (question, correct))


