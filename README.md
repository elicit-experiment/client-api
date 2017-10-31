
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