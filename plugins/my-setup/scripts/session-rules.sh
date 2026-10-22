#!/usr/bin/env bash
# SessionStart hook: adds the plugin's coding rules to the session context, the same way a
# CLAUDE.md would, without editing any file on the machine. Disable the plugin and they go.
set -euo pipefail
rules="${CLAUDE_PLUGIN_ROOT}/rules/coding.md"
[ -f "$rules" ] || exit 0
jq -n --rawfile ctx "$rules" \
  '{hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: $ctx}}'
