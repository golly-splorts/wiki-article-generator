import os
import json
import re
from pywikibot.page import Page
from templates_base import TableBase, PseudoCup, ToroidalCup


class DivTitleTable(TableBase):
    def __init__(self, site):
        if self.cup is None:
            raise NotImplemented("Error: DivTitleTable is a virtual class")

        self.site = site

        self.pages = {}
        for league in self.leagues:
            for division in self.divisions:

                league_label = re.sub(" ", "", league)
                self.page_title = (
                    f"Template:{self.cup}Cup{league_label}{division}TitleTable"
                )
                p = Page(self.site, self.page_title)
                self.pages[(league, division)] = p

        self.text_head = """{| class="wikitable"
|-
!Season
!Division Title Winner
!Season W-L Record
"""

        self.text_tail = """|}<noinclude>
[[Category:%s Cup]]
[[Category:Update Each Season]]
[[Category:Leagues Table Template]]
</noinclude>
""" % (
            self.cup
        )

    def update(self, season=None, dry_run=True):
        """
        Update the template to include information up to the latest season.
        IMPORTANT: season is 1-indexed.
        """
        if season is None or season < 1:
            last_season0 = self.get_last_season0()
            season = last_season0 + 1
        else:
            last_season0 = season - 1

        for league in self.leagues:

            for division in self.divisions:
                this_page = self.pages[(league, division)]

                new_lines = []

                new_lines.append(self.text_head)

                # The loops are ordered this way because we assemble
                # one table per league per division, and each table we
                # assemble has a row for each season. No shortcuts.
                for season0 in range(0, last_season0 + 1):
                    teams = self.get_teams(season0)

                    fname = (
                        f"gollyx-{self.cup.lower()}-data/season{season0}/season.json"
                    )
                    with open(fname, "r") as f:
                        season_dat = json.load(f)

                    sname = f"gollyx-{self.cup.lower()}-data/season{season0}/seed.json"
                    with open(sname, "r") as f:
                        seed_dat = json.load(f)

                    # To find the division title winner,
                    # go through the seed table from top to bottom
                    # and find the first team in this leage+division
                    division_label = division + " Division"
                    league_label = league + " League"
                    league_seed_dat = seed_dat[league_label]

                    title_team_name = ""
                    title_team_abbr = ""
                    title_team_seed0 = -1
                    for k, lsd in enumerate(league_seed_dat):
                        # Use the seed team name to get the league and division,
                        # and check if it matches. if not, keep going.
                        # Note, returned league/division names do not include "League" or "Division"
                        lsd_lea, lsd_div = self.get_team_league_div(lsd, teams)
                        if lsd_lea == league:
                            if lsd_div == division:
                                title_team_name = lsd
                                title_team_abbr = self.get_team_abbr(lsd, teams)
                                title_team_seed0 = k
                                break

                    if title_team_name=="" or title_team_abbr=="" or title_team_seed0 < 0:
                        raise Exception("Could not find team matching league {league} division {division} in seed table")

                    # We have the division title winner,
                    # now use the last day of the regular season
                    # to get their win-loss record.
                    last_day = season_dat[-1]

                    # Iterate over each game on the last day and look for
                    # our title winner.
                    for last_game in last_day:
                        if last_game['team1Abbr'] == title_team_abbr:
                            # Get the win-loss record (before the last game) and update it
                            # to account for outcome of the last game
                            title_team_wl = last_game['team1WinLoss']
                            if last_game['team1Score'] > last_game['team2Score']:
                                title_team_wl[0] += 1
                            else:
                                title_team_wl[1] += 1

                        elif last_game['team2Abbr'] == title_team_abbr:
                            title_team_wl = last_game['team2WinLoss']
                            if last_game['team2Score'] > last_game['team1Score']:
                                title_team_wl[0] += 1
                            else:
                                title_team_wl[1] += 1

                    # Assemble the new row
                    text_body = "|-\n"

                    # Season column
                    text_body += "| [[%s/Season %d|S%d]]\n" % (
                        self.cup,
                        season0 + 1,
                        season0 + 1,
                    )

                    # Team name and seed column

                    # Styling
                    text_body += '| style="font-weight:bold; text-align:center; '

                    # Team color and name
                    text_body += (
                        'background-color:{{TeamAbbrToHexColor|%s}}; color:#272B30;" | %s '
                        % (title_team_abbr, title_team_name)
                    )

                    # Seed number
                    text_body += f"(#{title_team_seed0+1})"

                    text_body += "\n"

                    # Team win-loss record column
                    text_body += '| style="font-weight:bold; text-align:center; '
                    text_body += (
                        'background-color:{{TeamAbbrToHexColor|%s}}; color:#272B30;" | %d-%d '
                        % (title_team_abbr, title_team_wl[0], title_team_wl[1])
                    )

                    text_body += "\n"

                    new_lines.append(text_body)

                
                # Done with season loop, now finish the title table
                new_lines.append(self.text_tail)

                new_text = "\n".join(new_lines)

                if dry_run:
                    print(new_text)
                else:
                    this_page.text = new_text
                    this_page.save(
                        "Updating title template for %s Cup %s League %s Division to season %d from pywikibot."
                        % (self.cup, league, division, int(season))
                    )


class PseudoDivTitleTable(PseudoCup, DivTitleTable):
    pass


class ToroidalDivTitleTable(ToroidalCup, DivTitleTable):
    pass
