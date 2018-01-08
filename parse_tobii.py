import csv
import json
import pandas as pd
import tobii_utils
import os
import pprint
import sys
import pyelicit

import examples_default
from example_helpers import *


##
# MAIN
##

pp = pprint.PrettyPrinter(indent=4)
examples_default.parser.add_argument(
    '--tobii_filename', default="tobii/tobii_resample.tsv", help="The Tobii file to load")
args = examples_default.parse_command_line_args()
#args.apiurl = "http://localhost:3000"
elicit = pyelicit.Elicit(pyelicit.ElicitCreds(),
                         args.apiurl, examples_default.send_opt)

#
# Load Tobii file
#

colidx = tobii_utils.colidx

tobiifile = os.path.abspath(args.tobii_filename)
parse_dates = {'LocalTime' : [colidx["RecordingDate"], colidx["LocalTimeStamp"]]}
dtypes = {
    'MouseEvent': str,
    'StudioEvent': str,
    'StudioEventData': str,
    'KeyPressEvent': str,
}
tobii_filename = os.path.basename(tobiifile)
df = pd.read_table(tobiifile, parse_dates=parse_dates, dtype=dtypes)

#
# Create StudyDefinition structure
#


#
# Login admin user
#
client = elicit.login()
investigator_user = examples_default.assert_admin(client, elicit)


def add_obj(op, args):
    return add_object(client, elicit, op, args)

#
# Create users
#

participants = df['ParticipantName'].unique()
participant_map = {}
group_name_map = {}
study_participants = []
for idx, participant in enumerate(list(participants)):
    participant_map[participant] = idx
    u = find_or_create_user(client,
                            elicit,
                            participant,
                            "password",
                            (participant+"@elicit.dtu.dk"),
                            'registered_user')
    pp.pprint(u)
    group_name_map[participant] = "control" if (idx < 8) else "signal"
    participant_map[participant] = u.id
    study_participants.append(u)

print(participant_map)


#
# Create StudyDefinition
#

study_definition = dict(title="Import from %s" % tobii_filename,
                        description='Study created from Tobii export',
                        version=1,
                        lock_question=1,
                        enable_previous=1,
                        footer_label="This is the footer of the study",
                        redirect_close_on_url=elicit.api_url+"/participant",
                        data="Put some data here.",
                        principal_investigator_user_id=investigator_user.id)
new_study = add_obj("addStudy",
                    dict(study=dict(study_definition=study_definition)))

#
# Add a new Protocol Definition
#

protocol_def = dict(name="Import from %s" % tobii_filename,
                    definition_data="foo",
                    summary="Tobii protocol",
                    description="Tobii protocol",
                    active=True)
args = dict(protocol_definition=dict(protocol_definition=protocol_def),
            study_definition_id=new_study.id)
new_protocol = add_obj("addProtocolDefinition", args)


#
# Add users to protocol
#

protocol_users = add_users_to_protocol(client,
                                       elicit,
                                       new_study,
                                       new_protocol,
                                       study_participants,
                                       group_name_map)


#
# Add a new Phase Definition
#

new_phase = dict(phase_definition=dict(definition_data="foo"))
new_phase = add_obj("addPhaseDefinition",
                    dict(phase_definition=new_phase,
                         study_definition_id=new_study.id,
                         protocol_definition_id=new_protocol.id))


images = df['MediaName'].unique()
trial_map = {}
trials = []
components = []
for idx, image in enumerate(list(images)):
    trial_map[image] = idx
    new_trial_definition = dict(trial_definition=dict(definition_data="foo"))
    args = dict(trial_definition=new_trial_definition,
                study_definition_id=new_study.id,
                protocol_definition_id=new_protocol.id,
                phase_definition_id=new_phase.id)
    new_trial_definition = add_obj("addTrialDefinition",
                                   args)

    trial_map[image] = new_trial_definition
    trials.append(new_trial_definition)

    component_definition = {
        "Component": {
            "Inputs": {
                "Instrument": None,
                "Stimulus": {
                    "Type": "image/png",
                    "URI": image,
                    "Label": "This is my stimuli Label"
                }
            },
            "Outputs": {
            }
        }
    }

    new_component = dict(component=dict(name=image,
                                        definition_data=component_definition))
    new_component = add_obj("addComponent",
                            dict(component=new_component,
                                 study_definition_id=new_study.id,
                                 protocol_definition_id=new_protocol.id,
                                 phase_definition_id=new_phase.id,
                                 trial_definition_id=new_trial_definition.id))


#
# Create StudyResults structures
#

# Gather markers for trial beginning/ending based on StudioEvent
start_end_events = df.loc[df['StudioEvent'].isin(['ImageStart', 'ImageEnd'])]

for idx, user in enumerate(study_participants):

    user_events = start_end_events.loc[
        (start_end_events['ParticipantName'] == user.username)]

    trial_starts = {}
    trial_ends = {}
    for media_name in start_end_events['MediaName'].unique():
        se = user_events.loc[(user_events['MediaName'] == media_name)][
            ['StudioEvent', 'LocalTime']]
        trial_starts[media_name] = list(
            se.loc[se['StudioEvent'] == 'ImageStart']['LocalTime'])[0]
        trial_ends[media_name] = list(
            se.loc[se['StudioEvent'] == 'ImageEnd']['LocalTime'])[0]

    stage_end = sorted([v for k, v in trial_ends.items()])[-1]
    stage_start = sorted([v for k, v in trial_starts.items()])[0]

    print(trial_starts)

    study_result = dict(study_result=dict(study_definition_id=new_study.id,
                                          user_id=user.id))
    study_result = add_obj("addStudyResult",
                           dict(study_result=study_result))

    experiment = dict(experiment=dict(protocol_user_id=protocol_users[idx].id,
                                      current_stage_id=None,
                                      num_stages_completed=1,
                                      num_stages_remaining=0,
                                      study_result_id=study_result.id,
                                      started_at=stage_start,
                                      completed_at=stage_end))
    experiment = add_obj("addExperiment",
                         dict(experiment=experiment,
                              study_result_id=study_result.id))

    stage = dict(stage=dict(protocol_user_id=protocol_users[idx].id,
                            phase_definition_id=new_phase.id,
                            experiment_id=experiment.id,
                            last_completed_trial=new_trial_definition.id,
                            current_trial=None,
                            started_at=stage_start,
                            completed_at=stage_end))
    stage = add_obj("addStage",
                    dict(stage=stage,
                         study_result_id=study_result.id))

    for media_name, trial in trial_map.items():
        trial_start = trial_starts[media_name]
        trial_end = trial_ends[media_name]

        session_name = "session1"

        trial_result = dict(protocol_user_id=protocol_users[idx].id,
                            phase_definition_id=new_phase.id,
                            trial_definition_id=trial.id,
                            experiment_id=experiment.id,
                            started_at=trial_start,
                            session_name=session_name,
                            completed_at=trial_end)
        args = dict(trial_result=dict(trial_result=trial_result),
                    study_result_id=study_result.id)
        trial_result = add_obj("addTrialResult", args)


#
# Upload TimeSeries
#

import requests
import cgi
from requests_toolbelt.multipart.encoder import MultipartEncoder
import gzip


with open(tobiifile, 'rb') as f_in, gzip.open(tobiifile+'.gz', 'wb') as f_out:
    f_out.writelines(f_in)

file = (tobiifile+".gz", open(tobiifile+".gz", 'rb'), 'text/tab-separated-values+gzip', {'Expires': '0'})
#file = (tobiifile+".gz", open(tobiifile+".gz", 'rb'), 'text/tab-separated-values+gzip', {'Expires': '0'})

metadata = {
    "date_field": "RecordingDate",
    "time_field": "LocalTimeStamp",
    "user_field": "ParticipantName"
}
multipart_data = MultipartEncoder(
    fields={
            # a file upload field
            'time_series[file]': file,
            # plain text fields
            'time_series[study_definition_id]': str(new_study.id),
            'time_series[protocol_definition_id]': str(new_protocol.id),
            'time_series[phase_definition_id]': str(new_phase.id),
            'time_series[schema]': "tobii_tsv",
            'time_series[schema_metadata]': json.dumps(metadata)
           }
    )

url = elicit.api_url + "/api/v1/study_results/time_series"

headers = {
    'Content-Type': multipart_data.content_type,
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/tab-separated-values',
    'Authorization':  elicit.auth_header,
}
pp.pprint(headers)
pp.pprint(multipart_data)
response = requests.post(url, data=multipart_data, headers=headers)
time_series = json.loads(response.content)

# TODO: check response OK

pp.pprint(time_series)
args = dict(id=time_series["id"])
pp.pprint(args)
resp = client.request(elicit['getTimeSeries'](**args))
pp.pprint(resp.status)
pp.pprint(resp.data)

#resp = client.request(elicit['getTimeSeriesContent'](**args))
#pp.pprint(resp.status)
#pp.pprint(resp.data)

def query_time_series(id, query_params):

    query = "&".join([("%s=%s"%(k,v)) for k,v in query_params.items()])

    url = elicit.api_url + "/api/v1/study_results/time_series/%d/content?%s"%(time_series["id"], query)

    headers = {
        'Content-Type': "text/tab-separated-values",
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/tab-separated-values',
        'Authorization':  elicit.auth_header,
    }
    with requests.get(url, headers=headers, stream=True) as r:

        pp.pprint(r.status_code)
        pp.pprint(r.headers)
        value, params = cgi.parse_header(r.headers['Content-Disposition'])
        query_filename=params['filename']
        with open(query_filename, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)

        query_df=pd.read_table(query_filename, parse_dates=parse_dates, dtype=dtypes)

        #print(query_df.loc[query_df['StudioEvent'].isin(['ImageStart', 'ImageEnd'])][['StudioEvent', 'ParticipantName', 'MediaName', 'LocalTime']].sort_values('LocalTime'))
        print(query_df[['StudioEvent', 'ParticipantName', 'MediaName', 'LocalTime']].sort_values('LocalTime'))

query_time_series(time_series["id"], {'username': 'P01'})

query_time_series(time_series["id"], {'username': 'P01', "trial_definition_id":str(trial_map['q4.2.png'].id)})

query_time_series(time_series["id"], {"trial_definition_id":str(trial_map['q4.2.png'].id)})

#response = requests.post(elicit.api_url + "/api/v1/media_files", files=multipart_data, headers=headers)
#pp.pprint(response)


