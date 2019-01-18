# Creating New Definitions for Components

```bash
PYTHONPATH=`pwd` pipenv run python3 extract_component_definitions.py --output_folder new_components_test --file experiment_xml/freetexttest.xml
PYTHONPATH=`pwd` pipenv run python3 extract_component_definitions.py --output_folder new_components_test --file experiment_xml/checkboxgrouptest.xml
```

This will generate the new component structures -- including the `.py` Python code -- for the given input XML.  In this case we're creating the freetext question.

You can then create a study based on these with:

```bash
PYTHONPATH=`pwd` pipenv run python3 create_new_component_study.py --env local --trial_definitions_file new_components_test/freetexttest.xml.py
PYTHONPATH=`pwd` pipenv run python3 create_new_component_study.py --env local --trial_definitions_file new_components_test/checkboxgrouptest.xml.py
```