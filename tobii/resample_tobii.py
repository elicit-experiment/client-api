import csv
import json
import pandas as pd
import tobii_utils
from os.path import basename

colidx = tobii_utils.colidx

root = "/Users/iainbryson/Projects/DTUCogSci/"
tobiifile = root+'elicit/client-api/tobii/allMediaBPMDS_slice.tsv'
tobiifile = root+'/Physiological/allMediaBPMDS.tsv'
parse_dates = []
#parse_dates = {'LocalTime' : [colidx["RecordingDate"], colidx["LocalTimeStamp"]]}
#parse_dates = ['LocalTime']
dtypes = {
    'MouseEvent': str,
    'StudioEvent': str,
    'StudioEventData': str,
    'KeyPressEvent': str,
#    'RecordingDate': str,
#    'LocalTimeStamp': str
}
tobii_filename = basename(tobiifile)
df = pd.read_table(tobiifile, parse_dates=parse_dates, dtype=dtypes)
#df.dropna(axis=1, how='all')

#print(df.loc[df['StudioEvent'].isin(['ImageStart', 'ImageEnd'])][['StudioEvent', 'ParticipantName', 'MediaName', 'LocalTime']].sort_values('LocalTime'))

markers = df.loc[df['StudioEvent'].isin(['ImageStart', 'ImageEnd'])]

data = df.loc[~df['StudioEvent'].isin(['ImageStart', 'ImageEnd'])][::10]

resample = df.loc[(df.index % 100 == 0) & ~df['StudioEvent'].isin(['ImageStart', 'ImageEnd']) | df['StudioEvent'].isin(['ImageStart', 'ImageEnd'])]

rmarkers = resample.loc[resample['StudioEvent'].isin(['ImageStart', 'ImageEnd'])]

resample.to_csv("tobii_resample.tsv", sep='\t', index=False)

