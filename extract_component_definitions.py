import xml.etree.cElementTree as ET
import json
from collections import defaultdict
import pprint
from pyswagger import App, Security
from pyswagger.contrib.client.requests import Client
from pyswagger.utils import jp_compose
import sys
import os
import argparse
from subprocess import call
import re
import pdprint

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
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.items()}}
        pp.pprint(t)
        print("\n==\n")
        pp.pprint(d)
        print("\n\n\n")
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


# h/t: https://stackoverflow.com/questions/60208/replacements-for-switch-statement-in-python
class ComponentParser:
    def lookupMethod(self, command):
        return getattr(self, 'do_' + command.upper(), None) or getattr(self, "do_default")
    def unknown(self, element):
        raise NotImplementedError("don't know how to parse %s" % element.tag)
    def do_default(self, element):
      d = etree_to_dict(element)
      if "Inputs" in d[element.tag]:
        if isinstance(d[element.tag]["Inputs"], dict) and "Events" in d[element.tag]["Inputs"]:
          del d[element.tag]["Inputs"]["Events"] # we're not uploading the _results_ of experiments
      if isinstance(d[element.tag]["Inputs"], dict):
        for e in d[element.tag]["Inputs"]:
          elval = d[element.tag]["Inputs"][e]
          d[element.tag][e] = elval if elval else {}
        del d[element.tag]["Inputs"]
      if "@Version" in d[element.tag]:
        del d[element.tag]["@Version"]
      if "Outputs" in d[element.tag]:
        del d[element.tag]["Outputs"]
      if "Instrument" in d[element.tag] and isinstance(d[element.tag]["Instrument"], dict):
        if "Stimulus" in d[element.tag]["Instrument"]:
          if  isinstance(d[element.tag]["Instrument"]["Stimulus"], dict):
            d["Stimuli"] = [d[element.tag]["Instrument"]["Stimulus"]]
          del d[element.tag]["Instrument"]["Stimulus"]
        d["Instruments"] = [ { "Instrument": { element.tag: d[element.tag]["Instrument"] } } ]
        del d[element.tag]
      return d
    def do_HEADER(self, element):
      return self.do_default(element)
      for headerLabel in element.iterfind('Inputs/HeaderLabel'):
        print("HEADER %s"%headerLabel.text)
    def do_FREETEXT(self, element):
        return self.do_default(element)
    def do_MONITOR(self, element):
        return None


##
## MAIN
##

pp = pprint.PrettyPrinter(indent=4)


#
# Parse command line and load XML tree
#

parser = argparse.ArgumentParser(prog='extract_component_definitions.py')
parser.add_argument('file', type=str,  nargs='?', default='experiment_xml/freetexttest.xml', help='experiment.xml format filename')
args = parser.parse_args()

print("Loading %s"%args.file)
tree = ET.ElementTree(file=args.file)

root = tree.getroot() # experiment
root_tags = list(map(lambda x: x.tag, root))


trials = root[root_tags.index('Trials')]

c_num = 0
with open(os.path.basename(args.file)+".json", 'w') as fd:
  components = []
  trial_components = []
  json_components = []
  for trial in trials:
    #c = list(map(lambda component: ComponentParser().lookupMethod(component.tag)(component), trial))
    #components = components + c
    trial_component_list = []
    for component in trial:
      c = ComponentParser().lookupMethod(component.tag)(component)
      if c is None:
        continue
      components.append(c)
      trial_component_list.append(c)
      c_num = c_num + 1
      component_json_filename = "%s_c%d.json"%(os.path.basename(args.file), c_num)
      component_json_schema_filename = "%s_s%d.json"%(os.path.basename(args.file), c_num)
      with open(component_json_filename, 'w') as jsonfd:
        jsonfd.write(json.dumps(c))
#      os.system("json-schema-generator %s --schema-version draft4 > %s"%(component_json_filename, component_json_schema_filename))
      json_components = json_components + list(map(lambda d: json.dumps(d, indent=2), c))
    trial_components.append(trial_component_list)
  with open(os.path.basename(args.file)+".py", 'w') as pyfd:
    trial_component_refs = []
    for trial_idx, trial_component in enumerate(trial_components):
      trial_component_ref = ("trial_components_%d"%trial_idx)
      trial_component_refs.append(trial_component_ref)
      component_refs = []
      for component_idx, component in enumerate(trial_component):
        component_ref = ("component_%d_%d"%(trial_idx, component_idx))
        component_refs.append(component_ref)
        pyfd.write("\n# Trial %d, component: %d\n"%(trial_idx, component_idx))
        pyfd.write("\n\n")
        pyfd.write("%s="%component_ref)
        c = pdprint.pformat(component, indent=2)
        pyfd.write(c)
        pyfd.write("\n\n")
      pyfd.write("%s=[ %s]"%(trial_component_ref , ", ".join(component_refs)))
      pyfd.write("\n\n")
    pyfd.write("\n# Trials %d\n"%(trial_idx))
    pyfd.write("trial_components=[ %s]"%(", ".join(trial_component_refs)))
    pyfd.write("\n\n")
  fd.write("[\n" + ",".join(json_components) + "\n]\n")


