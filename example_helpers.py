import pprint
from http import HTTPStatus

pp = pprint.PrettyPrinter(indent=4)

def add_users_to_protocol(client, elicit, new_study, new_protocol_definition, study_participants, group_name_map = None):
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

def find_or_create_user(client, elicit, username, password, email = None, role = None):
    resp = client.request(elicit['findUser'](id=username))

    if resp.status == HTTPStatus.NOT_FOUND:
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


def add_object(client, elicit, operation, args):
    resp = client.request(elicit[operation](**args))
    assert resp.status == HTTPStatus.CREATED
    if resp.status != HTTPStatus.CREATED:
        return(None)

    created_object = resp.data
    print("\n\nCreated new object with %s:\n"%operation)
    pp.pprint(created_object)

    return(created_object)

