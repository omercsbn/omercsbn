# Sourced by tools/profile.tape while VHS is hiding the frame. Pure bash: the
# VHS container has no Python, so the .ansi files are rendered beforehand by
# the workflow.

cp tools/term/out/neofetch.ansi "$HOME/.neofetch"
cp tools/term/out/stack.ansi    "$HOME/.stack"
cp tools/term/out/now.ansi      "$HOME/.now"

neofetch() { cat "$HOME/.neofetch"; }

export PS1='\[\033[1;38;2;63;185;80m\]omercsbn@github\[\033[0m\]:\[\033[38;2;88;166;255m\]~\[\033[0m\]$ '
