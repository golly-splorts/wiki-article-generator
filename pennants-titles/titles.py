import requests
import os
import pandas as pd


API_URL = "https://api.golly.life"
LAST_SEASON = 12


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

    divisions = sorted(list(set([j['division'] for j in teams])))
    leagues = sorted(list(set([j['league'] for j in teams])))

    # For each season,
    # Get the seeds
    # Find the first team from each particular division/league combination

    # title_winners stores the following:
    # season, league, division, division title winner, winner abbbr, season w-l record, seed rank
    title_winners = []

    for this_season in range(LAST_SEASON):

        season_dat = get_season(this_season)
        final_day = season_dat[-1]

        all_seeds = get_seeds(this_season)
        for league in leagues:
            league_seed = all_seeds[league]
            for division in divisions:
                for i in range(len(league_seed)):
                    seed_name = league_seed[i]
                    seed_league, seed_division = get_league_division_from_team_name(seed_name, teams)
                    seed_abbr = get_abbr_from_team_name(seed_name, teams)
                    if seed_league==league and seed_division==division:

                        seed_wl = ""
                        for final_game in final_day:
                            if final_game['team1Name']==seed_name:
                                if final_game['team1Score']>final_game['team2Score']:
                                    seed_wl = f"{final_game['team1WinLoss'][0]+1}-{final_game['team1WinLoss'][1]}"
                                else:
                                    seed_wl = f"{final_game['team1WinLoss'][0]}-{final_game['team1WinLoss'][1]+1}"
                                break
                            elif final_game['team2Name']==seed_name:
                                if final_game['team2Score']>final_game['team1Score']:
                                    seed_wl = f"{final_game['team2WinLoss'][0]+1}-{final_game['team2WinLoss'][1]}"
                                else:
                                    seed_wl = f"{final_game['team2WinLoss'][0]}-{final_game['team2WinLoss'][1]+1}"
                                break

                        seed_rank = i+1

                        # We found the division title winner, now save the info
                        title_winners.append((
                            this_season, league, division, seed_name, seed_abbr, seed_wl, seed_rank
                        ))
                        break


    # Sort by season
    title_winners.sort(key=lambda x: x[0])

    for league in leagues:
        league_prefix = league.split(" ")[0]
        for division in divisions:
            division_prefix = division.split(" ")[0]

            filename = f"titles_{league_prefix.lower()}_{division_prefix.lower()}.txt"

            with open(filename, 'w') as f:

                th = ""
                th += "{| class=\"wikitable\"\n"
                th += "|-\n"
                th += "!Season\n"
                th += "!Division Title Winner\n"
                th += "!Season W-L Record\n"

                tf = "|}<noinclude>\n[[Category:Hellmouth Cup]]\n[[Category:Update Each Season]]\n[[Category:Leagues Table Template]]\n</noinclude>\n"


                tb = ""

                # Already sorted by season
                ld_title_winners = [tw for tw in title_winners if tw[1]==league and tw[2]==division]
                for tw in ld_title_winners:
                    this_season = tw[0]
                    seed_name = tw[3]
                    seed_abbr = tw[4]
                    seed_wl = tw[5]
                    seed_rank = tw[6]

                    tb += "|-\n"
                    tb += f"| [[Season {this_season+1}|S{this_season+1}]]\n"
                    tb += f"| style=\"font-weight:bold; text-align:center; background-color:{{{{TeamAbbrToHexColor|{seed_abbr}}}}}; color:#272B30;\" | {seed_name} (#{seed_rank})\n"
                    tb += f"| style=\"font-weight:bold; text-align:center; background-color:{{{{TeamAbbrToHexColor|{seed_abbr}}}}}; color:#272B30;\" | {seed_wl}\n"

                print(th, file=f)
                print(tb, file=f)
                print(tf, file=f)

            print(f"{filename} done")


if __name__ == "__main__":
    main()
