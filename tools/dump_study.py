"""
Example for dumping the results of a study.
"""
import pprint
import json
import os
from pyelicit import elicit
from pyelicit import command_line
import yaml

from tools.study_definition_helpers import dump_study_definition

##
## DEFAULT ARGUMENTS
##

arg_defaults = {
    "study_id": 1309,
    "env": "prod",
    "user_id": None, # all users
    "output_root_dir": "/Users/iainbryson/Projects/elicit/client-api/results"
}

pp = pprint.PrettyPrinter(indent=4)

command_line.init_parser({"env": (arg_defaults.get("env") or "prod")}) # Allow the script to be reentrant: start with a fresh parser every time,
command_line.parser.add_argument(
    '--study_id', default=arg_defaults["study_id"], help="The study ID to dump", type=int)
command_line.parser.add_argument(
    '--output_root_dir', default=arg_defaults.get("output_root_dir") or "results", help="The root folder to dump to")
args = command_line.parse_command_line_args(arg_defaults)
pp.pprint(args)

el = elicit.Elicit(args)
client = el.client
user = el.assert_creator()
study_id = args.study_id

study_definition = dump_study_definition(study_id)

jsonable = json.loads(json.dumps(study_definition))
yaml.dump(jsonable, open(os.path.join(args.output_root_dir, f"study_{study_id}.yaml"), "w"))