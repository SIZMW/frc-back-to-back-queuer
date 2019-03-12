import calendar
import csv
import datetime
import json
import os
import requests

# The Blue Alliance parameters for sending requests
URL = 'http://www.thebluealliance.com/api/v3'
EVENT_URL = '/event/'
MATCHES_URL = '/matches'
TEAM_KEYS_URL = '/teams/keys'

HEADER_KEY = 'X-TBA-App-Id'
READ_KEY = 'X-TBA-Auth-Key'
HEADER_VAL = 'frc:back-to-back-queuer:v01'

QUALIFICATION_ID = 'qm'
TEAM_NUM_PREFIX_LEN = 3
KEY_FILE = 'key.json'

# The Blue Alliance response fields
ALLIANCES = 'alliances'
BLUE = 'blue'
COMP_LEVEL = 'comp_level'
MATCH_NUM = 'match_number'
RED = 'red'
TEAM_KEYS = 'team_keys'
MATCH_TIME = 'time'

# Custom fields
BA_KEY = 'key'

def file(path):
    """
    Return absolute path for a file.
    Arguments:
        path: The path to get the OS path for.
    Returns:
        A file path.
    """
    return os.path.abspath(path)


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


class Match(object):
    """
    This class represents a single match in the qualification schedule, with a match number and 3 blue alliance teams and 3 red alliance teams.
    """
    MATCH = 'match'
    NEXT_MATCH = 'next_match'
    TEAM = 'team'

    match_num = -1
    teams = None
    match_time = None
    match_time_str = None
    
    def __init__(self, match_num, match_time, blue_teams, red_teams):
        """
        Initializes the Match object from the keyword arguments.

        Arguments:
            match_num: The match number from the schedule.
            match_time: The datetime object representing the time of the match.
            blue_teams: The blue alliance in the match.
            red_teams: The red alliance in the match.
        """
        self.match_num = match_num
        self.teams = dict()
        self.match_time = match_time
        
        # Put all teams in dictionary by alliance and position
        # Clean team numbers to remove and prefixes from The Blue Alliance
        for i in range(len(blue_teams)):
            self.teams['B{}'.format(i + 1)] = {Match.TEAM: blue_teams[i][TEAM_NUM_PREFIX_LEN:], Match.NEXT_MATCH: None}
        
        for i in range(len(red_teams)):
            self.teams['R{}'.format(i + 1)] = {Match.TEAM: red_teams[i][TEAM_NUM_PREFIX_LEN:], Match.NEXT_MATCH: None}
    
    def __str__(self):
        """
        Returns a string representation of this object.

        Returns:
            A string
        """
        return '{:2d} [{}]: Blue:{},{},{} | Red:{},{},{}'.format(
            self.match_num,
            self.match_time,
            self.get_team_str(self.teams['B1']),
            self.get_team_str(self.teams['B2']),
            self.get_team_str(self.teams['B3']),
            self.get_team_str(self.teams['R1']),
            self.get_team_str(self.teams['R2']),
            self.get_team_str(self.teams['R3']))

    def __repr__(self):
        """
        Returns a representation of this object.

        Returns:
            A string
        """
        return '{:2d} [{}]: Blue:{},{},{} | Red:{},{},{}'.format(
            self.match_num,
            self.match_time,
            self.get_team_str(self.teams['B1']),
            self.get_team_str(self.teams['B2']),
            self.get_team_str(self.teams['B3']),
            self.get_team_str(self.teams['R1']),
            self.get_team_str(self.teams['R2']),
            self.get_team_str(self.teams['R3']))

    def get_team_str(self, team):
        """
        Function to format the output strings for debugging and file output for each team and their "back-to-back" match.

        Arguments:
            team: The team object from the match.
        Returns:
            A formatted string
        """
        # If there is a back-to-back match
        if team[Match.NEXT_MATCH] is not None:
            return '{} ({})'.format(team[Match.TEAM], team[Match.NEXT_MATCH])
        else:
            return team[Match.TEAM]

    def get_match_time_str(self):
        """
        Returns a string representation of this match's start time.

        Returns:
            A formatted string
        """

        # Get day of week, hour, and minutes of the match
        match_day = calendar.day_name[self.match_time.weekday()][0:3]
        match_moment = '{:02d}:{:02d}'.format(self.match_time.hour, self.match_time.minute)
        return '{} {}'.format(match_day, match_moment)


def search_alliance_teams(all_matches, total_match_count, current_match, max_matches_out):
    """
    Searches the subsequent matches for teams in the current match to determine which teams have "back-to-back" matches.

    Arguments:
        all_matches: The list of all Match objects in the qualification schedule.
        total_match_count: The total number of matches in the qualification schedule.
        current_match: The current match that we are searching out from.
        max_matches_out: Maximum number of matches to search out from a given match.
    """
    for team in current_match.teams.values():
        # Search forward in the schedule up to max_matches_out matches
        for next_index in range(1, max_matches_out + 1):
            next_match_index = index + next_index

            # If there are no more matches to check, stop checking further
            if next_match_index >= total_match_count:
                break
            
            next_match = all_matches[next_match_index]
            
            if update_back_to_back_from_next_alliance(team, next_match, next_index):
                break


def update_back_to_back_from_next_alliance(current_team, next_match, match_index_out):
    """
    Updates each team in the match schedule with their next upcoming match that is considered "back-to-back".

    Arguments:
        current_team: The current team being processed from the given match.
        next_match: The Match object for the succeeding match.
        match_index_out: The number of matches out that we are searching on this iteration.
    Returns:
        True if next_match contained current_team, False otherwise.
    """
    for next_team_key in next_match.teams.keys():
        next_team_val = next_match.teams[next_team_key]

        # If team exists in a back-to-back match
        if current_team[Match.TEAM] == next_team_val[Match.TEAM]:
            # Mark the match number, next alliance color, and number of matches out in the current match
            current_team[Match.NEXT_MATCH] = 'M{}:{}:+{}'.format(next_match.match_num, next_team_key, match_index_out)
            return True

    return False


def update_last_match_for_teams(all_matches, total_match_count, teams):
    """
    Updates each team in the match schedule with their last match of the event.

    Arguments:
        all_matches: The list of all Match objects in the qualification schedule.
        total_match_count: The total number of matches in the qualification schedule.
        teams: The dictionary of team number to counts, which by default are 0.
    """

    # Go through schedule in reverse
    for match_index in range(total_match_count - 1, 0, -1):
        current_match = all_matches[match_index]

        for team in current_match.teams.values():
            # If this is first visit of team number, mark as last match
            if teams[team[Match.TEAM]] == 0:
                team[Match.NEXT_MATCH] = 'L'
            teams[team[Match.TEAM]] = teams[team[Match.TEAM]] + 1

        # If the second to last match has not been visited for at least one team, keep going
        if not any(val == 1 for val in teams.values()):
            break


def load_match_data(json_response):
    """
    Parses the JSON response from The Blue Alliance and loads it into Match data.

    Arguments:
        json_response: The JSON response from The Blue Alliance.

    Returns:
        An array of matches (Match[])
    """
    matches = []

    # Filter and keep only qualification matches
    for match in json_response:
        if match[COMP_LEVEL] == QUALIFICATION_ID:
            # Track match number and all teams
            matches.append(
                Match(
                    match[MATCH_NUM],
                    datetime.datetime.fromtimestamp(int(match[MATCH_TIME])),
                    match[ALLIANCES][BLUE][TEAM_KEYS],
                    match[ALLIANCES][RED][TEAM_KEYS]))

    return matches

def load_api_key():
    """
    Loads the API key for The Blue Alliance.

    Returns:
        A string
    """
    with open(KEY_FILE) as key_json_file:
        key_obj = json.load(key_json_file)
        return key_obj[BA_KEY]


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser(description='Retrieves the qualification match schedule for a specific event from The Blue Alliance and generates the match schedule marked with all the back-to-back matches for each team.')
    parser.add_argument('-i', '--event_id', type=str, help='Event ID from The Blue Alliance for the specific event. Format is <year><event>.')
    parser.add_argument('-o', '--output_file', type=file, help='Output TSV file where the generated schedule will be saved.')
    parser.add_argument('-m', '--max_matches_out', type=int, help='Maximum number of matches to search out from a given match. In other words, the largest number of matches between two matches that considers them "back-to-back" for queuing purposes.')
    args = parser.parse_args()

    # Load API key
    read_key = load_api_key()

    # Get matches
    json_response = retrieve_event_matches(args.event_id, read_key)
    matches = load_match_data(json_response)
            
    # Sort by match number
    matches = sorted(matches, key=lambda x : x.match_num, reverse=False)
    matches_count = len(matches)

    # Find back-to-back matches for all teams in each match
    for index in range(matches_count):
        search_alliance_teams(matches, matches_count, matches[index], args.max_matches_out)

    # Find the last match of each team
    teams_json_response = retrieve_event_teams(args.event_id, read_key)
    event_teams = dict()

    for team in teams_json_response:
        team_num = team[TEAM_NUM_PREFIX_LEN:]
        event_teams[team_num] = 0

    update_last_match_for_teams(matches, matches_count, event_teams)

    # Write new schedule to TSV file
    with open(args.output_file, "wb") as tsv_file:
        writer = csv.writer(tsv_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_NONE)

        # Write header row
        writer.writerow(['Match', 'Time', 'Red 1', 'Red 2', 'Red 3', 'Blue 1', 'Blue 2', 'Blue 3'])
        
        # Write each match
        for match in matches:
            writer.writerow([
                match.match_num,
                match.get_match_time_str(),
                match.get_team_str(match.teams['R1']),
                match.get_team_str(match.teams['R2']),
                match.get_team_str(match.teams['R3']),
                match.get_team_str(match.teams['B1']),
                match.get_team_str(match.teams['B2']),
                match.get_team_str(match.teams['B3'])])
    
    print 'Wrote schedule to {}'.format(args.output_file)
