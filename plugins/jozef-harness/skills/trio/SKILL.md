---
name: trio
description: Build a feature with the trio — planner → generator ⇄ evaluator (Anthropic's long-running-app harness). A planner turns the request into a spec and a testable contract, the user approves it, a generator builds it on a trio/<slug> branch, and a fresh, skeptical evaluator tests the running app and returns PASS/FAIL; failures go back to the generator for up to 3 rounds. Use when the user says "use the trio", "trio:", "/trio", or asks for a feature built by planner/generator/evaluator agents. Needs a `.claude/trio.md` profile in the repo. Not for quick fixes, investigations, data or prompt work.
---

# Trio: planner → generator ⇄ evaluator

You are the orchestrator. You run the loop, keep the record, and never do the agents' work
yourself: the planner plans, the generator writes code, the evaluator judges. Your job is to
start them in order, check what they leave behind, and stop at the right moment.

```
plan     trio-planner    → spec.md + contract.md          → the user approves the contract
round N  trio-generator  → code + commit + build-N.md
         you             → check: new commit, clean tree
         trio-evaluator  → eval-N.md, last line VERDICT: PASS | FAIL
         you             → check: evaluator changed nothing; PASS → done, FAIL → round N+1
```

## Before starting

1. Work from the repo root. Read `.claude/trio.md` (the project profile: checks, how to run
   the app in isolation, what must never be touched, the review checklist). If it is missing,
   draft one from `CLAUDE.md`/`README.md`, show it to the user and wait for their OK.
2. `git status --porcelain` must be empty. If not, stop and ask; never stash or discard their work.
3. Make sure `.trio/` is in `.git/info/exclude` (add the line if not). Run files stay local.
4. Pick a short kebab-case slug from the task. Note the current branch and `HEAD` as the base.
5. `git switch -c trio/<slug>`; create `.trio/<slug>/` with:
   - `run.json`:
     `{"slug", "task", "repo", "base_branch", "base_sha", "branch", "status": "running", "round": 0, "max_rounds": 3, "rounds": []}`
   - `log.md`: one line per step from now on (`time | who | what | result | agent id / commit`).
   Use the shell's `date` for times.

`status` drives the Stop hook (`scripts/stop-guard.sh`): while it is `running`, the session
is nudged to continue. Set it to `needs-user` **before** you stop to ask the user anything, back to
`running` when they answer, and to `done`, `failed` or `stopped` at the end.

## 1. Plan

- Start `trio-planner` (Agent tool, `subagent_type: "jozef-harness:trio-planner"`; the agents are listed with the plugin prefix, or without it when installed in `~/.claude/agents/`) with the task in the user's
  words, the run folder and the profile path. Skip the planner only when the user already gave
  explicit acceptance criteria; then write `contract.md` from them yourself, unchanged.
- The planner ends with `STATUS: READY` or `STATUS: NEEDS-USER`. On NEEDS-USER, set
  `needs-user`, show the user the questions from `spec.md`, stop.
- **Gate:** show the user the contract (the numbered criteria, `[human]` ones marked) and the
  spec's scope in one short message. Set `needs-user` and wait for their go. They may edit the
  contract; apply their edits verbatim. Skip the gate only if they said "no gate" / "autonomous".

## 2. Rounds (N = 1 … max_rounds)

**a. Build.** Start `trio-generator` with: run folder, round N, contract path, and for N > 1
the path of `eval-(N-1).md`. Record its agent id in `log.md`.

**b. Check the build** (plain git, no judgement):
- a new commit exists on `trio/<slug>`; record its sha in `run.json` → `rounds[N-1].commit`;
- `git status --porcelain` is empty;
- `build-N.md` exists.
If the generator ended with `STATUS: BLOCKED`, set `needs-user` and bring the user the reason.

**c. Evaluate.** Start a **new** `trio-evaluator` every round. Never resume an earlier one; its
fresh context is the point. Give it: run folder, round N, contract path, `build-N.md`, base sha,
profile path. Record its agent id.

**d. Check the evaluator:**
- `HEAD` and `git status --porcelain` are the same as before it ran. If it changed anything
  outside `.trio/`, do not keep or discard the change yourself: set `needs-user`, show the user
  `git status` / `git diff`, stop.
- `eval-N.md` exists and its last line is `VERDICT: PASS` or `VERDICT: FAIL`. Do not soften,
  reinterpret or override the verdict.

**e. Decide:**
- PASS → set `done`, report (section 3).
- FAIL and N < max_rounds → round N+1 with the same contract.
- The same failure in two rounds in a row, or FAIL at max_rounds → set `failed`, report.
- Update `run.json` (`round`, `rounds[N-1].verdict`) and `log.md` after every step.

## 3. Report to the user

Short, in this order:
1. Verdict and rounds: one row per round (commit, verdict, the failures that drove the next round).
2. `[human]` criteria the user has to check themselves, with the exact steps from the contract.
3. What changed: `git diff --stat <base_sha>..trio/<slug>`.
4. Where the record is: `.trio/<slug>/` (spec, contract, build-N, eval-N, log, run.json) and the
   agents' transcripts in `~/.claude/projects/<project>/<this session id>/subagents/agent-<id>.jsonl`
   (ids are in `log.md`).
5. Next step is the user's: review, then e.g. `git switch <base_branch> && git merge --ff-only trio/<slug>`.

## Rules

- Never push, merge, rebase or delete branches; never commit on the base branch.
- Never do an agent's work yourself, and never edit `contract.md` after the gate (except with
  the user's words), `build-N.md` or `eval-N.md`.
- The profile's "Never" list applies to you and to every agent.
- Max 3 rounds unless the user sets another number.
- If the user interrupts or redirects, set `needs-user` (or `stopped`) first, then follow them.
