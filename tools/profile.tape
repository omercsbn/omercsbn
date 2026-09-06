# Recorded by .github/workflows/terminal.yml into assets/terminal.gif.
# Preview locally with:  vhs tools/profile.tape
# (needs vhs + ttyd + ffmpeg, and `python tools/term/render.py` run first)

Output assets/terminal.gif

Set Shell bash
Set FontFamily "JetBrains Mono"
Set FontSize 14
Set Width 860
Set Height 620
Set Padding 20
Set BorderRadius 8
Set WindowBar Colorful
Set Framerate 20
Set TypingSpeed 45ms
Set Theme { "background": "#0D1117", "foreground": "#C9D1D9", "cursor": "#3FB950", "selection": "#264F78", "black": "#0D1117", "red": "#FF7B72", "green": "#3FB950", "yellow": "#D29922", "blue": "#58A6FF", "magenta": "#BC8CFF", "cyan": "#39C5CF", "white": "#B1BAC4", "brightBlack": "#6E7681", "brightRed": "#FFA198", "brightGreen": "#56D364", "brightYellow": "#E3B341", "brightBlue": "#79C0FF", "brightMagenta": "#D2A8FF", "brightCyan": "#56D4DD", "brightWhite": "#F0F6FC" }

Hide
Type "source tools/term/setup.sh"
Enter
Type "clear"
Enter
Show

Sleep 1200ms

Type "neofetch"
Sleep 500ms
Enter
Sleep 3500ms

Type "cat ~/.stack"
Sleep 500ms
Enter
Sleep 3200ms

Type "cat ~/.now"
Sleep 500ms
Enter
Sleep 3500ms
