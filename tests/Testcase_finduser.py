"""
Testcase for queries
"""

import pprint

from pyelicit.command_line import parse_command_line_args
from pyelicit import elicit

##
## MAIN
##

pp = pprint.PrettyPrinter(indent=4)

# get the elicit object to define the experiment
elicit_object = elicit.Elicit(parse_command_line_args())

# Double-check that we have the right user: we need to be admin to create a study
user_admin = elicit_object.assert_investigator()

# Get a list of users who can participate in the study (the ones that have already registered in the system)
users = elicit_object.get_all_users(args=dict(query="iain"))

print(users)
