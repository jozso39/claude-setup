# claude-setup

My Claude Code harness as a plugin marketplace: the skills, agents and guard hooks I work
with every day, so that any machine (or any colleague) gets the same setup in two commands.
Read it before you install it: the hooks run shell commands, and that is the point.

```
/plugin marketplace add jozso39/claude-setup
/plugin install jozef-harness@jozso39
```

Then, optionally, the prose part that no plugin can install:

```bash
curl -fsSL https://raw.githubusercontent.com/jozso39/claude-setup/main/CLAUDE.global.md -o ~/.claude/CLAUDE.md
```

## What is in `jozef-harness`

| Piece | Kind | What it does | Enforced by |
|---|---|---|---|
| `repo-onboarding` | skill, auto | The first fifteen minutes in a repo you do not know: read README and CI, run tests before touching anything, write a 20-line `CLAUDE.md` if missing, branch | prose |
| `fresh-review` | skill, auto | A subagent with an empty context reviews the diff against the task statement; the session fixes, up to two rounds | prose |
| `report-validation` | skill, `/report-validation` | An independent `report-validator` agent reads a data report as its audience would and recomputes its numbers from the data; three rounds max | agent stop hook: must end with `VERDICT:` |
| `trio` | skill, `/trio` | Planner → generator ⇄ evaluator for a feature: spec and testable contract, you approve, the generator builds on `trio/<slug>`, a fresh evaluator runs the app and judges; three rounds max | write-guard hooks (who may write what), stop hooks (`STATUS:`/`VERDICT:` lines), Stop guard on the session |
| `guard.sh` | PreToolUse hook on Bash | Denies force-push, hard reset, blanket discard of changes, dropping stashes, `git clean`, recursive delete outside the tree, nested `--dangerously-skip-permissions` | hook, exit 2 |

Agents: `report-validator`, `trio-planner`, `trio-generator`, `trio-evaluator`. All run on
Opus with a fixed tool list and their own hooks, so the orchestrating session cannot talk
them out of their constraints.

## The idea behind it

- **Prose guides, mechanisms enforce.** A rule that matters is a hook or a test, not a
  sentence. The sentences explain why.
- **A fresh context judges.** The session that wrote something does not review it; a new
  agent with the inputs and nothing else does. Same for reports, same for features.
- **A command that has not been run is a claim.** Tests before trust, in every skill.
- **Small blast radius.** Agents get the smallest tool list that does the job, and the
  few commands that cost the most to get wrong are simply refused.

## What I use next to it

- [johnnyvizz/claude-kit](https://github.com/johnnyvizz/claude-kit): `savvy-flow` (orchestrator with tiered worker agents) and the `savvy-progress` panel. Not mine; installed as a second marketplace.
- Project-level `.claude/trio.md` profiles (how to run the app in isolation, what must never be touched) live in each repo, not here.

## Trust

Everything the plugin runs is in this repo: four shell scripts under 60 lines each and one
Python renderer. No network calls, no secrets, nothing written outside the repo you work in
except the `.trio/` run folder. MIT.
