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
