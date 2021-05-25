import os
import sys
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from pprint import pprint
import requests
import pandas as pd
import numpy as np
import seaborn as sns


"""
Season N win loss analytics using the /season endpoint of the golly.life API.
"""

API_URL = "https://cloud.golly.life"


def usage():
    print(f"{__file__}: usage:")
    print("")
    print(f"    {__file__} [season]")
    print("")
    print("Inputs:")
    print("    SEASON: one-indexed season (integer)")
    print("")
    print("Outputs:")
    print("    Directory named season<season>")
    print("")
    sys.exit(1)


def main():

    if len(sys.argv) != 2:
        usage()

    try:
        season1 = int(sys.argv[1])
        if season1 < 1:
            raise ValueError
    except ValueError:
        usage()

    season0 = season1 - 1
    doit(season0)


def doit(season0):

    # ----------------
    # Make the plots:
    #
    # Run differential vs days
    # GA500 vs days

    plt.style.use("dark_background")

    teams = get_teams(season0)
    teams.sort(key=lambda x: x["teamName"])

    maps = get_maps(season0)
    maps.sort(key=lambda x: x["mapName"])

    season = get_season(season0)

    # ## Parse
    #
    # Parse and load data into a pandas data frame.
    #
    # Season data is structured as a list of lists. The outer list is a list of days. The inner list is a list of games for each day. Each game is a dictionary containing team names, scores, map name, initial conditions, etc.
    #
    # Iterate over each day and each game and add them all to a data frame.

    season_df = pd.DataFrame()

    for day in season:
        for game in day:
            # Filter the WinLoss fields, since they aren't used and complicate the pandas import
            game = {k: v for k, v in game.items() if "WinLoss" not in k}
            # index=[0] necessary so we don't have to change {'a': 1} to {'a': [1]}
            game_df = pd.DataFrame(game, index=[0])
            # aaaand then we just ignore it again
            season_df = season_df.append(game_df, ignore_index=True)

    divisions = sorted(list(set([j["division"] for j in teams])))
    leagues = sorted(list(set([j["league"] for j in teams])))

    golly_gray = "#272B30"

    fig500, axes500 = plt.subplots(2, 2, figsize=(15, 10))

    figdiff, axesdiff = plt.subplots(2, 2, figsize=(15, 10))

    team_dfs = {}

    axid = 0
    ax500min = 0
    ax500max = 0
    axdiffmin = 0
    axdiffmax = 0
    for iL, league in enumerate(leagues):
        for iD, division in enumerate(divisions):
            division_teams = [
                team
                for team in teams
                if team["division"] == division and team["league"] == league
            ]

            ax500 = axes500[iL][iD]
            axdiff = axesdiff[iL][iD]

            for iT, division_team in enumerate(division_teams):

                team_name = division_team["teamName"]
                team_color = division_team["teamColor"]
                team_df = season_df.loc[
                    (season_df["team1Name"] == team_name)
                    | (season_df["team2Name"] == team_name)
                ]
                team_dfs[team_name] = team_df

                scores = team_df.apply(
                    lambda x: x["team1Score"]
                    if x["team1Name"] == team_name
                    else x["team2Score"],
                    axis=1,
                )
                scores_against = team_df.apply(
                    lambda x: x["team1Score"]
                    if x["team2Name"] == team_name
                    else x["team2Score"],
                    axis=1,
                )

                wins = team_df.apply(
                    lambda x: 1
                    if (
                        (
                            x["team1Name"] == team_name
                            and x["team1Score"] > x["team2Score"]
                        )
                        or (
                            x["team2Name"] == team_name
                            and x["team2Score"] > x["team1Score"]
                        )
                    )
                    else 0,
                    axis=1,
                )

                ga500 = team_df.apply(
                    lambda x: 0.5
                    if (
                        (
                            x["team1Name"] == team_name
                            and x["team1Score"] > x["team2Score"]
                        )
                        or (
                            x["team2Name"] == team_name
                            and x["team2Score"] > x["team1Score"]
                        )
                    )
                    else -0.5,
                    axis=1,
                )

                ga500cs = [0] + list(ga500.cumsum().values)
                ax500.plot(
                    [d + 1 for d in range(len(ga500cs))],
                    ga500cs,
                    "-",
                    color=team_color,
                    label=team_name,
                )

                ax500min = min(ax500min, min(ga500cs))
                ax500max = max(ax500max, max(ga500cs))

                rdcs = [0] + list((scores.cumsum() - scores_against.cumsum()).values)
                axdiff.plot(
                    [d + 1 for d in range(len(rdcs))],
                    rdcs,
                    "-",
                    color=team_color,
                    label=team_name,
                )

                axdiffmin = min(axdiffmin, min(rdcs))
                axdiffmax = max(axdiffmax, max(rdcs))

            ax500.set_xlim([1, 50])
            axdiff.set_xlim([1, 50])

            axdiff.set_xticks([1, 10, 20, 30, 40, 50])

            league_label = league.split(" ")[0]
            division_label = division.split(" ")[0]

            ax500.set_facecolor(golly_gray)
            ax500.set_xlabel("Day")
            ax500.set_ylabel("Games Above .500")
            ax500.set_title(
                f"{league_label} {division_label}: Season {season0+1} Games Above .500"
            )
            legend = ax500.legend()
            legend.get_frame().set_facecolor(golly_gray)

            axdiff.set_facecolor(golly_gray)
            axdiff.set_xlabel("Day")
            axdiff.set_ylabel("Point Differential")
            axdiff.set_title(
                f"{league_label} {division_label}: Season {season0+1} Score Differentials"
            )
            axdiff.legend()
            legend = axdiff.legend()
            legend.get_frame().set_facecolor(golly_gray)


    for iL, league in enumerate(leagues):
        for iD, division in enumerate(divisions):
            ax500 = axes500[iL][iD]
            axdiff = axesdiff[iL][iD]

            ax500.set_ylim([ - (abs(ax500min) + 2), ax500max + 2])
            axdiff.set_ylim([-(abs(axdiffmax)+300), axdiffmax + 300])

    fig500.patch.set_facecolor(golly_gray)
    figdiff.patch.set_facecolor(golly_gray)

    fig500.tight_layout()
    figdiff.tight_layout()

    dn = f"season{season0+1}"
    try:
        os.mkdir(dn)
    except FileExistsError:
        pass
    fig500.savefig(
        f"{dn}/golly_season{season0+1}_ga500.jpg", facecolor=fig500.get_facecolor()
    )
    figdiff.savefig(
        f"{dn}/golly_season{season0+1}_diffruns.jpg", facecolor=figdiff.get_facecolor()
    )


def get_endpoint_json(endpoint):
    url = API_URL + endpoint
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(
            f"Error fetching data from {url}: returned code {response.status_code}"
        )
    return response.json()


def get_teams(season0):
    endpoint = f"/teams/{season0}"
    teams = get_endpoint_json(endpoint)
    return teams


def get_maps(season0):
    endpoint = f"/maps/{season0}"
    maps = get_endpoint_json(endpoint)
    return maps


def get_season(seas):
    endpoint = f"/season/{seas}"
    season = get_endpoint_json(endpoint)
    return season


if __name__ == "__main__":
    main()
