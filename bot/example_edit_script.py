import pywikibot
from pywikibot.page import Page

site = pywikibot.Site()

page_title = "User:Ch4zm/BotTest"
new_page = Page(site, page_title)
lines = [j.strip() for j in new_page.text.split("\n")]

new_lines = []
for line in lines:
    if line == "Goodbye line!":
        new_lines.append("Hello new line!")
    else:
        new_lines.append(line)

new_page.text = "\n".join(new_lines)
new_page.save("Hello I am a bot this is my second edit")

