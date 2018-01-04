"""
Example for dumping the results of a study.
"""

import pprint
import sys
import pyelicit

import examples_default

##
# MAIN
##

pp = pprint.PrettyPrinter(indent=4)

examples_default.parser.add_argument(
    '--study_id', default=1, help="The study ID to dump")
examples_default.parser.add_argument(
    '--user_id', default=None, help="The study ID to dump")
examples_default.parser.add_argument(
    '--user_name', default=None, help="The study ID to dump")
args = examples_default.parse_command_line_args()
elicit = pyelicit.Elicit(pyelicit.ElicitCreds(),
                         args.apiurl, examples_default.send_opt)

#
# Login admin user to get study results
#
client = elicit.login()


user_id = args.user_id
if args.user_name:
    resp = client.request(elicit['findUser'](id=args.user_name))
    assert resp.status == 200
    user_id = resp.data.id

resp = client.request(elicit['findStudyResults']
                      (study_definition_id=args.study_id))
assert resp.status == 200
study_results = resp.data
print("\n\nSTUDY_RESULTS:\n")
pp.pprint(study_results)


if not user_id:
  user_id = study_result[0].user_id

study_result = next((x for x in study_results if x.user_id == user_id), None)
assert study_result != None

protocol_id = 1

resp = client.request(elicit['findProtocolUsers'](study_definition_id=study_result.study_definition_id,
                                                  protocol_definition_id=protocol_id))
assert resp.status == 200
protocol_users = resp.data
print("\n\nPROTOCOL USERS:\n")
pp.pprint(protocol_users)

protocol_users = list(filter(lambda p: p.user_id == user_id, protocol_users))
print("\n\nPROTOCOL USERS FOR USER %d:\n" % user_id)
pp.pprint(protocol_users)

protocol_user_id = list(protocol_users)[0].id

resp = client.request(elicit['findExperiments']
                      (study_result_id=study_result.id))

assert resp.status == 200

print("\n\nEXPERIMENTS:\n")
pp.pprint(resp.data)

# chose the first experiment
experiment = resp.data[0]


resp = client.request(elicit['findStages'](study_result_id=study_result.id,
                                           experiment_id=experiment.id))
assert resp.status == 200
print("\n\nSTAGES:\n")
pp.pprint(resp.data)

resp = client.request(elicit['findTrialResults'](study_result_id=study_result.id,
                                                 experiment_id=experiment.id))
assert resp.status == 200
print("\n\nTRIAL RESULTS:\n")
pp.pprint(resp.data)


resp = client.request(elicit['findDataPoints'](study_result_id=study_result.id,
                                               protocol_user_id=protocol_user_id))

assert resp.status == 200
print("\n\nDATA POINTS:\n")
pp.pprint(resp.data)
