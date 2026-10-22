---
name: repo-onboarding
description: >-
  The first fifteen minutes in a repository you do not know, before any change: read how it
  is built and tested, run the tests and the app, write a short CLAUDE.md if there is none,
  then branch. Use when the user opens an unfamiliar repo, says "onboard", "get to know
  this repo", "zorientuj se", or asks to add a feature or deploy a project you have not
  worked in before. Not for repos that already have a CLAUDE.md you have read this session.
argument-hint: "[task the user wants done afterwards]"
---

# Repo onboarding: map the perimeter, prove the baseline, then change things

A command that has not been run is a claim. Before you trust the repo, the agent, or
yourself, establish what "green" means here and make it green once with nothing changed.
Say out loud what you are doing and why at every step; the user may be watching.

## 1. Read, in this order (no edits)

1. `README*`, then the CI definition (`.gitlab-ci.yml`, `.github/workflows/*`, `Jenkinsfile`):
   CI tells you what the team considers "passing", README tells you what they wish were true.
2. The manifest: `package.json`, `composer.json`, `pyproject.toml`, `go.mod`, `Makefile`.
   Note the exact commands for install, test, lint, type-check, run.
3. `Dockerfile`, `docker-compose*.yml`, `.env.example`: how it runs and what it needs.
4. Entry points and the request path: where a request enters, which layers it crosses,
   where the domain logic lives, where I/O (database, HTTP clients, queues) is wrapped.
5. Existing conventions: `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING*`, lint config, test layout.

Answer these in two sentences each before going on: How do I run it? How do I test it?
Where would a new feature of the kind the user wants go? What must I not touch?

## 2. Prove the baseline (run, do not read)

- Install dependencies the way CI does.
- **Run the test suite before touching anything.** Record the result (count, duration,
  failures). A red baseline is the first problem to solve or to report; never build on it.
- Run the app (compose, dev script, or the binary) and hit one endpoint or screen.
- Run lint and type-check if they exist. These three commands are your verification loop
  for everything that follows.

## 3. Leave a map: `CLAUDE.md` in 20 to 40 lines

If the repo has none, write one now, from what you just verified, nothing invented:

```markdown
# <project> for agents
## Run / test / lint
<exact commands, one per line, as CI runs them>
## Layout
<five lines: where domain, I/O adapters, entry points, tests, config live>
## Conventions
<what differs from the language default: style, naming, error handling, test style>
## Do not touch
<generated files, migrations, vendored code, secrets, anything the user named>
```

If an `AGENTS.md` exists, make the first line of `CLAUDE.md` `@AGENTS.md` so it is loaded,
and do not duplicate it. Keep it short: anything the agent can infer from the code does
not belong in it.

## 4. Branch, then start the task

`git switch -c <type>/<slug>` (or a worktree if the user works that way). Restate the task
in three sentences including what is out of scope, write the acceptance test first, and
only then let an agent implement. The `fresh-review` skill closes the loop.

## What to say when something is missing

- No tests: say so, add one smoke test around the entry point before the change, and
  mention that the change will be covered by that test only.
- Tests fail on a clean checkout: stop and show the failure; ask whether to fix the
  baseline first or to proceed with the failing tests quarantined and listed.
- A language or framework you do not know: say it, ask the agent to explain the idioms,
  and lean on the repo's lint, type-check and tests as the loop. Never pretend.
