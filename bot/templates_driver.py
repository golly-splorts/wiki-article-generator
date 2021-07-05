from bot_classes import PseudoChampionsTable
from pywikibot import Site


if __name__ == "__main__":

    DRY_RUN = True
    site = Site()

    tab = PseudoChampionsTable(site)
    tab.update(dry_run=DRY_RUN)
