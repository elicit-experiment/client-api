import xml.etree.cElementTree as ET
import json
from collections import defaultdict
import pprint
from pyswagger import App, Security
from pyswagger.contrib.client.requests import Client
from pyswagger.utils import jp_compose
import sys

# usage:
# find . -iname "*.xml" -exec python from_experiment_xml.py {} \;

pp = pprint.PrettyPrinter(indent=4)

public_client_id = 'admin_public'
public_client_secret = 'czZCaGRSa3F0MzpnWDFmQmF0M2JW'

# load Swagger resource file into App object
app = App._create_('http://localhost:3000/apidocs/v1/swagger.json')

auth = Security(app)
#auth.update_with('api_key', 'admin_public') # api key
#auth.update_with('petstore_auth', 'czZCaGRSa3F0MzpnWDFmQmF0M2JW') # oauth2

# init swagger client
client = Client(auth)

# a request to create a new pet
auth_request=dict(client_id=public_client_id,
                  client_secret=public_client_secret,
                  grant_type='password',
                  email='foo5@bar.com',
                  password='abcd12_') 
print(auth_request)
# making a request
resp = client.request(app.op['getAuthToken'](auth_request=auth_request))

assert resp.status == 200


#
# Add access token 
#

access_token = resp.data.access_token
auth = 'Bearer ' + access_token
client._Client__s.headers['Authorization'] = auth



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


if len(sys.argv) >= 2:
  file = sys.argv[1]
else:
  file = 'freetexttest.xml'

tree = ET.ElementTree(file=file)

root = tree.getroot() # experiment
root_tags = list(map(lambda x: x.tag, root))

study_definition = dict(title=root[root_tags.index('Name')].text,
                        description=root[root_tags.index('ExperimentDescription')].text,
                        version=root[root_tags.index('Version')].text,
                        lock_question=root[root_tags.index('LockQuestion')].text,
                        enable_previous=root[root_tags.index('EnablePrevious')].text,
                        no_of_trials=root[root_tags.index('NoOfTrials')].text,
                        footer_label=root[root_tags.index('FooterLabel')].text,
                        redirect_close_on_url=root[root_tags.index('RedirectOnCloseUrl')].text,
                        data=root[root_tags.index('Id')].text,
                        principal_investigator_user_id=0)

new_study = dict(study_definition=study_definition)
resp = client.request(app.op['addStudy'](authorization=auth, study=new_study))

assert resp.status == 201

new_study = resp.data

print(new_study)

#
# Add a new Protocol Definition
#

new_protocol_definition = dict(protocol_definition=dict(name='Newly created protocol definition from Python', definition_data="foo"))
resp = client.request(app.op['addProtocolDefinition'](authorization=auth, protocol_definition=new_protocol_definition, study_definition_id=new_study.id))

assert resp.status == 201

new_protocol_definition = resp.data

print(new_protocol_definition)

#
# Add a new Phase Definition
#

new_phase_definition = dict(phase_definition=dict(name='Newly created phase definition from Python', definition_data="foo"))
resp = client.request(app.op['addPhaseDefinition'](authorization=auth, phase_definition=new_phase_definition, study_definition_id=new_study.id, protocol_definition_id=new_protocol_definition.id))

assert resp.status == 201

new_phase_definition = resp.data

print(new_phase_definition)

#
# Add a new Phase Order
#

new_phase_order = dict(phase_order=dict(name='Newly created phase order from Python', sequence_data="0", user_id=0))
resp = client.request(app.op['addPhaseOrder'](authorization=auth, phase_order=new_phase_order, study_definition_id=new_study.id, protocol_definition_id=new_protocol_definition.id))

assert resp.status == 201

new_phase_order = resp.data

print(new_phase_order)

trials = root[root_tags.index('Trials')]

for trial in trials:
  #
  # Add a new Trial Definition
  #

  new_trial_definition = dict(trial_definition=dict(name='Newly created trial definition from Python', definition_data="foo"))
  resp = client.request(app.op['addTrialDefinition'](authorization=auth, trial_definition=new_trial_definition, study_definition_id=new_study.id, protocol_definition_id=new_protocol_definition.id, phase_definition_id=new_phase_definition.id))

  assert resp.status == 201

  new_trial_definition = resp.data

  for component in trial:
    print(component.tag)
    component_data = ComponentParser().lookupMethod(component.tag)(component)

    #
    # Add a new Component
    #

    new_component = dict(component=dict(name='Newly created component definition from Python', definition_data=component_data))
    resp = client.request(app.op['addComponent'](authorization=auth, component=new_component, study_definition_id=new_study.id, protocol_definition_id=new_protocol_definition.id, phase_definition_id=new_phase_definition.id, trial_definition_id=new_trial_definition.id))

    assert resp.status == 201

    new_component = resp.data

    print(new_component)

#
# Add a new Trial Order
#

new_trial_order = dict(trial_order=dict(name='Newly created trial order from Python', sequence_data=",".join([str(x) for x in range(len(trials))]), user_id="0"))
resp = client.request(app.op['addTrialOrder'](authorization=auth, trial_order=new_trial_order, study_definition_id=new_study.id, protocol_definition_id=new_protocol_definition.id, phase_definition_id=new_phase_definition.id))

assert resp.status == 201

new_trial_order = resp.data

print(new_trial_order)


