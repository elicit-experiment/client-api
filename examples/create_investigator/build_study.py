"""
Example for dumping the results of a study.
"""

import pprint

import sys
import csv
import json

from examples_base import *
from pyelicit import elicit

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

investigator = el.find_or_create_user('MagnumPI', 'bad_password', 'investigator3@elicit.dk', 'investigator')

pp.pprint(investigator)

pp.pprint(el.find_study_definitions())