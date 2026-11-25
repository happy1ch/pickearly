import sys
from playwright.sync_api import sync_playwright

OUT = "/workspace/worktmp/shots"
import os
os.makedirs(OUT, exist_ok=True)

pages = [
    ("index.html", "home", 1440, 1000, True),
    ("articles/bespoke-ai-steam-auto.html", "art1", 1440, 1100, False),
    ("articles/ai-voice-recorder-boya-newyes.html", "art2", 1440, 1100, False),
    ("index.html", "home-mobile", 390, 844, False),
    ("articles/bespoke-ai-steam-auto.html", "art1-mobile", 390, 844, False),
    ("articles.html", "archive", 1440, 900, False),
    ("about.html", "about", 1440, 900, False),
]
with sync_playwright() as p:
    b = p.chromium.launch()
    for f, name, w, h, full in pages:
        pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
        pg.goto("file:///workspace/pickearly/docs/" + f)
        pg.wait_for_timeout(600)
        pg.screenshot(path=f"{OUT}/{name}.png", full_page=full)
        print(name, "ok")
        pg.close()
    b.close()
