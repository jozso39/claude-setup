#!/bin/bash
# PreToolUse guard for the trio agents (Write|Edit|MultiEdit|NotebookEdit).
#   write-guard.sh trio-only   planner, evaluator: may write only inside <repo>/.trio/
#   write-guard.sh not-judge   generator: may write anywhere except the files that judge
#                              it (contract, spec, eval reports, run state, log)
# Bash can still write; the orchestrator's git check after every agent catches that.

mode=$1
input=$(cat)

path=$(jq -r '.tool_input.file_path // .tool_input.notebook_path // empty' <<<"$input")
[ -z "$path" ] && exit 0

cwd=$(jq -r '.cwd // empty' <<<"$input")
[ -z "$cwd" ] && cwd=$PWD
root=$(git -C "$cwd" rev-parse --show-toplevel 2>/dev/null) || root=$cwd

case "$path" in
  /*) abs=$path ;;
  *) abs="$cwd/$path" ;;
esac

case "$mode" in
  trio-only)
    case "$abs" in
      "$root"/.trio/*) exit 0 ;;
    esac
    echo "trio: this agent may only write inside $root/.trio/ (tried $path). Report the problem in your output instead of changing the code." >&2
    exit 2
    ;;
  not-judge)
    case "$abs" in
      "$root"/.trio/*/contract.md | "$root"/.trio/*/spec.md | "$root"/.trio/*/eval-*.md | \
      "$root"/.trio/*/run.json | "$root"/.trio/*/log.md)
        echo "trio: the generator may not change $path. Disagree with the contract or an evaluation in build-N.md instead." >&2
        exit 2
        ;;
    esac
    exit 0
    ;;
esac

exit 0
