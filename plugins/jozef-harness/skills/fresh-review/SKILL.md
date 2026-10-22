---
name: fresh-review
description: >-
  Have the change this session made reviewed by a subagent with a fresh context, given the
  diff range, the task statement and nothing else; then act on its findings here. Use after
  implementing a feature or fix and before committing or opening a PR/MR, when the user says
  "review it", "fresh review", "nech to zreviewovat", or asks whether the change is good to
  go. Not for reviewing someone else's branch from scratch.
argument-hint: "[base ref, default merge-base with main] [--task <one sentence or ticket link>]"
---

# Fresh review: the author does not grade their own work

The session that wrote a change reads past its own gaps. A reviewer that starts empty
and is told only where the diff is and what it was supposed to do finds what the author
cannot. Your job is to give it exactly that, then to fix what it finds, up to two rounds.

```
commit or stage → spawn reviewer(diff range, task) → findings with file:line
      → fix here → run tests → spawn again (round 2) → report
```

## 1. Fix the inputs

- **Range:** `<base>...HEAD` where base is the argument, else `git merge-base HEAD main`
  (or `master`, `develop`, whatever the repo uses). Uncommitted work: stage it first so
  the reviewer sees `git diff --cached` as part of the picture; say so in the message.
- **Task:** one sentence in the user's words, or the ticket link. Do not add what you
  think the code does; the reviewer must infer that from the diff.
- **Checks:** the exact commands that make the repo green (from `CLAUDE.md` or CI).

## 2. Spawn the reviewer with facts only

One `Agent` call, `subagent_type: general-purpose`, a stronger model than the session's if
available, `run_in_background: true`. The message:

```
Review the change in <repo path>, range <base>...HEAD (plus staged changes: yes/no).
Task it was meant to do: <one sentence or link>.
Checks that must pass: <commands>.
Read the diff and the surrounding code; run the checks. Report, most severe first:
- correctness bugs (a concrete input or state → wrong result), with file:line;
- changes outside the task's scope, missing tests for new behaviour, suppressed errors,
  tests that assert a mock instead of behaviour, copied code where a call would do;
- what you would ask the author before merging.
Do not edit anything. End with one line: VERDICT: APPROVE or VERDICT: CHANGES — <n> findings.
```

Wait for the notification; do not poll.

## 3. Act on the findings, here

- A real defect: fix it, run the checks, note it.
- A scope or design question: ask the user once, with the reviewer's wording and your
  recommendation; do not quietly widen or narrow the change.
- A finding you are sure is wrong: say why in the next round's message with evidence
  (you re-ran it, not you remember writing it).

Round 2 only if something was fixed: same reviewer by `SendMessage` with "Re-review the same
range; since round 1: <finding → what changed>". Stop at APPROVE, at two rounds, or when
every open item is the user's decision.

## 4. Report

Verdict and rounds, each finding in one line with before → after, open questions, and
the exact commands you ran with their result. Then commit with a message that says what
and why; the PR/MR description lists how it was verified and what is left.
