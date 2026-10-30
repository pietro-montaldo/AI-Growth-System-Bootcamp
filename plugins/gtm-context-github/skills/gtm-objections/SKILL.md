---
name: gtm-objections
description: "Build or update the objections bank for your GTM context in your repo (gtm/objections.csv, or the objections log you already keep elsewhere): every reason people hesitate or say no, grouped by theme, with their exact words, how often it comes up, and the answer that works. Merges what already exists with objections mined from your calls, webinars, emails and DMs, and dedupes against the bank. Use for \"build my objections list\", \"what objections do I get\", \"update the objection bank\", \"how should I answer X\", \"refresh objections from my recent calls\", or as part of build-gtm-context. Not for handling a live objection in one specific deal."
metadata:
  version: "0.3.0"
---

# Objections bank

Objections are the most useful context for outreach and follow-ups, and the most perishable: new ones appear every few weeks. That's why they live in a bank that agents query by theme, not on a page they read whole.

## Reference files

- `references/mining-playbook.md`: what counts as an objection, the themes, and the privacy rules.
- `references/source-map.md`: where objections usually live and how to get in (connector, browser, export, paste).
- `references/repo-structure.md`: the columns of `gtm/objections.csv`, the themes, and how the helper script writes them.
- `scripts/gtm_csv.py`: query and update `gtm/objections.csv`. Call it by its full path in this skill's folder.

## Before starting

1. Read `~/gtm-context/gtm/README.md`. Every `gtm/` path in this skill is inside `~/gtm-context/`, the student's private gtm-context repo, whatever project they are in. If it's missing, run the build-gtm-context skill first, which sets up the folder.
2. Check the "Sources" list: if objections already live in a connected log (a Notion or Airtable database, a Google Sheet), that log is the bank. Write new rows there, using its own columns and theme names, and don't create `gtm/objections.csv`.
3. **On its own** (not inside build-gtm-context): when you find this section's sources, also settle where new objections will come from and who brings it in (`auto`, `auto, app only`, `you`, `none`), as in "Where each item comes from, now and later" in `references/source-map.md`. Prefer an automatic route. Update its line in the Sources list in `gtm/README.md` after the user's OK.

## Steps

### 1. Collect

Gather objections from up to three places:

1. **Handed over by gtm-messaging** (inside build-gtm-context): use that table as is.
2. **What already exists** (inside build-gtm-context this was found in its step 1): ask "Where do objections already show up? An objections doc or log, an FAQ page, refund or cancellation reasons in your platform, your support inbox?" Read each source using the access order in `references/source-map.md`. A platform without a connector (for example refund reasons in a course or payment dashboard) can be browsed read-only with Claude in Chrome, or exported into `gtm/.private/`.
   - A pasted list or file: read it and map each item to a theme.
   - A connected log: recommend using it as the bank instead of copying it.
3. **Fresh mining** (when this skill runs on its own and nothing was handed over): offer to start one `language-miner` agent per connected source, in parallel, with the brief "extract: objections". Window: since the bank's latest Last seen date, or 90 days if the bank is empty. Pasted transcripts or emails work too.

If the user has no list and no sources, ask them to name the 3 things prospects say most often before not buying, and record them with Source `pasted`.

### 2. Normalise

- One row per distinct objection, in plain words ("Too expensive for a team our size"), with the best verbatim quote.
- Assign one theme from the bank's themes (the list in `references/repo-structure.md`, or the user's own), and the Offer it's about (offers in scope).
- **Our answer:** if a thread shows an answer that moved the deal forward, use it and set Answer status `works`. Otherwise draft one in the user's voice and set `draft`.

### 3. Dedupe against the bank

If `gtm/objections.csv` doesn't exist yet, create it with `init` and the columns from `references/repo-structure.md`.

Run one query for the themes in this batch: `query gtm/objections.csv --any "Theme=price|effort|..." --cols "Objection,Theme,Offer,Times seen,Answer status"`. Compare the results with the new rows by meaning, not exact wording, within the same offer. The same objection about another offer is its own row, with its own count:
- **Same objection, same offer:** reuse the existing Objection text and Offer, so the upsert finds the row. Add to Times seen, set Last seen, keep the clearer quote, and keep an answer marked `works` unless the new evidence is better.
- **New objection:** a new row.

Never run one query per objection. One query per batch keeps it fast.

### 4. Pause: show the changes

Show two short tables: "New" and "Updated". Then ask the user to review every answer marked `draft`, because these are the lines they will actually use. Apply edits. Don't write on silence.

### 5. Write

Put the rows in a JSON file in `gtm/.private/` and write them with one `upsert --key "Objection,Offer"`. Delete the JSON file afterwards. Update the Objections row in the `gtm/README.md` table: one-line summary ("27 objections, top themes: price, effort, proof") and today's date.

## How other agents should read the bank

The `gtm/README.md` table already says it, so later agents query the bank by Theme (and Stage if useful), never read it whole, and prefer answers with status `works`.

## Rules

- Verbatim quotes, role and company type only. No names, emails or profile URLs.
- Query with filters, never read the whole bank. Write only with `upsert`.
