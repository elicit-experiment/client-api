import pprint
import pyelicit

from deprecated import examples_default

##
## MAIN
##

pp = pprint.PrettyPrinter(indent=4)
args = examples_default.parse_command_line_args()
args.apiurl = "http://localhost:3000"
elicit = pyelicit.Elicit(pyelicit.ElicitCreds(), args.apiurl, examples_default.send_opt)

#
# Login admin user to get study results
#
client = elicit.login()


def find_or_create_user(username, password, email = None, role = None):
  resp = client.request(elicit['findUser'](id=username))

  if resp.status == 404:
    pp.pprint(resp.data)
    pp.pprint(resp.status)
    print("Not found; Creating user:")
    user_details = dict(username=username,
                        password=password,
                        email=email or (username+"@elicit.dtu.dk"),
                        role=role or 'registered_user',
                        password_confirmation=password)
    resp = client.request(elicit['addUser'](user=dict(user=user_details)))
    return(resp.data)
  else:
    print("User already exists.")
    return(resp.data)

participant="P05"
u = find_or_create_user(participant,
                    "password",
                    (participant+"@elicit.dtu.dk"),
                    'registered_user')
pp.pprint(u)
