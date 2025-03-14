import csv
import json
from datetime import datetime
from collections import OrderedDict
import pandas as pd
import pyswagger.primitives

from dump_utilities import is_video_event
from result_path_generator import ResultPathGenerator


def process_datetime(dt):
    """
    Returns a tuple (raw, iso) where:
      - raw is the original datetime value
      - iso is the datetime converted to an ISO formatted string with 6-digit microseconds.
    If dt is an int/float, it's assumed to be a Unix timestamp.
    If it's a string, we try to parse it as ISO; if that fails, we leave it as-is.
    """
    raw = dt
    iso = None
    fmt = "%Y-%m-%dT%H:%M:%S.%f"  # this ensures 6 digits for microseconds
    if isinstance(dt, (int, float)):
        try:
            d = datetime.fromtimestamp(dt)
            iso = d.strftime(fmt)
        except Exception:
            iso = dt
    elif isinstance(dt, str):
        try:
            d = datetime.fromisoformat(dt)
            iso = d.strftime(fmt)
        except ValueError:
            iso = dt
    else:
        iso = dt
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
            self.emit_video_events()
            self.emit_video_layout_events()
            self.emit_mouse_tracking_summary_events()
            self.emit_landmarker_summary_events()

    def emit_answers(self):
        self.emit_to_csv(self.answers, "answers.csv")

    def add_answer(self, answer):
        self.answers.append(answer)

    def emit_experiment_events(self):
        base_events = pd.DataFrame.from_records(self.experiment_events)
        url_params = pd.DataFrame.from_records(self.url_parameters)
        mouse_tracking_summary = pd.DataFrame.from_records(self.mouse_tracking_summary)
        landmarker_summary = pd.DataFrame.from_records(self.landmarker_summary)

        merged_data = base_events.merge(url_params, on="user_id", how="outer") \
            .merge(mouse_tracking_summary, on="user_id", how="outer") \
            .merge(landmarker_summary, on="user_id", how="outer")

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
            raw_dt, iso_dt = process_datetime(dp["datetime"])
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

    def emit_video_events(self):
        video_events = filter(lambda x: is_video_event(x), self.data_points)
        video_events = list(video_events)
        self.emit_to_csv(video_events, "video_events.csv")

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
            video_layout_event["datetime"] = raw_dt
            video_layout_event["datestring"] = iso_dt
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

