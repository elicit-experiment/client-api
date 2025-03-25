import csv
import json
from datetime import datetime
from collections import OrderedDict
import pandas as pd
import pyswagger.primitives
from dump_utilities import is_video_event
from result_path_generator import ResultPathGenerator
from dateutil.parser import isoparse
from dateutil import parser

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

class ResultCollector:
    def __init__(self, result_path_generator: ResultPathGenerator):
        self.result_path_generator = result_path_generator
        self.answers = []
        self.experiment_events = []
        self.url_parameters = []
        self.trial_results = []
        self.data_points = []
        self.mouse_tracking_summary = []
        self.landmarker_summary = []
        self.trial_definitions = {}
    def emit(self):
        if len(self.answers) > 0:
            self.emit_answers()
        if len(self.experiment_events) > 0:
            self.emit_experiment_events()
        if len(self.url_parameters) > 0:
            self.emit_url_parameters()
        if len(self.trial_results) > 0:
            self.emit_trial_results()
        if len(self.data_points) > 0:
            self.emit_data_points()
            self.emit_video_events(self.trial_definitions)
            self.emit_video_layout_events()
            self.emit_video_playback_summary()            
            self.emit_mouse_tracking_summary_events()
            self.emit_landmarker_summary_events()

    def emit_answers(self):
        self.emit_to_csv(self.answers, "answers.csv")

    def add_answer(self, answer):
        self.answers.append(answer)

    def emit_experiment_events(self):
        base_events = pd.DataFrame.from_records(self.experiment_events)
        url_params = pd.DataFrame.from_records(self.url_parameters)
        landmarker_summary = pd.DataFrame.from_records(self.landmarker_summary)
    
        # Count the number of completed trials per user (assuming trial_results is available)
        trials_completed_df = pd.DataFrame(self.trial_results)
        trials_completed_count = trials_completed_df.groupby('user_id').size().reset_index(name='trials_completed')
    
        # Rename duration in landmarker_summary
        landmarker_summary = landmarker_summary.rename(columns={'duration': 'duration_landmark'})
    
        # Merge datasets carefully to avoid duplicates
        merged_data = base_events.merge(url_params, on="user_id", how="left", suffixes=(None, "_url"))
        merged_data = merged_data.merge(trials_completed_count, on="user_id", how="left")
        merged_data = merged_data.merge(landmarker_summary[['user_id', 'duration_landmark']], on="user_id", how="left")
    
        # Select and rename final columns
        final_columns = [
            "started_at", 
            "completed_at", 
            "duration", 
            "experiment_id", 
            "user_id", 
            "trials_completed",
            "STUDY_ID",  # From url_params
            "SESSION_ID",  # From url_params
            "PROLIFIC_PID",  # From url_params
            "duration_landmark",
            "mouse_filename",
            "face_landmark_filename",
        ]
    
        # Ensure all final columns exist (fill missing ones with NaN)
        for col in final_columns:
            if col not in merged_data.columns:
                merged_data[col] = pd.NA
    
        merged_data = merged_data[final_columns]
    
        self.emit_to_csv(merged_data.to_dict(orient="records"), "experiment_events.csv")


    def add_experiment_event(self, experiment, experiment_time_series):
        user_id = experiment['protocol_user']['user_id']
    
        # Check if both timestamps exist before computing duration
        if experiment.completed_at and experiment.started_at:
            duration = (
                datetime.fromisoformat(experiment.completed_at.to_json()) -
                datetime.fromisoformat(experiment.started_at.to_json())
            ).total_seconds()
        else:
            duration = None  # Or choose another default/handling mechanism
    
        # Create an OrderedDict for experiment_event
        experiment_event = OrderedDict()
        experiment_event["started_at"] = experiment.started_at
        experiment_event["completed_at"] = experiment.completed_at
        experiment_event["duration"] = duration
        experiment_event["experiment_id"] = experiment.id
        experiment_event["user_id"] = user_id
        
        # Add custom parameters in order
        custom_parameters = experiment['custom_parameters']
        for key, value in custom_parameters.items():
            experiment_event[key] = value
    
        # Add time series information
        for experiment_time_series_type, experiment_time_series_info in experiment_time_series.items():
            experiment_event[f"{experiment_time_series_type}_filename"] = experiment_time_series_info['filename']
    
        # Append the ordered event to the list
        self.experiment_events.append(experiment_event)
    
        # Similarly, construct an OrderedDict for url_parameters
        url_parameters = OrderedDict()
        for key, value in custom_parameters.items():
            url_parameters[key] = value
        url_parameters["user_id"] = user_id
        url_parameters["experiment_id"] = experiment.id
    
        self.url_parameters.append(url_parameters)

    def emit_url_parameters(self):
        self.emit_to_csv(self.url_parameters, "url_parameters.csv")

    def add_url_parameter(self, url_parameter):
        self.url_parameters.append(url_parameter)

    def emit_trial_results(self):
        self.emit_to_csv(self.trial_results, "trial_results.csv")

    def add_trial_results(self, experiment, trial_results, trial_definitions: pyswagger.primitives.Model):
        for trial_result in trial_results:
            trial_result_entry = OrderedDict()
            trial_result_entry["started_at"] = trial_result.started_at
            trial_result_entry["completed_at"] = trial_result.completed_at
            if trial_result.completed_at and trial_result.started_at:
                trial_result_entry["duration"] = (
                    datetime.fromisoformat(trial_result.completed_at.to_json()) -
                    datetime.fromisoformat(trial_result.started_at.to_json())
                ).total_seconds()
            else:
                trial_result_entry["duration"] = None
            trial_result_entry["protocol_definition_id"] = experiment['protocol_user']['protocol_definition_id']
            trial_result_entry["experiment_id"] = experiment.id
            trial_result_entry["phase_definition_id"] = trial_result.phase_definition_id
            trial_result_entry["trial_definition_id"] = trial_result.trial_definition_id
            trial_result_entry["user_id"] = experiment['protocol_user']['user_id']
            trial_result_entry["trial_type"] = json.loads(trial_definitions[trial_result.trial_definition_id]['definition_data'])['TrialType']
            trial_result_entry["trial_name"] = trial_definitions[trial_result.trial_definition_id]['name']
    
            self.trial_results.append(trial_result_entry)

    def emit_data_points(self):
        self.emit_to_csv(self.data_points, "data_points.csv")

    def add_data_points(self, experiment, trial_result, data_points):
        for dp in data_points:
            dp_entry = OrderedDict()
    
            # Process the datetime into two fields:
            raw_dt, iso_dt = process_datetime(dp.get("datetime"))    
            dp_entry["datestring"] = iso_dt
            dp_entry["datetime"] = raw_dt
            dp_entry["study_result_id"] = dp["study_result_id"]
            dp_entry["experiment_id"] = experiment.id
            dp_entry["phase_definition_id"] = trial_result.phase_definition_id
            dp_entry["trial_definition_id"] = trial_result.trial_definition_id
            dp_entry["component_id"] = dp["component_id"]
            dp_entry["protocol_user_id"] = experiment['protocol_user']['id']
            dp_entry["user_id"] = experiment['protocol_user']['user_id']
            dp_entry["id"] = dp["id"]
            dp_entry["point_type"] = dp["point_type"]
            dp_entry["kind"] = dp["kind"]
            dp_entry["method"] = dp["method"]
            dp_entry["entity_type"] = dp["entity_type"]
            dp_entry["value"] = dp["value"]
    
            self.data_points.append(dp_entry)


    def emit_video_events(self, trial_definitions):
        video_event_points = list(filter(lambda x: is_video_event(x), self.data_points))
       
        video_events = []
    
        for dp in video_event_points:
            video_event = OrderedDict()
    
            # Extract and process datetime
            raw_dt, iso_dt = process_datetime(dp.get("datetime"))
    
            if raw_dt is None or iso_dt is None:
                print(f"⚠️ Skipping event due to unparseable datetime: {dp.get('datetime')} FULL EVENT: {dp}")  # Log full event
                continue
    
            # Add all relevant fields back
            video_event["datestring"] = iso_dt
            video_event["datetime"] = raw_dt            
            video_event["experiment_id"] = dp.get("experiment_id")
            video_event["phase_definition_id"] = dp.get("phase_definition_id")
            video_event["trial_definition_id"] = dp.get("trial_definition_id")
            video_event["trial_name"] = get_trial_name(dp["trial_definition_id"], trial_definitions)
            video_event["component_id"] = dp.get("component_id")
            video_event["component_name"] = get_component_name(dp["trial_definition_id"], dp["component_id"], trial_definitions)
            video_event["protocol_user_id"] = dp.get("protocol_user_id")
            video_event["user_id"] = dp.get("user_id")
            video_event["id"] = dp.get("id")
            video_event["point_type"] = dp.get("point_type")
            video_event["value"] = dp.get("value")
    
            video_events.append(video_event)
    
        #print(f"✅ Successfully processed {len(video_events)} video events.")  # Debugging
        self.emit_to_csv(video_events, "video_events.csv")

    def emit_video_playback_summary(self):
        video_event_points = filter(lambda x: is_video_event(x), self.data_points)
        user_playback_events = {}
    
        for dp in video_event_points:
            user_id = dp["user_id"]
    
            if user_id not in user_playback_events:
                user_playback_events[user_id] = OrderedDict({
                    "datestring_start": None,  # ISO string
                    "datestring_end": None,  # ISO string
                    "datetime_start": None,  # Numerical timestamp
                    "datetime_end": None,    # Numerical timestamp
                    "duration": None,  # Playback duration
                    "study_result_id": dp["study_result_id"],
                    "experiment_id": dp["experiment_id"],
                    "phase_definition_id": dp["phase_definition_id"],
                    "trial_definition_id": dp["trial_definition_id"],
                    "component_id": dp["component_id"],
                    "user_id": dp["user_id"]
                })
    
            raw_dt, iso_dt = process_datetime(dp["datetime"])
    
            if raw_dt is None or iso_dt is None:
                print(f"⚠️ Skipping event due to unparseable datetime: {dp['datetime']}")
                continue  # Don't process unparseable timestamps
    
            event_type = dp["point_type"]
    
            if event_type == "PLAYING":
                user_playback_events[user_id]["datetime_start"] = raw_dt
                user_playback_events[user_id]["datestring_start"] = iso_dt
            elif event_type in ["ENDED", "PAUSED", "Stop"]:
                user_playback_events[user_id]["datetime_end"] = raw_dt
                user_playback_events[user_id]["datestring_end"] = iso_dt
    
        video_playback_summary = []
        for playback_event in user_playback_events.values():
            if playback_event["datetime_start"] and playback_event["datetime_end"]:
                playback_event["duration"] = playback_event["datetime_end"] - playback_event["datetime_start"]
    
            video_playback_summary.append(playback_event)
    
        self.emit_to_csv(video_playback_summary, "video_playback_summary.csv")
    
    def emit_video_layout_events(self):
        layout_data_points = list(filter(lambda x: x['point_type'] == 'Layout', self.data_points))
        if not layout_data_points:
            return
        layouts = []
        for layout_data_point in layout_data_points:
            video_layout = json.loads(layout_data_point['value'])
            # Process datetime into two forms:
            raw_dt, iso_dt = process_datetime(layout_data_point['datetime'])
            
            video_layout_event = OrderedDict()
            video_layout_event["datestring"] = iso_dt
            video_layout_event["datetime"] = raw_dt            
            video_layout_event["experiment_id"] = layout_data_point['experiment_id']
            video_layout_event["phase_definition_id"] = layout_data_point['phase_definition_id']
            video_layout_event["trial_definition_id"] = layout_data_point['trial_definition_id']
            video_layout_event["component_id"] = layout_data_point['component_id']
            video_layout_event["user_id"] = layout_data_point['user_id']
            video_layout_event["x"] = video_layout['x']
            video_layout_event["y"] = video_layout['y']
            video_layout_event["width"] = video_layout['width']
            video_layout_event["height"] = video_layout['height']
            video_layout_event["top"] = video_layout['top']
            video_layout_event["right"] = video_layout['right']
            video_layout_event["bottom"] = video_layout['bottom']
            video_layout_event["left"] = video_layout['left']
            layouts.append(video_layout_event)
        self.emit_to_csv(layouts, "video_layout_events.csv")

    def add_mouse_tracking_summary(self, user_id, mouse_tracking_configuration, duration, summary_df):
        summary_row = {
            "user_id": user_id,
            "duration": duration,
        }
        if summary_df is not None:
            point_count = summary_df['count'].sum()
            summary_row.update({
                "ms_point_count": point_count,
                "ms_points_per_second": point_count / duration,
            })

        if mouse_tracking_configuration is not None:
            summary_row.update(mouse_tracking_configuration)

        self.mouse_tracking_summary.append(summary_row)

    def emit_mouse_tracking_summary_events(self):
        self.emit_to_csv(self.mouse_tracking_summary, "mouse_tracking_summary.csv")

    def add_landmarker_configuration(self, user_id, landmarker_configuration, duration, summary_df):
        summary_row = {
            "user_id": user_id,
            "duration": duration,
        }
        if summary_df is not None:
            point_count = summary_df['acknowledged'].sum()
            summary_row.update({
                "lm_point_count": point_count,
                "lm_points_per_second": point_count / duration,
            })

        if landmarker_configuration is not None:
            summary_row.update(landmarker_configuration)

        self.landmarker_summary.append(summary_row)

    def emit_landmarker_summary_events(self):
        self.emit_to_csv(self.landmarker_summary, "landmarker_summary.csv")

    def emit_to_csv(self, data, filename):
        if data:
            # Use the keys from the first row as the header
            header = list(data[0].keys())
            # If subsequent rows might have extra keys, append them in order of appearance.
            for row in data[1:]:
                for key in row.keys():
                    if key not in header:
                        header.append(key)
            with open(self.result_path_generator.result_path_for(filename), 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=header)
                writer.writeheader()
                writer.writerows(data)

