# -*- coding: utf-8 -*-
"""
Example testing the Listselect
"""

import pprint
import sys
import csv
import json

from pyelicit.command_line import parse_command_line_args
from pyelicit import elicit
from random import shuffle

FontSize = 15;
FontSize_options = 12;

def embed_elicit_fontsize(str_input, FontSize):
    return "{{style|font-size: " + str(FontSize) + "px;|" + str_input + "}}"

## URLs
audio_url = "https://www.mfiles.co.uk/mp3-downloads/franz-liszt-liebestraum-3-easy-piano.mp3"
video_youtube_url = 'https://youtu.be/zr9leP_Dcm8'
video_mp4_url = 'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4'
test_image_url = 'https://dummyimage.com/750x550/996633/fff'

study_url = 'https://elicit-experiment.com/studies/'

##
## MAIN
##

NUM_REGISTERED_USERS = 0
NUM_ANONYMOUS_USERS = 10

pp = pprint.PrettyPrinter(indent=4)

arg_defaults = {
    "env": "prod",
    "env_file": "../prod.yaml",
}

# get the Elicit object to define the experiment
elicit_object = elicit.Elicit(parse_command_line_args(arg_defaults))


# Double-check that we have the right user: we need to be investigator to create a study
user_investigator = elicit_object.assert_creator()

#
# Add a new Study Definition
#

# Define study
study_definition_description = dict(title='Listselect test',
                        description="""This is a test of the Listselect component""",
                        version=1,
                        lock_question=1,
                        enable_previous=1,
                        allow_anonymous_users=True,  # allow taking the study without login
                        show_in_study_list=False,  # show in the (public) study list for anonymous protocols
                        footer_label="If you have any questions, you can email {{link|mailto:neuroccny@gmail.com|here}}",
                        redirect_close_on_url=elicit_object.elicit_api.api_url + "/participant",
                        data="Put some data here, we don't really care about it.",
                        principal_investigator_user_id=user_investigator.id)


study_object = elicit_object.add_study(study=dict(study_definition=study_definition_description))

#
# Create a Protocol Definition
#

# Define protocol
protocol_definition_descriptiopn = dict(name='Listselect test',
                               definition_data="whatever you want here",
                               summary="This is a test of the Listselect component",
                               description='This is a test of the Listselect component',
                               active=True)

# Add protocol
protocol_object = elicit_object.add_protocol_definition(protocol_definition=dict(protocol_definition=protocol_definition_descriptiopn),
                                          study_definition_id=study_object.id)

#
# Add users to protocol
#

# Get a list of users who can participate in the study
study_participants = elicit_object.ensure_users(NUM_REGISTERED_USERS, NUM_ANONYMOUS_USERS, False)


# add users to protocol
elicit_object.add_users_to_protocol(study_object, protocol_object, study_participants)

#
# Add Phase Definition
#

# Define phase
phase_definition_description = dict(phase_definition=dict(definition_data="First phase of the experiment"))

# Add phase
phase_object = elicit_object.add_phase_definition(phase_definition=phase_definition_description,
                                    study_definition_id=study_object.id,
                                    protocol_definition_id=protocol_object.id)

#only define a single phase for this experiment
phases = [phase_object]

trials = []


#%% Trial 1: ListSelect - with stimuli

# Trial definition
trial_definition_specification = dict(trial_definition=dict(name='Listselect with stimuli', definition_data=dict(TrialType='Listselect')))

trial_object = elicit_object.add_trial_definition(trial_definition=trial_definition_specification,
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id)
# save trial to later define trial orders
trials.append(trial_object)



# Component definition: Header Label
component_definition_description = dict(name='HeaderLabel',
                                        definition_data=dict(
                                                Instruments=[dict(
                                                        Instrument=dict(
                                                                Header=dict(HeaderLabel='{{center|1: This is a test of a Listselect component}}')))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)

component_definition_description = dict(name='ListSelect',
                                        definition_data=dict(Layout=dict(Type='column',
                                                                         ColumnWidthPercent=['30', '70']),
                                                            Instruments=[dict(
                                                                    Instrument=dict(
                                                                        ListSelect=dict(
                                                                            HeaderLabel='This is Listselect with image stimuli (inside)',
                                                                            IsOptional='0',
                                                                            TextField='Other',
                                                                            UserTextInput = True,
                                                                            UserInputBox = 'Inside',
                                                                            MaxNoOfSelections='4',
                                                                            MinNoOfSelections='2',
                                                                            Items=dict(
                                                                                Item=[
                                                                                      dict(Id='0',Label='Item-0',Selected='1',Correct=False),
                                                                                      dict(Id='1',Label='Item-1',Selected='0',Correct=False),
                                                                                      dict(Id='2',Label='Item-2',Selected='1',Correct=False),
                                                                                      dict(Id='3',Label='Item-3',Selected='0',Correct=False),
                                                                                      dict(Id='4',Label='Item-4',Selected='1', Correct=False),
                                                                                      dict(Id='5',Label='Item-5',Selected='1', Correct=False)]))))],
                                                            Stimuli=[dict(Height='100%',
                                                                          Width='100%',
                                                                          Label='This is a full size',
                                                                          Type='image',
                                                                          URI='https://dummyimage.com/750x550/996633/fff')]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)


component_definition_description = dict(name='ListSelect',
                                        definition_data=dict(Layout=dict(Type='column',
                                                                         ColumnWidthPercent=['30', '70']),
                                                            Instruments=[dict(
                                                                    Instrument=dict(
                                                                        ListSelect=dict(
                                                                            HeaderLabel='This is Listselect with image stimuli (outside)',
                                                                            IsOptional='0',
                                                                            TextField='Other',
                                                                            UserTextInput = True,
                                                                            UserInputBox = 'Outside',
                                                                            MaxNoOfSelections='5',
                                                                            MinNoOfSelections='3',
                                                                            Items=dict(
                                                                                Item=[
                                                                                      dict(Id='0',Label='Item-0',Selected='1',Correct=False),
                                                                                      dict(Id='1',Label='Item-1',Selected='0',Correct=False),
                                                                                      dict(Id='2',Label='Item-2',Selected='1',Correct=False),
                                                                                      dict(Id='3',Label='Item-3',Selected='0',Correct=False),
                                                                                      dict(Id='4',Label='Item-4',Selected='1', Correct=False),
                                                                                      dict(Id='5',Label='Item-5',Selected='1', Correct=False)]))))],
                                                            Stimuli=[dict(Height='100%',
                                                                          Width='100%',
                                                                          Label='This is a full size',
                                                                          Type='image',
                                                                          URI='https://dummyimage.com/750x550/996633/fff')]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)


#%% Trial 2: ListSelect - no stimuli

# Trial definition
trial_definition_specification = dict(trial_definition=dict(name='Listselect no stimuli', definition_data=dict(TrialType='Listselect')))

trial_object = elicit_object.add_trial_definition(trial_definition=trial_definition_specification,
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id)
# save trial to later define trial orders
trials.append(trial_object)



# Component definition: Header Label
component_definition_description = dict(name='HeaderLabel',
                                        definition_data=dict(
                                                Instruments=[dict(
                                                        Instrument=dict(
                                                                Header=dict(HeaderLabel='{{center|1: This is a test of a Listselect component}}')))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)

# ListSelect for edu_5
component_definition_description = dict(name='edu_5',
    definition_data=dict(
        Layout=dict(Type='column', ColumnWidthPercent=['30', '70']),
        Instruments=[dict(
            Instrument=dict(
                ListSelect=dict(
                    HeaderLabel=embed_elicit_fontsize("The educational material I seek out is usually …", FontSize),
                    IsOptional='0',
                    TextField="Other",
                    UserTextInput=True,
                    UserInputBox="Inside",
                    MaxNoOfSelections="5",
                    MinNoOfSelections="2",
                    Items=dict(
                        Item=[
                            dict(Id='0', Label=embed_elicit_fontsize("Slideshow presentations (e.g. PowerPoint, Google Slides, Prezi)", FontSize_options)),
                            dict(Id='1', Label=embed_elicit_fontsize("Books", FontSize_options)),
                            dict(Id='2', Label=embed_elicit_fontsize("Scientific papers / Research articles", FontSize_options)),
                            dict(Id='3', Label=embed_elicit_fontsize("Lecture videos (YouTube, Vimeo, etc.)", FontSize_options)),
                            dict(Id='4', Label=embed_elicit_fontsize("Short educational videos (YouTube, Vimeo, etc.)", FontSize_options)),
                            dict(Id='5', Label=embed_elicit_fontsize("Instagram reels / TikTok", FontSize_options)),
                            dict(Id='6', Label=embed_elicit_fontsize("Online Blogs", FontSize_options)),
                            dict(Id='7', Label=embed_elicit_fontsize("Games", FontSize_options)),
                            dict(Id='8', Label=embed_elicit_fontsize("Simulations / interactive learning experiences", FontSize_options))
                        ]
                    )
                )
            )
        )]
    )
)

elicit_object.add_component(
    component=dict(component=component_definition_description),
    study_definition_id=study_object.id,
    protocol_definition_id=protocol_object.id,
    phase_definition_id=phase_object.id,
    trial_definition_id=trial_object.id
)

#%% Trial 3: ListSelect - no stimuli no options

# Trial definition
trial_definition_specification = dict(trial_definition=dict(name='Listselect no stimuli', definition_data=dict(TrialType='Listselect')))

trial_object = elicit_object.add_trial_definition(trial_definition=trial_definition_specification,
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id)
# save trial to later define trial orders
trials.append(trial_object)



# Component definition: Header Label
component_definition_description = dict(name='HeaderLabel',
                                        definition_data=dict(
                                                Instruments=[dict(
                                                        Instrument=dict(
                                                                Header=dict(HeaderLabel='{{center|1: This is a test of a Listselect component}}')))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)

# ListSelect for edu_5
component_definition_description = dict(name='q_e',
    definition_data=dict(
        Layout=dict(Type='column', ColumnWidthPercent=['30', '70']),
        Instruments=[dict(
            Instrument=dict(
                ListSelect=dict(
                    HeaderLabel=embed_elicit_fontsize("List 3 reasons why Elicit is so great ;)", FontSize),
                    IsOptional='0',
                    TextField="Other",
                    UserTextInput=True,
                    UserInputBox="Inside",
                    MaxNoOfSelections="5",
                    MinNoOfSelections="3",
                    Items=dict(
                        Item=[]
                    )
                )
            )
        )]
    )
)

elicit_object.add_component(
    component=dict(component=component_definition_description),
    study_definition_id=study_object.id,
    protocol_definition_id=protocol_object.id,
    phase_definition_id=phase_object.id,
    trial_definition_id=trial_object.id
)


# ListSelect for edu_5
component_definition_description = dict(name='q_e',
    definition_data=dict(
        Layout=dict(Type='column', ColumnWidthPercent=['30', '70']),
        Instruments=[dict(
            Instrument=dict(
                ListSelect=dict(
                    HeaderLabel=embed_elicit_fontsize("List 2 reasons why Elicit makes surveys easy", FontSize),
                    IsOptional='0',
                    TextField="Other",
                    UserTextInput=True,
                    UserInputBox="Inside",
                    MaxNoOfSelections="5",
                    MinNoOfSelections="2",
                    Items=dict(
                        Item=[]
                    )
                )
            )
        )]
    )
)

elicit_object.add_component(
    component=dict(component=component_definition_description),
    study_definition_id=study_object.id,
    protocol_definition_id=protocol_object.id,
    phase_definition_id=phase_object.id,
    trial_definition_id=trial_object.id
)


#%% This is a combination of several components
component_objects = []  # Store all components

# Define frequency options for Likert scale (more detailed than standard Likert options)
frequency_options = [
    dict(Id='1', Label=embed_elicit_fontsize("Never", FontSize_options), Selected='0', Correct=False),
    dict(Id='2', Label=embed_elicit_fontsize("Rarely (a few times a semester)", FontSize_options), Selected='0', Correct=False),
    dict(Id='3', Label=embed_elicit_fontsize("Occasionally (a few times a month)", FontSize_options), Selected='0', Correct=False),
    dict(Id='4', Label=embed_elicit_fontsize("Often (a few times a week)", FontSize_options), Selected='0', Correct=False),
    dict(Id='5', Label=embed_elicit_fontsize("Very Often (almost every day)", FontSize_options), Selected='0', Correct=False),
    dict(Id='6', Label=embed_elicit_fontsize("Multiple times a day", FontSize_options), Selected='0', Correct=False),
    dict(Id='7', Label=embed_elicit_fontsize("Constantly throughout the day", FontSize_options), Selected='0', Correct=False)
]
  
  # Likert Scale Options
likert_options = [
      dict(Id='1', Label=embed_elicit_fontsize("Strongly Disagree", FontSize_options), Selected='0', Correct=False),
      dict(Id='2', Label=embed_elicit_fontsize("Disagree", FontSize_options), Selected='0', Correct=False),
      dict(Id='3', Label=embed_elicit_fontsize("Somewhat disagree", FontSize_options), Selected='0', Correct=False),
      dict(Id='4', Label=embed_elicit_fontsize("Neither agree nor disagree", FontSize_options), Selected='0', Correct=False),
      dict(Id='5', Label=embed_elicit_fontsize("Somewhat agree", FontSize_options), Selected='0', Correct=False),
      dict(Id='6', Label=embed_elicit_fontsize("Agree", FontSize_options), Selected='0', Correct=False),
      dict(Id='7', Label=embed_elicit_fontsize("Strongly Agree", FontSize_options), Selected='0', Correct=False)
]
  
  # Define social media platform options
social_media_sources = [
  "YouTube",
  "TikTok",
  "Instagram",
  "Reddit",
  "Facebook",
  "X (formerly Twitter)",
  "Snapchat",
  "LinkedIn",
  "Discord",
  "Twitch",
  "Podcasts (via Spotify, Apple, etc.)",
  "Educational Blogs/Websites",
  "Never use social media"
  ]
  
  # Create a trial for the Educational Material & Social Media Survey
trial_definition_specification = dict(
      trial_definition=dict(name='Student help Survey', definition_data=dict(TrialType='StudentHelp_Survey'))
)

trial_object = elicit_object.add_trial_definition(
    trial_definition=trial_definition_specification,
    study_definition_id=study_object.id,
    protocol_definition_id=protocol_object.id,
    phase_definition_id=phase_object.id
)

# save trial to later define trial orders
trials.append(trial_object)

component_definition_description = dict(name='HeaderLabel',
                                    definition_data=dict(
                                            Instruments=[dict(
                                                    Instrument=dict(
                                                            Header=dict(HeaderLabel='{{center|Coursework}}')))]))

# Component addition: add the component to the trial
component_objects.append(elicit_object.add_component(component=dict(component=component_definition_description),
                                                study_definition_id=study_object.id,
                                                protocol_definition_id=protocol_object.id,
                                                phase_definition_id=phase_object.id,
                                                trial_definition_id=trial_object.id))

  # Likert Scale Options for frequency of needing help
help_frequency_options = [
  dict(Id='1', Label=embed_elicit_fontsize("Never", FontSize_options), Selected='0', Correct=False),
  dict(Id='2', Label=embed_elicit_fontsize("Rarely (once a month or less)", FontSize_options), Selected='0', Correct=False),
  dict(Id='3', Label=embed_elicit_fontsize("Sometimes (a few times a month)", FontSize_options), Selected='0', Correct=False),
  dict(Id='4', Label=embed_elicit_fontsize("Often (a few times a week)", FontSize_options), Selected='0', Correct=False),
  dict(Id='5', Label=embed_elicit_fontsize("Very Often (almost every day)", FontSize_options), Selected='0', Correct=False),
  dict(Id='6', Label=embed_elicit_fontsize("Always (multiple times a day)", FontSize_options), Selected='0', Correct=False),
  ]
  
help_frequency_component = dict(
  name="help_frequency",
  definition_data=dict(
  Layout=dict(Type='row'),
  Instruments=[dict(
      Instrument=dict(
          LikertScale=dict(
              HeaderLabel=embed_elicit_fontsize("How often do you need help with your coursework?", FontSize),
              MaxNoOfScalings='1',
              MinNoOfScalings='1',
              IsOptional=False,
              Items=dict(Item=help_frequency_options)
          )
      )
  )]
  )
  )
  
# Add the component to the survey
component_objects.append(elicit_object.add_component(
      component=dict(component=help_frequency_component),
      study_definition_id=study_object.id,
      protocol_definition_id=protocol_object.id,
      phase_definition_id=phase_object.id,
      trial_definition_id=trial_object.id
  ))

  # ListSelect component: Most frequently used sources for coursework help
help_sources_frequent = [
  "Google the problem or concept"]
  
help_sources_frequent_component = dict(
  name="help_sources_frequent",
  definition_data=dict(
  Layout=dict(Type='row'),
  Instruments=[dict(
      Instrument=dict(
          ListSelect=dict(
              HeaderLabel=embed_elicit_fontsize("Which sources do you {{b|most frequently}} use to get help with coursework?", FontSize) + "{{n}}" + embed_elicit_fontsize("(List at least 3)", FontSize_options),
              IsOptional=False,
              TextField='List sources you get help',
              UserTextInput=True,
              UserInputBox='Outside',
              MaxNoOfSelections="10",  # Allow multiple selections
              MinNoOfSelections="3",
              Items=dict(
                  Item=[dict(Id=str(idx+1), Label=embed_elicit_fontsize(source, FontSize_options), Selected='0', Correct=False)
                        for idx, source in enumerate(help_sources_frequent)]
              )
          )
      )
  )]
  )
  )
  
# Add the component to the survey
component_objects.append(elicit_object.add_component(
      component=dict(component=help_sources_frequent_component),
      study_definition_id=study_object.id,
      protocol_definition_id=protocol_object.id,
      phase_definition_id=phase_object.id,
      trial_definition_id=trial_object.id
  ))
  

# Likert scale question about frequency of social media use for education
component_definition_description = dict(
   name="social_media_frequency",
   definition_data=dict(
   Layout=dict(Type='row'),
   Instruments=[dict(
       Instrument=dict(
           LikertScale=dict(
               HeaderLabel=embed_elicit_fontsize("In the past semester, I used social media (e.g., TikTok, YouTube, Instagram) in general ...", FontSize),
               MaxNoOfScalings='1',
               MinNoOfScalings='1',
               IsOptional=False,
               Items=dict(Item=frequency_options)
           )
       )
   )]
   )
   )
   
# Add to the survey
component_objects.append(elicit_object.add_component(
       component=dict(component=component_definition_description),
       study_definition_id=study_object.id,
       protocol_definition_id=protocol_object.id,
       phase_definition_id=phase_object.id,
       trial_definition_id=trial_object.id
   ))

# Likert scale question about frequency of social media use for education
component_definition_description = dict(
   name="social_media_frequency",
   definition_data=dict(
   Layout=dict(Type='row'),
   Instruments=[dict(
       Instrument=dict(
           LikertScale=dict(
               HeaderLabel=embed_elicit_fontsize("In the past semester, I used social media for {{b|educational purposes}}...", FontSize),
               MaxNoOfScalings='1',
               MinNoOfScalings='1',
               IsOptional=False,
               Items=dict(Item=frequency_options)
           )
       )
   )]
   )
   )
   
# Add to the survey
component_objects.append(elicit_object.add_component(
      component=dict(component=component_definition_description),
      study_definition_id=study_object.id,
      protocol_definition_id=protocol_object.id,
      phase_definition_id=phase_object.id,
      trial_definition_id=trial_object.id
  ))
  
# ListSelect question for preferred SoMe platforms for education
component_definition_description = dict(
  name="social_media_platforms",
  definition_data=dict(
  Layout=dict(Type='row'),
  Instruments=[dict(
      Instrument=dict(
          ListSelect=dict(
              HeaderLabel=embed_elicit_fontsize("My favorite social media platforms to find {{b|educational content}} is", FontSize) + "{{n}}" + embed_elicit_fontsize("(Select all that apply)", FontSize_options),
              IsOptional=False,
              TextField="Other (please specify)",
              UserTextInput=True,
              UserInputBox="Inside",
              MaxNoOfSelections="10",  # Allow a few extra user-defined selections
              MinNoOfSelections="1",
              Items=dict(
                  Item=[dict(Id=str(idx+1), Label=embed_elicit_fontsize(source, FontSize_options), Selected='0', Correct=False)
                        for idx, source in enumerate(social_media_sources)]
              )
          )
      )
  )]
  )
  )
  
# Add to the survey
component_objects.append(elicit_object.add_component(
      component=dict(component=component_definition_description),
      study_definition_id=study_object.id,
      protocol_definition_id=protocol_object.id,
      phase_definition_id=phase_object.id,
      trial_definition_id=trial_object.id
  ))
  
social_media_reasons_component = dict(
  name="social_media_reasons",
  definition_data=dict(
  Layout=dict(Type='row'),
  Instruments=[dict(
      Instrument=dict(
          ListSelect=dict(
              HeaderLabel=embed_elicit_fontsize("Why do you seek out social media for help with your coursework?", FontSize) + "{{n}}" + embed_elicit_fontsize("(List at least 3 reasons why)", FontSize_options),
              IsOptional=False,
              TextField='Please list reasons',
              UserTextInput=True,
              UserInputBox='Outside',
              MaxNoOfSelections="10",  # Allow up to 5 additional user inputs
              MinNoOfSelections="3",
              Items=dict(Item=[]))))]))
  
# Add the component to the survey
component_objects.append(elicit_object.add_component(
      component=dict(component=social_media_reasons_component),
      study_definition_id=study_object.id,
      protocol_definition_id=protocol_object.id,
      phase_definition_id=phase_object.id,
      trial_definition_id=trial_object.id
  ))
  
video_usage_questions = [
      "I watch educational videos on social media to help with my coursework.",
  ]
  
for idx, question in enumerate(video_usage_questions, start=1):
  component_definition_description = dict(
  name=f"socialmedia_usage_{idx}",
  definition_data=dict(
      Layout=dict(Type='row'),
      Instruments=[dict(
          Instrument=dict(
              LikertScale=dict(
                  HeaderLabel=embed_elicit_fontsize(question, FontSize),
                  MaxNoOfScalings='1',
                  MinNoOfScalings='1',
                  IsOptional=False,
                  Items=dict(Item=likert_options)
              )
          )
      )]
  )
  )
  
  component_objects.append(elicit_object.add_component(
  component=dict(component=component_definition_description),
  study_definition_id=study_object.id,
  protocol_definition_id=protocol_object.id,
  phase_definition_id=phase_object.id,
  trial_definition_id=trial_object.id
  ))
  
  educational_video_reasons_component = dict(
  name="educational_video_reasons",
  definition_data=dict(
      Layout=dict(Type='row'),
      Instruments=[dict(
          Instrument=dict(
              ListSelect=dict(
                  HeaderLabel=embed_elicit_fontsize("Why do you watch educational videos (e.g. on Youtube)?", FontSize) + "{{n}}" + embed_elicit_fontsize("(List at least 3 reasons why)", FontSize_options),
                  IsOptional=False,
                  TextField='Please enter reasons',
                  UserTextInput=True,
                  UserInputBox='Outside',
                  MaxNoOfSelections="5",
                  MinNoOfSelections="3",
                  Items=dict(Item=[])
              )
          )
      )]
  )
  )
  
  # Add the component to the survey
  component_objects.append(elicit_object.add_component(
  component=dict(component=educational_video_reasons_component),
  study_definition_id=study_object.id,
  protocol_definition_id=protocol_object.id,
  phase_definition_id=phase_object.id,
  trial_definition_id=trial_object.id
  ))
  
  # Question: AI Chatbot Usage Frequency
  component_definition_description_3 = dict(
name="ai_usage_3",
definition_data=dict(
    Layout=dict(Type='row'),
    Instruments=[dict(
        Instrument=dict(
            LikertScale=dict(
                HeaderLabel=embed_elicit_fontsize("In the past semester, I used AI-powered chatbots (e.g., ChatGPT, Gemini, Claude) in my coursework...", FontSize),
                MaxNoOfScalings='1',
                MinNoOfScalings='1',
                IsOptional=False,
                Items=dict(Item=frequency_options)  # Uses more detailed frequency scale
            )
        )
    )]
)
)

  component_objects.append(elicit_object.add_component(
component=dict(component=component_definition_description_3),
study_definition_id=study_object.id,
protocol_definition_id=protocol_object.id,
phase_definition_id=phase_object.id,
trial_definition_id=trial_object.id
))
  
  # Reasons (WHY students use LLMs)
  
  # ListSelect Component for selecting reasons (WHY)
  component_definition_reasons = dict(
  name="ai_usage_reasons",
  definition_data=dict(
  Layout=dict(Type='row'),
  Instruments=[dict(
      Instrument=dict(
          ListSelect=dict(
              HeaderLabel=embed_elicit_fontsize("In the past semester I used AI-powered chatbots (e.g., ChatGPT, Gemini, Claude) in my coursework because...", FontSize) + "{{n}}" + embed_elicit_fontsize("(List at least 3 reasons why)", FontSize_options),
              IsOptional=False,
              TextField='Please list reasons',
              UserTextInput=True,
              UserInputBox='Inside',
              MaxNoOfSelections="10",
              MinNoOfSelections="3",
              Items=dict(Item=[])
          )
      )
  )]
  )
  )
  
  # Add the components to the survey
  component_objects.append(elicit_object.add_component(
  component=dict(component=component_definition_reasons),
  study_definition_id=study_object.id,
  protocol_definition_id=protocol_object.id,
  phase_definition_id=phase_object.id,
  trial_definition_id=trial_object.id
  ))
  
  # ListSelect Component for selecting reasons (WHY)
  component_definition_reasons = dict(
  name="ai_usage_reasons",
  definition_data=dict(
  Layout=dict(Type='row'),
  Instruments=[dict(
      Instrument=dict(
          ListSelect=dict(
              HeaderLabel=embed_elicit_fontsize("When I use AI-powered chatbots (e.g., ChatGPT, Gemini, Claude) in my coursework i use them to...", FontSize) + "{{n}}" + embed_elicit_fontsize("(Please list at least 3 uses of AI)", FontSize_options),
              IsOptional=False,
              TextField='Please list uses',
              UserTextInput=True,
              UserInputBox='Outside',
              MaxNoOfSelections="10",
              MinNoOfSelections="3",
              Items=dict(Item=[])
          )
      )
  )]
  )
  )
  
  # Add the components to the survey
  component_objects.append(elicit_object.add_component(
  component=dict(component=component_definition_reasons),
  study_definition_id=study_object.id,
  protocol_definition_id=protocol_object.id,
  phase_definition_id=phase_object.id,
  trial_definition_id=trial_object.id
  ))


#%%  Trial 6: End of experiment page
#
# Trial definition
trial_definition_specification =  dict(trial_definition=dict(name='End of experiment', definition_data=dict(TrialType='EOE')))
trial_object_eoe = elicit_object.add_trial_definition(trial_definition=trial_definition_specification,
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id)

# Component definition: Header Label
component_definition_description = dict(name='HeaderLabel',
                            definition_data=dict(
                                    Instruments=[dict(
                                            Instrument=dict(
                                                    Header=dict(HeaderLabel='{{center|Thank you for your participation}}')))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object_eoe.id)



component_definition_description = dict(name='End of experiment',
                            definition_data=dict(
                                    Instruments=[dict(
                                            Instrument=dict(
                                                    EndOfExperiment=dict()))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id,
                                               trial_definition_id=trial_object_eoe.id)

#%% Add Trial Orders to the study
#trail_orders for anonymous users
for anonymous_participant in range(0,NUM_ANONYMOUS_USERS):
    trial_id = [int(trial.id) for trial in trials]
    #shuffle(trial_id)
    trial_id.append(trial_object_eoe.id)

    trial_order_specification_anonymous = dict(trial_order=dict(sequence_data=",".join(map(str,trial_id))))
    print(trial_order_specification_anonymous)
    
    # Trial order addition
    trial_order_object = elicit_object.add_trial_order(trial_order=trial_order_specification_anonymous,
                                                       study_definition_id=study_object.id,
                                                       protocol_definition_id=protocol_object.id,
                                                       phase_definition_id=phase_object.id)

#%% Add a new Phase Order
phase_sequence_data = ",".join([str(phase_definition.id) for phase_definition in phases])

phase_order_specification = dict(phase_order=dict(sequence_data=phase_sequence_data,
                                               user_id=user_investigator.id))

phase_order_object = elicit_object.add_phase_order(phase_order=phase_order_specification,
                                     study_definition_id=study_object.id,
                                     protocol_definition_id=protocol_object.id)

# print some basic details about the experiment
print('Study id: ' + str(study_object.id))
print('Protocol id: ' + str(str(protocol_object.id)))
print('Phase ids: ' , end='')
for phase_id in range(0, len(phases)):
    print(str(phases[phase_id].id) + ', ', end='')
print('')
print('Trial ids: ' , end='')
for trial_id in range(0, len(trials)):
    print(str(trials[trial_id].id) + ', ', end='')
print('')    

print('Added ' + str(len(study_participants)) + ' users to the protocol')
print('User ids: ', end='')
for user_id in range(0, len(study_participants)):
    print(str(study_participants[user_id].id) + ', ', end='')
print('')

print('Study link: ', end='')
print((study_url + str(study_object.id) + '/protocols/'  + str(protocol_object.id)))
                                                        