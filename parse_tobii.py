import csv
import pandas as pd
import tobii_utils
from os.path import basename

colidx = tobii_utils.colidx

root = "/Users/iainbryson/Projects/DTUCogSci/"
tobiifile = root+'elicit/client-api/tobii/allMediaBPMDS_slice.tsv'
tobiifile = root+'/Physiological/allMediaBPMDS.tsv'
tobiifile = root+'/elicit/client-api/tobii_markers.tsv'
#parse_dates = {'LocalTime' : [colidx["RecordingDate"], colidx["LocalTimeStamp"]]}
parse_dates = ['LocalTime']
dtypes = {
    'MouseEvent': str,
    'StudioEvent': str,
    'StudioEventData': str,
    'KeyPressEvent': str,
}
tobii_filename = basename(tobiifile)
df = pd.read_table(tobiifile, parse_dates=parse_dates, dtype=dtypes)
df.dropna(axis=1, how='all')

#df.loc[df['StudioEvent'].isin(['ImageStart', 'ImageEnd'])][['StudioEvent', 'ParticipantName', 'MediaName', 'LocalTime']].sort_values('LocalTime')

#df.loc[df['StudioEvent'].isin(['ImageStart', 'ImageEnd'])].to_csv("tobii_markers.tsv", sep='\t')

#
# Create StudyDefinition structure
#


import pprint
import sys
import pyelicit

import examples_default
from example_helpers import *


##
# MAIN
##

pp = pprint.PrettyPrinter(indent=4)
args = examples_default.parse_command_line_args()
args.apiurl = "http://localhost:3000"
elicit = pyelicit.Elicit(pyelicit.ElicitCreds(),
                         args.apiurl, examples_default.send_opt)

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
protocol_definition = add_obj("addProtocolDefinition",
                              args)


#
# Add users to protocol
#

protocol_users = addUsersToProtocol(client,
                                    elicit,
                                    new_study,
                                    protocol_definition,
                                    study_participants)


#
# Add a new Phase Definition
#

new_phase = dict(phase_definition=dict(definition_data="foo"))
new_phase = add_obj("addPhaseDefinition",
                    dict(phase_definition=new_phase,
                         study_definition_id=new_study.id,
                         protocol_definition_id=protocol_definition.id))


images = df['MediaName'].unique()
trial_map = {}
trials = []
components = []
for idx, image in enumerate(list(images)):
    trial_map[image] = idx
    new_trial_definition = dict(trial_definition=dict(definition_data="foo"))
    args = dict(trial_definition=new_trial_definition,
                study_definition_id=new_study.id,
                protocol_definition_id=protocol_definition.id,
                phase_definition_id=new_phase.id)
    new_trial_definition = add_obj("addTrialDefinition",
                                   args)

    trial_map[image] = new_trial_definition

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
                                 protocol_definition_id=protocol_definition.id,
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

    study_result = dict(study_result=dict(study_definition_id=new_study.id,
                                          user_id=user.id))
    study_result = add_obj("addStudyResult",
                           dict(study_result=study_result))

    experiment = dict(experiment=dict(protocol_user_id=protocol_users[idx].id,
                                      current_stage_id=1,
                                      num_stages_completed=1,
                                      num_stages_remaining=0,
                                      study_result_id=study_result.id,
                                      completed_at=stage_end))
    experiment = add_obj("addExperiment",
                         dict(experiment=experiment,
                              study_result_id=study_result.id))

    stage = dict(stage=dict(protocol_user_id=protocol_users[idx].id,
                            phase_definition_id=new_phase.id,
                            experiment_id=experiment.id,
                            last_completed_trial=new_trial_definition.id,
                            current_trial=None,
                            completed_at=stage_end))
    stage = add_obj("addStage",
                    dict(stage=stage,
                         study_result_id=study_result.id))

    for media_name, trial in trial_map.items():
        trial_start = trial_starts[media_name]
        trial_end = trial_ends[media_name]

        trial_result = dict(protocol_user_id=protocol_users[idx].id,
                            phase_definition_id=new_phase.id,
                            trial_definition_id=trial.id,
                            experiment_id=experiment.id,
                            started_at=trial_start,
                            completed_at=trial_end)
        args = dict(trial_result=dict(trial_result=trial_result),
                    study_result_id=study_result.id)
        trial_result = add_obj("addTrialResult",
                               args)

    break


#
# Upload TimeSeries
#

import requests

#from requests_toolbelt.multipart.encoder import MultipartEncoder

file = (tobiifile, open(tobiifile, 'rb'), 'text/tab-separated-values', {'Expires': '0'})
#file = (tobiifile+".gz", open(tobiifile+".gz", 'rb'), 'text/tab-separated-values+gzip', {'Expires': '0'})

#multipart_data = MultipartEncoder(
#    fields={
            # a file upload field
#            'file': file
            # plain text fields
#            'study_definition_id': new_study.id, 
#            'protocol_definition_id': new_protocol.id,
#            'phase_definition_id': new_phase.id,
#           }
#    )
multipart_data = {
    'time_series[file]': file,
    'time_series[study_definition_id]': (None, new_study.id),
    'time_series[protocol_definition_id]': (None, protocol_definition.id),
    'time_series[phase_definition_id]': (None, new_phase.id)
}

url = elicit.api_url + "/api/v1/study_results/time_series"

#curl  \
# -F "time_series[file]=@./tobii/allMediaBPMDS_slice.tsv.gz;type=text/tab-separated-values+gzip" \
# -F "time_series[stage_id]=1" \
#localhost:3000/api/v1/study_results/1/time_series \
# -H 'Accept-Encoding: gzip, deflate, br' \
# -H 'Accept: text/tab-separated-values' \
# -H 'Authorization: Bearer 2b3918fbde187e3948fdcc8e78695e80237bb1490d1ba3e69e530d9d131477a3' 

headers = {
#    'Content-Type': multipart_data.content_type,
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/tab-separated-values',
    'Authorization':  elicit.auth_header,
}
pp.pprint(headers)
pp.pprint(multipart_data)
response = requests.post(url, data=multipart_data, headers=headers)
pp.pprint(response)

#response = requests.post(elicit.api_url + "/api/v1/media_files", files=multipart_data, headers=headers)
#pp.pprint(response)


    # Generate trial results

# and (df['StudioEvent'] == 'ImageStart') and df['StudioEvent'] ==
# 'ImageStart'] and df['MediaName'] == k

# for user in df['ParticipantName'].unique():
#  print(user + ":")
#  df.loc[df['ParticipantName'] == user].to_csv(user + ".tsv", sep='\t')

#print(json.dumps( {k: v for v, k in enumerate(list(df))} , indent=4))
