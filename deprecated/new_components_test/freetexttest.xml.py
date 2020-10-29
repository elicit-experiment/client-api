
# Trial 0, component: 0


component_0_0=dict(
 Instruments=[ dict(
 Instrument=dict(Header=dict(HeaderLabel='Freetext test')))])


# Trial 0, component: 1


component_0_1=dict(
 Instruments=[ dict(
 Instrument=dict(
 Freetext=dict(
 BoxHeight=None,
                                             BoxWidth=None,
                                             Label='Only digits here '
                                                    '(LabelPosition=top)',
                                             LabelPosition='top',
                                             Resizable=None,
                                             Validation='^[0-9]+$')))])


# Trial 0, component: 2


component_0_2=dict(
 Instruments=[ dict(
 Instrument=dict(
 Freetext=dict(
 BoxHeight=None,
                                             BoxWidth=None,
                                             Label='Any char here '
                                                    '(LabelPosition=right)',
                                             LabelPosition='right',
                                             Resizable=None,
                                             Validation='.+')))])


# Trial 0, component: 3


component_0_3=dict(
 Instruments=[ dict(
 Instrument=dict(
 Freetext=dict(
 BoxHeight=None,
                                             BoxWidth=None,
                                             Label='This wants an email '
                                                    '(LabelPosition=left)',
                                             LabelPosition='left',
                                             Resizable=None,
                                             Validation='[-0-9a-zA-Z.+_]+@[-0-9a-zA-Z.+_]+\\.[a-zA-Z]{2,4}')))])

trial_components_0=[ component_0_0, component_0_1, component_0_2, component_0_3]


# Trial 1, component: 0


component_1_0=dict(
 Instruments=[ dict(
 Instrument=dict(
 Header=dict(
 HeaderLabel='Thank you for your '
                                                        'participation')))])


# Trial 1, component: 1


component_1_1=dict(EndOfExperiment=dict(Inputs=None))

trial_components_1=[ component_1_0, component_1_1]


# Trials 1
trial_components=[ trial_components_0, trial_components_1]

