import xml.etree.cElementTree as ET
import json
from collections import defaultdict
import lorem
import pyelicit

from deprecated import examples_default
from deprecated.example_helpers import *

# usage:
# find experiment_xml -iname "*.xml" -exec python3 from_experiment_xml.py --env local {} \;
# find experiment_xml_errors -iname "*.xml" -exec python3
# from_experiment_xml.py --env local {} \;


##
# UTILITIES
##

# https://stackoverflow.com/questions/7684333/converting-xml-to-dictionary-using-elementtree
def etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
              d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d


# h/t:
# https://stackoverflow.com/questions/60208/replacements-for-switch-statement-in-python
class ComponentParser:

    def lookupMethod(self, command):
        return getattr(self, 'do_' + command.upper(), None) or getattr(self, "do_default")

    def unknown(self, element):
        raise NotImplementedError("don't know how to parser %s" % element.tag)

    def do_default(self, element):
      d = etree_to_dict(element)
      if "Inputs" in d[element.tag]:
        if isinstance(d[element.tag]["Inputs"], dict) and "Events" in d[element.tag]["Inputs"]:
          # we're not uploading the _results_ of experiments
          del d[element.tag]["Inputs"]["Events"]
      if "@Version" in d[element.tag]:
        del d[element.tag]["@Version"]
      pp.pprint(d)
      data = json.dumps(d)
      return data

    def do_HEADER(self, element):
      return self.do_default(element)
      for headerLabel in element.iterfind('Inputs/HeaderLabel'):
        print("HEADER %s" % headerLabel.text)

    def do_FREETEXT(self, element):
        return self.do_default(element)


##
# MAIN
##

pp = pprint.PrettyPrinter(indent=4)

examples_default.parser.add_argument(
    'file', type=str,  nargs='?', default='experiment_xml/freetexttest.xml', help='experiment.xml format filename')
examples_default.parser.add_argument(
    '--active', default=True, help="The study is active and visible to participants.")
args = examples_default.parse_command_line_args()
elicit = pyelicit.Elicit(pyelicit.ElicitCreds(),
                         args.apiurl, examples_default.send_opt)


def add_obj(op, args):
    return add_object(client, elicit, op, args)

#
# Parse command line and load XML tree
#
print("Loading %s" % args.file)

tree = ET.ElementTree(file=args.file)

root = tree.getroot()  # experiment
root_tags = list(map(lambda x: x.tag, root))


def get_tag_or_default(tag, default=None):
  if tag in root_tags:
    return root[root_tags.index(tag)].text
  else:
    return default

#
# Login admin user to create study
#
client = elicit.login()

#
# Double-check that we have the right user
#

user = examples_default.assert_admin(client, elicit)

#
# Get list of users who will use the study
#

resp = client.request(elicit['findUsers']())

assert resp.status == 200

registered_users = list(
    filter(lambda x: x.role == 'registered_user', resp.data))

#
# Create Study
#
title = root[root_tags.index('Name')].text
description = args.file + " : " + \
    get_tag_or_default('ExperimentDescription', 'No description provided')
study_definition = dict(title=title,
                        description=description,
                        version=get_tag_or_default('Version', '1'),
                        lock_question=get_tag_or_default('LockQuestion', '0'),
                        enable_previous=get_tag_or_default(
                            'EnablePrevious', '1'),
                        footer_label=get_tag_or_default(
                            'FooterLabel', "Footer " + lorem.sentence()),
                        # root[root_tags.index('RedirectOnCloseUrl')].text,
                        redirect_close_on_url=elicit.api_url+"/participant",
                        data=root[root_tags.index('Id')].text,
                        principal_investigator_user_id=user.id)
new_study = add_obj("addStudy",
                    dict(study=dict(study_definition=study_definition)))


#
# Add a new Protocol Definition
#
proto_desc = description + " : " + lorem.paragraph()
new_protocol_definition = dict(name=title,
                               summary=title,
                               description=proto_desc,
                               definition_data="foo",
                               active=args.active)
args = dict(protocol_definition=dict(protocol_definition=new_protocol_definition),
            study_definition_id=new_study.id)
new_protocol = add_obj("addProtocolDefinition", args)


#
# Add user to protocol
#

protocol_users = add_users_to_protocol(client,
                                       elicit,
                                       new_study,
                                       new_protocol,
                                       registered_users)

#
# Add a new Phase Definition
#

new_phase_definition = dict(phase_definition=dict(definition_data="foo"))
args = dict(phase_definition=new_phase_definition,
            study_definition_id=new_study.id,
            protocol_definition_id=new_protocol.id)

new_phase = add_obj("addPhaseDefinition", args)
phase_definitions = [new_phase]

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


trials = root[root_tags.index('Trials')]
trial_defs = []

for trial in trials:
  #
  # Add a new Trial Definition
  #

  new_trial_definition = dict(trial_definition=dict(
      definition_data="I DON't KNOW WHAT WILL GO HERE"))
  args = dict(trial_definition=new_trial_definition,
              study_definition_id=new_study.id,
              protocol_definition_id=new_protocol.id,
              phase_definition_id=new_phase.id)
  new_trial_definition=add_obj("addTrialDefinition", args)
  trial_defs.append(new_trial_definition)

  for component in trial:
    print(component.tag)
    component_data=ComponentParser().lookupMethod(component.tag)(component)

    #
    # Add a new Component
    #

    new_component=dict(name='Newly created component definition from Python',
                                        definition_data=component_data)
    args=dict(component = dict(component = new_component),
              study_definition_id = new_study.id,
              protocol_definition_id = new_protocol.id,
              phase_definition_id = new_phase.id,
              trial_definition_id = new_trial_definition.id)
    new_component=add_obj("addComponent", args)

    # print(new_component)

#
# Add a new Trial Order
#

trial_sequence_data=",".join([str(trial_definition.id)
                             for trial_definition in trial_defs])

new_trial_order=dict(trial_order = dict(sequence_data = trial_sequence_data,
                                        user_id = user.id))
args=dict(trial_order=new_trial_order,
          study_definition_id=new_study.id,
          protocol_definition_id=new_protocol.id,
          phase_definition_id=new_phase.id)
new_trial_order=add_obj("addTrialOrder", args)