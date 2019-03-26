import json
import requests

from tba_constants import *

def retrieve_event_matches(event_id, read_key):
    """
    Sends the request to The Blue Alliance for all the matches at the specified event.

    Arguments:
        event_id: The unique event ID from The Blue Alliance.
        read_key: The API key to read from The Blue Alliance.
    Returns:
        A JSON object of the response
    """
    request_url = URL + EVENT_URL + event_id + MATCHES_URL

    # Add headers for The Blue Alliance application parameters
    return send_api_request(request_url, {HEADER_KEY: HEADER_VAL, READ_KEY: read_key})


def retrieve_event_teams(event_id, read_key):
    """
    Sends the request to The Blue Alliance for all the teams at the specified event.

    Arguments:
        event_id: The unique event ID from The Blue Alliance.
        read_key: The API key to read from The Blue Alliance.
    Returns:
        A JSON object of the response
    """
    request_url = URL + EVENT_URL + event_id + TEAM_KEYS_URL
    return send_api_request(request_url, {HEADER_KEY: HEADER_VAL, READ_KEY: read_key})


def send_api_request(request_url, headers):
    """
    Sends the request to The Blue Alliance for the given request and headers.

    Arguments:
        request_url: The request URL to send the request to.
        headers: The header parameters to send with the request.
    Returns:
        A JSON object of the response
    """
    response = requests.get(request_url, headers)
    json_response = response.json()
    return json_response


def load_qualification_match_data(json_response):
    """
    Parses the JSON response from The Blue Alliance and loads it into Match data.

    Arguments:
        json_response: The JSON response from The Blue Alliance.

    Returns:
        An array of JSON match data
    """
    matches = []

    # Filter and keep only qualification matches
    for match in json_response:
        if match[COMP_LEVEL] == QUALIFICATION_ID:
            # Track match number and all teams
            matches.append(match)

    return matches


def retrieve_event_match_data(event_id, read_key):
    """
    Sends the request to The Blue Alliance for all the matches at the specified event. Formats
    the response and returns an array of JSON match objects.

    Arguments:
        event_id: The unique event ID from The Blue Alliance.
        read_key: The API key to read from The Blue Alliance.
    Returns:
        An array of JSON match data
    """
    return load_qualification_match_data(retrieve_event_matches(event_id, read_key))
