import xml.etree.cElementTree as ET
import json
from collections import defaultdict
import pprint
from pyswagger import App, Security
from pyswagger.contrib.client.requests import Client
from pyswagger.utils import jp_compose
import sys
import argparse

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
      data = json.dumps(d, indent=2)
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

for trial in trials:

  print("\n\nSLIDE\n\n")
  for component in trial:
    #print(component.tag)
    component_data = ComponentParser().lookupMethod(component.tag)(component)

    print(component_data)


