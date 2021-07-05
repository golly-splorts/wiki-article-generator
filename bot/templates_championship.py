import os
import json
import re
from pywikibot.page import Page


class TableBase(object):
    def get_last_season0(self):
        """
        Uses some basic datetime math to get the
        current Cup season.
        """
        import pytz
        from datetime import datetime, timedelta

        time_zone = pytz.timezone("US/Pacific")
        start_date = self.GOLLYX_START_DATE
        start_hour = int(self.GOLLYX_START_HOUR)
        gold_start = datetime.fromisoformat(start_date).replace(hour=start_hour)
        gold_end = gold_start + timedelta(hours=48 + 7)
        today = datetime.now()
        delta = today - gold_end
        daysfromend = delta.days
        weeksfromend = daysfromend // 7
        last_season0 = weeksfromend
        return last_season0

    def get_teams(self, season0):
        """
        Get teams data for season0
        """
        tname = f"gollyx-{self.cup.lower()}-data/season{season0}/teams.json"
        with open(tname, "r") as f:
            teams = json.load(f)
        return teams

    def get_team_league_div(self, team_name, teams):
        """
        Given a team name, return the league and division
        (stripped of the "League" and "Division" suffix).
        If team name not found, returns a tuple (None, None).
        """
        for team_dat in teams:
            if team_dat["teamName"] == team_name:
                lea = re.sub(" League", "", team_dat["league"])
                div = re.sub(" Division", "", team_dat["division"])
                return lea, div
        return (None, None)


class PseudoCup(object):
    GOLLYX_START_DATE = "2021-05-24"
    GOLLYX_START_HOUR = "9"
    cup = "Pseudo"
    leagues = ["Monterey Bay", "San Francisco Bay"]


class ToroidalCup(object):
    GOLLYX_START_DATE = "2021-05-27"
    GOLLYX_START_HOUR = "9"
    cup = "Toroidal"
    leagues = ["Cold", "Hot"]


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
