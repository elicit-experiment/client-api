def dump_study_definition(elicit, el, study_id):
    elicit.add_get_api_fn('getStudyDefinition')
    elicit.add_find_api_fn('findTrialDefinitions')
    elicit.add_find_api_fn('findComponents')

    study_definition = el.get_study_definition(id=study_id)
    protocol_definition = study_definition['protocol_definitions'][0]
    phase_definition = protocol_definition['phase_definitions'][0]
    trial_definitions = el.find_trial_definitions(study_definition_id=study_id,
                                                  protocol_definition_id=protocol_definition['id'],
                                                  phase_definition_id=phase_definition['id'])
    phase_definition['trial_definitions'] = trial_definitions
    for trial_definition in trial_definitions:
        components = el.find_components(study_definition_id=study_id,
                                        protocol_definition_id=protocol_definition['id'],
                                        phase_definition_id=phase_definition['id'],
                                        trial_definition_id=trial_definition['id'])

        trial_definition['components'] = components

    return study_definition
