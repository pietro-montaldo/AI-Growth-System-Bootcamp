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
  - `shared/references/notion/hub-structure.md` and `shared/references/github/repo-structure.md` hold the storage schemas. The `NOTION_REFERENCES` and `GITHUB_REFERENCES` maps copy each into its own plugin only: into `build-gtm-context` and the bank skills (Notion: `gtm-customers`, `gtm-objections`; GitHub: `gtm-customers`, `gtm-competitors`, `gtm-objections`).
  - `shared/agents/` go into each plugin's `agents/`. The agents are storage-agnostic, so both plugins share them.
  - `shared/scripts/gtm_csv.py` goes into the GitHub plugin's skills that touch a CSV bank (`scripts/`). It is standard-library Python: `init`, `add-cols`, `query`, `count`, `upsert` (a key written `Email|LinkedIn URL|Customer` takes the first column that matches). Skills call it by full path from the skill folder. `upsert` takes several key columns and `--merge COL`. Keys per bank: customers `--key Company --merge Offer`, objections `--key "Objection,Offer"`, competitors `--key Name`. `--min` never matches a blank cell. Reads accept an Excel BOM.
  - `shared/scripts/gtm_home.py` goes into both plugins' `build-gtm-context`. It handles the pointer and `~/gtm-context`: `status` (mode, Hub link parsed from the pointer, old setup files), `init` (`--github` also creates `gtm/.private/` and its gitignore lines), `pointer` (idempotent memory block; keeps the Notion review line when `--updates` isn't given, and stops on a broken marker) and `allow` (adds the folder to `permissions.additionalDirectories` in `~/.claude/settings.json`, with a backup). `GTM_CONTEXT_HOME` and `CLAUDE_CONFIG_DIR` override the paths, for testing.
- `build-gtm-context` is the guide. It works in three moves: map where the user's GTM information already lives (`source-map.md`), read it all, then run the six section skills (`gtm-product`, `gtm-customers`, `gtm-competitors`, `gtm-icp`, `gtm-messaging`, `gtm-objections`). Each section drafts from what was found and asks only about gaps. Each section skill also works on its own, and then asks where its bucket lives first.
- The build ends with a handover (`shared/references/handover.md`): it creates one scheduled task of the student's own, `gtm-update`, whose prompt holds the whole update, then removes the course plugin (never the course marketplace while other course plugins are in use). Nothing else is installed: no personal plugin, no extra repo.
  - The task prompt and a review guide are filled in from the guide's `references/update-task-template.md` (one per plugin, storage-specific). The prompt holds the student's links, tools, a per-source plan of where new information comes from (`source-map.md`, "Where each item comes from, now and later"), the run steps, short reading briefs for general-purpose agents, and `update-playbook.md` plus parts of `mining-playbook.md` pasted in. Keep those briefs consistent with the agent files.
  - Review and settings changes happen in normal sessions: the review guide sits on the Notion "Updates to review" page or in `gtm/updates/README.md`, and the memory pointer gets a line pointing to it (`gtm_home.py pointer --updates` for Notion; added on its own for GitHub once the file exists). Settings live in the task prompt, changed with `update_scheduled_task`. GitHub students with CSV banks get `gtm_csv.py` committed to `~/gtm-context/scripts/`. State such as last run dates stays in the hub.
  - `source-reader` has a compare mode (baseline in, only ADDED/REMOVED/CHANGED out) for the monthly offer check. Scheduled runs are unattended: banks grow on their own, pages only get proposed updates in a dated report, one alert goes to the user. The task prompt holds the alert address, never a file or page.
- Sources without a connector (course and payment dashboards like Maven or Stripe) are read with a browser tool (Claude in Chrome for signed-in pages), read-only, or from an export.
- Three agents do the heavy reading in parallel, so the main conversation keeps only conclusions:
  - `source-reader`: one per existing doc, database, export or page.
  - `language-miner`: one per conversation source (email, calls, DMs, pasted text).
  - `competitor-researcher`: one per competitor.
  Agent files can't have references, so their rules are inline and must stay consistent with `source-map.md` and `mining-playbook.md`.
- ICP signals favour what's publicly checkable or available from an enrichment connector (`icp-checks.md`, "Public signals"). Each ICP is a battlecard with fixed labels (Who, Find them, Score, Trigger, Their words, Lead with, Expect, Not them, Say this), about 12 to 15 lines, so agents can act on it. Best customers come from 3 names for small B2B lists, or a behaviour rule for B2C and long lists (gtm-customers A3), per offer when buyers differ.
- Enrichment (gtm-customers A2, "Fill and enrich"): Clay first, then any other connected enrichment tool (for example Apollo). Count the gaps, quote the credits and get an OK before any lookup. Enrich both people and companies: when the best customers lack the buyer's role and seniority or their company's size and industry (B2B, and B2C sold to professionals), the ICP can't be inferred or scored, so enrichment is recommended (and without a connected tool, Clay is offered). Buyer and company fields only; never look up emails or phone numbers.
- Offers: the build lists every offer and the student picks the offers in scope (`source-map.md`, "Offers: one or several?"). Every section covers each offer in scope: product sections per offer, ICP cards per offer (up to 5 each), value props per offer, and customers and objections tagged with an Offer column.
- Item-by-item source plan (build step 1, `source-map.md`, "Where each item comes from, now and later"): for every item, how it was collected, where new information comes from and who brings it in (`auto`, `auto, app only`, `you`, `none`), preferring automatic routes. It's recorded in the hub's Sources list and reused by the handover.
- Notion page templates and database schemas live in `hub-structure.md`. The GitHub equivalent (folder layout, hub file, CSV columns and keys, git and privacy rules) is `repo-structure.md`. Edit them in `shared/references/notion/` and `shared/references/github/`, never in the plugins. Section skills point to their own copy rather than repeating schemas.
- The two plugins' section skills are near-copies. When changing a step, change it in both and keep only the storage wording different.

## Rules the skills must keep

- Notion: one GTM Hub page links to everything; skills fetch pages by the links on the Hub page (links table and "For agents" section) and never search for them; banks (objections, competitors, customers) are queried with filters, never read whole; dedupe with one filtered query per batch; no copies of context in the repo.
- GitHub: `gtm/README.md` links to everything; CSV banks are queried and written only through `gtm_csv.py`, never read whole; check the repo isn't public before writing data; raw exports stay in gitignored `gtm/.private/`; never commit or push without asking. Data that already lives in a connected system is linked under "Sources", not copied into CSV.
- Pages stay one or two screens with a summary at the top.
- Every write has an approval pause. Nothing is ever sent, posted or connected. The one exception is the student's scheduled update task, which the user authorises once at the handover: it may add to banks, write a report, and send one alert to the user's own email or Slack DM. It never changes curated pages and never contacts anyone else.
- Customer contact details (name, email, LinkedIn URL) live only in the customer database, one row per buyer, and only after the user says yes (gtm-customers A1b); otherwise the information is lost when the export is deleted. Everywhere else (pages, quotes, objections, agent results, reports): role and company type only. Customer logos are marked shareable only with explicit permission.
- Every mining step has a paste-it-in fallback, because many students can't connect email or a call recorder.

## Writing style

Students are non-technical (founders, consultants, operators). Write in plain language with short sentences. No em dashes or double dashes. Frontmatter `description` is one quoted string: what the skill does, quoted trigger phrases, then "Not for X". Keep SKILL.md under about 150 lines and push detail into `references/`.

## voice-miner

`plugins/voice-miner` is its own plugin in the marketplace, separate from the GTM context plugins. It doesn't use `shared/` or `sync-shared.sh`. Its script (`scripts/voice_mine.py`) is standard-library Python: `extract` (.mbox, .eml), `clean`, `score`, `fingerprint`, `redact`, `transcript`, `check`. Email kinds are `cold`, `followup`, `reply`, `new`, plus `post`, `dm`, `comment` for drafts. Skills call it by full path from the skill folder. The template's frontmatter `description` must stay a quoted string once filled in. Students' raw mailbox and transcript data go in a `voice-mining/` working folder, which is gitignored.

## do-not-contact

`plugins/do-not-contact` is its own plugin with three skills: `build-do-not-contact` (interview the student about who must never be contacted and advise on groups they missed, stop if their CRM already holds it all, ask where each group lives and where new ones will show up, pick Google Sheet or Notion, collect from those places only, approve, pointer, weekly schedule), `update-do-not-contact` (quick add, unattended scheduled run, review, settings) and `check-do-not-contact` (split a lead list into keep and drop, export a sending tool blocklist). One agent, `dnc-collector`, reads one source and returns rows in the list's columns, never message text.

- Its references and script live in `shared/do-not-contact/` and `scripts/sync-shared.sh` copies them into all three skills. Edit `shared/do-not-contact/` only.
- `dnc.py` is standard-library Python: `clean`, `normalize`, `merge`, `keys`, `check`, `blocklist`. It owns key cleaning (lowercase emails, `linkedin.com/in/<slug>`, old `/pub/` links with their full path, bare domains, no company blocks on personal email providers) and the `Until` expiry, so skills never compare keys by hand. When matching, `+tags` are ignored, and dots too for Gmail. A company block covers its subdomains. It reads CSV (comma, semicolon or tab) and the JSON the Sheets and Notion connectors return.
- The reason strength order lives in `dnc.py` `REASONS` (`dnc-collector` rule 5 repeats it). `merge` adds a row that's new, has a stronger reason, or brings a key not yet listed. `check` adds a `DNC check` column to `keep.csv` (blank, or `unchecked: <why>`).
- The list is found through a pointer block in `~/.claude/CLAUDE.md` between `do-not-contact:start` and `do-not-contact:end`. The GTM Hub or `gtm/README.md` may hold its link, never its rows.
- It keeps emails and LinkedIn URLs on purpose (the only other place is the customer database, when the student chose to keep contacts). No names or message text. Said no, unsubscribed, bounced and erasure request rows are never deleted automatically. The scheduled run only adds rows, fills `To review` (including "remove" proposals from the CRM's CHANGES, never applied on their own), updates Last run and sends one summary to the student. A cloud run can't read local exports or use Chrome, so those sources become reminders.
- The student leads: Claude suggests groups and usual places (`sources.md`), but reads only the places the student names and never adds a group they didn't confirm. The source plan (`Source | Groups | How we read it | Who | Last run`, plus a Business line) records which groups each source holds, and the scheduled run collects only those.
- When the student's CRM already holds every group they picked, the CRM is the list: the build gives tips, offers a CRM pointer block (`storage.md`) and builds nothing. The check and update skills read that pointer and work against the CRM.
- LinkedIn is paste only: never read the LinkedIn inbox with automation.
