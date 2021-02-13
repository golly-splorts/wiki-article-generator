import requests
import os
import pandas as pd
import numpy as np


API_URL = "https://api.golly.life"
LAST_SEASON = 9


def get_endpoint_json(endpoint):
    url = API_URL + endpoint
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(
            f"Error fetching data from {url}: returned code {response.code}"
        )
    return response.json()


def get_teams():
    endpoint = "/teams"
    teams = get_endpoint_json(endpoint)
    return teams


def get_maps(filter_new_maps=True):
    endpoint = "/maps"
    maps = get_endpoint_json(endpoint)
    if filter_new_maps:
        ignore_pattern = [
            "spaceshipcluster",
            "spaceshipcrash",
            "quadjustyna",
            "randompartition",
        ]
        maps = [m for m in maps if m["patternName"] not in ignore_pattern]
    return maps


def get_season(season):
    endpoint = f"/season/{season}"
    s = get_endpoint_json(endpoint)
    return s


def get_table_text(teama_name, teama_abbr, teamb_name, teamb_abbr, all_df):

    # Print table header
    th = ""
    th += '{| class="wikitable" style="text-align:center;" width="60%"\n'
    th += "|-\n"

    th += f"! colspan=4 | {{{{Team|{teama_abbr}|link=false|color=true}}}} vs. {{{{Team|{teamb_abbr}|link=false|color=true}}}}\n"
    #th += f"!{{{{Team|{teama_abbr}|link=false|color=true}}}} Wins\n"
    #th += f"!{{{{Team|{teamb_abbr}|link=false|color=true}}}} Wins\n"
    #th += f"!Runs ({teama_abbr} - {teamb_abbr})\n"

    th += "|-\n"
    th += "!Season\n"
    th += "!Wins\n"
    th += "!Runs\n"
    th += "!Crown Winner\n"

    tb = ""
    for this_season in range(LAST_SEASON):

        season_df = all_df.loc[all_df['season']==this_season]
        filter_df = season_df.loc[
            (
                (season_df["team1Name"] == teama_name)
                & (season_df["team2Name"] == teamb_name)
            )
            | (
                (season_df["team2Name"] == teama_name)
                & (season_df["team1Name"] == teamb_name)
            )
        ]

        def teama_runs_func(row):
            if row['winningTeamName']==teama_name:
                return row['winningTeamScore']
            elif row['losingTeamName']==teama_name:
                return row['losingTeamScore']

        def teamb_runs_func(row):
            if row['winningTeamName']==teamb_name:
                return row['winningTeamScore']
            elif row['losingTeamName']==teamb_name:
                return row['losingTeamScore']

        teama_wins = filter_df.loc[filter_df['winningTeamName']==teama_name].shape[0]
        teama_runs = filter_df.apply(teama_runs_func, axis=1).sum()

        teamb_wins = filter_df.loc[filter_df['winningTeamName']==teamb_name].shape[0]
        teamb_runs = filter_df.apply(teamb_runs_func, axis=1).sum()

        crown_winner = ""
        if teama_wins > teamb_wins:
            crown_winner = teama_name
            crown_winner_abbr = teama_abbr
        elif teamb_wins > teama_wins:
            crown_winner = teamb_name
            crown_winner_abbr = teamb_abbr
        else:
            # tie in wins, check runs
            if teama_runs > teamb_runs:
                crown_winner = teama_name
                crown_winner_abbr = teama_abbr
            elif teamb_runs > teama_runs:
                crown_winner = teamb_name
                crown_winner_abbr = teamb_abbr
            else:
                crown_winner = None
                crown_winner_abbr = None

        tb += "|-\n"
        tb += f"| [[Season {this_season+1}|S{this_season+1}]]\n"
        tb += f"| {{{{TeamLogo|{teama_abbr}}}}} {teama_wins} - {teamb_wins} {{{{TeamLogo|{teamb_abbr}}}}}\n"
        tb += f"| {{{{TeamLogo|{teama_abbr}}}}} {teama_runs} - {teamb_runs} {{{{TeamLogo|{teamb_abbr}}}}}\n"
        tb += f"| style=\"font-weight:bold; background-color:{{{{TeamAbbrToHexColor|{crown_winner_abbr}}}}}; color: #272B30;\" | {crown_winner}\n"


    tf = "|}"

    return th + tb + tf


def main():

    teams = get_teams()
    teams.sort(key=lambda x: x["teamName"])
    team_names = [t["teamName"] for t in teams]

    divisions = sorted(list(set([j["division"] for j in teams])))
    leagues = sorted(list(set([j["league"] for j in teams])))

    maps = get_maps()
    maps.sort(key=lambda x: x["mapName"])

    ##################################################
    # crown table

    all_df = pd.DataFrame()

    for this_season in range(LAST_SEASON):
        season_dat = get_season(this_season)

        for day in season_dat:
            for game in day:
                # Filter the WinLoss fields, since they aren't used and complicate the pandas import
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

                # index=[0] necessary so we don't have to change {'a': 1} to {'a': [1]}
                game_df = pd.DataFrame(game, index=[0])
                # aaaand then we just ignore it again
                all_df = all_df.append(game_df, ignore_index=True)

    with open('cactus_crown.txt', 'w') as f:
        f.write(
            get_table_text(
                "Elko Astronauts",
                "EA",
                "Tucson Butchers",
                "TB", 
                all_df
            )
        )
    print('cactus_crown.txt done')

    with open('texas_crown.txt', 'w') as f:
        f.write(
            get_table_text(
                "Baltimore Texas",
                "BTX",
                "Ft. Worth Piano Tuners",
                "FWPT", 
                all_df
            )
        )
    print('texas_crown.txt done')

    with open('cali_crown.txt', 'w') as f:
        f.write(
            get_table_text(
                "San Francisco Boat Shoes",
                "SFBS",
                "Sacramento Boot Lickers",
                "SAC", 
                all_df
            )
        )
    print('cali_crown.txt done')

    with open('pacific_crown.txt', 'w') as f:
        f.write(
            get_table_text(
                "Long Beach Flightless Birds",
                "LBFB",
                "San Diego Balloon Animals",
                "SDBA", 
                all_df
            )
        )
    print('pacific_crown.txt done')

    with open('midwest_crown.txt', 'w') as f:
        f.write(
            get_table_text(
                "Milwaukee Flamingos",
                "MILF",
                "Detroit Grape Chews",
                "DET", 
                all_df
            )
        )
    print('midwest_crown.txt done')


if __name__ == "__main__":
    main()
