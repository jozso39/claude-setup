#!/bin/bash
# Stop hook in a trio agent's frontmatter (runs as SubagentStop): the agent may not finish
# until the last line of its final message matches the pattern, e.g. "VERDICT: (PASS|FAIL)".
# The orchestrator reads that line, so it has to be there and exact. Nudges once per stop.

pattern=$1
input=$(cat)

[ "$(jq -r '.stop_hook_active // false' <<<"$input")" = "true" ] && exit 0

last=$(jq -r '.last_assistant_message // empty' <<<"$input" | sed '/^[[:space:]]*$/d' | tail -1)

if grep -Eq "^[*_\` ]*${pattern}[*_\` ]*\$" <<<"$last"; then
  exit 0
fi

echo "trio: end your final message with one line matching: ${pattern} (nothing after it)." >&2
exit 2
