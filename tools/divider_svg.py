#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render the section rules into assets/div-*.svg.

The section labels live inside the rule rather than in a markdown heading, so
they keep the terminal styling and travel with the repository instead of
depending on a font or a service.
"""

import io
import os

W, H = 900, 36
MID = W / 2.0
CH = 7.6          # advance width of the 13px monospace glyph used for labels
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

SECTIONS = {
    "divider":  "&lt;/&gt;",
    "projects": "~$ ls projects",
    "stats":    "~$ cat stats",
    "contact":  "~$ contact",
}


def build(label):
    # a label of n glyphs, letter-spaced, plus breathing room on both sides
    plain = label.replace("&lt;", "<").replace("&gt;", ">")
    half = (len(plain) * (CH + 1.4)) / 2.0 + 16

    return """<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="presentation">
  <defs>
    <linearGradient id="ln" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"   stop-color="#2EA043" stop-opacity="0"/>
      <stop offset="35%"  stop-color="#2EA043" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="#2EA043" stop-opacity="0.6"/>
    </linearGradient>
    <linearGradient id="rn" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"   stop-color="#2EA043" stop-opacity="0.6"/>
      <stop offset="65%"  stop-color="#2EA043" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="#2EA043" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="pulse" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"   stop-color="#3FB950" stop-opacity="0"/>
      <stop offset="50%"  stop-color="#3FB950" stop-opacity="1"/>
      <stop offset="100%" stop-color="#3FB950" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <rect x="40" y="17" width="{LW:.0f}" height="1.4" fill="url(#ln)"/>
  <rect x="{RX:.0f}" y="17" width="{RW:.0f}" height="1.4" fill="url(#rn)"/>

  <!-- a packet running down the wire -->
  <rect x="-180" y="16.2" width="180" height="3" rx="1.5" fill="url(#pulse)" opacity="0.85">
    <animate attributeName="x" from="-180" to="{W}" dur="4.2s" repeatCount="indefinite"/>
  </rect>

  <text x="{MID:.0f}" y="22" text-anchor="middle" font-size="13" letter-spacing="1.4"
        font-family="{MONO}" fill="#3FB950">{LABEL}</text>

  <g fill="#3FB950">
    <rect x="{D1:.0f}" y="16" width="3" height="3"><animate attributeName="opacity" values="0.15;1;0.15" dur="2.1s" begin="0s"   repeatCount="indefinite"/></rect>
    <rect x="{D2:.0f}" y="16" width="3" height="3"><animate attributeName="opacity" values="0.15;1;0.15" dur="2.7s" begin="0.9s" repeatCount="indefinite"/></rect>
  </g>
</svg>
""".format(W=W, H=H, MID=MID, MONO=MONO, LABEL=label,
           LW=(MID - half) - 40,
           RX=(MID + half),
           RW=860 - (MID + half),
           D1=(MID - half) - 14,
           D2=(MID + half) + 11)


def main():
    for name, label in SECTIONS.items():
        path = os.path.join(OUT, ("divider.svg" if name == "divider" else "div-%s.svg" % name))
        with io.open(path, "w", encoding="utf-8", newline=chr(10)) as f:
            f.write(build(label))
        print("wrote %s  (%s)" % (os.path.basename(path), label))


if __name__ == "__main__":
    main()
