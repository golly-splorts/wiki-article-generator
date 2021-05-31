import pywikibot
from pywikibot.page import Page

site = pywikibot.Site()

pageTitle="Main_Page"
newPage=Page(site,pageTitle)
print(newPage.text)
