#!/usr/bin/env bash
# Feeds sample PreToolUse inputs into guard-infra.sh and checks the exit codes.
set -uo pipefail
hook="$(dirname "$0")/guard-infra.sh"
fail=0

check() {  # check <expected-exit> <agent_id|-> <command>
  local want=$1 agent=$2 cmd=$3 json got
  if [[ "$agent" == - ]]; then
    json=$(jq -n --arg c "$cmd" '{hook_event_name:"PreToolUse",tool_name:"Bash",tool_input:{command:$c}}')
  else
    json=$(jq -n --arg c "$cmd" --arg a "$agent" \
      '{hook_event_name:"PreToolUse",tool_name:"Bash",agent_id:$a,tool_input:{command:$c}}')
  fi
  "$hook" <<<"$json" 2>/dev/null; got=$?
  if [[ "$got" == "$want" ]]; then echo "ok   $want  [${agent}] $cmd"
  else echo "FAIL want $want got $got  [${agent}] $cmd"; fail=1; fi
}

# agents: blocked
check 2 builder-1 'docker ps'
check 2 builder-1 'docker compose up -d db'
check 2 builder-1 'docker-compose down -v'
check 2 builder-1 'cd /x && docker compose down -v'
check 2 builder-1 'FOO=1 docker run --rm alpine'
check 2 builder-1 'sudo docker system prune'
check 2 builder-1 'echo $(docker ps -q)'
check 2 builder-1 'make dev'
check 2 builder-1 'make up'
check 2 builder-1 'make -C /x down'
check 2 builder-1 'podman compose down'
check 2 builder-1 'scripts/stack infra down'
check 2 builder-1 'STACK_ROLE=human scripts/stack infra reset'
check 2 reviewer-1 $'ls\ndocker ps'
# agents: allowed
check 0 builder-1 'scripts/stack run --db test --heavy -- make check-backend'
check 0 builder-1 'scripts/stack infra ensure'
check 0 builder-1 'make check-backend'
check 0 builder-1 'make reseed'
check 0 builder-1 'make download'
check 0 builder-1 'grep -n docker docs/playbooks/05-database.md'
check 0 builder-1 'git commit -m "docs: mention docker in the playbook"'
# known false positive, accepted: "compose down" matches anywhere, even in a message
check 2 builder-1 'git commit -m "docs: compose down is human-only"'
# main session: everything passes
check 0 - 'docker compose down -v'
check 0 - 'make dev'

exit $fail
