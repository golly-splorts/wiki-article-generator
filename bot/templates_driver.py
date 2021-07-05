from templates_championship import PseudoChampionsTable, ToroidalChampionsTable
from pywikibot import Site


if __name__ == "__main__":

    DRY_RUN = False
    site = Site()

    psu = PseudoChampionsTable(site)
    psu.update(dry_run=DRY_RUN)

    tor = ToroidalChampionsTable(site)
    tor.update(dry_run=DRY_RUN)
