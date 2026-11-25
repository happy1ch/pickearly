import os
from playwright.sync_api import sync_playwright

OUT = "/workspace/worktmp/shots"
os.makedirs(OUT, exist_ok=True)
targets = [
    ("articles/bespoke-ai-steam-auto.html", "a1-links", "#sec-6", 1440, 1100),
    ("articles/bespoke-ai-steam-auto.html", "a1-table", "#sec-5", 1440, 1100),
    ("articles/ai-voice-recorder-boya-newyes.html", "a2-cta", "#sec-4", 1440, 1100),
    ("articles/ai-voice-recorder-boya-newyes.html", "a2-check", "#sec-6", 1440, 1100),
    ("index.html", "home-mobile", None, 390, 844),
    ("articles/bespoke-ai-steam-auto.html", "a1-mobile", None, 390, 844),
    ("articles.html", "archive", None, 1440, 900),
    ("about.html", "about", None, 1440, 900),
]
with sync_playwright() as p:
    b = p.chromium.launch()
    for f, name, anchor, w, h in targets:
        pg = b.new_page(viewport={"width": w, "height": h})
        pg.goto("file:///workspace/pickearly/docs/" + f)
        if anchor:
            pg.eval_on_selector(anchor, "e => e.scrollIntoView()")
            pg.wait_for_timeout(300)
        pg.wait_for_timeout(500)
        pg.screenshot(path=f"{OUT}/{name}.png")
        print(name, "ok")
        pg.close()
    b.close()
