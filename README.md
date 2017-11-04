
# Elicit Client

This is the client API access code for Elicit.  It lets you write (Python) code to create experiments.

## Setup

```
sudo pip install pyswagger
sudo pip install requests
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
python dump_results.py
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

