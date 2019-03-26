import datetime
import json
import numpy as np

from match import *
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
        if current_team.team_number == next_team_val.team_number:
            # Mark the match number, next alliance color, and number of matches out in the current match
            current_team.next_match_num = next_match.match_num
            current_team.next_match_alliance = next_team_key
            current_team.next_match_matches_out = match_index_out
            next_match.teams[next_team_key].is_back_to_back_related = True
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
            if teams[team.team_number] == 0:
                team.is_last_match = True
            teams[team.team_number] = teams[team.team_number] + 1

        # If the second to last match has not been visited for at least one team, keep going
        if not any(val == 1 for val in teams.values()):
            break


def insert_schedule_breaks(all_matches, total_match_count):
    """
    Finds and inserts dummy match records representing breaks wherever the schedule has time breaks.

    Arguments:
        all_matches: The list of all Match objects in the qualification schedule.
        total_match_count: The total number of matches in the qualification schedule.
    """
    values = []

    # Calculate times between each match
    for i in range(0, total_match_count - 1):
        current_match = all_matches[i]
        next_match = all_matches[i + 1]
        values.append((next_match.match_time - current_match.match_time).total_seconds())

    # Find median of times between matches
    median_match_time = np.median(values)

    break_indices = []

    # If time between any two matches is larger than the median +- 10% of the median, track the next
    # match's index so we can insert a break before it
    for i in range(0, total_match_count - 1):
        current_match = all_matches[i]
        next_match_index = i + 1
        next_match = all_matches[next_match_index]

        abs_value = abs(next_match.match_time - current_match.match_time).total_seconds() - median_match_time
        if (abs_value) > median_match_time:
            break_indices.append(next_match_index)

    # Go through the break indices in reverse and add dummy match records for breaks
    for i in range (len(break_indices) - 1, -1, -1):
        all_matches.insert(break_indices[i], DummyMatch(MATCH_TYPE_BREAK))


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

        for i in range(len(match[ALLIANCES][BLUE][TEAM_KEYS])):
            match[ALLIANCES][BLUE][TEAM_KEYS][i] = match[ALLIANCES][BLUE][TEAM_KEYS][i][TEAM_NUM_PREFIX_LEN:]

        for i in range(len(match[ALLIANCES][RED][TEAM_KEYS])):
            match[ALLIANCES][RED][TEAM_KEYS][i] = match[ALLIANCES][RED][TEAM_KEYS][i][TEAM_NUM_PREFIX_LEN:]

        matches.append(
            Match(
                match[MATCH_NUM],
                datetime.datetime.fromtimestamp(int(match[MATCH_TIME])),
                match[ALLIANCES][BLUE][TEAM_KEYS],
                match[ALLIANCES][RED][TEAM_KEYS]))

    # Sort by match number
    matches = sorted(matches, key=lambda x : x.match_num, reverse=False)
    return matches
