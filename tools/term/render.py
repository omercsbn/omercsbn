#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Colourise the plain-text terminal blocks into ANSI for the VHS recording.

The .txt sources stay free of escape codes so their column alignment can be
eyeballed in any editor; the colours are applied by rule here. Output lands in
tools/term/out/ and is consumed by tools/term/setup.sh inside the VHS
container, which has no Python.
"""

import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

ESC = chr(27)
def fg(hexcolor):
    r, g, b = (int(hexcolor[i:i + 2], 16) for i in (0, 2, 4))
    return "%s[38;2;%d;%d;%dm" % (ESC, r, g, b)

RESET = ESC + "[0m"
BOLD = ESC + "[1m"
ACCENT = fg("3FB950")   # prompt / logo / headings
DIM = fg("8B949E")      # labels
VALUE = fg("C9D1D9")    # values
TRACK = fg("30363D")    # unfilled part of a bar

LOGO_COLS = 33          # the neofetch art occupies the first 33 columns


def bars(text):
    """Light up the filled cells of an ASCII bar, dim the empty ones."""
    out, mode = [], None
    for ch in text:
        want = ACCENT if ch == "█" else TRACK if ch == "░" else None
        if want != mode:
            out.append(want or RESET)
            mode = want
        out.append(ch)
    return "".join(out) + (RESET if mode else "")


def neofetch(lines):
    out = []
    for line in lines:
        art, info = line[:LOGO_COLS], line[LOGO_COLS:]
        row = ACCENT + art + RESET if art.strip() else art
        if info.strip():
            dotted = re.match(r"^(\s*[A-Za-z]+ \.+) (.*)$", info)
            if dotted:
                label, value = dotted.group(1), dotted.group(2)
                row += DIM + label + RESET + " " + VALUE + bars(value) + RESET
            elif set(info.strip()) <= {"─"}:
                row += DIM + info + RESET
            else:
                row += BOLD + ACCENT + info + RESET
        out.append(row)
    return out


def stack(lines):
    out = []
    for line in lines:
        if not line.strip():
            out.append(line)
            continue
        indent = len(line) - len(line.lstrip())
        name, rest = line[indent:indent + 12], line[indent + 12:]
        tools, _, bar = rest.rpartition("  ")
        out.append(" " * indent + ACCENT + name + RESET + DIM + tools + RESET
                   + "  " + bars(bar))
    return out


def now(lines):
    out = []
    for line in lines:
        if "→" in line:
            head, _, tail = line.partition("→")
            out.append(head + ACCENT + "→" + RESET + VALUE + tail + RESET)
        else:
            out.append(line)
    return out


def main():
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    for name, fn in [("neofetch", neofetch), ("stack", stack), ("now", now)]:
        src = os.path.join(HERE, name + ".txt")
        lines = io.open(src, encoding="utf-8").read().rstrip(chr(10)).split(chr(10))
        dst = os.path.join(OUT, name + ".ansi")
        with io.open(dst, "w", encoding="utf-8", newline=chr(10)) as f:
            f.write(chr(10).join(fn(lines)) + chr(10))
        print("wrote %s" % dst)


if __name__ == "__main__":
    main()
