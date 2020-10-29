"""
Example for dumping the results of a study.
"""

import pprint
#import pdprint

from examples_base import *
from pyelicit import elicit

##
## MAIN
##

pp = pprint.PrettyPrinter(indent=4)

parser.add_argument('--trial_definitions_file',
                    type=str,
                    nargs='?',
                    default='new_components_test/freetexttest.xml.py',
                    help='Trial definitions Python code (from extract_component_definitions.py)')
args = parse_command_line_args()

el = elicit.Elicit(args)

#
# Load trial definitions
#
trial_definitions_file = args.trial_definitions_file
trial_components = elicit.load_trial_definitions(trial_definitions_file)

study_title = args.trial_definitions_file.replace('/__init__.py', '').replace('.py', '').replace('.xml', '').replace('/', ' ').replace('_', ' ')
#
# Double-check that we have the right user: we need to be admin to create a study
#

user = el.assert_admin()

#
# Get list of users who will use the study
#
NUM_AUTO_CREATED_USERS=10
NUM_ANONYMOUS_USERS=5
NUM_REGISTERED_USERS=0
study_participants = el.ensure_users(NUM_REGISTERED_USERS, NUM_ANONYMOUS_USERS)

pp.pprint(study_participants)
pp.pprint(user)

#
# Add a new Study Definition
#
study_definition = dict(title=("New Component test study: %s"%study_title),
                        description='',
                        version=1,
                        lock_question=1,
                        enable_previous=1,
                        allow_anonymous_users=(NUM_AUTO_CREATED_USERS>0 or NUM_ANONYMOUS_USERS>0),  # allow taking the study without login
                        show_in_study_list=True,  # show in the (public) study list for anonymous protocols
                        max_auto_created_users=NUM_AUTO_CREATED_USERS, # up to ten workerId created users
                        max_concurrent_users=1, # NYI
                        footer_label="This is the footer of the study",
                        redirect_close_on_url=el.elicit_api.api_url+"/participant",
                        data="Put some custom data here.",
                        principal_investigator_user_id=str(user.id))
new_study = el.add_study(study=dict(study_definition=study_definition))

#
# Add a new Protocol Definition
#

new_protocol_definition = dict(name="Protocol for %s"%study_title,
                               definition_data="whatever you want here",
                               summary="Video Learning",
                               description="From %s"%trial_definitions_file,
                               active=True)
new_protocol = el.add_protocol_definition(protocol_definition=dict(protocol_definition=new_protocol_definition),
                                          study_definition_id=new_study.id)


#
# Add users to protocol
#

el.add_users_to_protocol(new_study, new_protocol, study_participants)


#
# Add a new Phase Definition
#

new_phase_definition = dict(phase_definition=dict(definition_data="foo"))

new_phase = el.add_phase_definition(phase_definition=new_phase_definition,
                                  study_definition_id=new_study.id,
                                  protocol_definition_id=new_protocol.id)
phase_definitions = [new_phase]

trials = []

# generate two trials for example
for trial_idx in range(len(trial_components)):
    #
    # Add a new Trial Definition
    #

    new_trial_definition_config = dict(trial_definition=dict(definition_data=dict()))
    new_trial_definition = el.add_trial_definition(trial_definition=new_trial_definition_config,
                                                   study_definition_id=new_study.id,
                                                   protocol_definition_id=new_protocol.id,
                                                   phase_definition_id=new_phase.id)
    trials.append(new_trial_definition)

    #
    # Add a new Component
    #

    for idx, component_definition in enumerate(trial_components[trial_idx]):
        new_component_config = dict(name='',
                                    definition_data=component_definition)
        new_component = el.add_component(component=dict(component=new_component_config),
                                         study_definition_id=new_study.id,
                                         protocol_definition_id=new_protocol.id,
                                         phase_definition_id=new_phase.id,
                                         trial_definition_id=new_trial_definition.id)

#
# Add a new Trial Orders
#

def make_fixed_trial_orders():
    for study_participant in study_participants:
      new_trial_order_config = dict(trial_order=dict(sequence_data=",".join([str(trial.id) for trial in trials]),
                                                     user_id=study_participant.id))
      new_trial_order = el.add_trial_order(trial_order=new_trial_order_config,
                                           study_definition_id=new_study.id,
                                           protocol_definition_id=new_protocol.id,
                                           phase_definition_id=new_phase.id)

def make_anonymous_trial_orders():
    for _ in study_participants:
      new_trial_order_config = dict(trial_order=dict(sequence_data=",".join([str(trial.id) for trial in trials])))
      new_trial_order = el.add_trial_order(trial_order=new_trial_order_config,
                                           study_definition_id=new_study.id,
                                           protocol_definition_id=new_protocol.id,
                                           phase_definition_id=new_phase.id)

make_anonymous_trial_orders()

#
# Add a new Phase Order
#

phase_sequence_data = ",".join(
  [str(phase_definition.id) for phase_definition in phase_definitions])
new_phase_order_config = dict(phase_order=dict(sequence_data=phase_sequence_data,
                                             user_id=user.id))
new_phase_order = el.add_phase_order(phase_order=new_phase_order_config,
                                   study_definition_id=new_study.id,
                                   protocol_definition_id=new_protocol.id)


