# claude-setup

My Claude Code harness as a plugin marketplace: the skills, agents and guard hooks I work
with every day, so that any machine (or any colleague) gets the same setup in two commands.
Read it before you install it: the hooks run shell commands, and that is the point.

```
/plugin marketplace add jozso39/claude-setup
/plugin install my-setup@jozso39
```

Then, optionally, the prose part that no plugin can install:

```bash
curl -fsSL https://raw.githubusercontent.com/jozso39/claude-setup/main/CLAUDE.global.md -o ~/.claude/CLAUDE.md
```

## Deny rules: not a plugin thing

A plugin's `settings.json` is read for `agent` and `subagentStatusLine` only; `permissions`
is dropped at load. So the deny and ask rules ship as
[`settings.example.json`](settings.example.json): copy its `permissions` block into
`~/.claude/settings.json` (or a repo's `.claude/settings.json`). On a company machine they
belong in `managed-settings.json`, which nothing in user settings can override. The guard
hook in the plugin refuses the same Bash commands one layer later, so you get the rules
even where the settings file was not copied.

## First prompt after installing

Plan mode first (`Shift+Tab` until it says plan), then:

```
Onboard me in this repo. Read how it is built and tested, run the tests and the app
before changing anything and tell me the baseline, write a short CLAUDE.md if there is
none, and render the repo map so I can see the structure. Then stop; I will give you the
task after I have read the map.
```

That one message triggers `repo-onboarding`. When the task is done, the second prompt is
`review it`, which triggers `fresh-review` before you commit. `/report-validation <file>`
is explicit, for data reports only.

## What is in `my-setup`

| Piece | Kind | What it does | Enforced by |
|---|---|---|---|
| `repo-onboarding` | skill, auto | The first fifteen minutes in a repo you do not know: read README and CI, run tests before touching anything, write a 20-line `CLAUDE.md` if missing, render a one-page HTML map of the repo (request path, layers, commands), branch | prose + `repo-map.py` |
| `fresh-review` | skill, auto | A subagent with an empty context reviews the diff against the task statement; the session fixes, up to two rounds | prose |
| `report-validation` | skill, `/report-validation` | An independent `report-validator` agent reads a data report as its audience would and recomputes its numbers from the data; three rounds max | agent stop hook: must end with `VERDICT:` |
| `rules/coding.md` | SessionStart hook | Adds five coding rules to every session, as a CLAUDE.md would: reuse before writing a helper, extract on the second copy, no single-implementation abstractions, one job per function, follow the module's patterns. Edits no file; disable the plugin and they are gone | hook |
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

Everything the plugin runs is in this repo: three shell scripts under 60 lines each and two
Python renderers. No network calls, no secrets, nothing written outside the repo you work in.
MIT.
