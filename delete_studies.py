"""
Example for deleting all study definitions belonging to a given user.
"""

import pprint
import sys
import pyelicit

##
## MAIN
##

pp = pprint.PrettyPrinter(indent=4)

elicit = pyelicit.Elicit(pyelicit.ElicitCreds(), "http://localhost:3000")
#elicit = pyelicit.Elicit()

#
# Login admin user to get study results
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

