import csv
import json
import datetime as dt
from dateutil.parser import isoparse
from dateutil.tz import tzutc
import pyswagger.primitives._time     # ← keep only if you really need it
import pandas as pd
import pyswagger.primitives
from dump_utilities import is_video_event
from result_path_generator import ResultPathGenerator
from collections import OrderedDict

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
    
ISO_FMT = "%Y-%m-%dT%H:%M:%S.%f"     # six‑digit µs -> we'll cut to 3 ms

def process_datetime(value):
    """
    Convert many datetime representations to UTC.

    Returns (epoch_utc_seconds, iso_utc_no_tz)  or  (None, None).
    """
    if value is None:
        return None, None

    try:
        # Swagger helper ----------------------------------------------------
        if isinstance(value, pyswagger.primitives._time.Datetime):
            value = value.to_json()

        # Numeric epoch ------------------------------------------------------
        if isinstance(value, (int, float)):
            ts = value / 1000.0 if value > 1e11 else float(value)
            d_utc = dt.datetime.utcfromtimestamp(ts).replace(tzinfo=tzutc())

        # ISO string ---------------------------------------------------------
        elif isinstance(value, str):
            d_local = isoparse(value)
            d_utc   = (
                d_local.replace(tzinfo=tzutc()) if d_local.tzinfo is None
                else d_local.astimezone(tzutc())
            )

        # datetime object ----------------------------------------------------
        elif isinstance(value, dt.datetime):
            d_utc = (
                value.replace(tzinfo=tzutc()) if value.tzinfo is None
                else value.astimezone(tzutc())
            )

        else:
            raise TypeError(f"Unsupported type: {type(value)}")

        # Outputs ------------------------------------------------------------
        epoch = d_utc.timestamp()
        iso   = d_utc.replace(tzinfo=None).strftime(ISO_FMT)[:-3]  # 3‑digit ms
        return epoch, iso

    except Exception as exc:
        print(f"⚠️  Could not parse datetime {value!r} → {exc}")
        return None, None
    
class ResultCollector:
    def __init__(self, result_path_generator: ResultPathGenerator):
        self.result_path_generator = result_path_generator
        self.answers = []
        self.experiment_events = []
        self.url_parameters = []
        self.trial_results = []
        self.data_points = []
        self.mouse_tracking_summary = []
        self.landmarker_event_summary = []
        self.landmarker_calibration_events = []
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
            self.emit_video_playback_summary(self.trial_definitions)            
            self.emit_mouse_tracking_summary_events()
            self.emit_landmarker_summary_events()
        if len(self.landmarker_calibration_events) > 0:
            self.emit_landmarker_calibration_events()
        
    def emit_answers(self):
        self.emit_to_csv(self.answers, "answers.csv")

    def add_answer(self, answer):
        self.answers.append(answer)

    def add_landmarker_calibration_events(self, raw_calibration_datapoints):
        """
        Given a list of raw face_landmark_calibration datapoints,
        flatten them so that each calibration point becomes one row with:
          - Common fields (datetime, experiment_id, etc.)
          - A "point" column (e.g. "Pt1", "Pt2", etc.)
          - Columns "x", "y", "width", "height", "top", "right", "bottom", "left" (if available)
        
        For Change events (user clicks) the value is already a flat dict.
        For Render events the value is a nested dict; we iterate over its keys.
        Then we deduplicate so that only one row per unique calibration point remains.
        """
        parsed_calibration_datapoints = []
        
        # The keys we want to include in our final flattened row:
        desired_keys = {
            "datetime", "datestring", "experiment_id", "phase_definition_id",
            "trial_definition_id", "component_id", "study_result_id", "id",
            "protocol_user_id", "user_id", "point_type", "kind", "method", "entity_type",
            "point", "x", "y", "width", "height", "top", "right", "bottom", "left"
        }
        
        for dp in raw_calibration_datapoints:
            # Build a dict of common fields
            common = {
                "datetime": dp.get("datetime"),
                "datestring": dp.get("datestring"),
                "experiment_id": dp.get("experiment_id"),
                "phase_definition_id": dp.get("phase_definition_id"),
                "trial_definition_id": dp.get("trial_definition_id"),
                "component_id": dp.get("component_id"),
                "study_result_id": dp.get("study_result_id"),
                "id": dp.get("id"),
                "protocol_user_id": dp.get("protocol_user_id"),
                "user_id": dp.get("user_id"),
                "point_type": dp.get("point_type"),
                "kind": dp.get("kind"),
                "method": dp.get("method"),
                "entity_type": dp.get("entity_type")
            }
            
            if dp.get("point_type") == "Change":
                # For Change events, the value is a flat dict
                val = dp.get("value", {})
                row = common.copy()
                row["point"] = val.get("Id")
                row["x"] = val.get("x")
                row["y"] = val.get("y")
                # For Change events we may not have width/height etc.
                row["width"] = None
                row["height"] = None
                row["top"] = None
                row["right"] = None
                row["bottom"] = None
                row["left"] = None
                # Filter to keep only desired keys
                row = {k: row[k] for k in row if k in desired_keys}
                parsed_calibration_datapoints.append(row)
                
            elif dp.get("point_type") == "Render":
                # For Render events, the value is a nested dict with keys like "#Pt1", "#Pt2", etc.
                val = dp.get("value", {})
                if isinstance(val, dict):
                    for raw_point_label, subdict in val.items():
                        # Create one row per calibration point
                        row = common.copy()
                        # Use the key (stripping the '#' character) as the "point" value
                        row["point"] = raw_point_label.lstrip('#')
                        if isinstance(subdict, dict):
                            row["x"] = subdict.get("x")
                            row["y"] = subdict.get("y")
                            row["width"] = subdict.get("width")
                            row["height"] = subdict.get("height")
                            row["top"] = subdict.get("top")
                            row["right"] = subdict.get("right")
                            row["bottom"] = subdict.get("bottom")
                            row["left"] = subdict.get("left")
                        else:
                            # If subdict isn’t a dict, skip it
                            continue
                        row = {k: row[k] for k in row if k in desired_keys}
                        parsed_calibration_datapoints.append(row)
                else:
                    # Fallback: if the value isn’t a dict, just use the common fields
                    row = common.copy()
                    row = {k: row[k] for k in row if k in desired_keys}
                    parsed_calibration_datapoints.append(row)
            else:
                # Skip any events that are not Change or Render
                continue
    
        # Convert to DataFrame and deduplicate so that for each user/trial/point only one row remains.
        df = pd.DataFrame(parsed_calibration_datapoints)
        df_unique = df.drop_duplicates(subset=["datetime","user_id", "trial_definition_id", "point","point_type"], keep="first")
        
        # Update the collector's calibration events (or however you wish to store them)
        self.landmarker_calibration_events.extend(df_unique.to_dict(orient="records"))

    
    def emit_landmarker_calibration_events(self):
        """
        Emit all calibration events to a CSV file.
        """
        if not self.landmarker_calibration_events:
            return

        # Convert to a DataFrame
        calibration_df = pd.DataFrame.from_records(self.landmarker_calibration_events)
        # Optionally, define a specific order of columns if desired:
        final_columns = [
            "datetime", "datestring", "experiment_id", "phase_definition_id",
            "trial_definition_id", "component_id", "study_result_id", "id",
            "protocol_user_id", "user_id", "point_type", "kind", "method", "entity_type"
        ]
        
        # Plus any calibration-specific columns. If columns vary, you may just use all:
        for col in calibration_df.columns:
            if col not in final_columns:
                final_columns.append(col)
        
        calibration_df = calibration_df[final_columns]
        
        # Use the result_path_generator to build the output file path, for example in a subfolder "calibration"
        self.emit_to_csv(calibration_df.to_dict(orient="records"), "face_landmark_calibration.csv")
        
    def emit_experiment_events(self):
        base_events = pd.DataFrame.from_records(self.experiment_events)
        url_params = pd.DataFrame.from_records(self.url_parameters)
        
        # landmarker event summary
        landmarker_event_summary = pd.DataFrame.from_records(self.landmarker_event_summary)
    
        # Count the number of completed trials per user (assuming trial_results is available)
        trials_completed_df = pd.DataFrame(self.trial_results)
        trials_completed_count = trials_completed_df.groupby('user_id').size().reset_index(name='trials_completed')
    
        # Rename duration in landmarker_event_summary
        landmarker_event_summary = landmarker_event_summary.rename(columns={'duration': 'duration_landmark_events'})
    
        # Merge datasets carefully to avoid duplicates
        merged_data = base_events.merge(url_params, on="user_id", how="left", suffixes=(None, "_url"))
        merged_data = merged_data.merge(trials_completed_count, on="user_id", how="left")
        merged_data = merged_data.merge(landmarker_event_summary[['user_id', 'duration_landmark_events']], on="user_id", how="left")
    
        # Select and rename final columns
        final_columns = [
            "datestring_started", 
            "datestring_completed", 
            "datetime_started", 
            "datetime_completed", 
            "duration", 
            "experiment_id", 
            "user_id", 
            "trials_completed",
            "STUDY_ID",  # From url_params
            "SESSION_ID",  # From url_params
            "PROLIFIC_PID",  # From url_params
            "duration_landmark_events",
            "points_landmark_timeseries",
            "datetime_start_landmark_timeseries",
            "datetime_end_landmark_timeseries",
            "datestring_start_landmark_timeseries",
            "datestring_end_landmark_timeseries",
            "duration_landmark_timeseries",
            "fs_mean_landmark_timeseries",
            "fs_median_landmark_timeseries",
            "filename_landmark_timeseries",
            "points_mouse_timeseries",
            "datetime_start_mouse_timeseries",
            "datetime_end_mouse_timeseries",
            "datestring_start_mouse_timeseries",
            "datestring_end_mouse_timeseries",
            "duration_mouse_timeseries",
            "fs_mouse_timeseries",
            "filename_mouse_timeseries",
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
        start_raw, start_iso = process_datetime(experiment.started_at)
        end_raw,   end_iso   = process_datetime(experiment.completed_at)

        duration = (end_raw - start_raw) if (start_raw and end_raw) else None

        # Create an OrderedDict for experiment_event
        experiment_event = OrderedDict()
        experiment_event["datestring_started"] = start_iso
        experiment_event["datestring_completed"] = end_iso
        experiment_event["datetime_started"] = start_raw
        experiment_event["datetime_completed"] = end_raw
        experiment_event["duration"] = duration
        experiment_event["experiment_id"] = experiment.id
        experiment_event["user_id"] = user_id
        
        # Add custom parameters in order
        custom_parameters = experiment['custom_parameters']
        for key, value in custom_parameters.items():
            experiment_event[key] = value
    
        # Add time series information
        for ts_type, ts_info in experiment_time_series.items():
            if ts_type == "face_landmark":
                experiment_event["filename_landmark_timeseries"] = ts_info["filename"]
                experiment_event["points_landmark_timeseries"] = ts_info["count_points"]
                experiment_event["datetime_start_landmark_timeseries"] = ts_info["datetime_start"]
                experiment_event["datetime_end_landmark_timeseries"] = ts_info["datetime_end"]
                experiment_event["datestring_start_landmark_timeseries"] = ts_info["datestring_start"]
                experiment_event["datestring_end_landmark_timeseries"] = ts_info["datestring_end"]
                experiment_event["duration_landmark_timeseries"] = ts_info["duration"]
                experiment_event["fs_mean_landmark_timeseries"] = ts_info["fs_mean_hz"]
                experiment_event["fs_median_landmark_timeseries"] = ts_info["fs_median_hz"]
    
            elif ts_type == "mouse":
                experiment_event["filename_mouse_timeseries"] = ts_info["filename"]
                experiment_event["points_mouse_timeseries"] = ts_info["count_points"]
                experiment_event["datetime_start_mouse_timeseries"] = ts_info["datetime_start"]
                experiment_event["datetime_end_mouse_timeseries"] = ts_info["datetime_end"]
                experiment_event["datestring_start_mouse_timeseries"] = ts_info["datestring_start"]
                experiment_event["datestring_end_mouse_timeseries"] = ts_info["datestring_end"]
                experiment_event["duration_mouse_timeseries"] = ts_info["duration"]
                experiment_event["fs_mouse_timeseries"] = ts_info["avg_fs_hz"]    
            else:
                # If there are other timeseries you don't care about, you can skip or handle them here
                pass
            
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
            
            start_raw, start_iso = process_datetime(trial_result.started_at)
            end_raw,   end_iso   = process_datetime(trial_result.completed_at)
            duration = (end_raw - start_raw) if (start_raw and end_raw) else None

            trial_result_entry = OrderedDict()
            trial_result_entry["datestring_started"] = start_iso
            trial_result_entry["datestring_completed"] = end_iso
            trial_result_entry["datetime_started"] = start_raw
            trial_result_entry["datetime_completed"] = end_raw
            trial_result_entry["duration"] = duration
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
    
        self.emit_to_csv(video_events, "video_events.csv")

    def emit_video_playback_summary(self, trial_definitions):
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
                    "trial_name": get_trial_name(dp["trial_definition_id"], trial_definitions),
                    "component_id": dp["component_id"],
                    "user_id": dp["user_id"],
                    "component_name": get_component_name(dp["trial_definition_id"], dp["component_id"], trial_definitions)                    
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
            # Only call json.loads if layout_data_point['value'] is a string
            if isinstance(layout_data_point['value'], str):
                video_layout = json.loads(layout_data_point['value'])
            else:
                video_layout = layout_data_point['value']
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

    def add_mouse_tracking_event_summary(self, user_id, mouse_tracking_configuration, duration, summary_df):
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

    def add_landmarker_event_configuration(self, user_id, landmarker_event_configuration, duration, summary_df):
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

        if landmarker_event_configuration is not None:
            summary_row.update(landmarker_event_configuration)

        self.landmarker_event_summary.append(summary_row)

    def emit_landmarker_summary_events(self):
        self.emit_to_csv(self.landmarker_event_summary, "landmarker_event_summary.csv")

    def emit_to_csv(self, data, filename, subfolder=None):
        if data:
            # Use the keys from the first row as the header
            header = list(data[0].keys())
            # If subsequent rows might have extra keys, append them in order of appearance.
            for row in data[1:]:
                for key in row.keys():
                    if key not in header:
                        header.append(key)
    
            # Pass subfolder=... so we store CSV in that folder
            csv_path = self.result_path_generator.result_path_for(filename, subfolder=subfolder)
            with open(csv_path, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=header)
                writer.writeheader()
                writer.writerows(data)

