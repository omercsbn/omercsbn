#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render the matrix-rain banner into assets/banner.svg.

Generated rather than hand-written: the rain is ~36 independently falling
columns, and writing those by hand would be unreadable. The seed is fixed so
re-running produces byte-identical output and does not churn the repository.

SMIL animation only -- no CSS, no script, no external refs. README images are
proxied or loaded as <img>, so anything the SVG tries to fetch is blocked, and
scripts never run.
"""

import io
import os
import random

W, H = 900, 260
COL_W = 25
FONT = 16
LINE = 18
SEED = 7

# Only glyphs every monospace font actually has. Half-width katakana would be
# more faithful to the film but renders as tofu wherever the font lacks it.
XML_ESC = {"&": "&amp;", "<": "&lt;", ">": "&gt;"}


def xesc(ch):
    return XML_ESC.get(ch, ch)


CHARS = "01{}[]<>/" + chr(92) + "#$%&*+=;:~^!?|-_01"

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "assets", "banner.svg")


def rain():
    rnd = random.Random(SEED)
    parts = []
    for i in range(W // COL_W + 1):
        x = i * COL_W + COL_W / 2.0
        n = rnd.randint(12, 20)
        col_h = n * LINE
        dur = rnd.uniform(6.5, 15.0)
        begin = -rnd.uniform(0.0, dur)

        spans = []
        for k in range(n):
            ch = rnd.choice(CHARS)
            head = (k == n - 1)
            # brightness ramps toward the leading glyph
            opacity = 0.10 + 0.62 * (k / max(1, n - 1))
            fill = "#B7FFCE" if head else "#2EA043"
            if head:
                opacity = 1.0
            dy = 0 if k == 0 else LINE
            spans.append('<tspan x="%.1f" dy="%d" fill="%s" opacity="%.2f">%s</tspan>'
                         % (x, dy, fill, opacity, xesc(ch)))

        parts.append(
            '<g><text y="0" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" '
            'font-size="%d" text-anchor="middle">%s</text>'
            '<animateTransform attributeName="transform" type="translate" '
            'from="0 %.0f" to="0 %d" dur="%.2fs" begin="%.2fs" repeatCount="indefinite"/></g>'
            % (FONT, "".join(spans), -col_h, H + col_h, dur, begin))
    return "\n".join(parts)

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"


NAME = "Ömercan Sabun"
CYCLE = 10.0        # seconds per loop
SCRAMBLE = 1.5      # how long the name spends resolving


def wordmark():
    """Layer the wordmark so it resolves out of noise, Matrix-style.

    SMIL cannot animate text content, so every step of the decode is its own
    <text> and the steps hand visibility to one another. Characters settle in a
    seeded random order, which keeps the reveal reproducible without looking
    mechanical.
    """
    rnd = random.Random(SEED + 1)
    slots = [i for i, c in enumerate(NAME) if c != " "]
    rnd.shuffle(slots)

    steps = 6
    per = len(slots) / float(steps)
    frames = []
    for k in range(steps):
        settled = set(slots[:int(round(per * k))])
        frames.append("".join(c if (c == " " or i in settled) else rnd.choice(CHARS)
                              for i, c in enumerate(NAME)))
    frames.append(NAME)

    step = SCRAMBLE / steps
    out = []
    for k, txt in enumerate(frames):
        if k < steps:
            a, b = (k * step) / CYCLE, ((k + 1) * step) / CYCLE
            keys, vals = "0;%.4f;%.4f;1" % (a, b), "0;1;0;0"
        else:
            keys, vals = "0;%.4f;1" % (SCRAMBLE / CYCLE), "0;1;1"
        out.append(
            '    <text x="450" y="126" text-anchor="middle" font-family="%s" '
            'font-size="42" font-weight="700" fill="#7CFFB0" letter-spacing="3" opacity="0">%s'
            '<animate attributeName="opacity" values="%s" keyTimes="%s" calcMode="discrete" '
            'dur="%.1fs" repeatCount="indefinite"/></text>'
            % (MONO, "".join(xesc(c) for c in txt), vals, keys, CYCLE))
    return chr(10).join(out)


def build():
    return """<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Omercan Sabun - Software Architect">
  <title>Ömercan Sabun — Software Architect</title>
  <defs>
    <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"   stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset="18%"  stop-color="#FFFFFF" stop-opacity="1"/>
      <stop offset="82%"  stop-color="#FFFFFF" stop-opacity="1"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
    <mask id="rainMask"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>

    <radialGradient id="vignette" cx="0.5" cy="0.5" r="0.62">
      <stop offset="0%"   stop-color="#010409" stop-opacity="0.94"/>
      <stop offset="55%"  stop-color="#010409" stop-opacity="0.80"/>
      <stop offset="100%" stop-color="#010409" stop-opacity="0"/>
    </radialGradient>

    <filter id="glow" x="-40%" y="-60%" width="180%" height="220%">
      <feGaussianBlur stdDeviation="4" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <rect width="{W}" height="{H}" rx="10" fill="#010409"/>

  <g mask="url(#rainMask)">
{RAIN}
  </g>

  <!-- darken the middle so the wordmark stays legible over the rain -->
  <ellipse cx="{CX}" cy="{CY}" rx="330" ry="104" fill="url(#vignette)"/>

  <!-- scanlines -->
  <g fill="#7CFFB0" opacity="0.05">
{SCANS}
  </g>

  <g filter="url(#glow)">
{WORDMARK}
  </g>
  <text x="{CX}" y="{SY}" text-anchor="middle" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
        font-size="14" fill="#8FE9AE" letter-spacing="6.5">SOFTWARE ARCHITECT</text>
  <text x="{CX}" y="{TY}" text-anchor="middle" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
        font-size="12" fill="#4E9E6B" letter-spacing="2">enterprise architecture · ai agents · distributed systems</text>

  <rect x="0.5" y="0.5" width="{W1}" height="{H1}" rx="10" fill="none" stroke="#2EA043" stroke-opacity="0.45"/>
</svg>
""".replace("{RAIN}", rain()) \
   .replace("{WORDMARK}", wordmark()) \
   .replace("{SCANS}", "\n".join('    <rect x="0" y="%d" width="%d" height="1"/>' % (y, W)
                                 for y in range(0, H, 4))) \
   .replace("{CX}", str(W // 2)).replace("{CY}", str(H // 2)) \
   .replace("{NY}", "126").replace("{SY}", "158").replace("{TY}", "186") \
   .replace("{W1}", str(W - 1)).replace("{H1}", str(H - 1)) \
   .replace("{W}", str(W)).replace("{H}", str(H))


def main():
    svg = build()
    with io.open(OUT, "w", encoding="utf-8", newline=chr(10)) as f:
        f.write(svg)
    print("wrote %s (%d bytes)" % (OUT, len(svg)))


if __name__ == "__main__":
    main()
