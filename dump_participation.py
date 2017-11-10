"""
Example for dumping the protocols a given user is eligeable to take.
"""
import pprint
import sys
import pyelicit

import examples_default

pp = pprint.PrettyPrinter(indent=4)

#
# Login registered user to get study eligeability
#
args = examples_default.parse_command_line_args()
elicit = pyelicit.Elicit(pyelicit.ElicitCreds('subject1@elicit.dk', 'abcd12_'), args.apiurl, examples_default.send_opt)

client = elicit.login()

resp = client.request(elicit['findEligeableProtocols']())

assert resp.status == 200

pp.pprint(resp.data)

