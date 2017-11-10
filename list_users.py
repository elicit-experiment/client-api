"""
Example for dumping the results of a study.
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
# Get the list of users
#

resp = client.request(elicit['findUsers']())

assert resp.status == 200
print("\n\nList of users:\n")
pp.pprint(resp.data)

registered_users = list(filter(lambda x: x.role == 'registered_user', resp.data))
print("\n\nList of registered_users (i.e. non-admins):\n")
pp.pprint(registered_users)