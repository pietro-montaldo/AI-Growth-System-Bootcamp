# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

The public repo for students of the AI Growth Systems Bootcamp (https://maven.com/pietro-montaldo/ai-growth-system-bootcamp-claude). It's a Claude Code plugin marketplace named `ai-growth-system-bootcamp` (`.claude-plugin/marketplace.json`, `plugins/`, `shared/`, `scripts/`). A skill only shows up for students once it's inside a plugin listed in `marketplace.json`. Today it ships two things:

- `plugins/voice-miner`: a standalone plugin with one skill. See "voice-miner" below.
- The GTM context kit, which helps students build a go-to-market context layer: product, ICP, competitors, customer language, objections, shareable customers. Later course systems (outbound and inbound agents) read that context first.

The GTM context kit has two plugins with the same skill and agent names. Only the storage steps differ:

- `plugins/gtm-context-notion`: context lives in Notion under one GTM Hub page. The student's project holds only `gtm-hub.md`, a list of links and data source IDs.
- `plugins/gtm-context-github`: context lives as markdown pages and CSV banks in a `gtm/` folder of the student's own (private) repo.

The skills are content, not code: SKILL.md files, agent files and reference markdown. There is no build step and no test suite.

## Commands

```bash
scripts/sync-shared.sh            # copy shared/ into the plugins (references, agents, scripts)
scripts/sync-shared.sh --check    # fail if a copy is out of date
claude plugin validate .          # validate the marketplace manifest
claude plugin validate plugins/gtm-context-notion
claude plugin validate plugins/gtm-context-github
python3 shared/scripts/gtm_csv.py --help   # the CSV helper the GitHub plugin ships
```

To try a plugin locally: `/plugin marketplace add ./` then `/plugin install gtm-context-notion@ai-growth-system-bootcamp` (or `gtm-context-github@ai-growth-system-bootcamp`).

The README is the student-facing page for everything in the repo: one row per skill or plugin in the table at the top, then one section each. Keep that shape when adding something.

## Structure that spans files

- `shared/` is the single source for everything both plugins need. Installed plugins can't read outside their own folder, so `scripts/sync-shared.sh` copies it in, using the maps at the top of the script. Edit `shared/` only, never the copies, then run the script.
  - `shared/references/` (`sections.md`, `icp-checks.md`, `mining-playbook.md`, `source-map.md`) go into each skill's `references/`.
  - `shared/agents/` go into each plugin's `agents/`. The agents are storage-agnostic, so both plugins share them.
  - `shared/scripts/gtm_csv.py` goes into the GitHub plugin's skills that touch a CSV bank (`scripts/`). It is standard-library Python: `init`, `query`, `count`, `upsert`. Skills call it by full path from the skill folder.
- `build-gtm-context` is the guide. It works in three moves: map where the user's GTM information already lives (`source-map.md`), read it all, then run the six section skills (`gtm-product`, `gtm-customers`, `gtm-competitors`, `gtm-icp`, `gtm-messaging`, `gtm-objections`). Each section drafts from what was found and asks only about gaps. Each section skill also works on its own, and then asks where its bucket lives first.
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

- Notion: one GTM Hub page links to everything; skills fetch pages by the links in `gtm-hub.md` and never search for them; banks (objections, competitors, customers) are queried with filters, never read whole; dedupe with one filtered query per batch; no copies of context in the repo.
- GitHub: `gtm/README.md` links to everything; CSV banks are queried and written only through `gtm_csv.py`, never read whole; check the repo isn't public before writing data; raw exports stay in gitignored `gtm/.private/`; never commit or push without asking. Data that already lives in a connected system is linked under "Sources", not copied into CSV.
- Pages stay one or two screens with a summary at the top.
- Every write has an approval pause. Nothing is ever sent, posted or connected.
- No personal names, emails or LinkedIn URLs in context: role and company type only. Customer logos are marked shareable only with explicit permission.
- Every mining step has a paste-it-in fallback, because many students can't connect email or a call recorder.

## Writing style

Students are non-technical (founders, consultants, operators). Write in plain language with short sentences. No em dashes or double dashes. Frontmatter `description` is one quoted string: what the skill does, quoted trigger phrases, then "Not for X". Keep SKILL.md under about 150 lines and push detail into `references/`.

## voice-miner

`plugins/voice-miner` is its own plugin in the marketplace, separate from the GTM context plugins. It doesn't use `shared/` or `sync-shared.sh`. Its script (`scripts/voice_mine.py`) is standard-library Python. Students' raw mailbox and transcript data go in a `voice-mining/` working folder, which is gitignored.
