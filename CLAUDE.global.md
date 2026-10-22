# How I work with Claude (every project)

Copy this to `~/.claude/CLAUDE.md`. Plugins cannot install it for you; it is the part of the
harness that lives in prose. Everything here guides; the hooks in the plugin enforce.

## Links and references
- Never mention a file without a clickable link: a markdown link in prose (`[name](path:line)`). Plain paths only inside commands and code.
- Tickets, merge requests and documents as named links, never bare ids, not even in a table or a status line; fetch the name if you don't have it.
- Lead with the verdict or outcome; a reader who sees only the last message must have the whole picture.
- No attribution lines anywhere: no "Generated with Claude Code", no `Co-Authored-By: Claude` trailer, nothing of the kind at the end of merge requests, commits, comments, documents or messages.

## What waits for my go
- Messages and e-mails on my behalf wait for my approval, ideally as a draft inside the app that I send myself.
- Publishing or promoting prompts and any production database change never happen without my explicit permission in the current session.
- Prepare it fully (the draft, the exact list, the dry run), then stop and ask. One go covers one action in the current session, not the next one.
- Commit and push on your own. Never merge a merge request unless I explicitly ask for that one.

## Credentials
- Never type credentials, and never read a token or a cookie out of my browser or into the conversation.
- When a script needs a secret, create a `.env` next to the script with the variable left unfilled (`API_TOKEN=<enter the value here>`), give me the link to that file, and have the script read it. The value never enters your context. Don't ask me to paste secrets into the chat.

## Verifying and reporting
- "Test it" means run the real thing (the job, the flow, the test file), never a static read.
- "Test it manually" means use the product yourself: drive the UI in the browser or call the API directly, through the whole feature rather than one happy path. Then fold what you exercised into the existing tests so the next run covers it.
- Report only numbers that were actually computed; evaluate everything in scope and tag what is incomplete instead of skipping it. A wrong claim costs more than a missing one.
- Before changing system state, check that the evidence supports that specific change.

## Code
The my-setup plugin adds these at session start; keep them here only if you do not install it.
- Before writing a helper, search the repo for an existing one and reuse it.
- Don't copy a block of logic. Extract it once it appears a second time.
- Don't add an interface, base class or factory that has only one implementation or one caller.
- Keep a function to one job. If you need "and" to describe it, split it.
- Follow the patterns already in the file and module, even where you would design it differently.

## Working on this machine
- Parallel Bash calls share one working directory: use `git -C <abs>` and absolute paths when two repos are involved, and verify with `git -C <abs> status` afterwards.
- One git worktree per task, next to the repo (`<parent>/worktrees/<repo>-<slug>`), created after `git fetch` from the remote copy of whatever branch the task builds on; local branches are stale.
- Keep the memory notes current: write the non-obvious lesson, not what the repo already records.
