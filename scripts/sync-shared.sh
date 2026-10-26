#!/usr/bin/env bash
# Copy shared files into every plugin that uses them.
# Installed plugins can't read files outside their own folder, so each skill
# carries its own copy. Edit shared/ only, then run this script.
#
#   shared/references/*  -> the skills listed in REFERENCES, in every plugin
#   shared/agents/*      -> agents/ in every plugin
#   shared/scripts/*     -> the skills listed in SCRIPTS, GitHub plugin only
#
#   scripts/sync-shared.sh          copy
#   scripts/sync-shared.sh --check  exit 1 if any copy is out of date

set -euo pipefail
cd "$(dirname "$0")/.."

# shared file : skill that needs it
REFERENCES="
sections.md:build-gtm-context
sections.md:gtm-product
sections.md:gtm-icp
icp-checks.md:gtm-icp
mining-playbook.md:gtm-messaging
mining-playbook.md:gtm-objections
source-map.md:build-gtm-context
source-map.md:gtm-product
source-map.md:gtm-customers
source-map.md:gtm-competitors
source-map.md:gtm-messaging
source-map.md:gtm-objections
"

# shared script : skill that needs it (GitHub plugin only: its banks are CSV files)
SCRIPTS="
gtm_csv.py:build-gtm-context
gtm_csv.py:gtm-customers
gtm_csv.py:gtm-competitors
gtm_csv.py:gtm-icp
gtm_csv.py:gtm-objections
"

check=0
[ "${1:-}" = "--check" ] && check=1
stale=0

# sync <source> <destination dir>
sync() {
  if [ "$check" = 1 ]; then
    if ! cmp -s "$1" "$2/$(basename "$1")"; then
      echo "out of date: $2/$(basename "$1")"
      stale=1
    fi
  else
    mkdir -p "$2"
    cp -p "$1" "$2/"
  fi
}

for plugin in plugins/*/; do
  for pair in $REFERENCES; do
    skill="${pair##*:}"
    [ -d "${plugin}skills/${skill}" ] || continue
    sync "shared/references/${pair%%:*}" "${plugin}skills/${skill}/references"
  done
  for agent in shared/agents/*.md; do
    sync "$agent" "${plugin}agents"
  done
done

for pair in $SCRIPTS; do
  skill="${pair##*:}"
  sync "shared/scripts/${pair%%:*}" "plugins/gtm-context-github/skills/${skill}/scripts"
done

if [ "$check" = 1 ]; then
  [ "$stale" = 0 ] && echo "all shared files in sync"
  exit "$stale"
fi
echo "synced shared files into $(ls -d plugins/*/ | wc -l | tr -d ' ') plugin(s)"
