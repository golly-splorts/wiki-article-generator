import requests
import os
import pandas as pd


API_URL = "https://api.golly.life"
LAST_SEASON = 10


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


def main():

    teams = get_teams()
    teams.sort(key = lambda x : x['teamName'])
    team_names = [t['teamName'] for t in teams]

    divisions = sorted(list(set([j['division'] for j in teams])))
    leagues = sorted(list(set([j['league'] for j in teams])))

    maps = get_maps()
    maps.sort(key = lambda x : x['mapName'])

    with open('shutouts.txt', 'w') as f:

        print("= Shutouts =\n\n", file=f)
        print("NOTE: Shutouts were much more frequent during Seasons 1 through 3 due to the bug that caused the \n", file=f)
        print("[[Season 3/Fixing Scandal|Season 3 Hellmouth Cup Fixing Scandal]], which led to more frequent shutouts.\n\n", file=f)

        for this_season in range(LAST_SEASON):

            # Print table header
            th = ""
            th += "{| class=\"wikitable\"\n"
            th += "|-\n"
            th += "!Season\n"
            th += "!Day\n"
            th += "!Winning Team\n"
            th += "!W Score\n"
            th += "!L Score\n"
            th += "!Losing Team\n"
            th += "!Game Link\n"

            tb = ""

            all_df = pd.DataFrame()

            season_dat = get_season(this_season)
            for day in season_dat:
                for game in day:
                    # Filter the WinLoss fields, since they aren't used and complicate the pandas import
                    game = {k: v for k, v in game.items() if 'WinLoss' not in k}
                    if game['team1Score'] > game['team2Score']:
                        game['winningTeamName'] = game['team1Name']
                        game['losingTeamName'] = game['team2Name']
                        game['winningTeamScore'] = game['team1Score']
                        game['losingTeamScore'] = game['team2Score']
                    else:
                        game['winningTeamName'] = game['team2Name']
                        game['losingTeamName'] = game['team1Name']
                        game['winningTeamScore'] = game['team2Score']
                        game['losingTeamScore'] = game['team1Score']

                    if game['losingTeamScore']==0:
                        # index=[0] necessary so we don't have to change {'a': 1} to {'a': [1]}
                        game_df = pd.DataFrame(game, index=[0])
                        # aaaand then we just ignore it again
                        all_df = all_df.append(game_df, ignore_index=True)

            all_df.sort_values('winningTeamScore', ascending=False)

            for i, row in all_df.iterrows():
                season = row['season']
                day = row['day']
                wteam = row['winningTeamName']
                wscore = row['winningTeamScore']
                lteam = row['losingTeamName']
                lscore = row['losingTeamScore']
                game_id = row['id']
                tb += "|-\n"
                tb += f"| [[Season {season+1}|S{season+1}]]\n"
                tb += f"| {day+1}\n"
                tb += f"| [[{wteam}]]\n"
                tb += f"| {wscore}\n"
                tb += f"| {lscore}\n"
                tb += f"| [[{lteam}]]\n"
                tb += f"| {{{{Game|{game_id}}}}}\n"

            tf = "|}\n\n"

            print(f"\n\n== Shutouts Season {this_season+1} ==\n", file=f)
            print(th, file=f)
            print(tb, file=f)
            print(tf, file=f)

        af = ""
        af += "{{Navbox stlats}}\n\n"
        af += "[[Category:Stlats]]\n"
        af += "[[Category:Update Each Season]]\n"

        print(af, file=f)
    
    print("shutouts.txt done")


if __name__ == "__main__":
    main()
