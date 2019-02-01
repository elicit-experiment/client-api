stars_video_url = 'https://youtu.be/soTEnpcn0ig'
video_component_definition = dict(
                                      Stimuli=[dict(
                                          Label='This video is pausable',
                                          Type='video/youtube',
                                          IsPausable=False,
                                          URI=stars_video_url)])

component_eoe = dict(
    Instruments=[dict(
        Instrument=dict(
            EndOfExperiment=dict()))]
)

trial_components = [
    [video_component_definition],
    [component_eoe]
]