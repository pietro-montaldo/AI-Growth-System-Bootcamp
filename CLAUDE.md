# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

The public repo for students of the AI Growth Systems Bootcamp (https://maven.com/pietro-montaldo/ai-growth-system-bootcamp-claude). It's a Claude Code plugin marketplace named `ai-growth-system-bootcamp` (`.claude-plugin/marketplace.json`, `plugins/`, `shared/`, `scripts/`). A skill only shows up for students once it's inside a plugin listed in `marketplace.json`. Today it ships three things:

- `plugins/voice-miner`: a standalone plugin with one skill. See "voice-miner" below.
- `plugins/do-not-contact`: a standalone plugin that builds one do-not-contact list every outreach system checks first. See "do-not-contact" below.
- The GTM context kit, which helps students build a go-to-market context layer: product, ICP, competitors, customer language, objections, shareable customers. Later course systems (outbound and inbound agents) read that context first.

The GTM context kit has two plugins with the same skill and agent names. Only the storage steps differ:

- `plugins/gtm-context-notion`: context lives in Notion under one GTM Hub page. The Hub is its own map: a links table plus a collapsed "For agents" section with data source IDs, sources, the best-customer rule and update settings. Nothing is saved locally except temporary exports.
- `plugins/gtm-context-github`: context lives as markdown pages and CSV banks in `gtm/`, inside a private `gtm-context` repo cloned at `~/gtm-context`.

Where it lives is never asked. A pointer block in the student's `~/.claude/CLAUDE.md` (between `gtm-context:start` and `gtm-context:end` markers) tells every session where it is: only the Hub link for Notion, the repo and `~/gtm-context` path for GitHub. See `shared/references/context-home.md`. Skills must never write `gtm/` or any context into the current project folder.

The skills are content, not code: SKILL.md files, agent files and reference markdown. There is no build step and no test suite.

## Commands

```bash
scripts/sync-shared.sh            # copy shared/ into the plugins (references, agents, scripts)
scripts/sync-shared.sh --check    # fail if a copy is out of date
claude plugin validate .          # validate the marketplace manifest
claude plugin validate plugins/gtm-context-notion
claude plugin validate plugins/gtm-context-github
python3 shared/scripts/gtm_csv.py --help   # the CSV helper the GitHub plugin ships
claude plugin validate plugins/do-not-contact
python3 shared/do-not-contact/scripts/dnc.py --help   # the do-not-contact helper
```

To try a plugin locally: `/plugin marketplace add ./` then `/plugin install gtm-context-notion@ai-growth-system-bootcamp` (or `gtm-context-github@ai-growth-system-bootcamp`).

The README is the student-facing page for everything in the repo: one row per skill or plugin in the table at the top, then one section each. Keep that shape when adding something.

## Structure that spans files

- `shared/` is the single source for everything both plugins need. Installed plugins can't read outside their own folder, so `scripts/sync-shared.sh` copies it in, using the maps at the top of the script. Edit `shared/` only, never the copies, then run the script.
  - `shared/references/` (`sections.md`, `icp-checks.md`, `mining-playbook.md`, `source-map.md`, `update-playbook.md`, `handover.md`, `context-home.md`) go into the skills' `references/` that need them.
  - `shared/agents/` go into each plugin's `agents/`. The agents are storage-agnostic, so both plugins share them.
  - `shared/scripts/gtm_csv.py` goes into the GitHub plugin's skills that touch a CSV bank (`scripts/`). It is standard-library Python: `init`, `query`, `count`, `upsert`. Skills call it by full path from the skill folder.
  - `shared/scripts/gtm_home.py` goes into both plugins' `build-gtm-context`. It handles the pointer and `~/gtm-context`: `status` (mode, Hub link parsed from the pointer, old setup files), `init`, `pointer` (idempotent memory block) and `allow` (adds the folder to `permissions.additionalDirectories` in `~/.claude/settings.json`, with a backup). `GTM_CONTEXT_HOME` and `CLAUDE_CONFIG_DIR` override the paths, for testing.
- `build-gtm-context` is the guide. It works in three moves: map where the user's GTM information already lives (`source-map.md`), read it all, then run the six section skills (`gtm-product`, `gtm-customers`, `gtm-competitors`, `gtm-icp`, `gtm-messaging`, `gtm-objections`). Each section drafts from what was found and asks only about gaps. Each section skill also works on its own, and then asks where its bucket lives first.
- The build ends with a handover (`shared/references/handover.md`): it creates the student's own plugin, `my-gtm-context`, with one skill, `update-gtm-context`, in a private `gtm-update` repo that is also a marketplace (`my-gtm`). The student adds it in Customize > Plugins, so it lives on their Claude account and works in Claude Code, Cowork and cloud scheduled tasks (cloud sessions don't load plugins installed with `/plugin`). The handover schedules it and then removes the course plugin (never the course marketplace while other course plugins are in use).
  - The update skill is filled in from the guide's `references/update-skill-template.md` (one per plugin, storage-specific). It holds the student's links, tools and a per-source plan of where new information comes from (`source-map.md`, "Will each source stay current?"). It has three modes: scheduled run, review, change settings. State such as last run dates stays in the hub, because skill files are read-only during runs.
  - Its rules are in `shared/references/update-playbook.md`, copied into the student's plugin with `mining-playbook.md`, `source-map.md`, two agents and (GitHub) `gtm_csv.py`. `source-reader` has a compare mode (baseline in, only ADDED/REMOVED/CHANGED out) for the monthly offer check. Scheduled runs are unattended: banks grow on their own, pages only get proposed updates in a dated report, one alert goes to the user. The scheduled prompt holds the alert address, never a file.
- Sources without a connector (course and payment dashboards like Maven or Stripe) are read with a browser tool (Claude in Chrome for signed-in pages), read-only, or from an export.
- Three agents do the heavy reading in parallel, so the main conversation keeps only conclusions:
  - `source-reader`: one per existing doc, database, export or page.
  - `language-miner`: one per conversation source (email, calls, DMs, pasted text).
  - `competitor-researcher`: one per competitor.
  Agent files can't have references, so their rules are inline and must stay consistent with `source-map.md` and `mining-playbook.md`.
- ICP signals favour what's publicly checkable or available from an enrichment connector (`icp-checks.md`, "Public signals"). Skills never name the enrichment tool to students: they say "public company data". Best customers come from 3 names for small B2B lists, or a behaviour rule for B2C and long lists (gtm-customers A3).
- Notion page templates and database schemas live in the Notion guide's `references/hub-structure.md`. The GitHub equivalent (folder layout, hub file, CSV columns, git and privacy rules) is the GitHub guide's `references/repo-structure.md`. Section skills point to these rather than repeating schemas.
- The two plugins' section skills are near-copies. When changing a step, change it in both and keep only the storage wording different.

## Rules the skills must keep

- Notion: one GTM Hub page links to everything; skills fetch pages by the links on the Hub page (links table and "For agents" section) and never search for them; banks (objections, competitors, customers) are queried with filters, never read whole; dedupe with one filtered query per batch; no copies of context in the repo.
- GitHub: `gtm/README.md` links to everything; CSV banks are queried and written only through `gtm_csv.py`, never read whole; check the repo isn't public before writing data; raw exports stay in gitignored `gtm/.private/`; never commit or push without asking. Data that already lives in a connected system is linked under "Sources", not copied into CSV.
- Pages stay one or two screens with a summary at the top.
- Every write has an approval pause. Nothing is ever sent, posted or connected. The one exception is the student's own update skill's scheduled run, which the user authorises once at the handover: it may add to banks, write a report, and send one alert to the user's own email or Slack DM. It never changes curated pages and never contacts anyone else.
- No personal names, emails or LinkedIn URLs in context: role and company type only. Customer logos are marked shareable only with explicit permission.
- Every mining step has a paste-it-in fallback, because many students can't connect email or a call recorder.

## Writing style

Students are non-technical (founders, consultants, operators). Write in plain language with short sentences. No em dashes or double dashes. Frontmatter `description` is one quoted string: what the skill does, quoted trigger phrases, then "Not for X". Keep SKILL.md under about 150 lines and push detail into `references/`.

## voice-miner

`plugins/voice-miner` is its own plugin in the marketplace, separate from the GTM context plugins. It doesn't use `shared/` or `sync-shared.sh`. Its script (`scripts/voice_mine.py`) is standard-library Python. Students' raw mailbox and transcript data go in a `voice-mining/` working folder, which is gitignored.

## do-not-contact

`plugins/do-not-contact` is its own plugin with three skills: `build-do-not-contact` (pick Google Sheet or Notion, map sources, collect, approve, pointer, weekly schedule), `update-do-not-contact` (quick add, unattended scheduled run, review, settings) and `check-do-not-contact` (split a lead list into keep and drop, export a sending tool blocklist). One agent, `dnc-collector`, reads one source and returns rows in the list's columns, never message text.

- Its references and script live in `shared/do-not-contact/` and `scripts/sync-shared.sh` copies them into all three skills. Edit `shared/do-not-contact/` only.
- `dnc.py` is standard-library Python: `clean`, `normalize`, `merge`, `keys`, `check`, `blocklist`. It owns key cleaning (lowercase emails, `linkedin.com/in/<slug>`, bare domains, no company blocks on personal email providers) and the `Until` expiry, so skills never compare keys by hand.
- The list is found through a pointer block in `~/.claude/CLAUDE.md` between `do-not-contact:start` and `do-not-contact:end`. The GTM Hub or `gtm/README.md` may hold its link, never its rows.
- It is the one place in the course that keeps emails and LinkedIn URLs on purpose. No names or message text. Said no, unsubscribed, bounced and erasure request rows are never deleted automatically. The scheduled run only adds rows, fills `To review`, updates Last run and sends one summary to the student.
- LinkedIn is paste only: never read the LinkedIn inbox with automation.
