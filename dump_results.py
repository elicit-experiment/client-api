"""
Example for dumping the results of a study.
"""

import pprint
import sys
import pyelicit

import examples_default
import requests
import cgi
from requests_toolbelt.multipart.encoder import MultipartEncoder
import gzip
import json
import os
##
# MAIN
##

pp = pprint.PrettyPrinter(indent=4)

examples_default.parser.add_argument(
    '--study_id', default=1, help="The study ID to dump", type=int)
examples_default.parser.add_argument(
    '--user_id', default=None, help="The user ID to dump", type=int)
examples_default.parser.add_argument(
    '--user_name', default=None, help="The user name to dump")
args = examples_default.parse_command_line_args()
elicit = pyelicit.Elicit(pyelicit.ElicitCreds(),
                         args.apiurl, args.send_opt)

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
  user_id = study_results[0].user_id

users_studies = (study_result for study_result in study_results if study_result.user_id == user_id)
#print(list(users_studies))
study_result = next(users_studies, None)
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

stage_ids = list((stage.id for stage in resp.data))

pp.pprint(stage_ids)

for stage_id in stage_ids:
    resp = client.request(elicit['findTimeSeries'](study_result_id=study_result.id, stage_id=stage_id))
    assert resp.status == 200
    print("\n\nTime Series for Stage %d:\n"%stage_id)
    pp.pprint(resp.data)

    time_series = resp.data[0]

    #url = elicit.api_url + "/api/v1/study_results/time_series/%d/content"%(time_series["id"])
    url =  elicit.api_url + "/public/" + json.loads(time_series.file.replace("'", '"'))['url']

    headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/tab-separated-values',
        'Authorization':  elicit.auth_header,
    }
    with requests.get(url, headers=headers, stream=True) as r:

        pp.pprint(r.status_code)
        pp.pprint(r.headers)
        content_disposition = r.headers.get('Content-Disposition')
        query_filename = os.path.basename(url)
        if content_disposition:
            value, params = cgi.parse_header(content_disposition)
            query_filename=params['filename']
        with open(query_filename, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)


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
