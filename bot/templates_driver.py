from bot_classes import PseudoChampsTable
from pywikibot import Site


if __name__ == "__main__":

    DRY_RUN = False
    site = Site()

    tab = PseudoChampsTable(site)
    tab.update(dry_run=DRY_RUN)
