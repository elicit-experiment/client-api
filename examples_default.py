import argparse

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

  assert resp.status == 200

  print("Current User:")
  pp.pprint(resp.data)

  user = resp.data

  assert(resp.data.role == 'admin') # must be admin!
