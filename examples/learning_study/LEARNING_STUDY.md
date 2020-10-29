

# Video Learning Study

### Create the Study

```bash
# local server
PYTHONPATH=`pwd` pipenv run python3 learning_study/build_study.py --env local

# local server on Docker
PYTHONPATH=`pwd` pipenv run python3 examples/learning_study/build_study.py --env local_docker --ignore_https true

# production server
PYTHONPATH=`pwd` pipenv run python3 examples/learning_study/build_study.py --env prod
```

### Dump Results

```bash
PYTHONPATH=`pwd` pipenv run python3 learning_study/analysis.py
PYTHONPATH=`pwd` pipenv run python3 learning_study/dump_results.py --study_id 1
PYTHONPATH=`pwd` pipenv run python3 dump_results.py --study_id 1
PYTHONPATH=`pwd` pipenv run python3 dump_results.py --study_id 9 --user_id 6
PYTHONPATH=`pwd` pipenv run python3 dump_results.py --study_id 1 --user_id 1 --env local
PYTHONPATH=`pwd` pipenv run python3 dump_results.py --study_id 1 --user_id 5 --env local_docker --ignore_https
```

```bash
PYTHONPATH=`pwd` pipenv run python3 learning_study/dump_results.py --study_id 3 --env local
```



