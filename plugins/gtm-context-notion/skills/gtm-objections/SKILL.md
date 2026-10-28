---
name: gtm-objections
description: "Build or update the Objections bank database in your Notion GTM Hub: every reason people hesitate or say no, grouped by theme, with their exact words, how often it comes up, and the answer that works. Merges an existing list you paste with objections mined from your calls, emails and DMs, and dedupes against what's already in the bank. Use for \"build my objections list\", \"what objections do I get\", \"update the objection bank\", \"how should I answer X\", \"refresh objections from my recent calls\", or as part of build-gtm-context. Not for handling a live objection in one specific deal."
metadata:
  version: "0.1.0"
---

# Objections bank

Objections are the most useful context for outreach and follow-ups, and the most perishable: new ones appear every few weeks. That's why they live in a database that agents query by theme, not on a page they read whole.

## Reference files

- `references/mining-playbook.md`: what counts as an objection, the themes, and the privacy rules.
- `references/source-map.md`: where objections usually live and how to get in (connector, browser, export, paste).

## Before starting

1. Fetch the GTM Hub page: its link is in the "GTM context" block of Claude's memory. Its links table and "For agents" section hold every link you need. If no Hub link is known, run the build-gtm-context skill first, which sets up the Hub.
2. Fetch the Objections bank by its link once, to read its columns and Theme options. Don't read its rows.

## Steps

### 1. Collect

Gather objections from up to three places:

1. **Handed over by gtm-messaging** (inside build-gtm-context): use that table as is.
2. **What already exists** (inside build-gtm-context this was found in its step 1): ask "Where do objections already show up? An objections doc or database, an FAQ page, refund or cancellation reasons in your platform, your support inbox?" Read each source using the access order in `references/source-map.md`. A platform without a connector (for example refund reasons in a course or payment dashboard) can be browsed read-only with Claude in Chrome, or exported.
   - A pasted list or file: read it and map each item to a theme.
   - A Notion database: recommend linking it as the bank instead of copying it (see "Reuse before you create" in build-gtm-context's `hub-structure.md`). Write new rows into it using its own columns and theme names, and move the empty Hub bank to Trash only with the user's OK.
3. **Fresh mining** (when this skill runs on its own and nothing was handed over): offer to start one `language-miner` agent per connected source, in parallel, with the brief "extract: objections". Window: since the bank's latest Last seen date, or 90 days if the bank is empty. Pasted transcripts or emails work too.

If the user has no list and no sources, ask them to name the 3 things prospects say most often before not buying, and record them with Source `pasted`.

### 2. Normalise

- One row per distinct objection, in plain words ("Too expensive for a team our size"), with the best verbatim quote.
- Assign one theme from the bank's Theme options.
- **Our answer:** if a thread shows an answer that moved the deal forward, use it and set Answer status `works`. Otherwise draft one in the user's voice and set `draft`.

### 3. Dedupe against the bank

Run one filtered query: Theme is any of the themes in this batch (and, if the bank is shared across offers, Products contains this offer). Select only the title, theme, reference and outcome columns. Compare the results with the new rows by meaning, not exact wording:
- **Same objection:** update the existing row: add to Times seen and set Last seen (if the bank has those columns), keep the clearer quote, and keep an answer marked `works` unless the new evidence is better. A linked log without a count column: skip the duplicate and say how many you skipped.
- **New objection:** create a row.

Never run one query per objection. One query per batch keeps it fast.

### 4. Pause: show the changes

Show two short tables: "New" and "Updated". Then ask the user to review every answer marked `draft`, because these are the lines they will actually use. Apply edits. Don't write on silence.

### 5. Write

Create and update the rows. Update the Objections row in the Hub links table: one-line summary ("27 objections, top themes: price, effort, proof") and today's date.

## How other agents should read the bank

Write this note once at the top of the database description, if it's not already there:

> Query by Theme (and Stage if useful). Don't read the whole bank. Prefer answers with status "works".

## Rules

- Verbatim quotes, role and company type only. No names, emails or profile URLs.
- Query with filters, never read the whole bank. Fetch by link, never search Notion.
