import datetime
import json

from match import Match
from file_util import *
from tba_api_requester import *
from tba_constants import *

def search_all_alliance_teams(all_matches, total_match_count, max_matches_out):
    """
    Searches the subsequent matches for teams in all matches to determine which teams have "back-to-back" matches.

    Arguments:
        all_matches: The list of all Match objects in the qualification schedule.
        total_match_count: The total number of matches in the qualification schedule.
        max_matches_out: Maximum number of matches to search out from a given match.
    """
    for index in range(total_match_count):
        search_alliance_teams(all_matches, total_match_count, all_matches[index], index, max_matches_out)


def search_alliance_teams(all_matches, total_match_count, current_match, current_match_index, max_matches_out):
    """
    Searches the subsequent matches for teams in the current match to determine which teams have "back-to-back" matches.

    Arguments:
        all_matches: The list of all Match objects in the qualification schedule.
        total_match_count: The total number of matches in the qualification schedule.
        current_match: The current match that we are searching out from.
        current_match_index: The current match index in the list of all matches.
        max_matches_out: Maximum number of matches to search out from a given match.
    """
    for team in current_match.teams.values():
        # Search forward in the schedule up to max_matches_out matches
        for next_index in range(1, max_matches_out + 1):
            next_match_index = current_match_index + next_index

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


def update_last_match_for_all_teams(event_id, read_key, all_matches, total_match_count):
    """
    Updates each team in each match in the schedule with their last match of the event.

    Arguments:
        event_id: The unique event ID from The Blue Alliance.
        read_key: The API key to read from The Blue Alliance.
        all_matches: The list of all Match objects in the qualification schedule.
        total_match_count: The total number of matches in the qualification schedule.
    """
    teams_json_response = retrieve_event_teams(event_id, read_key)
    event_teams = dict()

    for team in teams_json_response:
        team_num = team[TEAM_NUM_PREFIX_LEN:]
        event_teams[team_num] = 0

    update_last_match_for_teams(all_matches, total_match_count, event_teams)


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


def generate_match_data(json_matches):
    """
    Parses the JSON match array and loads it into Match data.

    Arguments:
        json_matches: An array of JSON match data.

    Returns:
        An array of matches (Match[])
    """
    matches = []

    for match in json_matches:
        # Track match number and all teams
        matches.append(
            Match(
                match[MATCH_NUM],
                datetime.datetime.fromtimestamp(int(match[MATCH_TIME])),
                match[ALLIANCES][BLUE][TEAM_KEYS],
                match[ALLIANCES][RED][TEAM_KEYS]))

    # Sort by match number
    matches = sorted(matches, key=lambda x : x.match_num, reverse=False)
    return matches
