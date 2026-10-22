#!/bin/bash
# Stop hook for the trio skill: a session may not end while a trio run in its repo is
# still "running". The loop is run by the model, which can drift; this makes it finish
# the round or say why it stops. It nudges once per stop (stop_hook_active), so it can
# never trap a session.
#
# Allowed statuses that let the session stop: needs-user, done, failed, stopped.

input=$(cat)

[ "$(jq -r '.stop_hook_active // false' <<<"$input")" = "true" ] && exit 0

cwd=$(jq -r '.cwd // empty' <<<"$input")
[ -z "$cwd" ] && cwd=$PWD
root=$(git -C "$cwd" rev-parse --show-toplevel 2>/dev/null) || root=$cwd

for run in "$root"/.trio/*/run.json; do
  [ -f "$run" ] || continue
  [ "$(jq -r '.status // empty' "$run" 2>/dev/null)" = "running" ] || continue

  slug=$(jq -r '.slug // "?"' "$run")
  round=$(jq -r '.round // "?"' "$run")
  max=$(jq -r '.max_rounds // "?"' "$run")
  echo "Trio run '$slug' is still running (round $round of $max). Continue the loop as the trio skill says. To stop and ask the user something, first set \"status\": \"needs-user\" in $run; to abandon the run, set \"status\": \"stopped\"." >&2
  exit 2
done

exit 0
