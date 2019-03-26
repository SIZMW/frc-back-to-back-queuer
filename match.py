import calendar
import datetime

from tba_constants import *

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
            self.teams['B{}'.format(i + 1)] = Team(blue_teams[i][TEAM_NUM_PREFIX_LEN:], None)
        
        for i in range(len(red_teams)):
            self.teams['R{}'.format(i + 1)] = Team(red_teams[i][TEAM_NUM_PREFIX_LEN:], None)
    
    def __str__(self):
        """
        Returns a string representation of this object.

        Returns:
            A string
        """
        return '{:2d} [{}]: Blue:{},{},{} | Red:{},{},{}'.format(
            self.match_num,
            self.match_time,
            str(self.teams['B1']),
            str(self.teams['B2']),
            str(self.teams['B3']),
            str(self.teams['R1']),
            str(self.teams['R2']),
            str(self.teams['R3']))

    def __repr__(self):
        """
        Returns a representation of this object.

        Returns:
            A string
        """
        return str(self)

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


class Team(object):
    """
    This class represents a single team in a qualification match with a team number and information about the team's recent and future matches.
    """

    team_number = None
    next_match_num = None
    next_match_alliance = None
    next_match_matches_out = None
    is_last_match = False
    is_back_to_back_related = False

    def __init__(self, team_number, next_match_num, next_match_alliance=None, next_match_matches_out=None):
        """
        Initializes the Team object from the keyword arguments.

        Arguments:
            team_number: The team number for this team.
            next_match_num: The match number for this team's next back to back match, if any.
            next_match_alliance: The alliance color for this team's next back to back match, if any.
            next_match_matches_out: The number of matches out to this team's next back to back match, if any.
        """
        self.team_number = team_number
        self.next_match_num = next_match_num
        self.next_match_alliance = next_match_alliance
        self.next_match_matches_out = next_match_matches_out
        self.is_last_match = False
        self.is_back_to_back_related = False

    def __str__(self):
        """
        Returns a string representation of this object.

        Returns:
            A string
        """

        return '{}{}{}{}'.format(
            self.team_number,
            ' (M{}:{}:+{})'.format(self.next_match_num, self.next_match_alliance, self.next_match_matches_out) if self.next_match_num else "",
            "" if not self.is_last_match else " (L)",
            "" if not self.is_back_to_back_related else " *")

    def __repr__(self):
        """
        Returns a representation of this object.

        Returns:
            A string
        """
        return str(self)
