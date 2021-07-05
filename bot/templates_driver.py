from bot_classes import PseudoChampsTable
from pywikibot import Site


if __name__ == "__main__":

    LAST_SEASON = 6
    DRY_RUN = True

    site = Site()
    tab = PseudoChampsTable(site)
    tab.update(season=LAST_SEASON, dry_run=DRY_RUN)
