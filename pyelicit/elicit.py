from http import HTTPStatus
from . import api
import pprint
import re

_pp = pp = pprint.PrettyPrinter(indent=4)

def proxy_print(fmt, **args):
    print(fmt, **args)

setattr(pp, 'print', proxy_print)

dir(api)

# camelCase to snake_case
def camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def assert_admin(client, elicit):
    resp = client.request(elicit['getCurrentUser']())

    assert resp.status == HTTPStatus.OK

    print("Current User:")
    print(resp.data)

    user = resp.data

    assert (resp.data.role == 'admin')  # must be admin!

    return user


def add_users_to_protocol(client, elicit, new_study, new_protocol_definition, study_participants, group_name_map=None):
    protocol_users = []
    for user in study_participants:
        group_name = group_name_map[user.username] if group_name_map else None
        protocol_user = dict(protocol_user=dict(user_id=user.id,
                                                study_definition_id=new_study.id,
                                                group_name=group_name,
                                                protocol_definition_id=new_protocol_definition.id))
        resp = client.request(elicit['addProtocolUser'](
            protocol_user=protocol_user,
            study_definition_id=new_study.id,
            protocol_definition_id=new_protocol_definition.id))

        assert resp.status == HTTPStatus.CREATED
        protocol_users.append(resp.data)
    return protocol_users


def find_or_create_user(client, elicit, username, password, email=None, role=None):
    resp = client.request(elicit['findUser'](id=username))

    if resp.status == HTTPStatus.NOT_FOUND:
        pp.pprint(resp.data)
        pp.pprint(resp.status)
        print("Not found; Creating user:")
        user_details = dict(username=username,
                            password=password,
                            email=email or (username + "@elicit.dtu.dk"),
                            role=role or 'registered_user',
                            password_confirmation=password)
        resp = client.request(elicit['addUser'](user=dict(user=user_details)))
        return (resp.data)
    else:
        print("User already exists.")
        return (resp.data)


def add_object(client, elicit, operation, pp = _pp, **args):
    resp = client.request(elicit[operation](**args))
    assert resp.status == HTTPStatus.CREATED
    if resp.status != HTTPStatus.CREATED:
        return (None)

    created_object = resp.data
    if pp != None:
        pp.print("\n\nCreated new object with %s:\n" % operation)
        pp.pprint(created_object)

    return (created_object)

def find_objects(client, elicit, operation, pp = _pp, **args):
    resp = client.request(elicit[operation](**args))
    assert resp.status == HTTPStatus.OK
    if resp.status != HTTPStatus.OK:
        return (None)

    found_objects = resp.data
    if pp != None:
        pp.print("\n\nFound objects with %s(%s):\n" %(operation, args))
        pp.pprint(found_objects)

    return (found_objects)


def load_trial_definitions(file_name):
    with open(file_name, 'r') as tdfd:
        lines = tdfd.readlines()
        td = "\n".join(lines)
        _locals = locals()
        exec(td, globals(), _locals)
        return _locals['trial_components']


class Elicit:
    def __init__(self, script_args):
        self.script_args = script_args  # parse_command_line_args()
        print(self.script_args.send_opt)
        self.elicit_api = api.ElicitApi(api.ElicitCreds(), self.script_args.apiurl, self.script_args.send_opt)
        self.client = self.elicit_api.login()

    def add_obj(self, op, args):
        return add_object(self.client, self.elicit_api, op, self.pp(), **args)

    def get_all_users(self):
        resp = self.client.request(self.elicit_api['findUsers']())
        assert resp.status == HTTPStatus.OK
        return resp.data

    def add_users_to_protocol(self, new_study, new_protocol, study_participants):
        add_users_to_protocol(self.client, self.elicit_api, new_study, new_protocol, study_participants)

    def assert_admin(self):
        return assert_admin(self.client, self.elicit_api)

    def pp(self):
        if self.script_args.debug:
            return _pp
        else:
            return None


def add_find_api_fn(api_name):
    fn_name = camel_to_snake(api_name)

    def fn(self, **kwargs):
        return find_objects(self.client, self.elicit_api, api_name, self.pp(), **kwargs)

    setattr(Elicit, fn_name, fn)

def add_add_api_fn(api_name):
    fn_name = camel_to_snake(api_name)

    def fn(self, **kwargs):
        return add_object(self.client, self.elicit_api, api_name, self.pp(), **kwargs)

    setattr(Elicit, fn_name, fn)

for api_name in ['findStudyResults', 'findExperiments', 'findStages', 'findDataPoints', 'findTimeSeries', 'findTrialResults',
                 'findComponents']:
    add_find_api_fn(api_name)

for api_name in []:
    add_add_api_fn(api_name)
