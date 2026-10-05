#!/usr/bin/env bash
# PreToolUse hook (Bash): subagents (hook input has agent_id) may not touch shared infra
# directly. They go through `scripts/stack`, which only does safe operations.
# The main session (no agent_id) is not restricted. Exit 2 = block, stderr goes to the agent.
set -euo pipefail

input="$(cat)"
agent_id="$(jq -r '.agent_id // empty' <<<"$input")"
[[ -z "$agent_id" ]] && exit 0
cmd="$(jq -r '.tool_input.command // empty' <<<"$input")"
[[ -z "$cmd" ]] && exit 0

# Start of a command: line start, or after ; & | ( ` $( , optionally behind sudo/env/VAR=x.
start='(^|[;&|(`]|\$\()[[:space:]]*(sudo[[:space:]]+)?(env[[:space:]]+)?([A-Za-z_][A-Za-z0-9_]*=[^[:space:]]*[[:space:]]+)*'
patterns=(
  "${start}(docker|docker-compose)([[:space:]]|$)"
  "${start}make([[:space:]]+[^;&|[:space:]]+)*[[:space:]]+(dev|up|down)([[:space:]]|$)"
  "compose[[:space:]]+down"
  "stack[[:space:]]+infra[[:space:]]+(down|reset)"
)

while IFS= read -r line; do
  for re in "${patterns[@]}"; do
    if [[ "$line" =~ $re ]]; then
      cat >&2 <<MSG
Blocked by guard-infra: agents must not run docker/compose or the human-only make targets
(matched: "${BASH_REMATCH[0]}").
Use the app stack instead:
  scripts/stack lease <owner>                     # once per worktree
  scripts/stack run --db test --heavy -- <cmd>    # tests;  --db dev for the dev DB, --ports for servers
  scripts/stack infra ensure                      # if Postgres/Redis are down
  make check-backend / make check-frontend
Anything destructive (down, reset, recreate): ask the human.
MSG
      exit 2
    fi
  done
done <<<"$cmd"
exit 0
