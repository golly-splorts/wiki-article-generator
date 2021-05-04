import requests
import os
import pandas as pd


API_URL = "https://cloud.golly.life"
LAST_SEASON = 21


def get_endpoint_json(endpoint):
    url = API_URL + endpoint
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(
            f"Error fetching data from {url}: returned code {response.status_code}"
        )
    return response.json()


def get_teams(season):
    endpoint = f"/teams/{season}"
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


def get_postseason(season):
    endpoint = f"/postseason/{season}"
    p = get_endpoint_json(endpoint)
    return p


def get_seeds(season):
    endpoint = f"/seeds/{season}"
    seeds = get_endpoint_json(endpoint)
    return seeds


def get_league_division_from_team_name(team_name, teams):
    for team in teams:
        if team["teamName"] == team_name:
            return team["league"], team["division"]
    return None


def get_abbr_from_team_name(team_name, teams):
    for team in teams:
        if team["teamName"] == team_name:
            return team["teamAbbr"]
    return None


def main():

    # For each season,
    # Get the teams playing in the Hellmouth Cup
    # This gives you the pennant winners for each season

    cup_winners = []

    for this_season in range(LAST_SEASON):

        teams = get_teams(this_season)
        teams.sort(key=lambda x: x["teamName"])
        team_names = [t["teamName"] for t in teams]

        leagues = sorted(list(set([j["league"] for j in teams])))


        postseason_dat = get_postseason(this_season)
        hc = postseason_dat["HCS"]
        try:
            lastday = hc[-1]
        except:
            continue

        game = lastday[0]

        if (
            game["team1SeriesWinLoss"][0] == 3
            and game["team1Score"] > game["team2Score"]
        ):
            winner = game["team1Name"]
            loser = game["team2Name"]
            winner_wl = (
                f"{game['team1SeriesWinLoss'][0]+1}-{game['team1SeriesWinLoss'][1]}"
            )
        elif (
            game["team2SeriesWinLoss"][0] == 3
            and game["team2Score"] > game["team1Score"]
        ):
            winner = game["team2Name"]
            loser = game["team1Name"]
            winner_wl = (
                f"{game['team2SeriesWinLoss'][0]+1}-{game['team2SeriesWinLoss'][1]}"
            )

        winner_abbr = get_abbr_from_team_name(winner, teams)
        winner_league, winner_div = get_league_division_from_team_name(winner, teams)

        loser_abbr = get_abbr_from_team_name(loser, teams)
        loser_league, loser_div = get_league_division_from_team_name(loser, teams)

        cup_winners.append(
            (
                this_season,
                winner_league,
                winner_div,
                winner,
                winner_abbr,
                winner_wl,
                loser_league,
                loser_div,
                loser,
                loser_abbr,
            )
        )

    # Sort by season
    cup_winners.sort(key=lambda x: x[0])

    with open("cup.txt", "w") as f:

        th = ""
        th += '{| class="wikitable"\n'
        th += "|-\n"
        th += "!Season\n"
        th += "!Hellmouth Cup Champion\n"
        th += "!Winning Division\n"
        th += "!Series W-L\n"
        th += "!Loser \n"
        th += "!Losing Division\n"

        tf = "|}<noinclude>\n[[Category:Hellmouth Cup]]\n[[Category:Update Each Season]]\n[[Category:Leagues Table Template]]\n</noinclude>\n"

        tb = ""

        for cw in cup_winners:
            this_season = cw[0]

            winner_league = cw[1].split(" ")[0]
            winner_div = cw[2].split(" ")[0]
            winner_name = cw[3]
            winner_abbr = cw[4]
            winner_wl = cw[5]

            loser_league = cw[6].split(" ")[0]
            loser_div = cw[7].split(" ")[0]
            loser_name = cw[8]
            loser_abbr = cw[9]

            winner_leadiv = winner_league + " " + winner_div
            loser_leadiv = loser_league + " " + loser_div

            tb += "|-\n"

            cprefix = f'| style="font-weight:bold; text-align:center; background-color:{{{{TeamAbbrToHexColor|{winner_abbr}}}}}; color:#272B30;" |'
            closerprefix = f'| style="font-weight:normal; text-align:center; background-color:{{{{TeamAbbrToHexColor|{loser_abbr}}}}}BB; color:#272B30;" |'

            tb += f"| [[Season {this_season+1}|S{this_season+1}]]\n"
            tb += f"{cprefix} {winner_name}\n"
            tb += f"{cprefix} {winner_leadiv}\n"
            tb += f"{cprefix} {winner_wl}\n"
            tb += f"{closerprefix} {loser_name}\n"
            tb += f"{closerprefix} {loser_leadiv}\n"

        print(th, file=f)
        print(tb, file=f)
        print(tf, file=f)

    print("cup.txt done")


if __name__ == "__main__":
    main()
