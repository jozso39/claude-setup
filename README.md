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
| `guard.sh` | PreToolUse hook on Bash | Denies force-push, hard reset, blanket discard of changes, dropping stashes, `git clean`, recursive delete outside the tree, nested `--dangerously-skip-permissions` | hook, exit 2 |

Agent: `report-validator`. It runs on Opus with a fixed tool list and its own stop hook (it
must end with a `VERDICT:` line), so the orchestrating session cannot talk it out of its
constraints.

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

## Trust

Everything the plugin runs is in this repo: two shell scripts under 60 lines each and one
Python renderer. No network calls, no secrets, nothing written outside the repo you work in.
MIT.
