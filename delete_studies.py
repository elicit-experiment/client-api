"""
Example for deleting all study definitions belonging to a given user.
"""

import pprint
import sys
import pyelicit

import examples_default

##
## MAIN
##

pp = pprint.PrettyPrinter(indent=4)

args = examples_default.parse_command_line_args()
elicit = pyelicit.Elicit(pyelicit.ElicitCreds(), args.apiurl, examples_default.send_opt)

#
# Login admin user to get study results
#
client = elicit.login()

#
# Double-check that we have the right user
#


#
# Get the list of Study Definitions
#

resp = client.request(elicit['findStudyDefinitions']())

assert resp.status == 200

my_studies = list(filter(lambda x: x.principal_investigator_user_id == user.id, resp.data))
print("\n\nList of my studies:\n")
pp.pprint(my_studies)

#
# Delete Study Definitions
#

for study_def in my_studies:
  resp = client.request(elicit['deleteStudyDefinition'](id=study_def.id))
  assert resp.status == 204

