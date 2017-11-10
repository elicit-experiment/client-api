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

examples_default.parser.add_argument('--study_id', type=int,  required=True)

args = examples_default.parse_command_line_args()
elicit = pyelicit.Elicit(pyelicit.ElicitCreds(), args.apiurl, examples_default.send_opt)

#
# Login admin user to get study results
#
client = elicit.login()

user = examples_default.assert_admin(client, elicit)

#
# Delete Study Definitions
#

resp = client.request(elicit['deleteStudyDefinition'](id=args.study_id))
assert resp.status == 204

