"""
Example for dumping the results of a study.
"""

import pprint
import sys
import pyelicit

import examples_default

##
## MAIN
##

pp = pprint.PrettyPrinter(indent=4)

args = examples_default.parse_command_line_args()
elicit = pyelicit.Elicit(pyelicit.ElicitCreds(), args.apiurl, examples_default.send_opt)

#
# Login admin user to get study results
#
client = elicit.login()


resp = client.request(elicit['findStudyResults'](study_definition_id=1))
assert resp.status == 200
study_results = resp.data
print("\n\nSTUDY_RESULTS:\n")
pp.pprint(study_results)


study_result = study_results[0]
user_id = study_result.user_id
protocol_id = 1

resp = client.request(elicit['findProtocolUsers'](study_definition_id=study_result.study_definition_id, protocol_definition_id=protocol_id))
assert resp.status == 200
protocol_users = resp.data
print("\n\nPROTOCOL USERS:\n")
pp.pprint(protocol_users)

protocol_users = filter(lambda p: p.user_id == user_id, protocol_users)
print("\n\nPROTOCOL USERS FOR USER %d:\n"%user_id)
pp.pprint(protocol_users)

protocol_user_id = protocol_users[0].id

resp = client.request(elicit['findExperiments'](study_results_id=study_result.id))

assert resp.status == 200

print("\n\nEXPERIMENTS:\n")
pp.pprint(resp.data)

# chose the first experiment
experiment = resp.data[0]


resp = client.request(elicit['findStages'](study_results_id=study_result.id, experiment_id=experiment.id))
assert resp.status == 200
print("\n\nSTAGES:\n")
pp.pprint(resp.data)


resp = client.request(elicit['findDataPoints'](study_results_id=study_result.id, protocol_user_id=protocol_user_id))

assert resp.status == 200
print("\n\nDATA POINTS:\n")
pp.pprint(resp.data)

