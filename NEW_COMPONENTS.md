# Creating New Definitions for Components

```bash
PYTHONPATH=`pwd` pipenv run python3 extract_component_definitions.py --output_folder new_components_test --file experiment_xml/freetexttest.xml
PYTHONPATH=`pwd` pipenv run python3 extract_component_definitions.py --output_folder new_components_test --file experiment_xml/checkboxgrouptest.xml
```

```
PYTHONPATH=`pwd` pipenv run python3 extract_component_definitions.py --output_folder new_components_experiments --file cockpit_test_experiments/experiment.xml
PYTHONPATH=`pwd` pipenv run python3 extract_component_definitions.py --output_folder new_components_experiments --file cockpit_test_experiments/experiment2.xml
PYTHONPATH=`pwd` pipenv run python3 extract_component_definitions.py --output_folder new_components_experiments --file cockpit_test_experiments/dtu_emotion_likert_001_e3cc09b6-f3ee-af3c-0001-000000000001.xml
```




This will generate the new component structures -- including the `.py` Python code -- for the given input XML.  In this case we're creating the freetext question.

You can then create a study based on these with:

```bash
PYTHONPATH=`pwd` pipenv run python3 create_new_component_study.py --env local --trial_definitions_file new_components_test/freetexttest.xml.py
PYTHONPATH=`pwd` pipenv run python3 create_new_component_study.py --env local --trial_definitions_file new_components_test/checkboxgrouptest.xml.py
```

PYTHONPATH=`pwd` pipenv run python3 create_new_component_study.py --env local --trial_definitions_file new_components_experiments/experiment/__init__.py
PYTHONPATH=`pwd` pipenv run python3 create_new_component_study.py --env local --trial_definitions_file new_components_experiments/experiment2/__init__.py

PYTHONPATH=`pwd` pipenv run python3 create_new_component_study.py --env local --trial_definitions_file new_components_experiments/dtu_emotion_likert_001_e3cc09b6-f3ee-af3c-0001-000000000001/__init__.py
cockpit_test_experiments/dtu_emotion_likert_001_e3cc09b6-f3ee-af3c-0001-000000000001.xml