#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render a terminal-styled stats card for the profile README.

Emits assets/stats-<theme>.svg for the light and dark themes. Everything is
inlined -- no webfonts, no external refs -- because GitHub serves README images
through camo, which blocks anything the SVG tries to fetch.

Run with GITHUB_TOKEN set to avoid the 60 req/hour unauthenticated limit.
"""

import io
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime

USER = os.environ.get("STATS_USER", "omercsbn")
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

# Byte-weighted language stats let markup and stylesheets dominate, which buries
# the systems work. GitHub's own top-langs card has the same flaw; `hide=` is the
# usual answer. Same idea, kept in one place.
IGNORED_LANGS = {
    "HTML", "CSS", "SCSS", "Sass", "Less", "Stylus",
    "EJS", "Handlebars", "Pug", "Blade", "Jupyter Notebook",
}

THEMES = {
    "dark": dict(border="#30363D", accent="#3FB950", key="#8B949E",
                 value="#C9D1D9", bar="#3FB950", track="#21262D", dim="#6E7681"),
    "light": dict(border="#D0D7DE", accent="#1A7F37", key="#57606A",
                  value="#1F2328", bar="#1A7F37", track="#EAEEF2", dim="#6E7681"),
}


def api(path):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "stats-svg"},
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def collect():
    user = api("/users/%s" % USER)
    repos = []
    page = 1
    while True:
        chunk = api("/users/%s/repos?per_page=100&page=%d" % (USER, page))
        repos.extend(chunk)
        if len(chunk) < 100:
            break
        page += 1

    own = [r for r in repos if not r["fork"]]
    stars = sum(r["stargazers_count"] for r in own)

    # Weight languages by bytes, the way GitHub's own language bar does it.
    langs = {}
    for r in own:
        try:
            for name, size in api("/repos/%s/languages" % r["full_name"]).items():
                if name in IGNORED_LANGS:
                    continue
                langs[name] = langs.get(name, 0) + size
        except urllib.error.HTTPError as e:
            print("  ! skipped %s (%s)" % (r["full_name"], e.code), file=sys.stderr)

    total = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:6]

    created = datetime.strptime(user["created_at"], "%Y-%m-%dT%H:%M:%SZ")
    return dict(
        stats=[
            ("public repos", str(user["public_repos"])),
            ("sources", "%d (%d forked)" % (len(own), len(repos) - len(own))),
            ("stars earned", str(stars)),
            ("followers", str(user["followers"])),
            ("member since", created.strftime("%b %Y")),
        ],
        langs=[(n, 100.0 * v / total) for n, v in top],
    )


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render(data, theme):
    c = THEMES[theme]
    CH = 8.4          # advance width of the 14px monospace glyph we lay out on
    LH = 21           # line height
    PAD = 22
    COL2 = 440        # x offset of the right column
    W, H = 860, 250

    def text(x, y, s, fill, weight="400", size=14):
        return ('<text x="%.1f" y="%d" fill="%s" font-size="%d" font-weight="%s" '
                'xml:space="preserve">%s</text>' % (x, y, fill, size, weight, esc(s)))

    p = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
         'viewBox="0 0 %d %d" font-family="ui-monospace,SFMono-Regular,'
         'Menlo,Consolas,&quot;Liberation Mono&quot;,monospace">' % (W, H, W, H)]
    p.append('<rect x="0.5" y="0.5" width="%d" height="%d" rx="6" fill="none" '
             'stroke="%s"/>' % (W - 1, H - 1, c["border"]))

    # ---- left column: counters -------------------------------------------
    y = PAD + 18
    p.append(text(PAD, y, "$ ", c["dim"]))
    p.append(text(PAD + 2 * CH, y, "git stats --author=%s" % USER, c["accent"], "600"))
    y += LH + 8
    for label, value in data["stats"]:
        dots = "." * max(1, 20 - len(label))
        p.append(text(PAD + CH, y, "%s %s" % (label, dots), c["key"]))
        p.append(text(PAD + CH * 23, y, value, c["value"], "600"))
        y += LH

    # ---- right column: language bars -------------------------------------
    y = PAD + 18
    p.append(text(COL2, y, "$ ", c["dim"]))
    p.append(text(COL2 + 2 * CH, y, "tokei ~/projects", c["accent"], "600"))
    y += LH + 8
    BAR_W, BAR_H = 150, 8
    for name, pct in data["langs"]:
        p.append(text(COL2 + CH, y, name[:12], c["key"]))
        bx, by = COL2 + CH * 14, y - 9
        p.append('<rect x="%d" y="%d" width="%d" height="%d" rx="4" fill="%s"/>'
                 % (bx, by, BAR_W, BAR_H, c["track"]))
        p.append('<rect x="%d" y="%d" width="%.1f" height="%d" rx="4" fill="%s"/>'
                 % (bx, by, max(3.0, BAR_W * pct / 100.0), BAR_H, c["bar"]))
        p.append(text(bx + BAR_W + 12, y, "%5.1f%%" % pct, c["value"], "600"))
        y += LH

    p.append(text(PAD, H - 14, "%s/%s - regenerated by .github/workflows/stats.yml"
                  % (USER, USER), c["dim"], size=11))
    p.append("</svg>")
    return "\n".join(p)


def sync_readme(data):
    """Keep the `Packages ....` line in the recorded neofetch block honest.

    Editing the source here rather than the README: the block now lives in the
    terminal recording, and touching this file is what tells the terminal
    workflow the GIF needs re-rendering.
    """
    path = os.path.join(os.path.dirname(OUT_DIR), "tools", "term", "neofetch.txt")
    count = dict(data["stats"])["public repos"]
    lines = io.open(path, encoding="utf-8").read().splitlines()
    changed = False
    for i, line in enumerate(lines):
        if "Packages ...." in line:
            head = line.split("Packages ....")[0]
            new = "%sPackages .... %s public repos" % (head, count)
            if new != line:
                lines[i], changed = new, True
    if changed:
        with io.open(path, "w", encoding="utf-8", newline=chr(10)) as f:
            f.write(chr(10).join(lines) + chr(10))
        print("synced neofetch repo count -> %s" % count)


def main():
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)
    print("collecting %s ..." % USER)
    data = collect()
    for theme in THEMES:
        path = os.path.join(OUT_DIR, "stats-%s.svg" % theme)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(render(data, theme))
        print("wrote %s" % path)
    sync_readme(data)
    for label, value in data["stats"]:
        print("  %-14s %s" % (label, value))
    for name, pct in data["langs"]:
        print("  %-14s %5.1f%%" % (name, pct))


if __name__ == "__main__":
    main()
