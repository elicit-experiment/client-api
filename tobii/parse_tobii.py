import csv
import pandas as pd



colidx = {
    "ExportDate": 0,
    "StudioVersionRec": 1,
    "StudioProjectName": 2,
    "StudioTestName": 3,
    "ParticipantName": 4,
    "RecordingName": 5,
    "RecordingDate": 6,
    "RecordingDuration": 7,
    "RecordingResolution": 8,
    "PresentationSequence": 9,
    "FixationFilter": 10,
    "MediaName": 11,
    "MediaPosX (ADCSpx)": 12,
    "MediaPosY (ADCSpx)": 13,
    "MediaWidth": 14,
    "MediaHeight": 15,
    "SegmentName": 16,
    "SegmentStart": 17,
    "SegmentEnd": 18,
    "SegmentDuration": 19,
    "SceneName": 20,
    "SceneSegmentStart": 21,
    "SceneSegmentEnd": 22,
    "SceneSegmentDuration": 23,
    "RecordingTimestamp": 24,
    "LocalTimeStamp": 25,
    "EyeTrackerTimestamp": 26,
    "MouseEventIndex": 27,
    "MouseEvent": 28,
    "MouseEventX (ADCSpx)": 29,
    "MouseEventY (ADCSpx)": 30,
    "MouseEventX (MCSpx)": 31,
    "MouseEventY (MCSpx)": 32,
    "KeyPressEventIndex": 33,
    "KeyPressEvent": 34,
    "StudioEventIndex": 35,
    "StudioEvent": 36,
    "StudioEventData": 37,
    "ExternalEventIndex": 38,
    "ExternalEvent": 39,
    "ExternalEventValue": 40,
    "EventMarkerValue": 41,
    "FixationIndex": 42,
    "SaccadeIndex": 43,
    "GazeEventType": 44,
    "GazeEventDuration": 45,
    "FixationPointX (MCSpx)": 46,
    "FixationPointY (MCSpx)": 47,
    "SaccadicAmplitude": 48,
    "AbsoluteSaccadicDirection": 49,
    "RelativeSaccadicDirection": 50,
    "AOI[window]Hit": 51,
    "AOI[title]Hit": 52,
    "AOI[graph]Hit": 53,
    "AOI[legend]Hit": 54,
    "AOI[Q3]Hit": 55,
    "AOI[Q2]Hit": 56,
    "AOI[Q1]Hit": 57,
    "AOI[window]Hit.1": 58,
    "AOI[title]Hit.1": 59,
    "AOI[graph]Hit.1": 60,
    "AOI[legend]Hit.1": 61,
    "AOI[Q1]Hit.1": 62,
    "AOI[Q2]Hit.1": 63,
    "AOI[Q3]Hit.1": 64,
    "AOI[Q4]Hit": 65,
    "AOI[QALL]Hit": 66,
    "AOI[window]Hit.2": 67,
    "AOI[title]Hit.2": 68,
    "AOI[graph]Hit.2": 69,
    "AOI[legend]Hit.2": 70,
    "AOI[Q3]Hit.2": 71,
    "AOI[Q1]Hit.2": 72,
    "AOI[Q2]Hit.2": 73,
    "AOI[QALL]Hit.1": 74,
    "AOI[title]Hit.3": 75,
    "AOI[legend]Hit.3": 76,
    "AOI[window]Hit.3": 77,
    "AOI[graph]Hit.3": 78,
    "AOI[Q1]Hit.3": 79,
    "AOI[Q2]Hit.3": 80,
    "AOI[Q3]Hit.3": 81,
    "AOI[window]Hit.4": 82,
    "AOI[title]Hit.4": 83,
    "AOI[legend]Hit.4": 84,
    "AOI[Q1]Hit.4": 85,
    "AOI[Q3]Hit.4": 86,
    "AOI[Q2]Hit.4": 87,
    "AOI[graph]Hit.4": 88,
    "AOI[QAll]Hit": 89,
    "AOI[window]Hit.5": 90,
    "AOI[title]Hit.5": 91,
    "AOI[graph]Hit.5": 92,
    "AOI[legend]Hit.5": 93,
    "AOI[Q1]Hit.5": 94,
    "AOI[Q2]Hit.5": 95,
    "AOI[Q3]Hit.5": 96,
    "AOI[window]Hit.6": 97,
    "AOI[graph]Hit.6": 98,
    "AOI[legend]Hit.6": 99,
    "AOI[title]Hit.6": 100,
    "AOI[Q1]Hit.6": 101,
    "AOI[Q2]Hit.6": 102,
    "AOI[Q3]Hit.6": 103,
    "AOI[Q4]Hit.1": 104,
    "AOI[QAll]Hit.1": 105,
    "AOI[window]Hit.7": 106,
    "AOI[title]Hit.7": 107,
    "AOI[graph]Hit.7": 108,
    "AOI[legend]Hit.7": 109,
    "AOI[Q1]Hit.7": 110,
    "AOI[Q2]Hit.7": 111,
    "AOI[Q3]Hit.7": 112,
    "GazePointIndex": 113,
    "GazePointLeftX (ADCSpx)": 114,
    "GazePointLeftY (ADCSpx)": 115,
    "GazePointRightX (ADCSpx)": 116,
    "GazePointRightY (ADCSpx)": 117,
    "GazePointX (ADCSpx)": 118,
    "GazePointY (ADCSpx)": 119,
    "GazePointX (MCSpx)": 120,
    "GazePointY (MCSpx)": 121,
    "GazePointLeftX (ADCSmm)": 122,
    "GazePointLeftY (ADCSmm)": 123,
    "GazePointRightX (ADCSmm)": 124,
    "GazePointRightY (ADCSmm)": 125,
    "StrictAverageGazePointX (ADCSmm)": 126,
    "StrictAverageGazePointY (ADCSmm)": 127,
    "EyePosLeftX (ADCSmm)": 128,
    "EyePosLeftY (ADCSmm)": 129,
    "EyePosLeftZ (ADCSmm)": 130,
    "EyePosRightX (ADCSmm)": 131,
    "EyePosRightY (ADCSmm)": 132,
    "EyePosRightZ (ADCSmm)": 133,
    "CamLeftX": 134,
    "CamLeftY": 135,
    "CamRightX": 136,
    "CamRightY": 137,
    "DistanceLeft": 138,
    "DistanceRight": 139,
    "PupilLeft": 140,
    "PupilRight": 141,
    "ValidityLeft": 142,
    "ValidityRight": 143,
    "IRMarkerCount": 144,
    "IRMarkerID": 145,
    "PupilGlassesRight": 146,
    "Unnamed: 147": 147
}

tobiifile='/Users/iainbryson/Projects/DTUCogSci/elicit/client-api/tobii/allMediaBPMDS_slice.tsv'
tobiifile='/Users/iainbryson/Projects/DTUCogSci/Physiological/allMediaBPMDS.tsv'
parse_dates = {'LocalTime' : [colidx["RecordingDate"], colidx["LocalTimeStamp"]]}
dtypes = {
  'MouseEvent' : str,
  'StudioEvent' : str,
  'StudioEventData' : str,
  'KeyPressEvent' : str,
}
df = pd.read_table(tobiifile, parse_dates=parse_dates, dtype=dtypes)
df.dropna(axis=1, how='all')
df.loc[df['StudioEvent'].isin(['ImageStart', 'ImageEnd'])][['StudioEvent', 'ParticipantName', 'MediaName', 'LocalTime']].sort_values('LocalTime')



#
# Create StudyDefinition structure
#


import pprint
import sys
import pyelicit

import examples_default

##
## MAIN
##

pp = pprint.PrettyPrinter(indent=4)
args = examples_default.parse_command_line_args()
args.apiurl = "http://localhost:3000"
elicit = pyelicit.Elicit(pyelicit.ElicitCreds(), args.apiurl, examples_default.send_opt)

#
# Login admin user to get study results
#
client = elicit.login()



participants=df['ParticipantName'].unique()
participant_map={}
for idx, participant in enumerate(list(participants)):
  participant_map[participant] = idx
  #resp = client.request(elicit['findUser'](id=participant))
  #pprint(resp)
  resp = client.request(elicit['addUser'](user=dict(user=dict(email=participant+"4@elicit.dtu.dk",
                                                    password="password",
                                                    password_confirmation="password"))))
  pp.pprint(resp.data)
  pp.pprint(resp.status)
  assert resp.status == 200
  participant_map[participant] = resp.data.id



print(participant_map)

images=df['MediaName'].unique()
trial_map={}
for idx, image in enumerate(list(images)):
  trial_map[image] = idx


  new_trial_definition = dict(trial_definition=dict(definition_data="foo"))
  #resp = client.request(elicit['addTrialDefinition'](trial_definition=new_trial_definition,
  #                                                   study_definition_id=new_study.id,
  #                                                   protocol_definition_id=new_protocol_definition.id,
  #                                                   phase_definition_id=new_phase_definition.id))
  #assert resp.status == 201

  #new_trial_definition = resp.data
  #print("\n\nCreated new trial definition:\n")
  #pp.pprint(new_trial_definition)
  #trials.append(new_trial_definition)
  #trial_map[image] = new_trial_definition.id

  component_definition={
    "Component": {
      "Inputs": {
        "Instrument": null,
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
  print("\n\nCreated new phase component:\n")
  assert resp.status == 201

  new_component = resp.data

  pp.pprint(new_component)


#
# Create StudyResults structures
#


# Generate Trials based on MediaNames

start_end_events=df.loc[df['StudioEvent'].isin(['ImageStart', 'ImageEnd'])]

for user in df['ParticipantName'].unique():
  print(user + ":")
  user_events=start_end_events.loc[(start_end_events['ParticipantName'] == user)]
  for k,v in trial_map.items():
    print("\t%s"%k)
    se=user_events.loc[(user_events['MediaName'] == k)][['StudioEvent', 'LocalTime']]
    trial_start = list(se.loc[se['StudioEvent'] == 'ImageStart']['LocalTime'])[0]
    trial_end = list(se.loc[se['StudioEvent'] == 'ImageEnd']['LocalTime'])[0]

    # Generate trial results

#   and (df['StudioEvent'] == 'ImageStart') and df['StudioEvent'] == 'ImageStart'] and df['MediaName'] == k

#for user in df['ParticipantName'].unique():
#  print(user + ":")
#  df.loc[df['ParticipantName'] == user].to_csv(user + ".tsv", sep='\t')

#print(json.dumps( {k: v for v, k in enumerate(list(df))} , indent=4))


#
# Upload TimeSeries
#

