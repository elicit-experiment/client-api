import csv
import json
from datetime import datetime

import pandas as pd
import pyswagger.primitives

from dump_utilities import is_video_event
from result_path_generator import ResultPathGenerator


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

        experiment_event = {
            "user_id": user_id,
            "started_at": experiment.started_at,
            "completed_at": experiment.completed_at,
            "duration": (datetime.fromisoformat(experiment.completed_at.to_json()) - datetime.fromisoformat(experiment.started_at.to_json())).total_seconds(),
            "experiment_id": experiment.id,
        }
        custom_parameters = experiment['custom_parameters']
        url_parameters = {key: value for key, value in custom_parameters.items()}
        experiment_event.update(url_parameters)

        for experiment_time_series_type, experiment_time_series_info in experiment_time_series.items():
            experiment_event[f"{experiment_time_series_type}_filename"] = experiment_time_series_info['filename']

        url_parameters.update({ "user_id": user_id, "experiment_id": experiment.id })

        self.experiment_events.append(experiment_event)
        self.url_parameters.append(url_parameters)

    def emit_url_parameters(self):
        self.emit_to_csv(self.url_parameters, "url_parameters.csv")

    def add_url_parameter(self, url_parameter):
        self.url_parameters.append(url_parameter)

    def emit_trial_results(self):
        self.emit_to_csv(self.trial_results, "trial_results.csv")

    def add_trial_results(self, experiment, trial_results, trial_definitions: pyswagger.primitives.Model):
        self.trial_results += [{
            "user_id": experiment['protocol_user']['user_id'],
            "started_at": trial_result.started_at,
            "completed_at": trial_result.completed_at,
            "duration": (datetime.fromisoformat(trial_result.completed_at.to_json()) - datetime.fromisoformat(trial_result.started_at.to_json())).total_seconds(),
            "experiment_id": experiment.id,
            "protocol_definition_id": experiment['protocol_user']['protocol_definition_id'],
            "phase_definition_id": trial_result.phase_definition_id,
            "trial_definition_id": trial_result.trial_definition_id,
            "trial_name": trial_definitions[trial_result.trial_definition_id]['name'],
            "trial_type": json.loads(trial_definitions[trial_result.trial_definition_id]['definition_data'])['TrialType']
        } for trial_result in trial_results]

    def emit_data_points(self):
        self.emit_to_csv(self.data_points, "data_points.csv")

    def add_data_points(self, experiment, trial_result, data_points):
        self.data_points += [{
            "id": data_point["id"],
            "phase_definition_id": trial_result.phase_definition_id,
            "trial_definition_id": trial_result.trial_definition_id,
            "component_id": data_point["component_id"],
            "study_result_id": data_point["study_result_id"],
            "experiment_id": experiment.id,
            "protocol_user_id": experiment['protocol_user']['id'],
            "user_id": experiment['protocol_user']['user_id'],
            "datetime": data_point["datetime"],
            "point_type": data_point["point_type"],
            "kind": data_point["kind"],
            "method": data_point["method"],
            "entity_type": data_point["entity_type"],
            "value": data_point["value"],
        } for data_point in data_points]

    def emit_video_events(self):
        video_events = filter(lambda x: is_video_event(x), self.data_points)
        video_events = list(video_events)
        self.emit_to_csv(video_events, "video_events.csv")

    def emit_video_layout_events(self):
        layout_data_points = list(filter(lambda x: x['point_type'] == 'Layout', self.data_points))
        if len(layout_data_points) == 0:
            return
        layouts = []
        for layout_data_point in layout_data_points:
            video_layout = json.loads(layout_data_point['value'])
            video_layout_event = {"x": video_layout['x'],
                                  "y": video_layout['y'],
                                  "width": video_layout['width'],
                                  "height": video_layout['height'],
                                  "top": video_layout['top'],
                                  "right": video_layout['right'],
                                  "bottom": video_layout['bottom'],
                                  "left": video_layout['left'],
                                  "datetime": layout_data_point['datetime'],
                                  "user_id": layout_data_point['user_id'],
                                  "experiment_id": layout_data_point['experiment_id'],
                                  "phase_definition_id": layout_data_point['phase_definition_id'],
                                  "trial_definition_id": layout_data_point['trial_definition_id'],
                                  "component_id": layout_data_point['component_id']}

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
            header = set().union(*(row.keys() for row in data))
            with open(self.result_path_generator.result_path_for(filename), 'w') as file:
                writer = csv.DictWriter(file, fieldnames=header)
                writer.writeheader()
                writer.writerows(data)
