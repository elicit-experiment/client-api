import xml.etree.cElementTree as ET
import json
from collections import defaultdict
import pprint
from pyswagger import App, Security
from pyswagger.contrib.client.requests import Client
from pyswagger.utils import jp_compose
import sys
import lorem
import pyelicit
# usage:
# find . -iname "*.xml" -exec python from_experiment_xml.py {} \;


##
## UTILITIES
##

# https://stackoverflow.com/questions/7684333/converting-xml-to-dictionary-using-elementtree
def etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.iteritems():
                dd[k].append(v)
        d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.iteritems()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.iteritems())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
              d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d


# h/t: https://stackoverflow.com/questions/60208/replacements-for-switch-statement-in-python
class ComponentParser:
    def lookupMethod(self, command):
        return getattr(self, 'do_' + command.upper(), None) or getattr(self, "do_default")
    def unknown(self, element):
        raise NotImplementedError, ("don't know how to parser %s" % element.tag)
    def do_default(self, element):
      d = etree_to_dict(element)
      if "Inputs" in d[element.tag]:
        if isinstance(d[element.tag]["Inputs"], dict) and "Events" in d[element.tag]["Inputs"]:
          del d[element.tag]["Inputs"]["Events"] # we're not uploading the _results_ of experiments
      if "@Version" in d[element.tag]:
        del d[element.tag]["@Version"]
      pp.pprint(d)
      data = json.dumps(d)
      return data
    def do_HEADER(self, element):
      return self.do_default(element)
      for headerLabel in element.iterfind('Inputs/HeaderLabel'):
        print("HEADER %s"%headerLabel.text)
      print element
    def do_FREETEXT(self, element):
        return self.do_default(element)


##
## MAIN
##

pp = pprint.PrettyPrinter(indent=4)

api_url = 'https://elicit.docker.local'
elicit = pyelicit.Elicit(pyelicit.ElicitCreds(), api_url)

#
# Parse command line and load XML tree
#

if len(sys.argv) >= 2:
  file = sys.argv[1]
else:
  file = 'freetexttest.xml'


tree = ET.ElementTree(file=file)

root = tree.getroot() # experiment
root_tags = list(map(lambda x: x.tag, root))


#
# Login admin user to create study
#
client = elicit.login()

#
# Double-check that we have the right user
#
resp = client.request(elicit['getCurrentUser']())

assert resp.status == 200

print("Current User:")
pp.pprint(resp.data)

user = resp.data

assert(resp.data.role == 'admin') # must be admin!

#
# Get list of users who will use the study
#

resp = client.request(elicit['findUsers']())

assert resp.status == 200

registered_users = list(filter(lambda x: x.role == 'registered_user', resp.data))

#
# Create Study
#
title = root[root_tags.index('Name')].text
description = root[root_tags.index('ExperimentDescription')].text
study_definition = dict(title=title,
                        description=description,
                        version=root[root_tags.index('Version')].text,
                        lock_question=root[root_tags.index('LockQuestion')].text,
                        enable_previous=root[root_tags.index('EnablePrevious')].text,
                        no_of_trials=root[root_tags.index('NoOfTrials')].text,
                        footer_label=root[root_tags.index('FooterLabel')].text,
                        redirect_close_on_url=api_url+"/participant",#root[root_tags.index('RedirectOnCloseUrl')].text,
                        data=root[root_tags.index('Id')].text,
                        principal_investigator_user_id=user.id)

new_study = dict(study_definition=study_definition)
resp = client.request(elicit['addStudy'](study=new_study))

if resp.status != 201:
  print("Failed to create study!")
  pp.pprint(resp.data)
assert resp.status == 201

new_study = resp.data

#
# Add a new Protocol Definition
#

new_protocol_definition = dict(protocol_definition=dict(name=title,
                                                        summary=title,
                                                        description=description + lorem.paragraph(),
                                                        definition_data="foo"))
resp = client.request(elicit['addProtocolDefinition'](
                                                      protocol_definition=new_protocol_definition,
                                                      study_definition_id=new_study.id))

assert resp.status == 201

new_protocol_definition = resp.data

print(new_protocol_definition)

#
# Add user to protocol
#

for user in registered_users:
  pp.pprint(user)
  protocol_user = dict(protocol_user=dict(user_id=user.id,
                                          study_definition_id=new_study.id,
                                          protocol_definition_id=new_protocol_definition.id))
  resp = client.request(elicit['addProtocolUser'](
                                                  protocol_user=protocol_user,
                                                  study_definition_id=new_study.id,
                                                  protocol_definition_id=new_protocol_definition.id))

  assert resp.status == 201

#
# Add a new Phase Definition
#

new_phase_definition = dict(phase_definition=dict(definition_data="foo"))
resp = client.request(elicit['addPhaseDefinition'](
                                                   phase_definition=new_phase_definition,
                                                   study_definition_id=new_study.id,
                                                   protocol_definition_id=new_protocol_definition.id))

assert resp.status == 201

new_phase_definition = resp.data

#
# Add a new Phase Order
#

new_phase_order = dict(phase_order=dict(sequence_data="0",
                                        user_id=user.id))
resp = client.request(elicit['addPhaseOrder'](
                                              phase_order=new_phase_order,
                                              study_definition_id=new_study.id,
                                              protocol_definition_id=new_protocol_definition.id))

assert resp.status == 201

new_phase_order = resp.data

trials = root[root_tags.index('Trials')]

for trial in trials:
  #
  # Add a new Trial Definition
  #

  new_trial_definition = dict(trial_definition=dict(definition_data="I DON't KNOW WHAT WILL GO HERE"))
  resp = client.request(elicit['addTrialDefinition'](
                                                     trial_definition=new_trial_definition,
                                                     study_definition_id=new_study.id,
                                                     protocol_definition_id=new_protocol_definition.id,
                                                     phase_definition_id=new_phase_definition.id))

  assert resp.status == 201

  new_trial_definition = resp.data

  for component in trial:
    print(component.tag)
    component_data = ComponentParser().lookupMethod(component.tag)(component)

    #
    # Add a new Component
    #

    new_component = dict(component=dict(definition_data=component_data))
    resp = client.request(elicit['addComponent'](
                                                 component=new_component,
                                                 study_definition_id=new_study.id,
                                                 protocol_definition_id=new_protocol_definition.id,
                                                 phase_definition_id=new_phase_definition.id,
                                                 trial_definition_id=new_trial_definition.id))

    assert resp.status == 201

    new_component = resp.data

    #print(new_component)

#
# Add a new Trial Order
#

new_trial_order = dict(trial_order=dict(sequence_data=",".join([str(x) for x in range(len(trials))]),
                                        user_id=user.id))
resp = client.request(elicit['addTrialOrder'](
                                              trial_order=new_trial_order,
                                              study_definition_id=new_study.id,
                                              protocol_definition_id=new_protocol_definition.id,
                                              phase_definition_id=new_phase_definition.id))

assert resp.status == 201

new_trial_order = resp.data


