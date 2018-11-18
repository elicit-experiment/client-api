# New Component Definitions

```bash
pipenv install
```

```
python3 extract_component_definitions.py experiment_xml/likertscaletest.xml
```

Generates `likertscaletest.xml.py`, Python code to create component definitions for the Likert scale.

```
python3 create_new_study_example.py --env local --outfile likertscaletest.xml.full.py likertscaletest.xml.py

pipenv run python3 create_new_study_example.py --env local --outfile likertscaletest.xml.full.py likertscaletest.xml.py
```


```bash
pipenv run python3 create_new_study_example2.py --env local
```

