#!/bin/bash
# Stop hook (SubagentStop when it runs inside an agent): the agent may not finish until
# the last non-empty line of its final message matches the pattern, e.g.
# "VERDICT: (APPROVED|NOT APPROVED|NO MR)". Nudges once per stop (stop_hook_active).

pattern=$1
input=$(cat)

[ "$(jq -r '.stop_hook_active // false' <<<"$input")" = "true" ] && exit 0

last=$(jq -r '.last_assistant_message // empty' <<<"$input" | sed '/^[[:space:]]*$/d' | tail -1)

if grep -Eq "^[*_\` ]*${pattern}[*_\` ]*\$" <<<"$last"; then
  exit 0
fi

echo "mr-reviewer: end your final message with one line matching: ${pattern} (nothing after it)." >&2
exit 2
