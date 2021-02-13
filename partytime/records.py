import requests
import os
import pandas as pd
import numpy as np
from pprint import pprint


####################
# this is all messed up
####################


API_URL = "https://api.golly.life"
LAST_SEASON = 0


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


def get_abbr_from_team_name(team_name, teams):
    for team in teams:
        if team['teamName'] == team_name:
            return team['teamAbbr']
    return None


def main():

    teams = get_teams()
    teams.sort(key = lambda x : x['teamName'])
    team_names = [t['teamName'] for t in teams]

    divisions = sorted(list(set([j['division'] for j in teams])))
    leagues = sorted(list(set([j['league'] for j in teams])))

    maps = get_maps()
    maps.sort(key = lambda x : x['mapName'])

    for league in leagues:

        league_prefix = league.split(" ")[0]
        filename = f"records_{league_prefix.lower()}.csv"

        all_records = pd.DataFrame()

        for this_season in range(LAST_SEASON+1):

            season_dat = get_season(this_season)

            for iD, day in enumerate(season_dat):

                day_records = {}

                day_records['season'] = day[0]['season']
                day_records['day'] = day[0]['day']
                for game in day:

                    if game['league']==league:

                        abbr1 = get_abbr_from_team_name(game['team1Name'], teams)
                        abbr2 = get_abbr_from_team_name(game['team2Name'], teams)

                        winkey1 = abbr1
                        winval1 = game['team1WinLoss'][0]

                        winkey2 = abbr2
                        winval2 = game['team2WinLoss'][0]

                        day_records[winkey1] = winval1
                        day_records[winkey2] = winval2

                # index=[0] necessary so we don't have to change {'a': 1} to {'a': [1]}
                record_df = pd.DataFrame(day_records, index=[0])
                # aaaand then we just ignore it again
                all_records = all_records.append(record_df, ignore_index=True)

                if iD==len(season_dat)-1:
                    last_day_records = {}
                    last_day_records['season'] = day[0]['season']
                    last_day_records['day'] = day[0]['day']+1
                    for game in day:
                        if game['league']==league:

                            w1add = 0
                            l1add = 0
                            w2add = 0
                            l2add = 0
                            if game['team1Score'] > game['team2Score']:
                                w1add = 1
                            elif game['team2Score'] > game['team1Score']:
                                w2add = 1

                            abbr1 = get_abbr_from_team_name(game['team1Name'], teams)
                            abbr2 = get_abbr_from_team_name(game['team2Name'], teams)

                            winkey1 = abbr1
                            winval1 = game['team1WinLoss'][0] + w1add

                            winkey2 = abbr2
                            winval2 = game['team2WinLoss'][0] + w2add

                            last_day_records[winkey1] = winval1
                            last_day_records[winkey2] = winval2

                    # index=[0] necessary so we don't have to change {'a': 1} to {'a': [1]}
                    lastrecord_df = pd.DataFrame(last_day_records, index=[0])
                    # aaaand then we just ignore it again
                    all_records = all_records.append(lastrecord_df, ignore_index=True)

        #print(all_records.columns)
        ds = ['season','day']
        sorted_team_columns = sorted(list(set(column_names)-set(ds)))
        sorted_columns = ds + sorted_team_columns
        all_records[sorted_columns].to_csv(filename, index=False)
        
        for abbr in sorted_team_columns:
            rank = f"{abbr}_Rank"
            def fun(series):
                ranklist = sorted(list(series[sorted_team_columns]))
                rank = {}
                for team in sorted_team_columns:
                    rank[team] = index(ranklist[team])
                return pd.Series(rank)
            rankseries = all_records.apply(fun)
            print("-"*40, abbr, "-"*40)
            print(rankseries)
            break



if __name__ == "__main__":
    main()
