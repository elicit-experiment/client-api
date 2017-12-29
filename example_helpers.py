def addUsersToProtocol(client, elicit, new_study, new_protocol_definition, study_participants):
  protocol_users = []
  for user in study_participants:
    protocol_user = dict(protocol_user=dict(user_id=user.id,
                                            study_definition_id=new_study.id,
                                            protocol_definition_id=new_protocol_definition.id))
    resp = client.request(elicit['addProtocolUser'](
                                                    protocol_user=protocol_user,
                                                    study_definition_id=new_study.id,
                                                    protocol_definition_id=new_protocol_definition.id))

    assert resp.status == 201
    protocol_users.append(resp.data)
  return protocol_users
