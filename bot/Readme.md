# Golly Wiki Bots

This directory contains scripts for running Golly Wiki bots.

These bots use pywikibot.

## Instructions

Before you begin, download a copy of the latest release and unzip it
to a new directory here called `core_stable`.

Also set up the virtual environment to have pywikibot installed.
(Note that we don't necessarily install pywikibot from the `core_stable`
directory, we are mainly using that directory for scripts and credentials
and things.)

Set up pywikibot to work with the Golly wiki family.

Log in with pywikibot so credentials are stored in `core_stable`.

Now run the scripts via the `pwb.py` script:

```
python core_stable/pwb.py templates_driver.py
```

