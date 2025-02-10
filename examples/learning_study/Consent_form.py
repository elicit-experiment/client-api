"""
Consent form for CCNY webgazer experiment
"""

import pprint
import sys
import csv
import json

from pyelicit.command_line import parse_command_line_args
from pyelicit import elicit

##
## MAIN
##

pp = pprint.PrettyPrinter(indent=4)

# get the elicit object to define the experiment
elicit_object = elicit.Elicit(parse_command_line_args())

# Double-check that we have the right user: we need to be admin to create a study
user_admin = elicit_object.assert_admin()

#
# Add a new Study Definition
#

# Define study
study_definition_description = dict(title='Consent form',
                                    description="""Consent form""",
                                    version=1,
                                    lock_question=1,
                                    enable_previous=1,
                                    allow_anonymous_users=True,  # allow taking the study without login
                                    show_in_study_list=True,  # show in the (public) study list for anonymous protocols
                                    footer_label="If you have any questions, you can email {{link|mailto:neuroccny@gmail.com|here}}",
                                    redirect_close_on_url=elicit_object.elicit_api.api_url + "/participant",
                                    data="Put some data here, we don't really care about it.",
                                    principal_investigator_user_id=user_admin.id)

study_object = elicit_object.add_study(study=dict(study_definition=study_definition_description))

#
# Create a Protocol Definition
#

# Define protocol
protocol_definition_descriptiopn = dict(name='Consent form',
                                        definition_data="whatever you want here",
                                        summary="This summary will be shown on the webpage? <br/> This is a test to show off all the capabilities of Elicit",
                                        description='This is the consent form used for the video webcam eye tracking experiment',
                                        active=True)

# Add protocol
protocol_object = elicit_object.add_protocol_definition(
    protocol_definition=dict(protocol_definition=protocol_definition_descriptiopn),
    study_definition_id=study_object.id)

#
# Add users to protocol
#

# Get a list of users who can participate in the study (the ones that have already registered in the system)
users = elicit_object.get_all_users()

# find registered users
study_participants = list(filter(lambda usr: usr.role == 'registered_user', users))

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

# only define a single phase for this experiment
phases = [phase_object]

trials = []

#
# Trial 1: Welcome slide
#
# Trial definition
trial_definition_specification = dict(trial_definition=dict(name='Consent form', definition_data=dict(TrialType='Consent form')))

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
                                                                Header=dict(HeaderLabel='{{center|Consent form}}')))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                 study_definition_id=study_object.id,
                                 protocol_definition_id=protocol_object.id,
                                 phase_definition_id=phase_object.id,
                                 trial_definition_id=trial_object.id)


# Component definition: Text Block
component_definition_description = dict(name='TextBlock',
                                        definition_data=dict(
                                            Instruments=[dict(
                                                Instrument=dict(
                                                    TextBlock=dict(
                                                        Text=("{{center|{{b|THE CITY UNIVERSITY OF NEW YORK}}{{n}}" + 
                                                              "{{i|The City College of New York}}{{n}}" + 
                                                              "{{i|Department of Biomedical Engineering}}}}{{n}}" + 
                                                              "{{n}}" + 
                                                              "{{center|{{b|INTERNET BASED INFORMED CONSENT}}}}{{n}}" + 
                                                              "{{n}}" + 
                                                              "{{center|Title of Research Study: Eye movement during video watching{{n}}" + 
                                                              "Principle Investigator: Lucas C. Parra, Ph.D.{{n}}" + 
                                                              "Professor of Biomedical Engineering}}{{n}}" + 
                                                              "{{center|You are being asked to voluntarily participate in this research study, {{n}}being a healthy adult " + 
                                                              " who can clearly read and understand the following instructions and explanations.}}{{n}}"
                                                              ))))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id,
                                               trial_definition_id=trial_object.id)

# Component definition: Text Block
component_definition_description = dict(name='TextBlock',
                                        definition_data=dict(
                                            Instruments=[dict(
                                                Instrument=dict(
                                                    TextBlock=dict(
                                                        Text=("{{center|{{b|{{u|Purpose:}}}}}}{{n}}" + 
                                                              "{{center|The purpose of this research study is to investigate basic visual perception when watching video clips.{{n}} " + 
                                                              "In particular, we are interested in how  the video and sound influences eye movements.}}{{n}}"
                                                              ))))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id,
                                               trial_definition_id=trial_object.id)

# Component definition: Text Block
component_definition_description = dict(name='TextBlock',
                                        definition_data=dict(
                                            Instruments=[dict(
                                                Instrument=dict(
                                                    TextBlock=dict(
                                                        Text=("{{center|{{b|{{u|Procedures:}}}}}}{{n}}" + 
                                                              "{{center|If you agree to participate, we will ask you to do the following:}} {{n}}" + 
                                                              "{{center|   - Before the experiment starts, we will ask questions about yourself (age, gender, etc.)}}{{n}} " +
                                                              "{{center|   - Your eye movements will be captured by your webcam. {{n}}"
                                                              "We will not store any pictures of videos of you, we will only record where on the screen you are looking. {{n}}"
                                                              "To this end you will carry out a short calibration procedure.}}{{n}}" +
                                                              "{{center|   - You will watch short video clips, in which you will need headphones or speakers.}}{{n}}" +                                                              
                                                              "{{center|   - After the video we will ask you questions about the material.{{n}}}}{{n}}" + 
                                                              "{{center|The experiment is estimated to take approximately 10-15 min. {{n}}If you complete the entire experiment you will receive $3 in compensation.}}{{n}}"
                                                              ))))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id,
                                               trial_definition_id=trial_object.id)


# Component definition: Text Block
component_definition_description = dict(name='TextBlock',
                                        definition_data=dict(
                                            Instruments=[dict(
                                                Instrument=dict(
                                                    TextBlock=dict(
                                                        Text=("{{center|{{b|{{u|Potential Risks or Discomforts:}}}}}}{{n}}" + 
                                                                "{{center|There are only minimal risks involved in the participation of this study. {{n}}" 
                                                                "Amazon does not give access to any personal identifying information, {{n}} nevertheless as with any online activity, {{n}}" +
                                                                "there is a minimal risk of breach of confidentiality. The application that extracts your eye gaze position runs {{n}}" +
                                                                "locally on your computer and no images are transferred over the internet to any other computer. {{n}}" +
                                                                "However, as with any online activity there is a theoretical risk of breach of confidentiality if for instance" +
                                                                "your computer security is breached.}}{{n}}"
                                                              ))))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id,
                                               trial_definition_id=trial_object.id)


# Component definition: Text Block
component_definition_description = dict(name='TextBlock',
                                        definition_data=dict(
                                            Instruments=[dict(
                                                Instrument=dict(
                                                    TextBlock=dict(
                                                        Text=("{{center|{{b|{{u|Data recorded:}}}}}}{{n}}" + 
                                                              "{{center|During the experiment we will record your eye movements and no picture/videos of your person will be recorded. {{n}}" +
                                                              "We will store all answers to questions, but there will be no information linking your answers to your person. We will make {{n}}" +
                                                              "our best efforts to maintain confidentiality of any information that is collected during this research study. {{n}}" +
                                                              "Any information from individual participants will not be disclosed unless required by law. Since Amazon handles all your {{n}}" +
                                                              "identifying information, we have no way of identifying or contacting you after this experiment.}}{{n}}" 
                                                              ))))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id,
                                               trial_definition_id=trial_object.id)



# Component definition: Text Block
component_definition_description = dict(name='TextBlock',
                                        definition_data=dict(
                                            Instruments=[dict(
                                                Instrument=dict(
                                                    TextBlock=dict(
                                                        Text=("{{center|{{b|{{u|Questions, Comments or Concerns:}}}}}}{{n}}" + 
                                                              "{{center|Your participation in this research is voluntary. If you have any questions, you can contact {{n}}" +
                                                              "Prof. Lucas Parra at parra@ccny.cuny.edu or (212) 650-7211. If you have any questions about your rights as a research participant {{n}}" +
                                                              "or if you would like to talk to someone other than the researchers, you can contact CUNY Research Compliance Administrator {{n}}" +
                                                              "at 646-664-8918 or HRPP@cuny.edu. {{n}}{{n}} If you agree to participate in this research study please press the next button.}}{{n}}"
                                                              ))))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                               study_definition_id=study_object.id,
                                               protocol_definition_id=protocol_object.id,
                                               phase_definition_id=phase_object.id,
                                               trial_definition_id=trial_object.id)



# Trial 2: End of experiment page
#
# Trial definition
trial_definition_specification = dict(trial_definition=dict(name='End of experiment', definition_data=dict(TrialType='End of experiment')))
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
                                                    Header=dict(
                                                        HeaderLabel='{{center|Thank you for your participation}}')))]))

# Component addition: add the component to the trial
component_object = elicit_object.add_component(component=dict(component=component_definition_description),
                                            study_definition_id=study_object.id,
                                            protocol_definition_id=protocol_object.id,
                                            phase_definition_id=phase_object.id,
                                            trial_definition_id=trial_object.id)

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
                                               trial_definition_id=trial_object.id)

#
# Add a Trial Orders to the study
#

# Define the trial orders
for study_participant in study_participants:
    trial_order_specification = dict(trial_order=dict(sequence_data=",".join([str(trial.id) for trial in trials]),
                                                      user_id=study_participant.id))

    # Trial order addition
    trial_order_object = elicit_object.add_trial_order(trial_order=trial_order_specification,
                                                       study_definition_id=study_object.id,
                                                       protocol_definition_id=protocol_object.id,
                                                       phase_definition_id=phase_object.id)

#
# Add a new Phase Order
#
phase_sequence_data = ",".join([str(phase_definition.id) for phase_definition in phases])

phase_order_specification = dict(phase_order=dict(sequence_data=phase_sequence_data,
                                                  user_id=user_admin.id))

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
#print(('https://elicit.compute.dtu.dk/api/v1/study_definitions/' + str(study_object.id) + '/protocol_definitions/' + str(protocol_object.id) + '/preview?phase_definition_id='  + str(phases[0].id) + '&trial_definition_id=' + str(trials[0].id)))    

print('Study link: ', end='')
print(('https://elicit.compute.dtu.dk/studies/' + str(study_object.id) + '/protocols/'  + str(protocol_object.id)))

