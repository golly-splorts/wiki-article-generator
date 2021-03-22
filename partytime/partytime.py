import requests
import os
import pandas as pd
import numpy as np
from pprint import pprint


API_URL = "https://cloud.golly.life"
LAST_SEASON = 15
DAYS_PER_SEASON = 49


def get_endpoint_json(endpoint):
    url = API_URL + endpoint
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(
            f"Error fetching data from {url}: returned code {response.status_code}"
        )
    return response.json()


def get_teams(this_season):
    endpoint = f"/teams/{this_season}"
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


def find_game_id(team_name, day, season_dat):
    today_games = season_dat[day]
    for game in today_games:
        if game["team1Name"] == team_name or game["team2Name"] == team_name:
            return game["gameid"]
    return None


def get_division_teams_from_team_abbr(team_abbr, teams):
    lea, div = get_league_division_from_team_name(
        get_name_from_team_abbr(team_abbr, teams), teams
    )
    ourdiv = set()
    for team in teams:
        if team["league"] == lea and team["division"] == div:
            ourdiv.add(team["teamAbbr"])
    return sorted(list(ourdiv))


def get_league_division_from_team_name(team_name, teams):
    for team in teams:
        if team["teamName"] == team_name:
            return team["league"], team["division"]
    return None


def get_name_from_team_abbr(team_abbr, teams):
    for team in teams:
        if team["teamAbbr"] == team_abbr:
            return team["teamName"]
    return None


def get_abbr_from_team_name(team_name, teams):
    for team in teams:
        if team["teamName"] == team_name:
            return team["teamAbbr"]
    return None


def main():

    filename = "partytime.txt"
    with open(filename, "w") as f:

        th = ""
        th += "== Partytime Runs ==\n\n"
        th += "Related: [[Partytime Clomputations]]\n\n"
        th += "'''Partytime''' refers to the state of being mathematically eliminated from the possibility of playing in the postseason.\n\n"
        th += '{| class="wikitable"\n'
        th += "|-\n"
        th += "!Season\n"
        th += "!Day\n"
        th += "!League\n"
        th += "!Partytime Entrant\n"
        th += "!Game\n"

        tf = "|}"

        cats = "\n{{Navbox stlats}}\n\n[[Category:Update Each Season]]\n"

        print(th, file=f)

        for this_season in range(LAST_SEASON):

            teams = get_teams(this_season)
            teams.sort(key=lambda x: x["teamName"])
            team_names = [t["teamName"] for t in teams]

            divisions = sorted(list(set([j["division"] for j in teams])))
            leagues = sorted(list(set([j["league"] for j in teams])))

            maps = get_maps(this_season)
            maps.sort(key=lambda x: x["mapName"])


            if this_season != 0:
                # Add inter-season spacers
                print("|-", file=f)
                print(
                    '| colspan="5" style="background-color: #181c21;" | &nbsp;', file=f
                )

            # We will add multiple rows below, so collect the parts of the table they share
            seasonrow_shared = ""

            seasonrow_shared = "|-\n"

            # Season column
            seasonrow_shared += f"| [[Season {this_season+1}|S{this_season+1}]]"

            for league in leagues:

                league_prefix = league.split(" ")[0]
                ############## filename = f"records_{league_prefix.lower()}.csv"

                all_records = pd.DataFrame()

                season_dat = get_season(this_season)

                for iD, day in enumerate(season_dat):

                    day_records = {}

                    day_records["season"] = day[0]["season"]
                    day_records["day"] = day[0]["day"]
                    for game in day:

                        if game["league"] == league:

                            abbr1 = get_abbr_from_team_name(game["team1Name"], teams)
                            abbr2 = get_abbr_from_team_name(game["team2Name"], teams)

                            winkey1 = abbr1
                            winval1 = game["team1WinLoss"][0]

                            winkey2 = abbr2
                            winval2 = game["team2WinLoss"][0]

                            day_records[winkey1] = winval1
                            day_records[winkey2] = winval2

                    # index=[0] necessary so we don't have to change {'a': 1} to {'a': [1]}
                    record_df = pd.DataFrame(day_records, index=[0])
                    # aaaand then we just ignore it again
                    all_records = all_records.append(record_df, ignore_index=True)

                    if iD == len(season_dat) - 1:
                        last_day_records = {}
                        last_day_records["season"] = day[0]["season"]
                        last_day_records["day"] = day[0]["day"] + 1
                        for game in day:
                            if game["league"] == league:

                                w1add = 0
                                l1add = 0
                                w2add = 0
                                l2add = 0
                                if game["team1Score"] > game["team2Score"]:
                                    w1add = 1
                                elif game["team2Score"] > game["team1Score"]:
                                    w2add = 1

                                abbr1 = get_abbr_from_team_name(
                                    game["team1Name"], teams
                                )
                                abbr2 = get_abbr_from_team_name(
                                    game["team2Name"], teams
                                )

                                winkey1 = abbr1
                                winval1 = game["team1WinLoss"][0] + w1add

                                winkey2 = abbr2
                                winval2 = game["team2WinLoss"][0] + w2add

                                last_day_records[winkey1] = winval1
                                last_day_records[winkey2] = winval2

                        # index=[0] necessary so we don't have to change {'a': 1} to {'a': [1]}
                        lastrecord_df = pd.DataFrame(last_day_records, index=[0])
                        # aaaand then we just ignore it again
                        all_records = all_records.append(
                            lastrecord_df, ignore_index=True
                        )

                ds = ["season", "day"]
                sorted_team_columns = sorted(list(set(all_records.columns) - set(ds)))
                sorted_columns = ds + sorted_team_columns

                ### all_records[sorted_columns].to_csv(filename, index=False)

                def get_rank(series):
                    """
                    Given a row from the data frame containing wins for each team,
                    compute the rank of that team
                    """
                    ranklist = list(reversed(sorted(list(series[sorted_team_columns]))))
                    rank = {}
                    for team in sorted_team_columns:
                        rank[team] = ranklist.index(series[team]) + 1
                    return pd.Series(rank)

                rank_df = all_records.apply(get_rank, axis=1)
                all_records = all_records.join(rank_df, rsuffix="_rank")

                def get_partytime_number(series):
                    """
                    Given a row from the data frame containing wins and rank of each team,
                    determine the partytime number of the team.

                    A team only has a partytime number if they are not in current top 4.
                    If a team is in 5-8 place, then Team A is 4th place team, Team B is 5-8 place team.

                    Partytime number = S + 1 - W_A - L_B

                    S = games in season
                    A = 4th place team
                    B = 5-8 place teams

                    IMPORTANT: we store win-loss records as the win-loss record on day $day0,
                               before the game happens. When we switch to 1-indexed games,
                               we can think of that as the win-loss record on $day0 before the game
                               becoming the win-loss record on $day0+1 after the game.
                               So, saying "the win-loss record on day X" means, taking into account
                               the game on day X.
                    """
                    partytime = {}

                    # Because wins can be tied, we can end up with 2 3rd place teams and no 4th place team, etc.
                    # Figure out the number of wins of the lowest-ranked top-4 team
                    top_ranks_present = []
                    for team_abbr in sorted_team_columns:
                        rank = series[team_abbr + "_rank"]
                        if rank <= 4:
                            wins = series[team_abbr]
                            top_ranks_present.append((rank, wins))
                            # no need to find partytime for these teams
                            partytime[team_abbr] = 999
                    top_ranks_present.sort(
                        key=lambda x: x[1]
                    )  # sort puts lowest first, giving us least top rank
                    least_top_rank_wins = top_ranks_present[0][1]

                    # Now loop over bottom 4 teams
                    for team_abbr in sorted_team_columns:

                        # Also figure out the rank of the top team in this division,
                        # in case they are lower than 4th
                        division_team_abbrs = get_division_teams_from_team_abbr(
                            team_abbr, teams
                        )

                        divfirst_minrank = 999
                        divfirst_wins = 0
                        divfirst_abbr = ""
                        for division_team_abbr in division_team_abbrs:
                            if division_team_abbr != team_abbr:
                                if (
                                    series[division_team_abbr + "_rank"]
                                    < divfirst_minrank
                                ):
                                    # New first place in division
                                    divfirst_minrank = series[
                                        division_team_abbr + "_rank"
                                    ]
                                    divfirst_wins = series[division_team_abbr]
                                    divfirst_abbr = division_team_abbr

                        target_wins = min(divfirst_wins, least_top_rank_wins)

                        rank = series[team_abbr + "_rank"]
                        if rank > 4:
                            bottom_wins = series[team_abbr]
                            bottom_losses = series["day"] - bottom_wins

                            # Here it is!
                            partytime[team_abbr] = (
                                DAYS_PER_SEASON + 1 - target_wins - bottom_losses
                            )

                    return pd.Series(partytime)

                partytime_df = all_records[::-1].apply(get_partytime_number, axis=1)
                partytime_nteams = (partytime_df < 0).sum(axis=1)

                # Get the first day when a team is in partytime
                partytime_first_day = min(
                    partytime_nteams.loc[partytime_nteams > 0].index
                )
                z = partytime_df.loc[partytime_first_day]
                partytime_first_teams = list(z[z < 0].index)

                # Finally, a team having a negative partytime number on day X is taking into account
                # the loss on day X, so we want to see the game ID for the game on day X
                # (but day X is 1-indexed!)
                day = season_dat[partytime_first_day - 1]
                partytime_first_gameids = []
                partytime_first_opponents = []
                partytime_first_scores = []
                for partytime_first_team in partytime_first_teams:
                    full_name = get_name_from_team_abbr(partytime_first_team, teams)
                    for game in day:
                        if (
                            game["team1Name"] == full_name
                            or game["team2Name"] == full_name
                        ):
                            partytime_first_gameids.append(game["gameid"])
                            if game["team1Name"] == full_name:
                                partytime_first_opponents.append(
                                    get_abbr_from_team_name(game["team2Name"], teams)
                                )
                                partytime_first_scores.append(
                                    str(game["team1Score"])
                                    + "-"
                                    + str(game["team2Score"])
                                )
                            else:
                                partytime_first_opponents.append(
                                    get_abbr_from_team_name(game["team1Name"], teams)
                                )
                                partytime_first_scores.append(
                                    str(game["team2Score"])
                                    + "-"
                                    + str(game["team1Score"])
                                )

                if partytime_first_day < DAYS_PER_SEASON:

                    # Append a new row for each partytime entrant to table body

                    prefix1 = (
                        f'| style="font-weight:bold; text-align:center; color:#272B30; '
                    )

                    for (first_team, first_opponent, first_gameid, first_score,) in zip(
                        partytime_first_teams,
                        partytime_first_opponents,
                        partytime_first_gameids,
                        partytime_first_scores,
                    ):
                        prefix2 = f'background-color:{{{{TeamAbbrToHexColor|{first_team}}}}};" |'
                        prefix = f"{prefix1}{prefix2}"

                        ptname = get_name_from_team_abbr(first_team, teams)
                        ptoppname = get_name_from_team_abbr(first_opponent, teams)

                        entrant_col = f"{prefix} {ptname}"
                        game_col = f'{prefix} <span style="background-color: #272B30; margin: 5px;">{{{{Game|{first_gameid}}}}}</span><br />vs {ptoppname}'

                        # Shared columns
                        print(seasonrow_shared, file=f)

                        # Day/League columns
                        print(f"| {partytime_first_day}", file=f)
                        print(f"| {league_prefix}", file=f)

                        # Entrant/game columns
                        print(entrant_col, file=f)
                        print(game_col, file=f)

                else:

                    # Append a null row, no partytime

                    prefix = f'| style="font-weight:bold; text-align:center; background-color:#272B30; color:#eee;" |'

                    entrant_col = f"{prefix} nO pArTyTiMe SpEeDrUnS!!1!"
                    game_col = f"{prefix} &nbsp;"

                    # Shared columns
                    print(seasonrow_shared, file=f)

                    # Day/League columns
                    print(f"| {partytime_first_day}", file=f)
                    print(f"| {league_prefix}", file=f)

                    # Entrant/game columns
                    print(entrant_col, file=f)
                    print(game_col, file=f)

        print(tf, file=f)
        print(cats, file=f)


if __name__ == "__main__":
    main()
