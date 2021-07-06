import os
import json
import re
from pywikibot.page import Page
from templates_base import TableBase, PseudoCup, ToroidalCup


class PennantTable(TableBase):
    def __init__(self, site):
        if self.cup is None:
            raise NotImplemented("Error: PennantsTable is a virtual class")

        self.site = site

        self.pages = {}
        for league in self.leagues:
            label = re.sub(" ", "", league)
            self.page_title = f"Template:{self.cup}Cup{label}PennantTable"
            p = Page(self.site, self.page_title)
            self.pages[league] = p

        self.text_head = """{| class="wikitable"
|-
!Season
!League Pennant Winner
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

            this_page = self.pages[league]

            new_lines = []

            new_lines.append(self.text_head)

            for season0 in range(0, last_season0 + 1):
                teams = self.get_teams(season0)

                fname = (
                    f"gollyx-{self.cup.lower()}-data/season{season0}/postseason.json"
                )
                with open(fname, "r") as f:
                    dat = json.load(f)

                sname = (
                    f"gollyx-{self.cup.lower()}-data/season{season0}/seed.json"
                )
                with open(sname, "r") as f:
                    seed_dat = json.load(f)

                pcs = dat["HCS"]

                last_day = pcs[-1]
                last_game = last_day[0]

                team1_lea, team1_div = self.get_team_league_div(
                    last_game["team1Name"], teams
                )
                team2_lea, team2_div = self.get_team_league_div(
                    last_game["team2Name"], teams
                )

                this_team_abbr = ""
                this_team_name = ""
                if team1_lea == league:
                    this_team_abbr = last_game["team1Abbr"]
                    this_team_name = last_game["team1Name"]
                elif team2_lea == league:
                    this_team_abbr = last_game["team2Abbr"]
                    this_team_name = last_game["team2Name"]

                # Assemble the new row
                text_body = "|-\n"

                # Season column
                text_body += "| [[%s/Season %d|S%d]]\n" % (self.cup, season0 + 1, season0 + 1)

                # Styling
                text_body += '| style="font-weight:bold; text-align:center; '

                # Team color and name
                text_body += (
                    'background-color:{{TeamAbbrToHexColor|%s}}; color:#272B30;" | %s '
                    % (this_team_abbr, this_team_name)
                )

                # Seed number
                league_lab = league + " League"
                seed = seed_dat[league_lab].index(this_team_name)
                if seed >= 0:
                    text_body += f"(#{seed+1})"

                text_body += "\n"

                new_lines.append(text_body)

            # Complete the pennant table for this league
            new_lines.append(self.text_tail)

            new_text = "\n".join(new_lines)

            if dry_run:
                print(new_text)
            else:
                this_page.text = new_text
                this_page.save(
                    "Updating pennant template for %s Cup %s League to season %d from pywikibot."
                    % (self.cup, league, int(season))
                )


class PseudoPennantTable(PseudoCup, PennantTable):
    pass


class ToroidalPennantTable(ToroidalCup, PennantTable):
    pass


