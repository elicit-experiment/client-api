from pyelicit import elicit
from collections import namedtuple

def Struct(**kwargs):
    return namedtuple('Struct', ' '.join(kwargs.keys()))(**kwargs)

el = elicit.Elicit(Struct(apiurl='https://elicit.compute.dtu.dk',send_opt=dict(verify=True),debug=True))
client = el.client

user_id = 919
study_definition_id = 394
experiment_result_id = 711
study_result_id = 711
page_size = 10

el.find_trial_results(study_result_id=study_result_id, experiment_id=experiment_result_id, page_size=page_size)
