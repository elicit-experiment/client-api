import argparse
from http import HTTPStatus
import pyelicit
from example_helpers import *

ENVIRONMENTS = {
  'local' : 'http://localhost:3000',
  'local_docker': 'https://elicit.docker.local',
  'prod' : 'https://elicit.compute.dtu.dk'
}
parser = argparse.ArgumentParser(prog='elicit')
parser.add_argument('--env', choices=ENVIRONMENTS.keys(), default='prod', help='Service environment to communicate with')
parser.add_argument('--apiurl', type=str, default=None)
parser.add_argument('--ignore_https', type=str, default=False)

send_opt = dict(verify=True)

def parse_command_line_args():
  args = parser.parse_args()

  if None == args.apiurl:
    args.apiurl = ENVIRONMENTS[args.env]

  if args.apiurl.endswith('docker.local'):
    args.ignore_https = False

  send_opt = dict(verify=args.ignore_https)

  return args

def assert_admin(client, elicit):
  resp = client.request(elicit['getCurrentUser']())

  assert resp.status == HTTPStatus.OK

  print("Current User:")
  print(resp.data)

  user = resp.data

  assert(resp.data.role == 'admin') # must be admin!

  return user

def load_trial_definitions(file_name):
  with open(file_name, 'r') as tdfd:
    lines = tdfd.readlines()
    td = "\n".join(lines)
    _locals = locals()
    exec(td, globals(), _locals)
    return _locals['trial_components']


class ElicitClientApi:
  def __init__(self):
    self.script_args = parse_command_line_args()
    self.elicit_api = pyelicit.Elicit(pyelicit.ElicitCreds(), self.script_args.apiurl, send_opt)
    self.client = self.elicit_api.login()

  def add_obj(self, op, args):
      return add_object(self.client, self.elicit_api, op, args)

  def get_all_users(self):
    resp = self.client.request(self.elicit_api['findUsers']())
    assert resp.status == HTTPStatus.OK
    return resp.data

  def add_users_to_protocol(self, new_study, new_protocol, study_participants):
    add_users_to_protocol(self.client, self.elicit_api, new_study, new_protocol, study_participants)

