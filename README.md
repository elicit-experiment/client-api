
# Elicit Client

This is the client API access code for Elicit.  It lets you write (Python) code to create experiments.

## Setup

```
sudo pip install pyswagger
sudo pip install requests
sudp pip install requests_toolbelt
```

## Examples

### Load an Experiment from `Experiment.xml`

```
python from_experiment_xml.py <experiment.xml>
```

Or, alternatively, load a while directory full of `experiment.xml`s:

```
find . -iname "*.xml" -exec python from_experiment_xml.py {} \;
```

### Dump Experiment Results

You can dump experiment results via:

```
python3 dump_results.py --env local --study_id 3 --user_name subject1
```

### Create an Experiment

You can create a simple experiment via:

```
python create_study_example.py
```

### Find out which Protocols a User May Take

Find out which studies a user is eligeable for with:

```
python dump_participation.py
```

### List all the users in the System


```
python list_users.py
```


# Time Series


## Examples Using `curl`


Get user token:

```
curl 'http://localhost:3000/api/v1/oauth/token' -H 'Pragma: no-cache' -H 'Origin: http://localhost:3000' -H 'Accept-Encoding: gzip, deflate, br' -H 'Accept-Language: en-US,en;q=0.9,fr;q=0.8' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36' -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'Cache-Control: no-cache' -H 'Referer: http://localhost:3000/login' -H 'Connection: keep-alive' --data-binary '{"client_id":"admin_public","client_secret":"czZCaGRSa3F0MzpnWDFmQmF0M2JW","grant_type":"password","email":"admin@elicit.dk","password":"password"}' --compressed

```

Post the Tobii file as a `TimeSeries`:

```
curl  \
 -F "time_series[file]=@./tobii/allMediaBPMDS_slice.tsv;type=text/tab-separated-values" \
 -F "time_series[study_definition_id]=49" \
 -F "time_series[protocol_definition_id]=49" \
 -F "time_series[phase_definition_id]=49" \
 -F "time_series[schema]=tobii_tsv" \
 -F "time_series[schema_metadata]={'time_field': 'LocalTime', 'user_field': 'ParticipantName'}" \
localhost:3000/api/v1/study_results/time_series \
 -H 'Accept-Encoding: gzip, deflate, br' \
 -H 'Accept: text/tab-separated-values' \
 -H 'Authorization: Bearer 9aa479382e46ced8fc90b9f233d53d665236c53ba0cad8d9fc2a04ce19500ed1' 
```


Post the Tobii file as a `TimeSeries` gzip'ed:

```
curl  \
 -F "time_series[file]=@./tobii/allMediaBPMDS_slice.tsv.gz;type=text/tab-separated-values+gzip" \
 -F "time_series[stage_id]=1" \
localhost:3000/api/v1/study_results/1/time_series \
 -H 'Accept-Encoding: gzip, deflate, br' \
 -H 'Accept: text/tab-separated-values' \
 -H 'Authorization: Bearer 2b3918fbde187e3948fdcc8e78695e80237bb1490d1ba3e69e530d9d131477a3' 
```

## Examples using the Python scripts

Parse the Tobii file, create the StudyDefinition and StudyResults and post the Tobii file, then query it:

```
python3 parse_tobii.py
```

##
python3 extract_component_definitions.py experiment_xml/likertscaletest.xml 

for f in likertscaletest.xml_c*; do (cat "${f}"; echo) >> x.jsonl; done
skinfer --jsonlines x.json



