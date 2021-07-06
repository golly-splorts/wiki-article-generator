import os
import json
import re
from templates_base import TableBase, PseudoCup, ToroidalCup
from pywikibot.page import Page


class ChampionsTable(TableBase):
    def __init__(self, site):
        if self.cup is None:
            raise NotImplemented("Error: ChampionsTable is a virtual class")

        self.site = site
        self.page_title = f"Template:{self.cup}CupChampionsTable"
        self.pseudo_champions_page = Page(self.site, self.page_title)

        self.text_head = """{| class="wikitable"
|-
!Season
!%s Cup Champion
!Winning Division
!Series W-L
!Loser
!Losing Division
""" % (
            self.cup
        )

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

        new_lines = []

        new_lines.append(self.text_head)

        for season0 in range(0, last_season0 + 1):
            teams = self.get_teams(season0)

            fname = f"gollyx-{self.cup.lower()}-data/season{season0}/postseason.json"
            with open(fname, "r") as f:
                dat = json.load(f)

            pcs = dat["HCS"]

            last_day = pcs[-1]
            last_game = last_day[0]

            if last_game["team1Score"] > last_game["team2Score"]:
                win_team_abbr = last_game["team1Abbr"]
                win_team_name = last_game["team1Name"]
                win_team_lea, win_team_div = self.get_team_league_div(
                    win_team_name, teams
                )
                win_team_w = 4

                los_team_abbr = last_game["team2Abbr"]
                los_team_name = last_game["team2Name"]
                los_team_lea, los_team_div = self.get_team_league_div(
                    los_team_name, teams
                )
                los_team_w = last_game["team2SeriesWinLoss"][0]

            else:
                win_team_abbr = last_game["team2Abbr"]
                win_team_name = last_game["team2Name"]
                win_team_lea, win_team_div = self.get_team_league_div(
                    win_team_name, teams
                )
                win_team_w = 4

                los_team_abbr = last_game["team1Abbr"]
                los_team_name = last_game["team1Name"]
                los_team_lea, los_team_div = self.get_team_league_div(
                    los_team_name, teams
                )
                los_team_w = last_game["team1SeriesWinLoss"][0]

            text_body = "|-\n"
            text_body += "| [[%s/Season %d|S%d]]\n" % (self.cup, season0 + 1, season0 + 1)

            text_body += '| style="font-weight:bold; text-align:center; '
            text_body += (
                'background-color:{{TeamAbbrToHexColor|%s}}; color:#272B30;" | %s '
                % (win_team_abbr, win_team_name)
            )
            text_body += "\n"

            text_body += '| style="font-weight:bold; text-align:center; '
            text_body += (
                'background-color:{{TeamAbbrToHexColor|%s}}; color:#272B30;" | %s %s '
                % (win_team_abbr, win_team_lea, win_team_div)
            )
            text_body += "\n"

            text_body += '| style="font-weight:bold; text-align:center; '
            text_body += (
                'background-color:{{TeamAbbrToHexColor|%s}}; color:#272B30;" | %d-%d'
                % (win_team_abbr, win_team_w, los_team_w)
            )
            text_body += "\n"

            text_body += '| style="font-weight:bold; text-align:center; '
            text_body += (
                'background-color:{{TeamAbbrToHexColor|%s}}BB; color:#272B30;" | %s '
                % (los_team_abbr, los_team_name)
            )
            text_body += "\n"

            text_body += '| style="font-weight:bold; text-align:center; '
            text_body += (
                'background-color:{{TeamAbbrToHexColor|%s}}BB; color:#272B30;" | %s %s '
                % (los_team_abbr, los_team_lea, los_team_div)
            )
            text_body += "\n"

            new_lines.append(text_body)

        new_lines.append(self.text_tail)
        new_text = "\n".join(new_lines)

        if dry_run:
            print(new_text)
        else:
            self.pseudo_champions_page.text = new_text
            self.pseudo_champions_page.save(
                "Updating %s Cup champions table to season %d from pywikibot"
                % (self.cup, int(season))
            )


class PseudoChampionsTable(PseudoCup, ChampionsTable):
    pass


class ToroidalChampionsTable(ToroidalCup, ChampionsTable):
    pass
