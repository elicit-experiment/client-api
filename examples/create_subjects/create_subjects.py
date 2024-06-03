"""
Example for dumping the results of a study.
"""

import pprint

from examples_base import *
from pyelicit import elicit
from pyelicit import api

##
## MAIN
##

pp = pprint.PrettyPrinter(indent=4)

args = parse_command_line_args()

el = elicit.Elicit(args)

#
# Double-check that we have the right user: we need to be admin to create an investigator
#

user = el.assert_admin()

investigator = el.find_or_create_user('MagnumPI', 'bad_password', 'subject@elicit.com', 'registered_user')

pp.pprint(investigator)

# now login as investigator
el = elicit.Elicit(args, api.ElicitCreds(_admin_user='investigator3@elicit.dk', _admin_password='bad_password'))

pp.pprint(el.find_study_definitions())