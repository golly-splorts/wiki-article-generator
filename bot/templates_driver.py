from templates_championship import (
    PseudoChampionsTable,
    PseudoPenantTable,
    ToroidalChampionsTable,
    ToroidalPenantTable,
)
from pywikibot import Site


if __name__ == "__main__":

    DRY_RUN = False
    site = Site()

    # psu = PseudoChampionsTable(site)
    # psu.update(dry_run=DRY_RUN)

    # tor = ToroidalChampionsTable(site)
    # tor.update(dry_run=DRY_RUN)

    psup = PseudoPenantTable(site)
    psup.update(dry_run=DRY_RUN)

    tsup = ToroidalPenantTable(site)
    tsup.update(dry_run=DRY_RUN)
