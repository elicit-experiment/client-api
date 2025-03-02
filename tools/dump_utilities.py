from datetime import datetime
import os
import csv

ELICIT_API_DATEFMT= '%Y-%m-%dT%H:%M:%S.%fZ'
RESULTS_OUTPUT_DATEFMT='%Y-%m-%d %H:%M:%S.%f%Z'

def parse_datetime(field: str, state: dict) -> dict:
    """Parse the (ISO8601) format from Elicit API into a datetime object. pyswagger uses its own datetime object format, so converting to/from string is necessary."""
    state[field] = datetime.strptime(state[field], ELICIT_API_DATEFMT)
    return state


def with_dates(o: dict) -> dict:
    """ Parse all the datetime fields in an elicit object. Relies upon the convention that the DB objects in Elicit have the `at` suffix."""
    o = (o.copy())
    for key in o:
        if key.endswith('_at') and o[key] is not None:
            o[key] = o[key].v.strftime(RESULTS_OUTPUT_DATEFMT)
    return o


def is_video_event(data_point):
    """Determine whether a data point is a video event."""
    return (data_point['point_type'] != 'State') and ('video' in data_point['kind'].lower())
