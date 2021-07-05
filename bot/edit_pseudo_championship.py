import json
import re
import pywikibot
from pywikibot.page import Page


LAST_SEASON = 6
DRY_RUN = False


site = pywikibot.Site()

page_title = "Template:PseudoCupChampionsTable"
pseudo_champions_page = Page(site, page_title)
lines = [j.strip() for j in pseudo_champions_page.text.split("\n")]

new_lines = []

text_head = """
{| class="wikitable"
|-
!Season
!Pseudo Cup Champion
!Winning Division
!Series W-L
!Loser
!Losing Division
"""

new_lines.append(text_head)

for season0 in range(0, LAST_SEASON):

    tname = f'gollyx-pseudo-data/season{season0}/teams.json'
    with open(tname, 'r') as f:
        teams = json.load(f)

    def get_team_league_div(team_name):
        for team_dat in teams:
            if team_dat['teamName'] == team_name:
                lea = re.sub(' League', '', team_dat['league'])
                div = re.sub(' Division', '', team_dat['division'])
                return lea, div
        return (None, None)

    fname = f'gollyx-pseudo-data/season{season0}/postseason.json'
    with open(fname, 'r') as f:
        dat = json.load(f)

    pcs = dat['HCS']

    last_day = pcs[-1]
    last_game = last_day[0]

    if last_game['team1Score'] > last_game['team2Score']:
        win_team_abbr = last_game['team1Abbr']
        win_team_name = last_game['team1Name']
        win_team_lea, win_team_div = get_team_league_div(win_team_name)
        win_team_w = 4

        los_team_abbr = last_game['team2Abbr'] 
        los_team_name = last_game['team2Name'] 
        los_team_lea, los_team_div = get_team_league_div(los_team_name)
        los_team_w = last_game['team2SeriesWinLoss'][0]

    else:
        win_team_abbr = last_game['team2Abbr']
        win_team_name = last_game['team2Name']
        win_team_lea, win_team_div = get_team_league_div(win_team_name)
        win_team_w = 4

        los_team_abbr = last_game['team1Abbr'] 
        los_team_name = last_game['team1Name'] 
        los_team_lea, los_team_div = get_team_league_div(los_team_name)
        los_team_w = last_game['team1SeriesWinLoss'][0]

    text_body = "|-\n"
    text_body += "| [[Season %d|S%d]]\n"%(season0+1, season0+1)

    text_body += '| style="font-weight:bold; text-align:center; '
    text_body += 'background-color:{{TeamAbbrToHexColor|%s}}; color:#272B30;" | %s '%(win_team_abbr, win_team_name)
    text_body += "\n"

    text_body += '| style="font-weight:bold; text-align:center; '
    text_body += 'background-color:{{TeamAbbrToHexColor|%s}}; color:#272B30;" | %s %s '%(win_team_abbr, win_team_lea, win_team_div)
    text_body += "\n"

    text_body += '| style="font-weight:bold; text-align:center; '
    text_body += 'background-color:{{TeamAbbrToHexColor|%s}}; color:#272B30;" | %d-%d'%(win_team_abbr, win_team_w, los_team_w)
    text_body += "\n"

    text_body += '| style="font-weight:bold; text-align:center; '
    text_body += 'background-color:{{TeamAbbrToHexColor|%s}}BB; color:#272B30;" | %s '%(los_team_abbr, los_team_name)
    text_body += "\n"

    text_body += '| style="font-weight:bold; text-align:center; '
    text_body += 'background-color:{{TeamAbbrToHexColor|%s}}BB; color:#272B30;" | %s %s '%(los_team_abbr, los_team_lea, los_team_div)
    text_body += "\n"

    new_lines.append(text_body)

text_tail = """|}<noinclude>
[[Category:Pseudo Cup]]
[[Category:Update Each Season]]
</noinclude>
"""

new_lines.append(text_tail)
new_text = "\n".join(new_lines)

if DRY_RUN:
    print(new_text)
else:
    new_page = Page(site, page_title)
    new_page.text = new_text
    new_page.save("Updating {{Tl|PseudoCupChampionsTable}} to season %d from pywikibot"%(LAST_SEASON))
