import csv
import os

from match import *
from file_util import *
from tba_api_requester import *
from tba_constants import *
from frc_back_to_back_queuer import *

# Custom fields
BA_KEY = 'key'
KEY_FILE = 'key.json'

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser(description='Retrieves the qualification match schedule for a specific event from The Blue Alliance and generates the match schedule marked with all the back-to-back matches for each team.')
    parser.add_argument('-i', '--event_id', type=str, help='Event ID from The Blue Alliance for the specific event. Format is <year><event>.')
    parser.add_argument('-o', '--output_file', type=file, help='Output TSV file where the generated schedule will be saved.')
    parser.add_argument('-m', '--max_matches_out', type=int, help='Maximum number of matches to search out from a given match. In other words, the largest number of matches between two matches that considers them "back-to-back" for queuing purposes.')
    args = parser.parse_args()

    # Load API key
    read_key = load_api_key(KEY_FILE, BA_KEY)

    # Get matches
    print 'Retrieving match data...'
    raw_match_data = retrieve_event_match_data(args.event_id, read_key)

    print 'Parsing match data...'
    matches = generate_match_data(raw_match_data)
    matches_count = len(matches)

    # Find back-to-back matches for all teams in each match
    print 'Searching for back to back matches...'
    search_all_alliance_teams(matches, matches_count, args.max_matches_out)

    # Find the last match of each team
    print 'Finding last matches per team...'
    update_last_match_for_all_teams(args.event_id, read_key, matches, matches_count)

    # Find breaks within the schedule
    print 'Finding breaks in the schedule...'
    insert_schedule_breaks(matches, matches_count)

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
                str(match.teams['R1']),
                str(match.teams['R2']),
                str(match.teams['R3']),
                str(match.teams['B1']),
                str(match.teams['B2']),
                str(match.teams['B3'])])
    
    print 'Wrote schedule to {}'.format(args.output_file)
