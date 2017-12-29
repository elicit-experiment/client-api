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
import example_helpers


def find_or_create_user(username, password, email = None, role = None):
  resp = client.request(elicit['findUser'](id=username))

  if resp.status == 404:
    pp.pprint(resp.data)
    pp.pprint(resp.status)
    print("Not found; Creating user:")
    user_details = dict(username=username,
                        password=password,
                        email=email or (username+"@elicit.dtu.dk"),
                        role=role or 'registered_user',
                        password_confirmation=password)
    resp = client.request(elicit['addUser'](user=dict(user=user_details)))
    return(resp.data)
  else:
    print("User already exists.")
    return(resp.data)

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

#
# Create users
#

participants=df['ParticipantName'].unique()
participant_map={}
study_participants=[]
for idx, participant in enumerate(list(participants)):
  participant_map[participant] = idx
  u = find_or_create_user(participant,
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
new_study = dict(study_definition=study_definition)
resp = client.request(elicit['addStudy'](study=new_study))
assert resp.status == 201

new_study = resp.data
print("\n\nCreated new study:\n")
pp.pprint(new_study)

#
# Add a new Protocol Definition
#

new_protocol_definition = dict(protocol_definition=dict(name='Newly created protocol definition from Python',
                                                        definition_data="foo",
                                                        summary="Tobii protocol",
                                                        description="Tobii protocol",
                                                        active=True))
resp = client.request(elicit['addProtocolDefinition'](protocol_definition=new_protocol_definition,
                                                      study_definition_id=new_study.id))

assert resp.status == 201


new_protocol_definition = resp.data
print("\n\nCreated new protocol:\n")
pp.pprint(new_protocol_definition)


#
# Add users to protocol
#

protocol_users = example_helpers.addUsersToProtocol(client, elicit, new_study, new_protocol_definition, study_participants)



#
# Add a new Phase Definition
#

new_phase_definition = dict(phase_definition=dict(definition_data="foo"))
resp = client.request(elicit['addPhaseDefinition'](phase_definition=new_phase_definition,
                                                   study_definition_id=new_study.id,
                                                   protocol_definition_id=new_protocol_definition.id))

assert resp.status == 201

new_phase_definition = resp.data
print("\n\nCreated new phase:\n")
pp.pprint(new_phase_definition)



images=df['MediaName'].unique()
trial_map={}
trials=[]
components=[]
for idx, image in enumerate(list(images)):
  trial_map[image] = idx
  new_trial_definition = dict(trial_definition=dict(definition_data="foo"))
  resp = client.request(elicit['addTrialDefinition'](trial_definition=new_trial_definition,
                                                     study_definition_id=new_study.id,
                                                     protocol_definition_id=new_protocol_definition.id,
                                                     phase_definition_id=new_phase_definition.id))
  assert resp.status == 201
  new_trial_definition = resp.data
  trials.append(new_trial_definition)
  print("\n\nCreated new trial definition:\n")
  pp.pprint(new_trial_definition)

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
  resp = client.request(elicit['addComponent'](component=new_component,
                                               study_definition_id=new_study.id,
                                               protocol_definition_id=new_protocol_definition.id,
                                               phase_definition_id=new_phase_definition.id,
                                               trial_definition_id=new_trial_definition.id))
  print("\n\nCreated new component:\n")
  assert resp.status == 201

  new_component = resp.data
  components.append(new_component)

  pp.pprint(new_component)


#
# Create StudyResults structures
#

# Gather markers for trial beginning/ending based on StudioEvent
start_end_events=df.loc[df['StudioEvent'].isin(['ImageStart', 'ImageEnd'])]

for idx, user in enumerate(study_participants):

  user_events=start_end_events.loc[(start_end_events['ParticipantName'] == user.username)]

  trial_starts={}
  trial_ends={}
  for media_name in df['MediaName'].unique():
    se=user_events.loc[(user_events['MediaName'] == media_name)][['StudioEvent', 'LocalTime']]
    trial_starts[media_name] = list(se.loc[se['StudioEvent'] == 'ImageStart']['LocalTime'])[0]
    trial_ends[media_name] = list(se.loc[se['StudioEvent'] == 'ImageEnd']['LocalTime'])[0]  

  stage_end=sorted([v for k,v in trial_ends.items()])[-1]
  stage_start=sorted([v for k,v in trial_starts.items()])[0]


  study_result = dict(study_result=dict(study_definition_id=new_study.id,
                                        user_id=user.id))
  pp.pprint(study_result)
  resp = client.request(elicit['addStudyResult'](study_result=study_result))
  print("\n\nCreated new Study Result for %s:\n"%user.username)
  assert resp.status == 201

  study_result = resp.data

  pp.pprint(study_result)

  experiment = dict(experiment=dict(protocol_user_id=protocol_users[idx].id,
                                    current_stage_id=1,
                                    num_stages_completed=1,
                                    num_stages_remaining=0,
                                    study_result_id=study_result.id,
                                    completed_at=stage_end))
  resp = client.request(elicit['addExperiment'](experiment=experiment,
                                                study_result_id=study_result.id))
  print("\n\nCreated new Experiment for %s:\n"%user.username)
  assert resp.status == 201

  experiment = resp.data

  pp.pprint(experiment)


  stage = dict(stage=dict(protocol_user_id=protocol_users[idx].id,
                          phase_definition_id=new_phase_definition.id,
                          experiment_id = experiment.id,
                          last_completed_trial=new_trial_definition.id,
                          current_trial=None,
                          completed_at=stage_end))
  resp = client.request(elicit['addStage'](stage=stage,
                                           study_result_id=study_result.id))
  print("\n\nCreated new Stage for %s:\n"%user.username)
  assert resp.status == 201

  stage = resp.data

  pp.pprint(stage)


  for media_name, trial in trial_map.items():
    trial_start = trial_starts[media_name]
    trial_end = trial_ends[media_name]

    trial_result = dict(trial_result=dict(protocol_user_id=protocol_users[idx].id,
                            phase_definition_id=new_phase_definition.id,
                            trial_definition_id=trial.id,
                            experiment_id = experiment.id,
                            started_at=trial_start,
                            completed_at=trial_end))
    #pp.pprint(trial_result)
    resp = client.request(elicit['addTrialResult'](trial_result=trial_result,
                                                   study_result_id=study_result.id))
    print("\n\nCreated new TrialResult for %s:\n"%user.username)
    assert resp.status == 201

    trial_result = resp.data

    pp.pprint(trial_result)

  break


# Upload TimeSeries
#




    # Generate trial results

#   and (df['StudioEvent'] == 'ImageStart') and df['StudioEvent'] == 'ImageStart'] and df['MediaName'] == k

#for user in df['ParticipantName'].unique():
#  print(user + ":")
#  df.loc[df['ParticipantName'] == user].to_csv(user + ".tsv", sep='\t')

#print(json.dumps( {k: v for v, k in enumerate(list(df))} , indent=4))


