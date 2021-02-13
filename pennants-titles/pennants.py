import requests
import os
import pandas as pd


API_URL = "https://api.golly.life"
LAST_SEASON = 9


def get_endpoint_json(endpoint):
    url = API_URL + endpoint
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error fetching data from {url}: returned code {response.status_code}")
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


def get_postseason(season):
    endpoint = f"/postseason/{season}"
    p = get_endpoint_json(endpoint)
    return p


def get_seeds(season):
    endpoint = f'/seeds/{season}'
    seeds = get_endpoint_json(endpoint)
    return seeds


def get_league_division_from_team_name(team_name, teams):
    for team in teams:
        if team['teamName'] == team_name:
            return team['league'], team['division']
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

    leagues = sorted(list(set([j['league'] for j in teams])))

    # For each season,
    # Get the teams playing in the Hellmouth Cup
    # This gives you the pennant winners for each season

    pennant_winners = []

    for this_season in range(LAST_SEASON):

        all_seeds = get_seeds(this_season)

        postseason_dat = get_postseason(this_season)
        hc = postseason_dat['WS']
        day = hc[0]
        postgame = day[0]

        team1 = postgame['team1Name']
        abbr1 = get_abbr_from_team_name(team1, teams)
        league1, _ = get_league_division_from_team_name(team1, teams)
        team1seed = 0
        for i in range(len(all_seeds[league1])):
            if all_seeds[league1][i]==team1:
                team1seed = i+1
                break

        team2 = postgame['team2Name']
        abbr2 = get_abbr_from_team_name(team2, teams)
        league2, _ = get_league_division_from_team_name(team2, teams)
        team2seed = 0
        for i in range(len(all_seeds[league2])):
            if all_seeds[league2][i]==team2:
                team2seed = i+1
                break

        pennant_winners.append((
            this_season, league1, team1, abbr1, team1seed
        ))

        pennant_winners.append((
            this_season, league2, team2, abbr2, team2seed
        ))

    # Sort by season
    pennant_winners.sort(key=lambda x: x[0])

    for league in leagues:
        league_prefix = league.split(" ")[0]

        filename = f"pennants_{league_prefix.lower()}.txt"

        with open(filename, "w") as f:

            th = ""
            th += "{| class=\"wikitable\"\n"
            th += "|-\n"
            th += "!Season\n"
            th += "!League Pennant Winner\n"

            tf  = "|}<noinclude>\n[[Category:Hellmouth Cup]]\n[[Category:Update Each Season]]\n[[Category:Leagues Table Template]]</noinclude>"

            print("= League Pennants =", file=f)
            print("", file=f)
            print("The teams that finish at the top of their league win a League Pennant and a spot in the [[Hellmouth Cup]].", file=f)
            print("", file=f)
            print("The following tables list league pennant winners for each season for the Hot and Cold Leagues:", file=f)
            print("", file=f)

            tb = ""

            # Already sorted by season
            lea_pennant_winners = [tw for tw in pennant_winners if tw[1]==league]
            for tw in lea_pennant_winners:
                this_season = tw[0]
                seed_name = tw[2]
                seed_abbr = tw[3]
                seed_rank = tw[4]

                tb += "|-\n"
                tb += f"| [[Season {this_season+1}|S{this_season+1}]]\n"
                tb += f"| style=\"font-weight:bold; text-align:center; background-color:{{{{TeamAbbrToHexColor|{seed_abbr}}}}}; color:#272B30;\" | {seed_name} (#{seed_rank})\n"

            print(th, file=f)
            print(tb, file=f)
            print(tf, file=f)

        print(f"{filename} done")


if __name__ == "__main__":
    main()
