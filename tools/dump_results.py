"""
Example for dumping the results of a study.
"""
import pprint
import json
import os
import collections
import pandas as pd
import pyswagger.primitives
import yaml
from pyelicit import elicit
from pyelicit import command_line
from dump_time_series import convert_msgpack_to_ndjson, uncompress_datapoint, fetch_time_series
import shutil
from study_definition_helpers import dump_study_definition
from dump_utilities import with_dates
from result_path_generator import ResultPathGenerator
from result_collector import ResultCollector
from collections import OrderedDict
from datetime import datetime
import re
from dateutil.parser import parse
from dateutil.parser import isoparse
from dateutil import parser

##
## DEFAULT ARGUMENTS
##

arg_defaults = {
    "study_id": 1423,
    "env": "prod",
    "user_id": None, # all users
    "result_root_dir": "../../results",
    "env_file": "../prod.yaml"
}


##
## HELPERS
##

def remove_elicit_formatting(text: str) -> str:
    # Remove literal tokens that we know should vanish.
    text = text.replace("{{n}}", "")
    
    # This pattern matches the innermost double curly braces with no nested ones.
    pattern = re.compile(r"\{\{([^{}]+?)\}\}")
    
    # Continue replacing until no further changes occur.
    while True:
        # The replacement function:
        # If the match contains a pipe, return the text after the last pipe.
        # Otherwise, remove the match completely.
        new_text = pattern.sub(lambda m: m.group(1).split('|')[-1].strip() if '|' in m.group(1) else "", text)
        if new_text == text:
            break
        text = new_text
    return text.strip()

def remove_formatting_recursive(val):
    if isinstance(val, str):
        return remove_elicit_formatting(val)
    elif isinstance(val, dict):
        return {k: remove_formatting_recursive(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [remove_formatting_recursive(item) for item in val]
    else:
        return val

def remove_html_tags(text: str) -> str:
    return re.sub(r'<[^>]+>', '', text)

def clean_multi_answer_value(val):
    """
    If val is a dict containing a "Tags" key (as in a ListSelect component),
    clean the "Label" fields while preserving other fields such as "Id", "Kind", and "Selected".
    Otherwise, fall back to the generic recursive cleaning.
    """
    if isinstance(val, dict) and "Tags" in val and isinstance(val["Tags"], list):
        cleaned_tags = []
        for tag in val["Tags"]:
            # Make a copy so we don't modify the original.
            cleaned_tag = tag.copy()
            if "Label" in cleaned_tag and isinstance(cleaned_tag["Label"], str):
                # Remove elicit formatting and HTML tags from the Label.
                cleaned_tag["Label"] = remove_elicit_formatting(cleaned_tag["Label"])
                cleaned_tag["Label"] = remove_html_tags(cleaned_tag["Label"])
            cleaned_tags.append(cleaned_tag)
        new_val = val.copy()
        new_val["Tags"] = cleaned_tags
        return new_val
    else:
        return remove_formatting_recursive(val)

def process_datetime(dt):
    """
    Converts various datetime formats into:
      - A raw numerical timestamp (seconds since epoch)
      - A cleaned ISO 8601 string WITHOUT timezone info
    Ensures compatibility across all functions using this.
    """
    if dt is None:
        return None, None  # Handle missing timestamps safely

    fmt = "%Y-%m-%dT%H:%M:%S.%f"  # Ensure microsecond precision
    raw = None
    iso = None

    try:
        # Handle pyswagger.primitives._time.Datetime
        if isinstance(dt, pyswagger.primitives._time.Datetime):
            dt = dt.to_json()  # Convert to string

        if isinstance(dt, (int, float)):  # Unix timestamp
            d = datetime.utcfromtimestamp(dt)
            raw = d.timestamp()
            iso = d.strftime(fmt)

        elif isinstance(dt, str):  # String timestamps
            dt_cleaned = dt.replace("Z", "").replace("+00:00", "")  # Remove timezone offsets
            d = isoparse(dt_cleaned)
            raw = d.timestamp()
            iso = d.strftime(fmt)

        elif isinstance(dt, datetime):  # Already a datetime object
            d = dt.replace(tzinfo=None)  # Ensure timezone is removed
            raw = d.timestamp()
            iso = d.strftime(fmt)

        if raw is None or iso is None:
            raise ValueError("Conversion failed")

    except Exception as e:
        print(f"⚠️ Could not parse datetime: {dt} → Error: {e}")
        return None, None  # Prevent breaking the script

    return raw, iso

def debug_log(message):
    if args.debug:
        print(message)

def extract_selected_info(val):
    """
    Expects val to be a dict with a "Tags" key (as in a ListSelect component).
    Returns a tuple (indices, labels) where:
      - indices: a list of zero-based positions for which 'Selected' is True.
      - labels: a list of the cleaned labels corresponding to those selected tags.
    """
    indices = []
    labels = []
    if isinstance(val, dict) and "Tags" in val and isinstance(val["Tags"], list):
        for i, tag in enumerate(val["Tags"]):
            if tag.get("Selected"):
                indices.append(i)
                # Clean the label using your formatting removal functions.
                label = tag.get("Label", "")
                # Remove elicit formatting and HTML tags:
                label = remove_elicit_formatting(label)
                label = remove_html_tags(label)
                labels.append(label)
    return indices, labels

def ensure_study_info(el, study_id, result_path_generator: ResultPathGenerator = None):
    filename = result_path_generator.result_path_for(f"study_{study_id}.yaml")
    if os.path.exists(filename):
        print(f"Using existing study info file {filename}")
        return yaml.safe_load(open(filename, 'r'))
    else:
        print(f"Generating study info file {filename}")
        study_info = dump_study_definition(elicit, el, study_id)
        with open(filename, 'w') as file:
            yaml.dump(json.loads(json.dumps(study_info)), file)
        return study_info


def face_landmark_summary(data_points):
    summary_data_points = []

    for summary in data_points:
        if summary['point_type'] == 'send_points_summary' and summary['kind'] == 'face_landmark':
            summary_data_points.append({
                'datetime': summary['datetime'],
                'queued': summary['value']['queued'],
                'posted': summary['value']['posted'],
                'acknowledged': summary['value']['acknowledged'],
                'posted_bytes': summary['value']['posted_bytes'],
                'posted_compressed_bytes': summary['value']['posted_compressed_bytes'],
                'acknowledged_bytes': summary['value']['acknowledged_bytes'],
                'acknowledged_compressed_bytes': summary['value']['acknowledged_compressed_bytes'],
            })

    return pd.DataFrame(summary_data_points)

def analyze_landmarker_summary(datapoints, user_id):
    """
    Finds the landmarker summary datapoints and extracts them for analysis in order to provide a quick overview of the experiment.
    Analyzes and filters data points for specific 'point_type' values:
    'face_landmark_lifecycle_start' and 'face_landmark_lifecycle_end'.
    """

    start = list(
        filter(lambda dp: dp['point_type'] in ['face_landmark_lifecycle_start'],
               datapoints))
    end = list(
        filter(lambda dp: dp['point_type'] in ['face_landmark_lifecycle_stop'],
               datapoints))

    if len(start) != 1:
       return None, None, None

    print(f"\n\nFACE LANDMARK SUMMARY for user {user_id}\n\n")

    landmarker_configuration = start[0]['value']
    print(f"Landmarker configuration: {landmarker_configuration}\n")

    if len(end) != 1:
        return landmarker_configuration, None, None

    time_range = end[0]['datetime'] - start[0]['datetime']

    face_landmark_summary_df = face_landmark_summary(datapoints)
    if not face_landmark_summary_df.empty:
        print('Aggregate values for entire experiment')
        pp.pprint(face_landmark_summary_df.drop('datetime', axis=1).sum())
        print('\nRates count/s')
        pp.pprint(face_landmark_summary_df.drop('datetime', axis=1).sum() / time_range)
        print("\n")

    return landmarker_configuration, time_range, face_landmark_summary_df


def mouse_tracking_summary(data_points):
    summary_data_points = []

    for summary in data_points:
        if summary['point_type'] == 'send_points_summary' and summary['kind'] == 'mouse':
            summary_data_points.append({
                'datetime': summary['datetime'],
                'count': summary['value']['numPoints'],
            })

    return pd.DataFrame(summary_data_points)

def analyze_mouse_tracking_summary(datapoints, user_id):
    """
    Finds the mouse summary datapoints and extracts them for analysis in order to provide a quick overview of the experiment.
    """

    start = list(
        filter(lambda dp: dp['point_type'] in ['mouse_tracking_lifecycle_start'],
               datapoints))
    end = list(
        filter(lambda dp: dp['point_type'] in ['mouse_tracking_lifecycle_stop'],
               datapoints))

    if len(start) != 1:
       return None, None, None

    mouse_tracking_configuration = start[0]['value']
    print(f"\n\nMOUSE TRACKING SUMMARY for user {user_id}\n\n")

    print(f"Landmarker configuration: {mouse_tracking_configuration}\n")

    if len(end) != 1:
        return mouse_tracking_configuration, None, None

    duration = end[0]['datetime'] - start[0]['datetime']

    mouse_tracking_summary_df = mouse_tracking_summary(datapoints)
    if not mouse_tracking_summary_df.empty:
        print('Aggregate values for entire experiment')
        pp.pprint(mouse_tracking_summary_df.drop('datetime', axis=1).sum())
        print('\nRates count/s')
        pp.pprint(mouse_tracking_summary_df.drop('datetime', axis=1).sum() / duration)
        print("\n")

    return mouse_tracking_configuration, duration, mouse_tracking_summary_df

def fetch_datapoints(study_result: pyswagger.primitives.Model, experiment: dict, trial_result: dict, protocol_user_id: int, user_id: int) -> list[dict]:
    """
           Fetch datapoints for an experiment and trial result.

           Args:
               experiment (dict): Experiment data.
               trial_result (dict): Trial result data.
               protocol_user_id (int): ID of the protocol user.
               user_id (int): ID of the user.

           Returns:
               list[dict]: List of datapoints.
           """
    ...

    response_data_points = []
    page = 1
    page_size = 1000
    while True:
        dps = el.find_data_points(study_result_id=study_result.id,
                                  trial_definition_id=trial_result.trial_definition_id,
                                  protocol_user_id=protocol_user_id,
                                  page_size=page_size, page=page)
        response_data_points += dps
        if len(dps) < page_size:
            break
        page += 1

    debug_log(f"Got {len(response_data_points)} datapoints for study result {study_result.id}, trial result {trial_result.id} protocol user {protocol_user_id}")

    make_data_point_row = lambda data_point: ({
        "datetime": data_point.datetime,
        "experiment_id": experiment.id,
        
        "phase_definition_id": trial_result.phase_definition_id,
        "trial_definition_id": trial_result.trial_definition_id,
        "component_id": data_point['component_id'],
        "study_result_id": study_result.id,
        "id": data_point.id,
        "protocol_user_id": protocol_user_id,
        "user_id": user_id,        
        "point_type": data_point.point_type,
        "kind": data_point.kind,
        "method": data_point.method,
        "entity_type": data_point.entity_type,
        "value": data_point.value,
    })

    # ids = [x.id for x in response_data_points]
    # duplicate_ids = [item for item, count in collections.Counter(ids).items() if count > 1]
    # pp.pprint(duplicate_ids)

    return list(map(make_data_point_row, response_data_points))

    def emit_video_events(data_points, result_path_generator):
        """
        Extracts video-specific events from the data_points and emits them to a CSV file (video_events.csv).
    
        Extracted events include:
        - UNSTARTED
        - PLAYING
        - PAUSED
        - STOPPED
        - ENDED
        - BUFFERING
        - CUED
        - START
        - COMPLETED
    
        """
        video_events = ["UNSTARTED", "PLAYING", "PAUSED", "STOPPED", "ENDED", "BUFFERING", "CUED", "Start", "Stop"]
    
        video_data_points = [dp for dp in data_points if dp['point_type'] in video_events]
    
        if not video_events:
            return
    
        video_event_rows = []
    
        for dp in video_events:
            video_event = OrderedDict()
    
            # Extract basic info
            raw_dt, iso_dt = process_datetime(dp.get('datetime'))
            video_event["datetime"] = raw_dt
            video_event["datestring"] = iso_dt
            video_event["experiment_id"] = dp.get('experiment_id')
            video_event["phase_definition_id"] = dp.get('phase_definition_id')
            video_event["trial_definition_id"] = dp.get('trial_definition_id')
            video_event["component_id"] = dp.get('component_id')
            video_event["study_result_id"] = dp.get('study_result_id')
            video_event["protocol_user_id"] = dp.get('protocol_user_id')
            video_event["user_id"] = dp.get('user_id')
            video_event["id"] = dp.get('id')
            video_event["point_type"] = dp.get('point_type')
            video_event["kind"] = dp.get('kind')
            video_event["method"] = dp.get('method')
            video_event["entity_type"] = dp.get('entity_type')
            video_event["value"] = dp.get('value')
    
            video_events.append(video_event)
    
        return video_events
    
def synthesize_answers(datapoints: list[dict], trial_definitions: pyswagger.primitives.Model):
    """
    Synthesize answers from datapoints & trial/component definitions.
    
    Transforms the data points into a more convenient format by aligning the final state of each 
    component with the render of that component and enriching the result with labels to make 
    the result easier for humans to understand.
    """
    
    # Define the desired column order explicitly.
    desired_order = [
        "datestring", "datetime", "experiment_id", "phase_definition_id", "trial_definition_id", "trial_name",
        "component_id", "id", "study_result_id", "protocol_user_id", "user_id", "answer_component_id",
        "point_type", "kind", "method", "entity_type", 
        "render_id", "render_label", "component_name", "HeaderLabel", "value", "answer_id", "answer",
    ]
    
    answer_datapoints = list(filter(lambda row: row['point_type'] in ['State', 'Render'], datapoints))
    grouped_answer_datapoints = {}
    for data_point in answer_datapoints:
        comp_id = data_point['component_id']
        grouped_answer_datapoints.setdefault(comp_id, []).append(data_point)
        
    answers = []
    for answer_component_id, group in grouped_answer_datapoints.items():
        render_answer_datapoints = [row for row in group if row['point_type'] == 'Render']
        state_answer_datapoints = [row for row in group if row['point_type'] == 'State']
        
        if not state_answer_datapoints and not render_answer_datapoints:
            print("WARN: Found answer datapoints for component %d without both Render and State datapoints" % answer_component_id)
            continue

        # Use state answer datapoint if available, else render datapoint.
        if state_answer_datapoints:
            base_answer = state_answer_datapoints[0]
        else:
            base_answer = render_answer_datapoints[0]

        # Build a new OrderedDict in the desired order.
        new_answer = OrderedDict()
        for key in desired_order:
            new_answer[key] = base_answer.get(key, None)
        
        kind = base_answer.get("kind", "")
        
        # Branch based on component kind.
        if kind in ["CheckBoxGroup"]:
            try:
                if isinstance(base_answer.get('value'), dict):
                    state_values = base_answer['value']
                else:
                    state_values = json.loads(base_answer.get('value'))
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Error decoding JSON from base_answer['value'] for CheckBoxGroup: {e} {base_answer}")
                state_values = {}
        
            cleaned_state_values = remove_formatting_recursive(state_values)
            new_answer["value"] = cleaned_state_values
        
            # Convert selections to ints.
            selections = cleaned_state_values.get("Selections", [])
            try:
                selected_ids = [int(s) for s in selections]
            except Exception:
                selected_ids = selections
            new_answer["answer_id"] = selected_ids
        
            if render_answer_datapoints:
                try:
                    render_value = render_answer_datapoints[0].get("value")
                    if isinstance(render_value, str):
                        render_options = json.loads(render_value)
                    else:
                        render_options = render_value
                except Exception as e:
                    print(f"Error decoding Render value for CheckBoxGroup: {e}")
                    render_options = []
        
                all_rendered_ids = []
                all_rendered_labels = []
                selected_labels = []
                for opt in render_options:
                    # Get the rendered ID, remove formatting, and then try to convert to int.
                    rid_str = str(opt.get("Id", "")).strip()
                    cleaned_rid_str = remove_elicit_formatting(rid_str)
                    try:
                        rid_int = int(cleaned_rid_str)
                    except ValueError:
                        rid_int = cleaned_rid_str  # fallback if conversion fails.
                    all_rendered_ids.append(rid_int)
        
                    # Clean the rendered label.
                    raw_label = opt.get("Label", "")
                    cleaned_label = remove_elicit_formatting(raw_label)
                    cleaned_label = remove_html_tags(cleaned_label)
                    all_rendered_labels.append(cleaned_label)
        
                    # Check if the rendered ID is in the list of selected IDs.
                    if rid_int in selected_ids:
                        selected_labels.append(cleaned_label)
                
                new_answer["render_id"] = all_rendered_ids
                new_answer["render_label"] = all_rendered_labels
                new_answer["answer"] = selected_labels
            else:
                new_answer["render_id"] = []
                new_answer["render_label"] = []
                new_answer["answer"] = selections

        elif kind in ["RadioButtonGroup"]:
            # Process state value.
            try:
                if isinstance(base_answer.get('value'), dict):
                    state_values = base_answer['value']
                else:
                    state_values = json.loads(base_answer.get('value'))
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Error decoding JSON from base_answer['value'] for RadioButtonGroup: {e} {base_answer}")
                state_values = {}
            
            if 'Id' not in state_values:
                continue
        
            try:
                answer_id = int(state_values['Id'])
            except ValueError:
                print(f"WARN: Found answer datapoint for RadioButtonGroup with Id {state_values['Id']} but it is not an integer")
                answer_id = state_values['Id']
            
            # Process the raw value.
            value = base_answer.get("value")
            if isinstance(value, str):
                new_answer["value"] = remove_elicit_formatting(value)
            else:
                new_answer["value"] = remove_formatting_recursive(value)
            new_answer["answer_id"] = answer_id
            new_answer["answer"] = state_values['Id']  # default to the raw value for now
        
            # Process the Render datapoint.
            if render_answer_datapoints:
                try:
                    render_value = render_answer_datapoints[0].get("value")
                    if isinstance(render_value, str):
                        render_options = json.loads(render_value)
                    else:
                        render_options = render_value
                except Exception as e:
                    print(f"Error decoding Render value for RadioButtonGroup: {e}")
                    render_options = []
                
                all_rendered_ids = []
                all_rendered_labels = []
                selected_label = None
                for opt in render_options:
                    # Get and clean the rendered ID.
                    rid_str = str(opt.get("Id", "")).strip()
                    cleaned_rid_str = remove_elicit_formatting(rid_str)
                    try:
                        rid_int = int(cleaned_rid_str)
                    except ValueError:
                        rid_int = cleaned_rid_str
                    all_rendered_ids.append(rid_int)
                    
                    # Clean the rendered label.
                    raw_label = opt.get("Label", "")
                    cleaned_label = remove_elicit_formatting(raw_label)
                    cleaned_label = remove_html_tags(cleaned_label)
                    all_rendered_labels.append(cleaned_label)
                    
                    # If this option's ID matches the answer_id, record its label.
                    if rid_int == answer_id:
                        selected_label = cleaned_label
                
                new_answer["render_id"] = all_rendered_ids
                new_answer["render_label"] = all_rendered_labels
                if selected_label is not None:
                    new_answer["answer"] = selected_label
                else:
                    new_answer["answer"] = state_values['Id']
            else:
                new_answer["render_id"] = []
                new_answer["render_label"] = []
                
        elif kind in ["ListSelect", "Main_ListSelect_ListSelect"]:
                    try:
                        if isinstance(base_answer.get('value'), dict):
                            state_values = base_answer['value']
                        else:
                            state_values = json.loads(base_answer.get('value'))
                    except (json.JSONDecodeError, TypeError) as e:
                        print(f"Error decoding JSON from base_answer['value'] for ListSelect: {e} {base_answer}")
                        state_values = {}
                    
                    cleaned_state_values = remove_formatting_recursive(state_values)
                    new_answer["value"] = cleaned_state_values
        
                    # For ListSelect, expect structure like {'Tags': [ { 'Id': '1', 'Label': ..., 'Selected': True}, ... ]}
                    indices = []
                    labels = []
                    tags = cleaned_state_values.get("Tags", [])
                    for i, tag in enumerate(tags):
                        if tag.get("Selected"):
                            indices.append(i)
                            label = tag.get("Label", "")
                            label = remove_elicit_formatting(label)
                            label = remove_html_tags(label)
                            labels.append(label)
                    new_answer["answer_id"] = indices
                    new_answer["answer"] = labels
        elif kind in ["Freetext"]:
            try:
                value_field = base_answer.get("value")
                if isinstance(value_field, str):
                    state_obj = json.loads(value_field)
                else:
                    state_obj = value_field
            except Exception as e:
                print(f"Error decoding Freetext state: {e}")
                state_obj = {}
        
            try:
                render_obj = {}
                if render_answer_datapoints:
                    render_field = render_answer_datapoints[0].get("value")
                    if isinstance(render_field, str):
                        render_obj = json.loads(render_field)
                    else:
                        render_obj = render_field
            except Exception as e:
                print(f"Error decoding Freetext render: {e}")
                render_obj = {}
        
            # For Freetext, we want to use the state object's "Text" field for the answer.
            raw_text = state_obj.get("Text", "")
            cleaned_text = raw_text
            if isinstance(raw_text, str):
                cleaned_text = remove_elicit_formatting(raw_text)
                cleaned_text = remove_html_tags(cleaned_text)
            
            # Set value, answer_id, and answer to the cleaned text from the state.
            new_answer["value"] = cleaned_text
            new_answer["answer_id"] = cleaned_text
            new_answer["answer"] = cleaned_text
        
            # Use the render event to set render_label (if available).
            if render_obj:
                render_text = render_obj.get("Text", "")
                cleaned_render_text = render_text
                if isinstance(render_text, str):
                    cleaned_render_text = remove_elicit_formatting(render_text)
                    cleaned_render_text = remove_html_tags(cleaned_render_text)
                new_answer["render_id"] = []  # No IDs for Freetext.
                new_answer["render_label"] = [cleaned_render_text]
            else:
                new_answer["render_id"] = []
                new_answer["render_label"] = []

        else:
            # For single-answer components (e.g., LikertScale, RadioButtonGroup).
            if isinstance(base_answer.get('value'), dict):
                state_values = base_answer['value']
            else:
                try:
                    state_values = json.loads(base_answer.get('value'))
                except (json.JSONDecodeError, TypeError) as e:
                    print(f"Error decoding JSON from base_answer['value']: {e} {base_answer}")
                    state_values = {}
            
            if 'Id' not in state_values:
                continue

            try:
                answer_id = int(state_values['Id'])
            except ValueError:
                print(f"WARN: Found answer datapoint for component {answer_component_id} with Id {state_values['Id']} but it is not an integer")
                answer_id = state_values['Id']
            
            value = base_answer.get("value")
            if isinstance(value, str):
                new_answer["value"] = remove_elicit_formatting(value)
            else:
                new_answer["value"] = remove_formatting_recursive(value)
            new_answer["answer_id"] = state_values['Id']
            new_answer["answer"] = state_values['Id']

        # Retrieve additional metadata.
        component_name = get_component_name(base_answer['trial_definition_id'], answer_component_id, trial_definitions)
        header_label = remove_elicit_formatting(get_component_header_label(base_answer['trial_definition_id'], answer_component_id, trial_definitions))
        trial_name = get_trial_name(base_answer['trial_definition_id'], trial_definitions)
        
        new_answer["HeaderLabel"] = header_label
        new_answer["trial_name"] = trial_name
        #new_answer["render_id"] = None
        #new_answer["render_label"] = None
        new_answer["component_name"] = component_name
        new_answer["answer_component_id"] = answer_component_id

        # Process datetime.
        raw_dt, iso_dt = process_datetime(base_answer.get("datetime"))
        new_answer["datetime"] = raw_dt
        new_answer["datestring"] = iso_dt

        answers.append(new_answer)
    return answers
    
def get_trial_name(trial_definition_id, trial_definitions):
        trial_def = trial_definitions.get(trial_definition_id, {})
        return trial_def.get("name", "")
    
def get_component_name(trial_definition_id, answer_component_id, trial_definitions):
        component_name = ''
        for component in trial_definitions[trial_definition_id]['components']:
            if component['id'] == answer_component_id:
                # def_data = json.loads(component['definition_data'])['Instruments'][0]['Instrument']
                # component_name = next(iter(def_data.values()))['HeaderLabel']
                component_name = component['name']
        return component_name
    
def get_component_header_label(trial_definition_id, answer_component_id, trial_definitions):
        header_label = ''
        # Loop over components in the specified trial definition.
        for component in trial_definitions[trial_definition_id]['components']:
            if component['id'] == answer_component_id:
                # Get the definition_data which might be a dictionary or JSON string.
                def_data = component.get('definition_data')
                if isinstance(def_data, str):
                    try:
                        def_data = json.loads(def_data)
                    except Exception as e:
                        print("Error parsing definition_data:", e)
                        return header_label
                # Look for the Instruments key.
                instruments = def_data.get('Instruments')
                if instruments and isinstance(instruments, list) and len(instruments) > 0:
                    # Get the first instrument.
                    instrument_data = instruments[0].get('Instrument')
                    if instrument_data and isinstance(instrument_data, dict):
                        # There could be different instrument types.
                        # Loop over the instrument types and extract HeaderLabel from the first one.
                        for instrument_key, instrument in instrument_data.items():
                            header_label = instrument.get('HeaderLabel', '')
                            break  # Found the first instrument, break out.
                break
        return header_label

def fetch_all_time_series(study_result, experiment):
    user_id = experiment['protocol_user']['user_id']

    stages = el.find_stages(study_result_id=study_result.id, experiment_id=experiment.id)
    print("\n\nSTAGES\n\n")
    if args.debug:
        print(stages)
    else:
        print(f"\tGot {len(stages)} stages for experiment {experiment.id}: #{[stage.id for stage in stages]}")

    experiment_time_series = {}

    for stage_id in (stage.id for stage in stages):
        time_series = el.find_time_series(study_result_id=study_result.id, stage_id=stage_id)

        if len(time_series) < 1:
            print(f"       No time series for stage {stage_id} (user {user_id})\n")
            continue

        print(
            f"        Got {len(time_series)} time series for stage {stage_id} (user {user_id}). {['%s (%s)' % (ts.id, ts.series_type) for ts in time_series]}\n")

        for time_series in time_series:
            url = time_series.file_url

            base_filename = result_path_generator.result_path_for(f"{args.study_id}_{user_id}_", user_id=user_id)
            query_filename = base_filename + time_series.series_type + "." + time_series.file_type

            final_filename = fetch_time_series(url, time_series.file_type, base_filename=base_filename,
                                               filename=query_filename, authorization=el.auth_header(),
                                               verify=True)

            # Move the file to the preferred naming convention.
            shutil.move(final_filename, query_filename)
            final_filename = query_filename

            if time_series.series_type == 'face_landmark':
                if time_series.file_type == 'msgpack':
                    ndjson_filename = final_filename.replace('.msgpack', '.ndjson')

                    convert_msgpack_to_ndjson(final_filename, ndjson_filename)
                else:
                    ndjson_filename = final_filename

                uncompressed_filename = final_filename.replace('face_landmark.json',
                                                               'face_landmark_uncompressed.json')

                print(f"        Processing face landmark data for stage {stage_id} (user {user_id}) {time_series.file_type} to {uncompressed_filename}")

                with open(uncompressed_filename, 'a') as uncompressed_file:
                    with open(ndjson_filename, 'r') as ndjson_file:
                        try:
                            for line in ndjson_file:
                                stripped_line = line.strip()
                                if stripped_line == '':
                                    continue
                                try:
                                    data = json.loads(stripped_line)
                                    transformed_data = json.dumps(uncompress_datapoint(data))

                                    if transformed_data != '':
                                        uncompressed_file.write(transformed_data + '\n')
                                    else:
                                        print(f"WARN: Skipping empty line in {ndjson_filename} for {data}")
                                    final_filename = uncompressed_filename
                                except json.JSONDecodeError:
                                    print(f"Error: Line '{stripped_line}' is not valid JSON.")
                        except Exception as e:
                            print(f"Error maybe uncompressed file #{ndjson_filename}: {e}")
            else:
                print(f"        Skipping face landmark data for stage {stage_id} (user {user_id}), type {time_series.series_type}")

            experiment_time_series[time_series.series_type] = {
                "filename": final_filename,
            }

    return experiment_time_series

def analyze_and_dump_user_data_points(user_datapoints, user_id):
    """Dump json data points for a single user."""
    with open(result_path_generator.result_path_for(f"{args.study_id}_{user_id}_datapoints.json", user_id), 'w') as outfile:
        list(map(lambda row: row.update({"datetime": row["datetime"].v.timestamp()}), user_datapoints))
        list(map(lambda row: row.update({"value": json.loads(row["value"])}) if row['value'].startswith(
            '{"') else row, user_datapoints))
        json.dump(user_datapoints, outfile, indent=2)

        print(
            f"Wrote {len(user_datapoints)} datapoints for user {user_id} to {result_path_generator.result_path_for('datapoints.json', user_id)}")

        landmarker_configuration, duration, summary_df = analyze_landmarker_summary(user_datapoints, user_id)
        collector.add_landmarker_configuration(user_id, landmarker_configuration, duration, summary_df)

        mouse_tracking_configuration, duration, summary_df = analyze_mouse_tracking_summary(user_datapoints, user_id)
        collector.add_mouse_tracking_summary(user_id, mouse_tracking_configuration, duration, summary_df)


def process(collector: ResultCollector, results_path_generator: ResultPathGenerator):
    study_results = el.find_study_results(study_definition_id=args.study_id)
    study_info = ensure_study_info(el, args.study_id, results_path_generator)
    phase_definition = study_info['protocol_definitions'][0]['phase_definitions'][0]
    trial_definitions = {}
    for trial_def in phase_definition["trial_definitions"]:
        if 'id' in trial_def:
            trial_definitions[trial_def['id']] = trial_def

    collector.trial_definitions = trial_definitions
    print("\n\nSTUDY_RESULTS\n\n")
    if args.debug:
        pp.pprint([with_dates(study_result) for study_result in study_results])
    else:
        print(f"\tGot {len(study_results)} study results: #{[study_result.id for study_result in study_results]}")

    for study_result in study_results:
        experiments = el.find_experiments(study_result_id=study_result.id)

        print("\n\nEXPERIMENTS\n\n")

        if args.debug:
            pp.pprint([with_dates(experiment) for experiment in experiments])
        else:
            print(f"\tGot {len(experiments)} experiments for study result {study_result.id}")

        for experiment in experiments:
            user_id = experiment['protocol_user']['user_id']

            if args.user_id and args.user_id != user_id:
                print("Skipping user %d (not %d)" % (user_id, args.user_id))
                continue

            experiment_time_series = fetch_all_time_series(study_result, experiment)
            collector.add_experiment_event(experiment, experiment_time_series)

            trial_results = el.find_trial_results(study_result_id=study_result.id, experiment_id=experiment.id)

            collector.add_trial_results(experiment, trial_results, trial_definitions)

            user_datapoints = []
            for trial_result in trial_results:
                response_data_points = fetch_datapoints(study_result, experiment, trial_result, trial_result.protocol_user_id, user_id)
                user_datapoints += response_data_points

                collector.add_data_points(experiment, trial_result, response_data_points)
                print(f"        Got {len(response_data_points)} data points for trial {trial_result.id} (user {user_id})")

            analyze_and_dump_user_data_points(user_datapoints, user_id)
            for answer in synthesize_answers(user_datapoints, trial_definitions):
                collector.add_answer(answer)


##
## MAIN
##

pp = pprint.PrettyPrinter(indent=4)

command_line.init_parser({"env": (arg_defaults.get("env") or "prod")}) # Allow the script to be reentrant: start with a fresh parser every time,
command_line.parser.add_argument(
    '--study_id', default=arg_defaults["study_id"], help="The study ID to dump", type=int)
command_line.parser.add_argument(
    '--user_id', default=arg_defaults["user_id"], help="The user ID to dump", type=int)
command_line.parser.add_argument(
    '--user_name', default=None, help="The user name to dump")
command_line.parser.add_argument(
    '--result_root_dir', default=arg_defaults.get("result_root_dir") or "results", help="The root folder to dump to")
args = command_line.parse_command_line_args(arg_defaults)
pp.pprint(args)

el = elicit.Elicit(args)
client = el.client

#
# Double-check that we have the right user
#

user = el.assert_creator()

if __name__ == "__main__":
    print("\nExecution of dump_results.py script started...")

    result_path_generator = ResultPathGenerator(args.result_root_dir, args.study_id)
    collector = ResultCollector(result_path_generator)

    process(collector, result_path_generator)

    collector.emit()
    print("\nExecution completed. Results have been emitted.")
