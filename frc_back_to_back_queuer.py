import requests
import json
import csv
import os

# The Blue Alliance parameters for sending requests
URL = 'http://www.thebluealliance.com/api/v3'
EVENT_URL = '/event/'
MATCHES_URL = '/matches'
HEADER_KEY = 'X-TBA-App-Id'
READ_KEY = 'X-TBA-Auth-Key'
HEADER_VAL = 'frc:back-to-back-queuer:v01'
QUALIFICATION_ID = 'qm'
KEY_FILE = 'key.json'

def file(path):
    """
    Return absolute path for a file.
    Arguments:
        path: The path to get the OS path for.
    Returns:
        A file path.
    """
    return os.path.abspath(path)


def get_event_matches(event_id, read_key):
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
    response = requests.get(request_url, headers={HEADER_KEY: HEADER_VAL, READ_KEY: read_key})
    json_response = response.json()
    
    return json_response


def get_team_str(team):
    """
    Function to format the output strings for debugging and file output for each team and their "back-to-back" match.

    Arguments:
        team: The team object from the match.
    Returns:
        A formatted string
    """
    # If there is a back-to-back match
    if team['next_match'] is not None:
        return '{} ({})'.format(team['team'], team['next_match'])
    else:
        return team['team']


class Match(object):
    """
    This class represents a single match in the qualification schedule, with a match number and 3 blue alliance teams and 3 red alliance teams.
    """
    match_num = -1
    teams = None
    
    def __init__(self, match_num, blue_teams, red_teams):
        """
        Initializes the Match object from the keyword arguments.

        Arguments:
            match_num: The match number from the schedule.
            blue_teams: The blue alliance in the match.
            red_teams: The red alliance in the match.
        """
        self.match_num = match_num
        self.teams = dict()
        
        # Put all teams in dictionary by alliance and position
        # Clean team numbers to remove and prefixes from The Blue Alliance
        for i in range(len(blue_teams)):
            self.teams['B{}'.format(i + 1)] = {'team': blue_teams[i][3:], 'next_match': None}
        
        for i in range(len(red_teams)):
            self.teams['R{}'.format(i + 1)] = {'team': red_teams[i][3:], 'next_match': None}
    
    def __str__(self):
        """
        Returns a string representation of this object.

        Returns:
            A string
        """
        return '{:2d}: Blue:{},{},{} | Red:{},{},{}'.format(self.match_num, get_team_str(self.teams['B1']), get_team_str(self.teams['B2']), get_team_str(self.teams['B3']), get_team_str(self.teams['R1']), get_team_str(self.teams['R2']), get_team_str(self.teams['R3']))

    def __repr__(self):
        """
        Returns a representation of this object.

        Returns:
            A string
        """
        return '{:2d}: Blue:{},{},{} | Red:{},{},{}'.format(self.match_num, get_team_str(self.teams['B1']), get_team_str(self.teams['B2']), get_team_str(self.teams['B3']), get_team_str(self.teams['R1']), get_team_str(self.teams['R2']), get_team_str(self.teams['R3']))


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

            # If we searched too far in the schedule or out of bounds
            if next_match_index >= total_match_count:
                continue
            
            next_match = all_matches[next_match_index]
            update_back_to_back_from_next_alliance(team, next_match, next_index)


def update_back_to_back_from_next_alliance(current_team, next_match, match_index_out):
    """
    Updates each team in the match schedule with their next upcoming match that is considered "back-to-back".

    Arguments:
        current_team: The current team being processed from the given match.
        next_match: The Match object for the succeeding match.
        match_index_out: The number of matches out that we are searching on this iteration.
    Returns:
        N/A
    """
    for next_team_key in next_match.teams.keys():
        next_team_val = next_match.teams[next_team_key]

        # If team exists in a back-to-back match
        if current_team['team'] == next_team_val['team']:
            # Mark the match number, next alliance color, and number of matches out in the current match
            current_team['next_match'] = 'M{}:{}:+{}'.format(next_match.match_num, next_team_key, match_index_out)


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser(description='Retrieves the qualification match schedule for a specific event from The Blue Alliance and generates the match schedule marked with all the back-to-back matches for each team.')
    parser.add_argument('-i', '--event_id', type=str, help='Event ID from The Blue Alliance for the specific event. Format is <year><event>.')
    parser.add_argument('-o', '--output_file', type=file, help='Output TSV file where the generated schedule will be saved.')
    parser.add_argument('-m', '--max_matches_out', type=int, help='Maximum number of matches to search out from a given match. In other words, the largest number of matches between two matches that considers them "back-to-back" for queuing purposes.')
    args = parser.parse_args()

    # Load API key
    read_key = None

    with open(KEY_FILE) as key_json_file:
        key_obj = json.load(key_json_file)
        read_key = key_obj['key']

    # Get matches
    json_response = get_event_matches(args.event_id, read_key)
    matches = []

    # Filter and keep only qualification matches
    for match in json_response:
        if match['comp_level'] == QUALIFICATION_ID:
            # Track match number and all teams
            matches.append(Match(match['match_number'], match['alliances']['blue']['team_keys'], match['alliances']['red']['team_keys']))
            
    # Sort by match number
    matches = sorted(matches, key=lambda x : x.match_num, reverse=False)
    matches_count = len(matches)

    # Find back-to-back matches for all teams in each match
    for index in range(matches_count):
        search_alliance_teams(matches, matches_count, matches[index], args.max_matches_out)

    # Write new schedule to TSV file
    with open(args.output_file, "wb") as tsv_file:
        writer = csv.writer(tsv_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_NONE)

        # Write header
        writer.writerow(['Match Number', 'Blue 1', 'Blue 2', 'Blue 3', 'Red 1', 'Red 2', 'Red 3'])
        
        # Write each match
        for match in matches:
            writer.writerow([match.match_num, get_team_str(match.teams['B1']), get_team_str(match.teams['B2']), get_team_str(match.teams['B3']), get_team_str(match.teams['R1']), get_team_str(match.teams['R2']), get_team_str(match.teams['R3'])])
    
    print 'Wrote schedule to {}'.format(args.output_file)
