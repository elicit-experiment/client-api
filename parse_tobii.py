import csv
import pandas as pd
import tobii_utils

colidx = tobii_utils.colidx

tobiifile='/Users/iainbryson/Projects/DTUCogSci/elicit/client-api/tobii/allMediaBPMDS_slice.tsv'
tobiifile='/Users/iainbryson/Projects/DTUCogSci/Physiological/allMediaBPMDS.tsv'
tobiifile='/Users/iainbryson/Projects/DTUCogSci/elicit/client-api/tobii_markers.tsv'
#parse_dates = {'LocalTime' : [colidx["RecordingDate"], colidx["LocalTimeStamp"]]}
parse_dates = ['LocalTime']
dtypes = {
'MouseEvent' : str,
'StudioEvent' : str,
'StudioEventData' : str,
'KeyPressEvent' : str,
}
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
## MAIN
##

pp = pprint.PrettyPrinter(indent=4)
args = examples_default.parse_command_line_args()
args.apiurl = "http://localhost:3000"
elicit = pyelicit.Elicit(pyelicit.ElicitCreds(), args.apiurl, examples_default.send_opt)

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

participants=df['ParticipantName'].unique()
participant_map={}
study_participants=[]
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

study_definition = dict(title='Newly created from Python: create_study_example.py',
                        description='Fun study created with Python ',
                        version=1,
                        lock_question=1,
                        enable_previous=1,
                        footer_label="This is the footer of the study",
                        redirect_close_on_url=elicit.api_url+"/participant",
                        data="Put some data here, we don't really care about it.",
                        principal_investigator_user_id=investigator_user.id)
new_study = add_obj("addStudy",
                    dict(study=dict(study_definition=study_definition)))

#
# Add a new Protocol Definition
#

protocol_def = dict(protocol_definition=dict(name='Newly created protocol definition from Python',
                                             definition_data="foo",
                                             summary="Tobii protocol",
                                             description="Tobii protocol",
                                             active=True))
protocol_definition = add_obj("addProtocolDefinition",
                                 dict(protocol_definition=protocol_def,
                                      study_definition_id=new_study.id))


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



images=df['MediaName'].unique()
trial_map={}
trials=[]
components=[]
for idx, image in enumerate(list(images)):
    trial_map[image] = idx
    new_trial_definition = dict(trial_definition=dict(definition_data="foo"))
    new_trial_definition = add_obj("addTrialDefinition",
                                       dict(trial_definition=new_trial_definition,
                                            study_definition_id=new_study.id,
                                            protocol_definition_id=protocol_definition.id,
                                            phase_definition_id=new_phase.id))



    trial_map[image] = new_trial_definition

    component_definition={
    "Component": {
    "Inputs": {
    "Instrument": None,
    "Stimulus" : {
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
start_end_events=df.loc[df['StudioEvent'].isin(['ImageStart', 'ImageEnd'])]

for idx, user in enumerate(study_participants):

    user_events=start_end_events.loc[(start_end_events['ParticipantName'] == user.username)]

    trial_starts={}
    trial_ends={}
    for media_name in start_end_events['MediaName'].unique():
        se=user_events.loc[(user_events['MediaName'] == media_name)][['StudioEvent', 'LocalTime']]
        trial_starts[media_name] = list(se.loc[se['StudioEvent'] == 'ImageStart']['LocalTime'])[0]
        trial_ends[media_name] = list(se.loc[se['StudioEvent'] == 'ImageEnd']['LocalTime'])[0]  

    stage_end=sorted([v for k,v in trial_ends.items()])[-1]
    stage_start=sorted([v for k,v in trial_starts.items()])[0]


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
                            experiment_id = experiment.id,
                            last_completed_trial=new_trial_definition.id,
                            current_trial=None,
                            completed_at=stage_end))
    stage = add_obj("addStage",
                       dict(stage=stage,
                            study_result_id=study_result.id))


    for media_name, trial in trial_map.items():
        trial_start = trial_starts[media_name]
        trial_end = trial_ends[media_name]

        trial_result = dict(trial_result=dict(protocol_user_id=protocol_users[idx].id,
                                              phase_definition_id=new_phase.id,
                                              trial_definition_id=trial.id,
                                              experiment_id = experiment.id,
                                              started_at=trial_start,
                                              completed_at=trial_end))

        trial_result = add_obj("addTrialResult",
                                  dict(trial_result=trial_result,
                                       study_result_id=study_result.id))

    break


# Upload TimeSeries
#




    # Generate trial results

#   and (df['StudioEvent'] == 'ImageStart') and df['StudioEvent'] == 'ImageStart'] and df['MediaName'] == k

#for user in df['ParticipantName'].unique():
#  print(user + ":")
#  df.loc[df['ParticipantName'] == user].to_csv(user + ".tsv", sep='\t')

#print(json.dumps( {k: v for v, k in enumerate(list(df))} , indent=4))


