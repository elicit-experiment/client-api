"""
Example for dumping the protocols a given user is eligeable to take.
"""
import pprint
import sys
import pyelicit

pp = pprint.PrettyPrinter(indent=4)

#
# Login registered user to get study eligeability
#
elicit = pyelicit.Elicit(pyelicit.ElicitCreds('subject1@elicit.dk', 'abcd12_'))

client = elicit.login()

resp = client.request(elicit['findEligeableProtocols']())

assert resp.status == 200

pp.pprint(resp.data)

