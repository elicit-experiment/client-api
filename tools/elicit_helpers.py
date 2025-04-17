import pprint
import re
import time
import pyswagger.primitives
import filecmp
import json
import os
import shutil
import yaml
import csv
import pandas as pd
import datetime as dt
import numpy as np
from datetime import datetime
from dateutil.parser import isoparse
from dateutil.tz import tzutc
from result_path_generator import ResultPathGenerator
from pyelicit import elicit
from dump_time_series import convert_msgpack_to_ndjson, uncompress_datapoint, fetch_time_series
from study_definition_helpers import dump_study_definition
from collections import OrderedDict

pp = pprint.PrettyPrinter(indent=4)

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

ISO_FMT = "%Y-%m-%dT%H:%M:%S.%f"   # we’ll trim to 3 ms digits later

def process_datetime(value):
    """
    Convert *anything* to UTC.

    Accepts
      • int / float  – epoch (s or ms)
      • str          – ISO‑8601 (tz‑aware OR naïve)
      • datetime     – tz‑aware OR naïve
      • pyswagger.primitives._time.Datetime

    Returns (epoch_seconds_UTC, iso_string_UTC_no_tz) or (None, None) on failure.

    The iso string always shows millisecond precision and NO timezone suffix,
    e.g.  '2025-03-15T18:09:18.162'
    """
    if value is None:
        return None, None

    try:
        # ------------------------------------------------------------------ #
        # Swagger helper
        # ------------------------------------------------------------------ #
        if isinstance(value, pyswagger.primitives._time.Datetime):
            value = value.to_json()

        # ------------------------------------------------------------------ #
        # 1. numeric epoch
        # ------------------------------------------------------------------ #
        if isinstance(value, (int, float)):
            ts = value / 1000.0 if value > 1e11 else float(value)
            d_utc = dt.datetime.utcfromtimestamp(ts).replace(tzinfo=tzutc())

        # ------------------------------------------------------------------ #
        # 2. ISO string
        # ------------------------------------------------------------------ #
        elif isinstance(value, str):
            d = isoparse(value)
            # if the string is naïve, treat it as UTC
            if d.tzinfo is None:
                d_utc = d.replace(tzinfo=tzutc())
            else:
                d_utc = d.astimezone(tzutc())

        # ------------------------------------------------------------------ #
        # 3. datetime object
        # ------------------------------------------------------------------ #
        elif isinstance(value, dt.datetime):
            if value.tzinfo is None:
                d_utc = value.replace(tzinfo=tzutc())
            else:
                d_utc = value.astimezone(tzutc())

        else:
            raise TypeError(f"Unsupported type: {type(value)}")

        # ------------------------------------------------------------------ #
        # final canonical outputs
        # ------------------------------------------------------------------ #
        epoch = d_utc.timestamp()

        # make an ISO string **without tzinfo** but still representing UTC time
        naive_utc = d_utc.replace(tzinfo=None)
        iso = naive_utc.strftime(ISO_FMT)[:-3]   # keep exactly 3 ms digits

        return epoch, iso

    except Exception as e:
        print(f"⚠️ Could not parse datetime: {value} → {e}")
        return None, None

def remove_file_retry(filepath, retries=5, delay=0.5):
    for attempt in range(retries):
        try:
            os.remove(filepath)
            return True
        except PermissionError as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise e
                
def safe_copy_and_remove(src, dst):
    if os.path.exists(dst):
        if filecmp.cmp(src, dst, shallow=False):
            if os.path.abspath(src) != os.path.abspath(dst):
                remove_file_retry(src)
            return dst
        else:
            remove_file_retry(dst)
    shutil.copy(src, dst)
    if os.path.abspath(src) != os.path.abspath(dst):
        remove_file_retry(src)
    return dst
    
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

def face_landmark_event_summary(data_points):
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

def analyze_landmarker_event_summary(datapoints, user_id):
    """
    Finds the landmarker summary datapoints and extracts them for analysis in order to provide a quick overview of the experiment.
    Analyzes and filters data points for specific 'point_type' values:
    'face_landmark_lifecycle_start' and 'face_landmark_lifecycle_end'.
    """

    start = sorted(
        filter(lambda dp: dp['point_type'] in ['face_landmark_lifecycle_start'],
               datapoints),
        key=lambda dp: dp['datetime']
    )
    end = sorted(
        filter(lambda dp: dp['point_type'] in ['face_landmark_lifecycle_stop'],
               datapoints),
        key=lambda dp: dp['datetime'],
        reverse=True
    )

    if (len(start) != 1) or (len(end) != 1):
        print(f"\tUnexpected number of start/end datapoints found for user {user_id}: {len(start)} start, {len(end)} end")

    if len(start) == 0:
       print(f"No start datapoint `face_landmark_lifecycle_start` found for user {user_id}")
       return None, None, None

    print(f"\n\nFACE LANDMARK SUMMARY for user {user_id}\n\n")

    landmarker_configuration = start[0]['value']
    print(f"Landmarker configuration: {landmarker_configuration}\n")

    face_landmark_event_summary_df = face_landmark_event_summary(datapoints)

    if len(end) == 0:
        print(f"No end datapoint `face_landmark_lifecycle_stop` found for user {user_id}")
        if len(face_landmark_event_summary_df) == 0:
            return landmarker_configuration, None, None
        face_landmark_event_summary_df = face_landmark_event_summary_df.sort_values(by='datetime')
        time_range = face_landmark_event_summary_df.iloc[-1]['datetime'] - face_landmark_event_summary_df.iloc[0]['datetime']
    else:
        time_range = end[0]['datetime'] - start[0]['datetime']

    if not face_landmark_event_summary_df.empty:
        print(f'Aggregate values for entire experiment {time_range}s')
        pp.pprint(face_landmark_event_summary_df.drop('datetime', axis=1).sum())
        print('\nRates count/s')
        pp.pprint(face_landmark_event_summary_df.drop('datetime', axis=1).sum() / time_range)
        print("\n")

    return landmarker_configuration, time_range, face_landmark_event_summary_df


def mouse_tracking_event_summary(data_points):
    summary_data_points = []

    for summary in data_points:
        if summary['point_type'] == 'send_points_summary' and summary['kind'] == 'mouse':
            summary_data_points.append({
                'datetime': summary['datetime'],
                'count': summary['value']['numPoints'],
            })

    return pd.DataFrame(summary_data_points)

def analyze_mouse_tracking_event_summary(datapoints, user_id):
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

    mouse_tracking_event_summary_df = mouse_tracking_event_summary(datapoints)
    if not mouse_tracking_event_summary_df.empty:
        print('Aggregate values for entire experiment')
        pp.pprint(mouse_tracking_event_summary_df.drop('datetime', axis=1).sum())
        print('\nRates count/s')
        pp.pprint(mouse_tracking_event_summary_df.drop('datetime', axis=1).sum() / duration)
        print("\n")

    return mouse_tracking_configuration, duration, mouse_tracking_event_summary_df

def fetch_datapoints(el, study_result, experiment, trial_result, protocol_user_id, user_id):
    """
    Fetch datapoints for an experiment and trial result, converting their 'datetime' to a float and an ISO string.
    Also parse 'value' into a dict if it's JSON.
    """
    response_data_points = []
    page = 1
    page_size = 1000

    while True:
        dps = el.find_data_points(
            study_result_id=study_result.id,
            trial_definition_id=trial_result.trial_definition_id,
            protocol_user_id=protocol_user_id,
            page_size=page_size,
            page=page
        )
        response_data_points += dps
        if len(dps) < page_size:
            break
        page += 1

    print(f"\tGot {len(response_data_points)} datapoints for study result {study_result.id}, trial result {trial_result.id} protocol user {protocol_user_id}")

    mapped_data_points = []
    for raw_dp in response_data_points:
        # Convert the pyswagger datetime to (float, iso)
        raw_ts, iso_ts = process_datetime(raw_dp.datetime)

        dp = {
            "datetime": raw_ts,    # float in seconds since epoch
            "datestring": iso_ts,  # ISO8601 with no tz
            "experiment_id": experiment.id,
            "phase_definition_id": trial_result.phase_definition_id,
            "trial_definition_id": trial_result.trial_definition_id,
            "component_id": raw_dp['component_id'],
            "study_result_id": study_result.id,
            "id": raw_dp.id,
            "protocol_user_id": protocol_user_id,
            "user_id": user_id,
            "point_type": raw_dp.point_type,
            "kind": raw_dp.kind,
            "method": raw_dp.method,
            "entity_type": raw_dp.entity_type,
            "value": raw_dp.value,
        }

        # If 'value' is a JSON string, parse it
        if isinstance(dp["value"], str) and dp["value"].startswith("{"):
            try:
                dp["value"] = json.loads(dp["value"])
            except json.JSONDecodeError as e:
                print(f"Warning: unable to parse dp['value'] as JSON (dp id {dp['id']}): {e}")

        mapped_data_points.append(dp)

    return mapped_data_points

def parse_datapoints(user_datapoints, category):
    """
    Filter datapoints from user_datapoints according to the specified category
    and return a tuple (extracted, remaining) without modifying the original list.
    """
    extracted = []
    remaining = []
    for dp in user_datapoints:
        if category == 'face_landmark':
            if dp.get("kind") == "face_landmark":
                extracted.append(dp)
            else:
                remaining.append(dp)
        elif category == 'mouse':
            if dp.get("kind") == "mouse":
                extracted.append(dp)
            else:
                remaining.append(dp)
        elif category == 'face_landmark_calibration':
            if dp.get("kind") == "FaceLandmarkCalibration":
                extracted.append(dp)
            else:
                remaining.append(dp)
        elif category == 'instruments':
            if dp.get("entity_type") == "Instrument":
                extracted.append(dp)
            else:
                remaining.append(dp)
        elif category == 'stimulus':
            if dp.get("entity_type") == "Stimulus":
                extracted.append(dp)
            else:
                remaining.append(dp)
        else:
            remaining.append(dp)
    return extracted, remaining

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
                #print(f"WARN: Found answer datapoint for RadioButtonGroup with Id {state_values['Id']} but it is not an integer")
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

def fetch_all_time_series(el,study_id,study_result, experiment,result_path_generator):
        user_id = experiment['protocol_user']['user_id']
        stages = el.find_stages(study_result_id=study_result.id, experiment_id=experiment.id)
        experiment_time_series = {}

        for stage in stages:
            stage_id = stage.id
            # Ensure time_series_list is a list
            time_series_list = el.find_time_series(study_result_id=study_result.id, stage_id=stage_id) or []
            
            if not time_series_list:
                continue
    
            print(f"Stage {stage_id} (user {user_id}) => {len(time_series_list)} time series")
    
            # Separate them by type
            face_landmark_series = [ts for ts in time_series_list if ts.series_type == 'face_landmark']
            mouse_series = [ts for ts in time_series_list if ts.series_type == 'mouse']
            print(f"Found {len(face_landmark_series)} face_landmark time series and {len(mouse_series)} mouse time series for stage {stage_id}")
    
            # --------------------------------------------------------
            # FACE_LANDMARK
            # --------------------------------------------------------
            face_landmark_uncompressed_file = None
            file_count_face_landmark = 0
            count_points_face_landmark = 0
            intervals_face_landmark_s = []
            timestamp_face_landmark_previous_s = None
            timestamp_face_landmark_s_min = None
            timestamp_face_landmark_s_max = None
    
            if face_landmark_series:
                # Path for the final uncompressed file. 
                base_filename = result_path_generator.result_path_for(f"{study_id}_{user_id}_", subfolder='face_landmark')
                face_landmark_uncompressed_file = os.path.join(
                    base_filename + "face_landmark_uncompressed.json"
                )
    
                # If a leftover file exists from prior runs, remove it so we start fresh
                if os.path.exists(face_landmark_uncompressed_file):
                    os.remove(face_landmark_uncompressed_file)
    
            # Now loop over each face_landmark time series, appending
            for ts in face_landmark_series:
                query_base = result_path_generator.result_path_for(f"{study_id}_{user_id}_", subfolder='face_landmark')
                query_filename = query_base + ts.series_type + "." + ts.file_type
    
                # Download the file
                downloaded_filename = fetch_time_series(
                    url=ts.file_url,
                    file_type=ts.file_type,
                    base_filename=query_base,
                    filename=query_filename,
                    authorization=el.auth_header(),
                    verify=True
                )
                safe_copy_and_remove(downloaded_filename, query_filename)
                final_filename = query_filename
    
                # Possibly convert msgpack -> NDJSON
                if ts.file_type == 'msgpack':
                    ndjson_filename = final_filename.replace('.msgpack', '.ndjson')
                    convert_msgpack_to_ndjson(final_filename, ndjson_filename)
                else:
                    ndjson_filename = final_filename
    
                # Append to the single uncompressed file
                file_count_face_landmark += 1
                local_count = 0
                timestamp_local_min = None
                timestamp_local_max = None
    
                with open(face_landmark_uncompressed_file, 'a') as out_f, open(ndjson_filename, 'r') as in_f:
                    for line in in_f:
                        stripped = line.strip()
                        if not stripped:
                            continue
                        try:
                            data = json.loads(stripped)
                        except json.JSONDecodeError:
                            continue
    
                        data_uncompressed = uncompress_datapoint(data)

                        # Update local stats
                        local_count += 1

                        # get timestamp                        
                        timestamp_face_landmark_ms = data_uncompressed.get("timeStamp")        # original value
                        
                        if timestamp_face_landmark_ms is not None:
                            timestamp_face_landmark_s = timestamp_face_landmark_ms / 1000.0
                        
                            if timestamp_face_landmark_previous_s is not None:
                                    delta_s = timestamp_face_landmark_s - timestamp_face_landmark_previous_s
                                    if delta_s > 0:
                                        intervals_face_landmark_s.append(delta_s)
                            timestamp_face_landmark_previous_s = timestamp_face_landmark_s
    
                            data_row = {"timestamp_ms": timestamp_face_landmark_ms,
                                        "timestamp_s":  timestamp_face_landmark_s,
                                        **data_uncompressed
                                        }
                        
                            # update local min / max (in seconds)
                            if timestamp_local_min is None or timestamp_face_landmark_s < timestamp_local_min:
                                timestamp_local_min = timestamp_face_landmark_s
                            if timestamp_local_max is None or timestamp_face_landmark_s > timestamp_local_max:
                                timestamp_local_max = timestamp_face_landmark_s
    
                        # Write line
                        out_f.write(json.dumps(data_row) + "\n")
    
                # Now merge local stats into the global face-landmark stats
                count_points_face_landmark += local_count
    
                if timestamp_local_min is not None:
                    if timestamp_face_landmark_s_min is None or timestamp_local_min < timestamp_face_landmark_s_min:
                        timestamp_face_landmark_s_min = timestamp_local_min
    
                if timestamp_local_max is not None:
                    if timestamp_face_landmark_s_max is None or timestamp_local_max > timestamp_face_landmark_s_max:
                        timestamp_face_landmark_s_max = timestamp_local_max
    
            # after we processed all face_landmark timestamps for this stage
            if face_landmark_series and count_points_face_landmark > 0:
                if timestamp_face_landmark_s_min is not None and timestamp_face_landmark_s_max is not None:
                    duration_face_landmark_s = timestamp_face_landmark_s_max - timestamp_face_landmark_s_min
                else:
                    duration_face_landmark_s = None
            
                if intervals_face_landmark_s:
                    mean_dt  = np.mean(intervals_face_landmark_s)      # s
                    median_dt = np.median(intervals_face_landmark_s)   # s
                    fs_face_landmark_mean  = 1.0 / mean_dt                                   # Hz
                    fs_face_landmark_median = 1.0 / median_dt                                # Hz
                else:
                    mean_dt = median_dt = fs_face_landmark_mean = fs_face_landmark_median = None
    
                # raw = epoch seconds, iso = string
                datetime_start, datestring_start = process_datetime(timestamp_face_landmark_s_min)
                datetime_end,   datestring_end   = process_datetime(timestamp_face_landmark_s_max)
            
                experiment_time_series["face_landmark"] = {
                    "filename": os.path.basename(face_landmark_uncompressed_file),
                    "file_count":  file_count_face_landmark,
                    "count_points": count_points_face_landmark,
                    "datetime_start": datetime_start,          # seconds since epoch
                    "datetime_end":   datetime_end,
                    "datestring_start": datestring_start,
                    "datestring_end":   datestring_end,
                    "duration": duration_face_landmark_s,   # seconds
                    "fs_mean_hz": fs_face_landmark_mean,
                    "fs_median_hz": fs_face_landmark_median
                }
    
            # --------------------------------------------------------
            # MOUSE
            # --------------------------------------------------------
            mouse_file_count = len(mouse_series)
            if mouse_series:
                base_filename = result_path_generator.result_path_for(f"{study_id}_{user_id}_", subfolder='mouse')
                # If you expect only one mouse time series, simply use that file.
                if mouse_file_count == 1:
                    ts = mouse_series[0]
                    query_filename = base_filename + ts.series_type + "." + ts.file_type
                    downloaded_filename = fetch_time_series(
                        url=ts.file_url,
                        file_type=ts.file_type,
                        base_filename=base_filename,
                        filename=query_filename,
                        authorization=el.auth_header(),
                        verify=True
                    )
                    safe_copy_and_remove(downloaded_filename, query_filename)
                    final_filename = query_filename
    
                    # Compute stats directly from this file.
                    mouse_count_points = 0
                    mouse_ts_min = None
                    mouse_ts_max = None
    
                    with open(final_filename, 'r', encoding='utf-8') as in_f:
                        in_reader = csv.DictReader(in_f, delimiter='\t')
                        for row in in_reader:
                            if (row.get("x", "").lower() == "x" and 
                                row.get("y", "").lower() == "y" and 
                                row.get("timeStamp", "").lower() == "timestamp"):
                                continue
                            try:
                                ts_val = float(row["timeStamp"])
                            except (ValueError, KeyError):
                                continue
                            mouse_count_points += 1
                            if mouse_ts_min is None or ts_val < mouse_ts_min:
                                mouse_ts_min = ts_val
                            if mouse_ts_max is None or ts_val > mouse_ts_max:
                                mouse_ts_max = ts_val
    
                    if mouse_ts_min is not None and mouse_ts_max is not None:
                        mouse_duration_s = (mouse_ts_max - mouse_ts_min) / 1000.0
                        mouse_fs = mouse_count_points / mouse_duration_s if mouse_duration_s > 0 else None
                    else:
                        mouse_duration_s = None
                        mouse_fs = None
    
                    datetime_start,datestring_start = process_datetime(mouse_ts_min)
                    datetime_end,datestring_end = process_datetime(mouse_ts_max)
                    
                    experiment_time_series["mouse"] = {
                        "filename": os.path.basename(final_filename),
                        "file_count": 1,
                        "count_points": mouse_count_points,
                        "datetime_start": datetime_start,
                        "datetime_end": datetime_end,
                        "datestring_start": datestring_start,
                        "datestring_end": datestring_end,
                        "duration": mouse_duration_s,
                        "avg_fs_hz": mouse_fs
                    }
                else:
                    print(f"Warning: Expected only one mouse time series, but found {mouse_file_count}.")
                    # (Optional: add unification logic here if needed)
    
        # Return after processing all stages
        return experiment_time_series

def dump_user_data_points(user_datapoints, study_id, user_id, result_path_generator, suffix=""):
    """
    Dump JSON datapoints for a single user.
    
    The filename is generated as:
      "{study_id}_{user_id}_datapoints{optional_suffix}.json"
    If suffix is provided (for example "mouse"), the filename becomes:
      "{study_id}_{user_id}_datapoints_mouse.json"
    """
    # Build the filename dynamically
    file_suffix = f"_{suffix}" if suffix else ""
    filename = result_path_generator.result_path_for(
        f"{study_id}_{user_id}_datapoints{file_suffix}.json",
        subfolder='datapoints'
    )
    
    with open(filename, 'w') as outfile:
        # Convert datetime to a float timestamp if necessary.
        for row in user_datapoints:
            # If row["datetime"] is a pyswagger datetime, convert it:
            if hasattr(row.get("datetime"), "v"):
                row["datetime"] = row["datetime"].v.timestamp()
            # If value is a JSON string, try to parse it
            if isinstance(row.get("value"), str) and row["value"].startswith("{"):
                try:
                    row["value"] = json.loads(row["value"])
                except json.JSONDecodeError as e:
                    print(f"Warning: unable to parse dp['value'] for dp {row.get('id')}: {e}")
        json.dump(user_datapoints, outfile, indent=2)
    
    print(f"Wrote {len(user_datapoints)} datapoints for user {user_id} to {filename}")