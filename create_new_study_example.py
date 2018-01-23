"""
Example for dumping the results of a study.
"""

import pprint
import pdprint

import sys
import json
import pyelicit
import lorem
import re

import examples_default
from example_helpers import *

##
## MAIN
##

pp = pprint.PrettyPrinter(indent=4)

examples_default.parser.add_argument('--active',
                                     default=False,
                                     help="The study is active and visible to participants.")
examples_default.parser.add_argument(
    'file', type=str,  nargs='?', default='likertscaletest.xml.py', help='python trial format filename')
examples_default.parser.add_argument(
    '--outfile', type=str,  nargs='?', default='likertscaletest.xml.full.py', help='python trial format filename')
script_args = examples_default.parse_command_line_args()
elicit = pyelicit.Elicit(pyelicit.ElicitCreds(), script_args.apiurl, examples_default.send_opt)

fullfd = open(script_args.outfile, "w")

def out_obj(obj, var_name):
  fullfd.write("%s="%var_name)
  fullfd.write(re.sub(r"'json.dumps\((.+)\)'","json.dumps(\\1)",pdprint.pformat(obj, indent=2)))
  fullfd.write("\n\n")

def add_obj(op, args):
    return add_object(client, elicit, op, args)

#
# Load trial definitions
#

with open(script_args.file, 'r') as tdfd:
  lines = tdfd.readlines()
  td = "\n".join(lines)
  fullfd.write("".join(lines))
  exec(td)

#
# Login admin user to get study results
#
client = elicit.login()

for cd in trial_components:
  pp.pprint(cd)

#
# Double-check that we have the right user
#

user = examples_default.assert_admin(client, elicit)

#
# Get list of users who will use the study
#

resp = client.request(elicit['findUsers']())

assert resp.status == 200

study_participants = list(filter(lambda x: x.role == 'registered_user', resp.data))

#
# Add a new Study Definition
#
study_definition = dict(title='Newly created from Python: create_study_example.py',
                        description='Fun study created with Python ' + lorem.paragraph(),
                        version=1,
                        lock_question=1,
                        enable_previous=1,
                        footer_label="This is the footer of the study",
                        redirect_close_on_url=elicit.api_url+"/participant",
                        data="Put some data here, we don't really care about it.",
                        principal_investigator_user_id=user.id)
args = dict(study=dict(study_definition=study_definition))
new_study = add_obj("addStudy", args)
out_obj(args, "study_definition")



#
# Add a new Protocol Definition
#

new_protocol_definition = dict(name='Newly created protocol definition from Python',
                               definition_data="foo",
                               summary=lorem.sentence(),
                               description=lorem.paragraph(),
                               active=script_args.active)
args = dict(protocol_definition=dict(protocol_definition=new_protocol_definition),
            study_definition_id=new_study.id)
new_protocol = add_obj("addProtocolDefinition", args)
out_obj(args, "protocol_definition")


#
# Add users to protocol
#

add_users_to_protocol(client, elicit, new_study, new_protocol, study_participants)


# generate two phases for example
phase_definitions = []
for phase_idx in range(2):
      #
      # Add a new Phase Definition
      #

      new_phase_definition = dict(phase_definition=dict(definition_data="foo"))
      args = dict(phase_definition=new_phase_definition,
                  study_definition_id=new_study.id,
                  protocol_definition_id=new_protocol.id)

      new_phase = add_obj("addPhaseDefinition", args)
      out_obj(args, ("phase_definition_%d"%phase_idx))
      phase_definitions = [new_phase]

      trials = []

      # generate two trials for example
      for trial_idx in range(len(trial_components)):
            #
            # Add a new Trial Definition
            #

            new_trial_definition = dict(trial_definition=dict(definition_data="foo"))
            args = dict(trial_definition=new_trial_definition,
                        study_definition_id=new_study.id,
                        protocol_definition_id=new_protocol.id,
                        phase_definition_id=new_phase.id)
            new_trial_definition=add_obj("addTrialDefinition", args)
            trials.append(new_trial_definition)
            out_obj(args, ("trial_definition_%d"%phase_idx))

            #
            # Add a new Component
            #

            for idx, component_definition in enumerate(trial_components[trial_idx]):

                  new_component = dict(name='Newly created component definition from Python',
                                       definition_data=json.dumps(component_definition))
                  args=dict(component = dict(component = new_component),
                            study_definition_id = new_study.id,
                            protocol_definition_id = new_protocol.id,
                            phase_definition_id = new_phase.id,
                            trial_definition_id = new_trial_definition.id)
                  ex_args = args
                  args['component']['component']['definition_data'] = ("json.dumps(trial_components[%d][%d])"%(trial_idx, idx))
                  new_component=add_obj("addComponent", args)
                  new_component.definition_data = ("json.dumps(trial_components[%d][%d])"%(trial_idx, idx))
                  out_obj(args, ("component_%d"%new_phase.id))


      #
      # Add a new Trial Order
      #

      new_trial_order = dict(trial_order=dict(sequence_data=",".join([str(trial.id) for trial in trials]),
                                              user_id=study_participants[0].id))
      args=dict(trial_order=new_trial_order,
                study_definition_id=new_study.id,
                protocol_definition_id=new_protocol.id,
                phase_definition_id=new_phase.id)
      new_trial_order=add_obj("addTrialOrder", args)
      out_obj(args, ("trial_order_%d"%phase_idx))


#
# Add a new Phase Order
#

phase_sequence_data = ",".join(
    [str(phase_definition.id) for phase_definition in phase_definitions]),
new_phase_order = dict(phase_order=dict(sequence_data=phase_sequence_data,
                                        user_id=user.id))
args = dict(phase_order=new_phase_order,
          study_definition_id=new_study.id,
          protocol_definition_id=new_protocol.id)
new_phase_order = add_obj("addPhaseOrder", args)
out_obj(args, ("phase_order_%s"%new_protocol.id))





