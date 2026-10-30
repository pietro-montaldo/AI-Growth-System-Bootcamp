#!/usr/bin/env bash
# Copy shared files into every plugin that uses them.
# Installed plugins can't read files outside their own folder, so each skill
# carries its own copy. Edit shared/ only, then run this script.
#
#   shared/references/*  -> the skills listed in REFERENCES, in both GTM plugins
#   shared/references/notion/* -> the skills listed in NOTION_REFERENCES (Notion plugin only)
#   shared/references/github/* -> the skills listed in GITHUB_REFERENCES (GitHub plugin only)
#   shared/agents/*      -> agents/ in both GTM plugins (not voice-miner)
#   shared/scripts/*     -> the skills listed in SCRIPTS_ALL (every GTM plugin) and SCRIPTS (GitHub only)
#   shared/do-not-contact/* -> every skill of the do-not-contact plugin
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
mining-playbook.md:build-gtm-context
mining-playbook.md:gtm-messaging
mining-playbook.md:gtm-objections
source-map.md:build-gtm-context
source-map.md:gtm-product
source-map.md:gtm-customers
source-map.md:gtm-competitors
source-map.md:gtm-messaging
source-map.md:gtm-objections
source-map.md:gtm-icp
update-playbook.md:build-gtm-context
handover.md:build-gtm-context
context-home.md:build-gtm-context
"

# storage schema : skill that needs it, in one GTM plugin only
# (the Hub and database layout for Notion, the gtm/ folder and CSV columns for GitHub)
NOTION_REFERENCES="
hub-structure.md:build-gtm-context
hub-structure.md:gtm-customers
hub-structure.md:gtm-objections
page-style.md:build-gtm-context
page-style.md:gtm-product
page-style.md:gtm-icp
page-style.md:gtm-messaging
page-style.md:gtm-competitors
"
GITHUB_REFERENCES="
repo-structure.md:build-gtm-context
repo-structure.md:gtm-customers
repo-structure.md:gtm-competitors
repo-structure.md:gtm-objections
"

# shared script : skill that needs it, in every GTM plugin
SCRIPTS_ALL="
gtm_home.py:build-gtm-context
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

for plugin in plugins/gtm-context-*/; do
  for pair in $REFERENCES; do
    skill="${pair##*:}"
    [ -d "${plugin}skills/${skill}" ] || continue
    sync "shared/references/${pair%%:*}" "${plugin}skills/${skill}/references"
  done
  for agent in shared/agents/*.md; do
    sync "$agent" "${plugin}agents"
  done
  for pair in $SCRIPTS_ALL; do
    sync "shared/scripts/${pair%%:*}" "${plugin}skills/${pair##*:}/scripts"
  done
done

for pair in $NOTION_REFERENCES; do
  sync "shared/references/notion/${pair%%:*}" "plugins/gtm-context-notion/skills/${pair##*:}/references"
done
for pair in $GITHUB_REFERENCES; do
  sync "shared/references/github/${pair%%:*}" "plugins/gtm-context-github/skills/${pair##*:}/references"
done

for pair in $SCRIPTS; do
  skill="${pair##*:}"
  sync "shared/scripts/${pair%%:*}" "plugins/gtm-context-github/skills/${skill}/scripts"
done

# do-not-contact: every skill gets the same references and script
for skill in plugins/do-not-contact/skills/*/; do
  for ref in shared/do-not-contact/references/*.md; do
    sync "$ref" "${skill}references"
  done
  sync shared/do-not-contact/scripts/dnc.py "${skill}scripts"
done

if [ "$check" = 1 ]; then
  [ "$stale" = 0 ] && echo "all shared files in sync"
  exit "$stale"
fi
echo "synced shared files into $(ls -d plugins/gtm-context-*/ | wc -l | tr -d ' ') plugin(s)"
