import requests
import os
import pandas as pd
import numpy as np


API_URL = "https://cloud.golly.life"
LAST_SEASON = 17


def get_endpoint_json(endpoint):
    url = API_URL + endpoint
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error fetching data from {url}: returned code {response.code}")
    return response.json()


def get_teams(this_season):
    endpoint = f"/teams/{this_season}"
    teams = get_endpoint_json(endpoint)
    return teams


def get_maps(this_season):
    endpoint = f'/maps/{this_season}'
    maps = get_endpoint_json(endpoint)
    return maps


def get_season(season):
    endpoint = f"/season/{season}"
    s = get_endpoint_json(endpoint)
    return s


def get_postseason(season):
    endpoint = f"/postseason/{season}"
    p = get_endpoint_json(endpoint)
    return p


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

    class Streak(object):
        def __init__(self, team_name, team_df, streak_length, streak_end_day):
            self.team_name = team_name
            self.team_df = team_df
            self.streak_length = streak_length

            season = list(set(team_df['season'].values))
            if len(season)>1:
                raise Exception("Error with team df passed to Streak: too many seasons! One at a time.")
            self.season = season[0]

            self.df = None
            streak_days = range(streak_end_day-streak_length+1, streak_end_day+1)
            self.streak_days = streak_days
            for today in streak_days:
                z = team_df.loc[team_df['day']==today]
                if self.df is None:
                    self.df = z
                else:
                    self.df = self.df.append(z)
        def __repr__(self):
            s = ""

            # Columns:
            # season
            # days
            # length
            # team
            # team runs
            # opponent runs
            # opponents list

            s += "|-\n"
            s += f"| [[Season {self.season+1}|S{self.season+1}]]\n"
            s += f"| {', '.join([str(j+1) for j in self.streak_days])}\n"
            s += f"| {self.streak_length}\n"
            s += f"| [[{self.team_name}]]\n"

            our_score = 0
            their_score = 0
            opponents_list = set()
            for irow, row in self.df.iterrows():
                if row['team1Name']==self.team_name:
                    our_score += row['team1Score']
                    their_score += row['team2Score']
                    opponents_list.add(row['team2Name'])
            opponents_list = sorted(list(opponents_list))

            s += f"| {our_score}\n"
            s += f"| {their_score}\n"
            s += f"| [[{']], [['.join(opponents_list)}]]\n"

            return s


    ##################################################
    # streak tables

    with open('streaks.txt', 'w') as f:

        th = ""
        th += "{| class=\"wikitable\"\n"
        th += "|-\n"
        th += "!Season\n"
        th += "!Days\n"
        th += "!Length\n"
        th += "!Team\n"
        th += "!Score\n"
        th += "!Opp. Score\n"
        th += "!Opponents\n"

        wtb = ""
        ltb = ""

        wstreaks = []
        lstreaks = []
        for this_season in range(LAST_SEASON):

            teams = get_teams(this_season)
            teams.sort(key=lambda x: x["teamName"])
            team_names = [t["teamName"] for t in teams]

            divisions = sorted(list(set([j["division"] for j in teams])))
            leagues = sorted(list(set([j["league"] for j in teams])))

            maps = get_maps(this_season)
            maps.sort(key=lambda x: x["mapName"])

            season_dat = get_season(this_season)
            postseason_dat = get_postseason(this_season)

            games_df = pd.DataFrame()
            for day in season_dat:
                for game in day:
                    # Filter the WinLoss fields, since they aren't used and complicate the pandas import
                    game = {k: v for k, v in game.items() if 'WinLoss' not in k}
                    game_df = pd.DataFrame(game, index=[0])
                    games_df = games_df.append(game_df, ignore_index=True)

            for series in postseason_dat:
                miniseries = postseason_dat[series]
                for day in miniseries:
                    for game in day:
                        game = {k: v for k, v in game.items() if "WinLoss" not in k}
                        game_df = pd.DataFrame(game, index=[0])
                        games_df = games_df.append(game_df, ignore_index=True)

            team_dfs = {}
            for iL, league in enumerate(leagues):
                for iD, division in enumerate(divisions):
                    division_teams = [team for team in teams if team['division']==division and team['league']==league]
                    for iT, division_team in enumerate(division_teams):
                        team_name = division_team['teamName']
                        team_df = games_df.loc[(games_df['team1Name']==team_name) | (games_df['team2Name']==team_name)]
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
                    lstreakmag = abs(lstreak)
                    s = Streak(team_name, team_df, lstreakmag, lstreak_end_day)
                    lstreaks.append((lstreakmag, this_season, s))

            # Get length of record winning streaks for this season
            wstreaks_this_season = [j for j in wstreaks if j[1]==this_season]
            wstreaks_this_season.sort(key=lambda x: x[0], reverse=True)
            wstreaks_record_season = max(set([j[0] for j in wstreaks_this_season]))
            # Print out each one
            for w in wstreaks_this_season:
                if w[0]==wstreaks_record_season:
                    wtb += str(w[2])

            # Get length of record losing streaks for this season
            lstreaks_this_season = [j for j in lstreaks if j[1]==this_season]
            lstreaks_this_season.sort(key=lambda x: x[0], reverse=True)
            lstreaks_record_season = max(set([j[0] for j in lstreaks_this_season]))
            # Print out each one
            for lo in lstreaks_this_season:
                if lo[0]==lstreaks_record_season:
                    ltb += str(lo[2])

        tf = "|}\n\n"

        print("\n= Winning Streaks =\n\n", file=f)
        print("This table lists the longest winning streak(s) for each season.\n\n", file=f)
        print(th,  file=f)
        print(wtb, file=f)
        print(tf,  file=f)

        print("\n= Losing Streaks =\n\n", file=f)
        print("This table lists the longest losing streak(s) for each season.\n\n", file=f)
        print(th,  file=f)
        print(ltb, file=f)
        print(tf,  file=f)

        af = ""
        af += "{{Navbox stlats}}\n\n"
        af += "[[Category:Stlats]]\n"
        af += "[[Category:Update Each Season]]\n"

        print(af, file=f)

    print("streaks.txt done")

if __name__ == "__main__":
    main()
