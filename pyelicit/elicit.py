from http import HTTPStatus
from . import api
import pprint
import re
import json
import random
import string

_pp = pp = pprint.PrettyPrinter(indent=4)

def proxy_print(fmt, **args):
    print(fmt, **args)

setattr(pp, 'print', proxy_print)

def search(d, key, default=None):
    """Return a dict containing to the specified key in the (possibly
    nested) within dictionary d. If there is no item with that key, return
    default.
    """
    stack = [d]
    while stack:
        cur_d = stack[-1]
        stack.pop()
        for k, v in cur_d.items():
            if k == key:
                return cur_d
            elif isinstance(v, dict):
                stack.append(v)
    return default


# camelCase to snake_case
def camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


# Parse the pagination link headers out of the HTTP response
def parse_pagination_links(link_header):
    pp.pprint(link_header)
    link = link_header[0].split(',')
    link_matches = [re.match(r'\s*<([^>]+)>;\s*rel="([a-z]+)"', x) for x in link]
    links = [dict(href=m.group(1), rel=m.group(2)) for m in link_matches]
    last_page_link = list(filter(lambda link: link['rel'] == 'last', links))
    next_page_link = list(filter(lambda link: link['rel'] == 'next', links))
    return last_page_link, next_page_link



def assert_admin(client, elicit):
    resp = client.request(elicit['getCurrentUser']())

    assert resp.status == HTTPStatus.OK

    print("Current User:")
    pp.pprint(resp.data)

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
    definition_data_parent = search(args, 'definition_data')
    if definition_data_parent:
        if isinstance(definition_data_parent['definition_data'], dict):
            definition_data_parent['definition_data'] = json.dumps(definition_data_parent['definition_data'])
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
    next_link = True
    last_page = ""
    found_objects = []
    page = 0
    pagination_aware = 'page' in args
    while next_link:
        page += 1

        if not pagination_aware:
            page_size = args['page_size'] if 'page_size' in args else 3
            args = dict(args, page=page, page_size=page_size)

        resp = client.request(elicit[operation](**args))

        assert resp.status == HTTPStatus.OK
        if resp.status != HTTPStatus.OK:
            return None

        next_link = False
        result_len = len(resp.data)
        if result_len > 0:
            link_header = resp.header['Link'] if 'Link' in resp.header else []
            if not pagination_aware:
                if list(filter(None, link_header)):
                    last_page_link, next_page_link = parse_pagination_links(link_header)

                    if len(last_page_link) == 1:
                        last_page = re.search(r'.*page=(\d+).*', last_page_link[0]['href']).group(1)
                        if pp is not None:
                            pp.print("last_page (%s)" % last_page)

                    if len(next_page_link) == 1:
                        next_link = bool(next_page_link[0]['href'])
                        if pp is not None:
                            pp.pprint("found next page link (%s)"%next_page_link[0]['href'])
                elif result_len >= page_size:
                    #  no header, but full page. N+1 risk
                    if pp is not None:
                        pp.print("Full page: %d/%d; getting next page" % (result_len, page_size))
                    next_link = True

            found_objects += resp.data

    if pp is not None:
        pp.print("\n\nFound objects with %s(%s) in %d/%s pages:\n" % (operation, args, int(page), last_page))
        pp.pprint(found_objects)

    return found_objects


def get_object(client, elicit, operation, pp = _pp, **args):
    resp = client.request(elicit[operation](**args))
    assert resp.status == HTTPStatus.OK
    if resp.status != HTTPStatus.OK:
        return (None)

    found_object = resp.data
    if pp != None:
        pp.print("\n\nGot object with %s(%s):\n" %(operation, args))
        pp.pprint(found_object)

    return (found_object)


def load_trial_definitions(file_name):
    with open(file_name, 'r') as tdfd:
        lines = tdfd.readlines()
        td = "\n".join(lines)
        _locals = locals()
        exec(td, globals(), _locals)
        return _locals['trial_components']


class Elicit:
    def __init__(self, script_args, creds=api.ElicitCreds()):
        self.script_args = script_args  # parse_command_line_args()
        self.elicit_api = api.ElicitApi(creds, self.script_args.apiurl, self.script_args.send_opt)
        self.client = self.elicit_api.login()

    def api_url(self):
        return self.script_args.apiurl

    def auth_header(self):
        return self.elicit_api.auth_header

    def add_obj(self, op, args):
        return add_object(self.client, self.elicit_api, op, self.pp(), **args)

    def get_all_users(self):
        resp = self.client.request(self.elicit_api['findUsers']())
        assert resp.status == HTTPStatus.OK
        return resp.data

    def find_or_create_user(self, username, password, email=None, role=None):
        user = find_or_create_user(self.client, self.elicit_api, username, password, email, role)
        return user

    def ensure_users(self, num_registered, num_anonymous):
        page = 0
        next_link = 'first'
        study_participants = []
        while ((num_registered > 0) or (num_anonymous > 0)) and next_link:
            page += 1
            print("GETTING page %d next %s"%(page, next_link))
            resp = self.client.request(self.elicit_api['findUsers'](page=page, page_size=3))
            assert resp.status == HTTPStatus.OK
            users = resp.data

            print("got %d users"%len(users))

            link_header = resp.header['Link']

            last_page_link, next_page_link = parse_pagination_links(link_header)

            if len(last_page_link) == 1:
                last_page = re.search(r'.*page=(\d+).*', last_page_link[0]['href']).group(1)
                print("last_page %s"%last_page)

            if len(next_page_link) == 1:
                next_link = next_page_link[0]['href']
            else:
                next_link = ''

            for user in users:
                if user.role == 'registered_user':
                    if num_registered > 0:
                        study_participants += [user]
                        num_registered -= 1
                elif user.role == 'anonymous_user':
                    if (num_anonymous > 0) and not "mturk" in user.email:
                        study_participants += [user]
                        num_anonymous -= 1
            print("Got existing %d users.  %d registered and %d anonymous users remain."%(len(study_participants), num_registered, num_anonymous))

        if (num_registered > 0) or (num_anonymous > 0):
            print('Creating remaining users')

        for i in range(num_anonymous):
            username = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)])
            role = 'anonymous_user'
            password = 'password'
            user_details = dict(username=username,
                                password=password,
                                email=username + "@elicit.dtu.dk",
                                role=role or 'registered_user',
                                anonymous=True,
                                password_confirmation=password)
            new_user = self.add_user(user=dict(user=user_details))
            study_participants += [new_user]

        for i in range(num_registered):
            username = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)])
            role = 'registered_user'
            password = 'password'
            user_details = dict(username=username,
                                password=password,
                                email=username + "@elicit.dtu.dk",
                                role=role or 'registered_user',
                                anonymous=False,
                                password_confirmation=password)
            new_user = self.add_user(user=dict(user=user_details))
            study_participants += [new_user]

        return study_participants

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


def add_get_api_fn(api_name):
    fn_name = camel_to_snake(api_name)

    def fn(self, **kwargs):
        return get_object(self.client, self.elicit_api, api_name, self.pp(), **kwargs)

    setattr(Elicit, fn_name, fn)


def add_add_api_fn(api_name):
    fn_name = camel_to_snake(api_name)

    def fn(self, **kwargs):
        return add_object(self.client, self.elicit_api, api_name, self.pp(), **kwargs)

    setattr(Elicit, fn_name, fn)


for api_name in ['findStudyResults', 'findExperiments', 'findStages', 'findDataPoints', 'findTimeSeries',
                 'findTrialResults', 'findComponents', 'findTimeSeries', 'findStudyDefinitions']:
    add_find_api_fn(api_name)

for api_name in ['addStudy', 'addProtocolDefinition', 'addPhaseDefinition', 'addTrialDefinition', 'addTrialOrder',
                 'addPhaseOrder', 'addProtocolUser', 'addComponent', 'addUser']:
    add_add_api_fn(api_name)

for api_name in ['getComponent']:
    add_get_api_fn(api_name)
