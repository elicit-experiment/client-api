component_random_radio = dict(
    Instruments=[dict(
        Instrument=dict(
            RadioButtonGroup=dict(
                AlignForStimuli='0',
                HeaderLabel='Do you have '
                            'any hearing '
                            'disorders',
                RandomizeOrder=True,
                Items=dict(
                    Item=[dict(
                        Id='1',
                        Label='Yes',
                        Selected='0'),
                        dict(
                            Id='2',
                            Label='No',
                            Selected='0'),
                        dict(
                            Id='3',
                            Label='Dont '
                                  'know',
                            Selected='0')]))))])

component_random_checkbox = dict(
    Instruments=[dict(
        Instrument=dict(
            CheckBoxGroup=dict(
                AlignForStimuli='0',
                HeaderLabel='checkboxgroup (pre selected options, [1 3 5])',
                MaxNoOfSelections='1',
                MinNoOfSelections='0',
                RandomizeOrder=True,
                Items=dict(
                    Item=[
                        dict(Id='0', Label='yes', Selected='1'),
                        dict(Id='1', Label='no', Selected='0'),
                        dict(Id='2', Label='dont know', Selected='1'),
                        dict(Id='3', Label='kinda', Selected='0'),
                        dict(Id='4', Label='a little', Selected='1')]))))])

component_completion_code = dict(
    Instruments=[dict(
        Instrument=dict(
            CompletionCode=dict(
                Label='Completion Code{{n}}'
                      '(Click to copy to clipboard; or select & copy)',
                LabelPosition='top',
                Validation='.+')))])

component_eoe_textblock = dict(
    Instruments=[dict(
        Instrument=dict(
            TextBlock=dict(
                Text='The experiment is over '
                     '{{n}} Thank you for your '
                     'participation in this '
                     'experiment :D')))])

component_eoe = dict(
    Instruments=[dict(
        Instrument=dict(
            EndOfExperiment=dict()))]
)

trial_components = [
    [component_random_radio, component_random_checkbox],
    [component_completion_code, component_eoe_textblock, component_eoe]
]
