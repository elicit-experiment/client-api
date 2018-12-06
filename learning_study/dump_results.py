"""
Example for dumping the results of a study.
"""

import csv
import json

from examples_base import *

##
## MAIN
##

with open('questions.json', 'r') as questionsfd:
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

#
# Double-check that we have the right user
#

user = el.assert_admin()

study_results = el.find_study_results(study_definition_id=args.study_id)

all_answers = []
raw_questions = dict()

for study_result in study_results:
    experiments = el.find_experiments(study_result_id=study_result.id)

    for experiment in experiments:
        protocol_user_id = experiment['protocol_user_id']
        stages = el.find_stages(study_result_id=study_result.id, experiment_id=experiment.id)

        trial_results = el.find_trial_results(study_result_id=study_result.id, experiment_id=experiment.id)

        data_points = el.find_data_points(study_result_id=study_result.id, protocol_user_id=protocol_user_id)

        states = filter(lambda x: x['point_type'] == 'State', data_points)

        def fetch_answer(state):
            out = state.copy()
            out['value'] = json.loads(state['value'])
            if 'Id' in out['value']:
                out['answer_id'] = out['value']['Id']
            else:
                out['answer_id'] = None
            return out

        states = map(fetch_answer, states)

        answers = list (map(lambda x: (x['protocol_user']['user_id'], x['answer_id'], x['datetime'], x['component_id']), states))

        all_answers += answers

        for answer in answers:
            if not (answer[3] in raw_questions):
                component = el.get_component(component_id = answer[3])
                raw_questions[answer[3]] = component

pp.pprint(raw_questions)

with open('answer.csv', 'w', newline='') as csvfile:
    answerwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    answerwriter.writerow(['user_id', 'answer_id', 'datetime', 'component_id', 'question', 'correct'])
    for answer in all_answers:
        id = answer[1]
        if id == None:
            continue
        question = 'unknown'
        correct = False
        if str(answer[3]) in questions:
            item = questions[str(answer[3])]['items']['Item']
            question = questions[str(answer[3])]['question']
            answered_option = next((x for x in item if x['Id'] == str(id)))
            pp.pprint(answered_option)
            correct = answered_option['Correct']
        elif answer[3] in raw_questions:
            component_def = json.loads(component['definition_data'])
            pp.pprint(component_def)
            radio_button_def = component_def['Instruments'][0]['Instrument']['RadioButtonGroup']
            items = radio_button_def['Items']['Item']
            question = radio_button_def['HeaderLabel']
            print(question)
            print(answer[1])
            answered_option = next((x for x in items if x['Id'] == str(id)))
            correct = answered_option['Correct']

        answerwriter.writerow(answer + (question, correct))


