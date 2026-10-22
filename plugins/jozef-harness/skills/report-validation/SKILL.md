---
name: report-validation
description: >-
  Validate a finished data report (HTML page, Markdown or PDF analysis) with an independent
  report-validator subagent (Opus, extended thinking, fresh context) that reads the report as
  its audience will and recomputes its numbers from the data files, then fix what it found and
  have it checked again, up to 3 rounds. Use it whenever a report, analysis page, dashboard
  export or methodology document is about to be published or sent to a stakeholder or a team,
  whenever the user says "validate the report", "zkontroluj report", "check the numbers",
  "report validation", "/report-validation", or after rebuilding a report's data or HTML
  (quality reports, billing or usage analyses). Not for code review (that is fresh-review) and not for writing the report itself.
argument-hint: "<report path> [--data <path>...] [--rounds N]"
---

# Report validation: an independent reader checks the page, then the numbers

A report written in this session cannot be checked by this session: the author knows what
every number means and reads past the gaps. The `report-validator` subagent starts with a
fresh context and only three things: the report, its rendered text and the data. It runs on
Opus with extended thinking because the second phase is real work: rebuilding the report's
numbers from CSV/JSON and finding where they diverge. Your job here is to give it exactly
those inputs, then act on its findings and send it back, at most three times.

```
render → spawn report-validator(round 1) → validation-1.json
      → fix report defects here → rebuild + render → spawn again (round 2) …
      → PASS, or nothing left to fix, or 3 rounds → report to the user
```

## 1. Collect the inputs

1. **The report.** The path from the arguments, or the HTML/MD file this session just
   built. One file; a multi-page site is validated page by page.
2. **Its data.** Everything the report claims to be computed from, in this order of
   preference: the exported data package next to it (a `data-<date>/` folder or zip with
   CSVs and a README), the data file the page embeds or loads (`data.json`), the build
   script and its inputs, and the methodology document (`METODIKA*.md`, `README-data.md`).
   Look in the report's folder first; `--data` adds paths. If you cannot find any data,
   stop and ask the user: a validator without data can only do phase 1, and they should know.
3. **The rendered text.** Reports built with JavaScript show nothing in their source, so
   render first:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/report-validation/scripts/render_report.py" <report> --out <report-dir>/validation/rendered.txt
   ```
   It prints how it rendered (headless Chrome, or static source only) and any `NaN` /
   `undefined` tokens it saw. Read `rendered.txt.meta.json` for the page outline; if the
   outline is empty or the text is tiny, the page did not render — fix that before
   validating anything (a longer `--wait-ms`, a missing data file).
4. **The workspace** is `<report-dir>/validation/`. Rounds are numbered; nothing in there
   is part of the report. If the report folder is published or zipped as a whole, mention
   the folder in your final message so the user can exclude it.

Data with patient or customer text stays where it is; pass paths, never copy the data
somewhere else.

## 2. Spawn the validator: paths and nothing else

One `Agent` call, `subagent_type: report-validator`, `run_in_background: true` (a round
takes a while). Agent definitions load when a session starts, so a session older than
the plugin install does not know the type: then spawn `general-purpose`
with `model: opus`, `effort: xhigh` and open the message with "You are acting as the
`report-validator` agent: read `${CLAUDE_PLUGIN_ROOT}/agents/report-validator.md` first and
follow it exactly" (the stop hook that enforces the VERDICT line is lost, so check for it). The message lists only facts; do not describe what the report is supposed to
say or which numbers you are proud of, the validator must find that out itself:

```
Validate this report. Round 1 of up to 3.
Report: <path>
Rendered text: <report-dir>/validation/rendered.txt  (meta: rendered.txt.meta.json)
Data: <path 1> — <one line: what it is>
      <path 2> — …
Methodology: <path>  (if any)
Build: <build script path>  (if any)
Validation folder: <report-dir>/validation/
Audience: <who reads it, one line>   (if known: the owner, the dev team, a client)
Write validation-1.json and validation-1.md there and end with the VERDICT line.
```

Wait for the notification; do not poll. Then read `validation-<n>.json`.

## 3. Act on the findings

Triage every finding:

- **Report defects, fix them here:** a wrong or stale number, a label without a
  definition, a broken cell, a sentence that contradicts its table, inconsistent
  formatting, a methodology line that does not match the computation. Fix the source
  (template, build script, methodology), rebuild the report the way it is built
  (`build.py`, `export.py`, whatever the folder uses), re-render, and note the fix.
- **Method or scope questions, ask the user:** a finding that would change what a number
  means (a different denominator, a filter, a definition) or that the validator could not
  verify because data is missing. Collect these and ask once, after the round, with the
  validator's wording and your recommendation. Do not silently change a definition to make
  a mismatch go away.
- **Validator mistakes:** when you are sure the validator is wrong (it applied the wrong
  filter, misread a unit), say so in the next round's message with the evidence, so it can
  re-check instead of repeating itself. Being sure means you recomputed it, not that you
  remember writing it.

Then the next round: re-render, spawn `report-validator` again (fresh context) with the same
inputs, `Round <n>`, `Previous: <validation-(n-1).json>` (its helper scripts live in
`validation/scripts/` and can be re-run) and a block `What changed since round <n-1>
(author's notes, verify rather than trust): …` listing each finding id and what you did,
including what you left unchanged on purpose and why. The validator re-checks those first
and marks them fixed / open / not applicable, so the next summary says what moved.

Stop when the verdict is PASS and nothing should-fix is left, when every open finding is one
only the user can decide, or after the third round. A PASS with should-fix items still open is
worth one more round when rounds remain: they are cheap to fix and the next reader is
the one who decides.

## 4. Report to the user

Short, in the conversation:

- rounds run and the final verdict (a round takes 10–15 minutes and a few hundred
  thousand tokens of the subagent's own context on a 500 KB page; say so if it matters);
- what was fixed, one line each, with the number before → after where a number changed;
- open findings that need their decision, with the validator's evidence and your
  recommendation;
- `unverifiable` items and what data would settle them;
- links to the last `validation-<n>.md` and to the rebuilt report.

The validation folder stays: the next person can read what was checked and how.
