import requests
import os
import pandas as pd
import numpy as np


API_URL = "https://api.golly.life"


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


def streak_summary(team_name, team_df):
    
    result = team_df.apply(lambda x: 1 if (
        (x['team1Name']==team_name and x['team1Score'] > x['team2Score']) or
        (x['team2Name']==team_name and x['team2Score'] > x['team1Score'])
    ) else -1, axis=1)
    
    # Create streak counts
    # [-1 -1 -1 1 1 1 1] <-- result
    # [-1 -2 -3 1 2 3 4] <-- streakcount
    # https://stackoverflow.com/a/27626699
    streakcount = result * (result.groupby((result != result.shift()).cumsum()).cumcount() + 1)
    
    # For each streak, get the last item in streakcount (length of streak)
    lastinstreak = (streakcount * streakcount.shift(-1, fill_value=0)) < 0
    
    # # streakcount and result are the same length
    # for c, r, last in zip(streakcount.values, result.values, lastinstreak.values):
    #     if last:
    #         lab = 'W' if r==1 else 'L'
    #         print(f"{lab} {c}")
    
    # this is basically a list of streak lengths, plus indices in team_df where they happen
    return streakcount.loc[lastinstreak]



def main():

    print('loading initial data')

    teams = get_teams()
    teams.sort(key = lambda x : x['teamName'])
    team_names = [t['teamName'] for t in teams]

    divisions = sorted(list(set([j['division'] for j in teams])))
    leagues = sorted(list(set([j['league'] for j in teams])))

    maps = get_maps()
    maps.sort(key = lambda x : x['mapName'])

    class Streak(object):
        def __init__(self, team_name, team_df, streak_length, streak_end_day):
            self.team_name = team_name
            self.team_df = team_df
            self.streak_length = streak_length

            self.df = None
            streak_days = range(streak_end_day-streak_length+1, streak_end_day+1)
            for today in streak_days:
                z = team_df.loc[team_df['day']==today]
                if self.df is None:
                    self.df = z
                else:
                    self.df = self.df.append(z)
        def __repr__(self):
            s = ""
            s += f"{self.team_name} Streak: {self.streak_length}n\n"
            for irow, row in self.df.iterrows():
                s += f"    {row['team1Name']} {row['team1Score']:>4} - {row['team2Score']:<4} {row['team2Name']}\n"
            return s

    wstreaks = []
    lstreaks = []

    for this_season in range(6):

        print(f'parsing season {this_season+1} data')

        season_dat = get_season(this_season)
        season_df = pd.DataFrame()
        for day in season_dat:
            for game in day:
                # Filter the WinLoss fields, since they aren't used and complicate the pandas import
                game = {k: v for k, v in game.items() if 'WinLoss' not in k}
                # index=[0] necessary so we don't have to change {'a': 1} to {'a': [1]}
                game_df = pd.DataFrame(game, index=[0])
                # aaaand then we just ignore it again
                season_df = season_df.append(game_df, ignore_index=True)

        team_dfs = {}
        for iL, league in enumerate(leagues):
            for iD, division in enumerate(divisions):
                division_teams = [team for team in teams if team['division']==division and team['league']==league]
                for iT, division_team in enumerate(division_teams):
                    team_name = division_team['teamName']
                    team_df = season_df.loc[(season_df['team1Name']==team_name) | (season_df['team2Name']==team_name)]
                    team_dfs[team_name] = team_df

        for team in teams:
            team_name = team['teamName']
            team_df = team_dfs[team_name]
            summary = streak_summary(team_name, team_df)

            wstreak = max(summary)
            wstreak_end_days = list(team_df.loc[summary.loc[summary==max(summary)].index]['day'].values)
            for wstreak_end_day in wstreak_end_days:
                s = Streak(team_name, team_df, wstreak, wstreak_end_day)
                wstreaks.append((wstreak, this_season, s))

            lstreak = min(summary)
            lstreak_end_days = list(team_df.loc[summary.loc[summary==min(summary)].index]['day'].values)
            for lstreak_end_day in lstreak_end_days:
                s = Streak(team_name, team_df, lstreak, lstreak_end_day)
                lstreaks.append((lstreak, this_season, s))

    # Sort by streak length
    wstreaks.sort(key=lambda x: x[0], reverse=True)
    lstreaks.sort(key=lambda x: x[0], reverse=True)

    # Now step through each season:
    # - find the record for that season plus all prior seasons
    # - find the record for that season only
    # - if this season greater than or equal to, include it
    # in the table of records
    for this_season in range(6):
        wstreaks_record_allprev = max(set([j[0] for j in wstreaks if j[1]<=this_season]))
        wstreaks_record_season = max(set([j[0] for j in wstreaks if j[1]==this_season]))
        print(f'season {this_season}:')
        if wstreaks_record_season>=wstreaks_record_allprev:
            for w in wstreaks:
                if w[0]==wstreaks_record_season:
                    print(w[2])


if __name__ == "__main__":
    main()
