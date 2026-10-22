#!/bin/bash
# PreToolUse guard for Bash. Reads the tool call on stdin, exits 2 (deny, reason on stderr)
# for commands an agent should never run on its own. Everything else passes (exit 0).
# Deliberately short: a guard that tries to be clever gets bypassed or ignored.
input=$(cat)
cmd=$(jq -r '.tool_input.command // empty' <<<"$input")
[ -z "$cmd" ] && exit 0

deny() { echo "guard: $1 — do it by hand, or ask the user to run it." >&2; exit 2; }

case "$cmd" in
  *"git push"*"--force"*|*"git push"*" -f "*|*"git push -f"*) deny "force-push rewrites shared history" ;;
  *"git reset --hard"*)          deny "hard reset throws away uncommitted work" ;;
  *"git checkout -- ."*|*"git restore ."*|*"git restore --staged ."*) deny "discarding every local change at once" ;;
  *"git stash drop"*|*"git stash clear"*) deny "dropping stashes loses work" ;;
  *"git clean -"*[fF]*[dDxX]*|*"git clean -"*[dDxX]*[fF]*) deny "git clean deletes untracked files" ;;
  *"rm -rf /"*|*"rm -rf ~"*|*"rm -rf \$HOME"*|*"rm -rf .."*) deny "recursive delete outside the working tree" ;;
  *"--dangerously-skip-permissions"*) deny "nested agent without permissions" ;;
esac
exit 0
