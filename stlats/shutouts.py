import time
import requests
import os
import pandas as pd


API_URL = "https://cloud.golly.life"
LAST_SEASON = 18


def get_endpoint_json(endpoint):
    url = API_URL + endpoint
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error fetching data from {url}: returned code {response.status_code}")
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


def main():

    with open('shutouts.txt', 'w') as f:

        print("= Shutouts =\n\n", file=f)
        print("NOTE: Shutouts were much more frequent during Seasons 1 through 3 due to the bug that caused the \n", file=f)
        print("[[Season 3/Fixing Scandal|Season 3 Hellmouth Cup Fixing Scandal]], which led to more frequent shutouts.\n\n", file=f)

        for this_season in range(LAST_SEASON+1):

            print(f"Now processing season {this_season}")

            teams = get_teams(this_season)
            teams.sort(key=lambda x: x["teamName"])
            team_names = [t["teamName"] for t in teams]

            divisions = sorted(list(set([j["division"] for j in teams])))
            leagues = sorted(list(set([j["league"] for j in teams])))

            maps = get_maps(this_season)
            maps.sort(key=lambda x: x["mapName"])

            season_dat = get_season(this_season)
            postseason_dat = get_postseason(this_season)

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
            postseason_dat = get_postseason(this_season)

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
                        game_df = pd.DataFrame(game, index=[0])
                        all_df = all_df.append(game_df, ignore_index=True)

            for series in postseason_dat:
                miniseries = postseason_dat[series]
                for day in miniseries:
                    for game in day:
                        game = {k: v for k, v in game.items() if "WinLoss" not in k}
                        if game["team1Score"] > game["team2Score"]:
                            game["winningTeamName"] = game["team1Name"]
                            game["losingTeamName"] = game["team2Name"]
                            game["winningTeamScore"] = game["team1Score"]
                            game["losingTeamScore"] = game["team2Score"]
                        else:
                            game["winningTeamName"] = game["team2Name"]
                            game["losingTeamName"] = game["team1Name"]
                            game["winningTeamScore"] = game["team2Score"]
                            game["losingTeamScore"] = game["team1Score"]

                        if game['losingTeamScore']==0:
                            game_df = pd.DataFrame(game, index=[0])
                            all_df = all_df.append(game_df, ignore_index=True)

            all_df = all_df.sort_values('winningTeamScore', ascending=False)

            for i, row in all_df.iterrows():
                season = row['season']
                day = row['day']
                wteam = row['winningTeamName']
                wscore = row['winningTeamScore']
                lteam = row['losingTeamName']
                lscore = row['losingTeamScore']
                game_id = row['gameid']
                tb += "|-\n"
                tb += f"| [[Season {season+1}|S{season+1}]]\n"
                if day+1 > 49:
                    tb += f"| {day+1}*\n"
                else:
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

            time.sleep(15)
            
        af = ""
        af += "{{Navbox stlats}}\n\n"
        af += "[[Category:Stlats]]\n"
        af += "[[Category:Update Each Season]]\n"

        print(af, file=f)
    
    print("shutouts.txt done")


if __name__ == "__main__":
    main()
