import requests
import os
import pandas as pd
import numpy as np
from pprint import pprint


####################
# this is messed up
####################


API_URL = "https://api.golly.life"
LAST_SEASON = 1


def get_endpoint_json(endpoint):
    url = API_URL + endpoint
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error fetching data from {url}: returned code {response.code}")
    return response.json()


def get_teams():
    endpoint = '/teams'
    teams = get_endpoint_json(endpoint)
    return teams


def get_maps(filter_new_maps = True):
    endpoint = '/maps'
    maps = get_endpoint_json(endpoint)
    if filter_new_maps:
        ignore_pattern = ['spaceshipcluster', 'spaceshipcrash', 'quadjustyna', 'randompartition']
        maps = [m for m in maps if m['patternName'] not in ignore_pattern]
    return maps


def get_season(season):
    endpoint = f"/season/{season}"
    s = get_endpoint_json(endpoint)
    return s


def find_game_id(team_name, day, season_dat):
    today_games = season_dat[day]
    for game in today_games:
        if game['team1Name'] == team_name or game['team2Name'] == team_name:
            return game['id']
    return None


def main():

    teams = get_teams()
    teams.sort(key = lambda x : x['teamName'])
    team_names = [t['teamName'] for t in teams]

    divisions = sorted(list(set([j['division'] for j in teams])))
    leagues = sorted(list(set([j['league'] for j in teams])))

    maps = get_maps()
    maps.sort(key = lambda x : x['mapName'])

    ##################################################
    # magic number: first to partytime

    print("= Party Time Speed Runs =")
    for this_season in range(LAST_SEASON):

        # Print table header
        th = ""
        th += "{| class=\"wikitable\"\n"
        th += "|-\n"
        th += "!Season\n"
        th += "!League\n"
        th += "!Team(s)\n"
        th += "!Days to Party Time\n"
        th += "!Party Time Loss\n"

        tb = ""

        all_df = pd.DataFrame()

        # Store (league, days_to_partytime, team_names)
        first_to_partytime = []

        season_dat = get_season(this_season)
        for league in reversed(leagues):

            for i, day in enumerate(season_dat):
                # Get the rankings of each team as of today
                today_ranking_list = []
                for game in day:
                    if game['league'] == league:
                        today_ranking_list.append((game['team1Name'], game['team1WinLoss'][0]))
                        today_ranking_list.append((game['team2Name'], game['team2WinLoss'][0]))
                today_ranking_list.sort(key=lambda x: x[1], reverse=True)

                # Get the names of the bottom 4 teams as of today
                today_bottom4_names = set()
                for k in range(4, 8):
                    today_bottom4_names.add(today_ranking_list[k][0])

                # Get the rankings of each team if the bottom 4 teams take the remaining games
                # (use 49 here not 48 because w/l records are 1 day behind)
                days_remaining = 49 - i
                future_ranking_list = []
                for k in range(4):
                    # leage top 4 wins are unchanged
                    future_ranking_list.append(today_ranking_list[k])
                for k in range(4, 8):
                    # leage bottom 4 wins are boosted
                    today_name, today_wins = today_ranking_list[k]
                    future_ranking_list.append((today_name, today_wins+days_remaining))
                future_ranking_list.sort(key=lambda x: x[1], reverse=True)

                # Get the names of the bottom 4 teams in the future scenario
                future_bottom4_names = set()
                for k in range(4, 8):
                    future_bottom4_names.add(future_ranking_list[k][0])

                # If we have overlap... welcome to partytime!
                partypeople = today_bottom4_names.intersection(future_bottom4_names)
                if len(partypeople)>0:

                    for partyperson in partypeople:
                        # Get current rank of this potential party person
                        partyperson_wins = 0
                        for future_ranking in future_ranking_list:
                            if future_ranking[0]==partyperson:
                                partyperson_wins = future_ranking[1]
                        # If potential party person has same number of wins as #4 spot,
                        # they aren't in party time just yet...
                        if partyperson_wins<future_ranking_list[3][1]:
                            # This is indeed party time

                            # The days get a little bit confusing here.
                            # We are using win loss records from day0 = i
                            # But the win loss record is from the conclusion of the day before
                            # So, if a team has entered partytime on day i,
                            # they actually entered partytime with their loss on day i-1
                            #first_to_partytime.append((league, i-1, sorted(list(partypeople))))
                            first_to_partytime.append((league, i-1, sorted(list(partypeople))))

                    if len(first_to_partytime)>0:
                        break

        # Sort by first to partytime
        first_to_partytime.sort(key=lambda x: x[1], reverse=False)

        # One row per partyperson
        for league, day, partypeople in first_to_partytime:
            for partyperson in partypeople:
                game_id = find_game_id(partyperson, day, season_dat)
                tb += "|-\n"
                tb += f"| [[Season {this_season+1}|S{this_season+1}]]\n"
                tb += f"| {league}\n"
                tb += f"| [[{partyperson}]]\n"
                tb += f"| style=\"text-align: center;\" | {day}\n"
                if game_id is not None:
                    tb += f"| {{{{Game|{game_id}}}}}\n"
                else:
                    tb += "| &nbsp;\n"

        tf = "|}"

        print(f"\n\n== Season {this_season+1} ==\n")
        print(th)
        print(tb)
        print(tf)



if __name__ == "__main__":
    main()
