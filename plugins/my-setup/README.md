# my-setup

See the [marketplace README](../../README.md) for what each piece does and why.

Layout:

```
skills/repo-onboarding/   first fifteen minutes in an unknown repo (auto); scripts/repo-map.py renders the HTML map
skills/fresh-review/      diff reviewed by a fresh subagent (auto)
skills/report-validation/ data report validated by the report-validator agent (/report-validation)
agents/                   report-validator
hooks/hooks.json          PreToolUse Bash guard, SessionStart coding rules
rules/coding.md           the coding rules the SessionStart hook adds to every session
scripts/guard.sh          the Bash guard
scripts/session-rules.sh  prints rules/coding.md as session context
scripts/final-line.sh     stop hook: an agent must end with its STATUS/VERDICT line
```

Requirements: `jq` for the hooks, `git`, Python 3 for the report renderer (headless Chrome
optional, for JavaScript-built reports).
