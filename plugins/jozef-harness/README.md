# jozef-harness

See the [marketplace README](../../README.md) for what each piece does and why.

Layout:

```
skills/repo-onboarding/   first fifteen minutes in an unknown repo (auto)
skills/fresh-review/      diff reviewed by a fresh subagent (auto)
skills/report-validation/ data report validated by the report-validator agent (/report-validation)
skills/trio/              planner → generator ⇄ evaluator loop (/trio); scripts: write-guard, stop-guard
agents/                   report-validator, trio-planner, trio-generator, trio-evaluator
hooks/hooks.json          PreToolUse Bash guard, Stop guard for running trio loops
scripts/guard.sh          the Bash guard
scripts/final-line.sh     stop hook: an agent must end with its STATUS/VERDICT line
```

Requirements: `jq` for the hooks, `git`, Python 3 for the report renderer (headless Chrome
optional, for JavaScript-built reports).
