---
name: build-do-not-contact
description: "Build your do-not-contact list with you: everyone your outreach must skip. It finds them where they already are (email replies that said no or unsubscribe, bounces, your CRM's customers and open deals, your sending tool's unsubscribes, your course or payment platform's buyers) and saves them in a Google Sheet or a Notion database, your choice. Then it tells every later system to check the list before contacting anyone, and schedules a weekly update. Use for \"build my do-not-contact list\", \"set up a suppression list\", \"make sure I never message people who said no\", \"stop double-texting people\", \"who shouldn't I contact\", or the first time you use this plugin. Not for adding one person (use update-do-not-contact) or checking a lead list (use check-do-not-contact)."
metadata:
  version: "1.0.0"
---

# Build your do-not-contact list

One list that every outreach system checks before it contacts anyone. It holds people who said no, unsubscribed or bounced, plus customers, open deals and anyone the student keeps off-limits. This guide finds them where they already are, saves them in a Google Sheet or Notion, and keeps the list growing every week.

## Reference files

- `references/storage.md`: Google Sheet or Notion, with the pros and cons table, the columns, the tabs or databases, the tools, and the pointer block.
- `references/sources.md`: who belongs on the list, where they usually are, how to get into each source, and what counts as a no.
- `references/rules.md`: matching, what is never deleted, approvals, privacy, and sending tools.
- `scripts/dnc.py`: cleans keys, merges new rows without duplicates, checks lead lists and writes blocklists. Run it with `python3` by its full path in this skill's folder. `--help` lists the commands.

Temporary files go in `~/do-not-contact/.private/` (create it). Delete them at the end.

## Start

Explain in three lines:
- What they'll end up with: one list every system checks first, so nobody who said no hears from them again, and no customer gets a cold pitch.
- How it works: "Tell me where your replies, customers and unsubscribes live. I'll read them, show you who I found, and save the list after your OK." About 15 minutes of their time.
- Nothing is ever sent. The list keeps emails and profile links only, never names or messages.

## Step 0. Check what exists

- Look for a `do-not-contact:start` block in `~/.claude/CLAUDE.md`. If it's there, the list exists. Say so and offer:
  - collect again from all sources (go to step 2, then 5 onwards; the merge skips what's listed);
  - change the sources or the schedule (use update-do-not-contact, settings);
  - stop.
- If they use the GTM context kit (a `gtm-context:start` block), read its "Sources". The CRM, inbox and platforms are already known.

## Step 1. Pick where it lives

Show the pros and cons table from `storage.md` and recommend, following its rules: Google Sheet for most students, Notion when their CRM is in Notion and they don't send from an email tool. Ask with AskUserQuestion.

Then check the connector: Google Sheets (and Drive) for a Sheet, Notion for Notion. If it's missing, say so and say where to turn it on. For a Sheet, offer the no-connector path in `storage.md` as a fallback.

## Step 2. Map the sources

- Show the "What to collect" table from `sources.md`. Ask for each row in one message: a tool, a link, or "none". Ask "B2B or B2C?" only if it isn't obvious.
- Then settle access per source, using the order in `sources.md`: connector, browser (read-only), export, paste.
- LinkedIn is paste only. Ask them to paste the profile links of people who said no there, if they remember any.

## Step 3. Create the list

Follow `storage.md`:
- **Sheet:** create it with three tabs (`Do not contact`, `To review`, `Read me`) and the header rows.
- **Notion:** the `Do not contact` page with the two databases. Ask for the parent page, or use the GTM Hub if they have one.

Fill the source plan (`Source | How we read it | Who | Last run`) from step 2. Leave Last run empty for now.

## Step 4. Collect

- Start one `dnc-collector` agent per source, in parallel. Each brief holds:
  - the source and how to get in;
  - the window (last 12 months for the inbox, all records for the CRM and platforms);
  - B2B or B2C;
  - which records to read.
- Run browser sources in the main conversation, one page at a time, since the browser is shared.
- Save the ROWS from every agent into one file, `~/do-not-contact/.private/new.csv`. Keep the UNSURE lists for step 5.
- Add rows for anything the student typed or pasted (partners, competitors, friends, LinkedIn links), with Source manual or LinkedIn.

## Step 5. Show and approve

Run:

```bash
python3 <skill folder>/scripts/dnc.py merge ~/do-not-contact/.private/new.csv [--existing ~/do-not-contact/.private/existing.csv] -o ~/do-not-contact/.private/add.csv
```

- `--existing` is only for a list that already has rows. Export its key columns first (`storage.md`).
- The script cleans every key, drops duplicates and skips rows it can't use, with the reason.

Show:
- counts by reason and by source;
- five sample rows;
- anything the script skipped.

Then go through the unsure list with AskUserQuestion, up to 4 per question, each one "add" or "leave out". Add the yes's as rows.

Ask once: "Save these <n> rows to your list?" On yes, write `add.csv` with the tools in `storage.md`, then confirm the new row count.

## Step 6. Tell every system about it

- Show the pointer block from `storage.md` and write it into `~/.claude/CLAUDE.md` after one OK.
- If they have a GTM Hub or `gtm/README.md`, offer to add the one-line link there too.

## Step 7. Keep it growing

Recommend a weekly update (Monday 08:00). Say in two lines each:
- **A scheduled task in the Claude app** (recommended): runs on their computer while the app is open, can use Claude in Chrome. Create it with `create_scheduled_task`, taskId `do-not-contact-update`, cron `0 8 * * 1`.
- **A cloud scheduled task:** runs even when the computer is off, connectors only. It needs this course marketplace added in Claude under Customize > Plugins, because cloud runs don't load plugins installed with `/plugin`. Create it with the `/schedule` skill.

Ask where to send the weekly summary: their own email or a Slack DM to themself. The prompt, for either kind:

```
Scheduled run of the do-not-contact update. Use the update-do-not-contact skill (do-not-contact plugin) in "scheduled run" mode.
List: <link> (<Google Sheet | Notion>). Business: <B2B | B2C>.
Send the summary to: <their email or "my Slack DM">. Send nothing to anyone else.
```

Create it only after they confirm the timing. Offer to run it once now.

Last, if they send email from a sending tool: suggest switching on its global blocklist, and offer a first blocklist file now (check-do-not-contact, blocklist).

## Wrap up

- Delete the files in `~/do-not-contact/.private/`.
- Tell them in four lines:
  - where the list is and how many rows it has;
  - when it updates;
  - "Say 'add <email or profile link>, said no' any time someone says no on LinkedIn or a call";
  - "Before any campaign, say 'check this list against my do-not-contact list'".
