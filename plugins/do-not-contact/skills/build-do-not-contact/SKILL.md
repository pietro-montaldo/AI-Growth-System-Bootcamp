---
name: build-do-not-contact
description: "Build your do-not-contact list with you, starting from your own description of who your outreach must never reach. It interviews you about those people (people who said no, customers, open deals, testimonial givers, friends, family, partners and others) and advises you, then reads only the places you point it to, and saves the list in a Google Sheet or a Notion database, your choice. If your CRM already holds all of this, it tells you a second list isn't needed and stops. Otherwise it tells every later system to check the list before contacting anyone, and schedules a weekly update from the sources you named. Use for \"build my do-not-contact list\", \"set up a suppression list\", \"make sure I never message people who said no\", \"stop double-texting people\", \"who shouldn't I contact\", or the first time you use this plugin. Not for adding one person (use update-do-not-contact) or checking a lead list (use check-do-not-contact)."
metadata:
  version: "1.3.0"
---

# Build your do-not-contact list

One list that every outreach system checks before it contacts anyone. The student decides who goes on it. This guide interviews them, advises, reads only the places they point to, saves the list in a Google Sheet or Notion, and keeps it growing every week from those same places.

## Reference files

- `references/sources.md`: the interview, the groups people usually keep off-limits and where they tend to be, the CRM check, how to get into each source, and what counts as a no.
- `references/storage.md`: Google Sheet or Notion, with the pros and cons table, the columns, the tabs or databases, the tools, and the pointer block.
- `references/rules.md`: matching, what is never deleted, approvals, privacy, and sending tools.
- `scripts/dnc.py`: cleans keys, merges new rows without duplicates, checks lead lists and writes blocklists. Run it with `python3` by its full path in this skill's folder. `--help` lists the commands.

Temporary files go in `~/do-not-contact/.private/` (create it). Delete them at the end.

## Start

Explain in three lines:
- What they'll end up with: one list every system checks first, so nobody they want to protect hears from them by mistake.
- How it works: "Tell me who you never want your outreach to reach. I'll help you think it through, you tell me where those people are, and I'll build the list from there." About 15 minutes of their time.
- Nothing is ever sent. The list keeps emails, profile links and domains only, never names or messages.

## Step 0. Check what exists

- Look for a `do-not-contact:start` block in `~/.claude/CLAUDE.md`.
- If it says the CRM is the list, say so. Offer to run the interview again (things may have changed), or stop.
- If it links a list, the list exists. Say so and offer:
  - collect again from the same sources (steps 5 and 6 only; the list, pointer and schedule already exist, the source plan holds the groups and B2B or B2C, and the merge skips what's listed);
  - change the sources or the schedule (use update-do-not-contact, settings);
  - stop.
- If they use the GTM context kit (a `gtm-context:start` block), read its "Sources" quietly. Use it only to make better suggestions in steps 1 and 2. The student still decides.

## Step 1. The interview: who must never hear from you

Follow "The interview" in `sources.md`. In short:
1. Ask the open question first and let them answer in their own words: "Who should your outreach never reach?"
2. Play their answer back as groups, then suggest the groups they didn't mention from "Groups people usually keep off-limits", as advice, one line each on why. They pick. Never add a group they didn't confirm.
3. Ask "B2B or B2C?" only if it isn't obvious.

**The CRM check.** Then ask about the groups they picked, by name: "Do you already keep all of these in a CRM?"
- **Yes, all of it:** the CRM already is their do-not-contact list, so a second list would only drift out of date. Say so plainly, give the tips in `sources.md` ("When the CRM is the list"), offer the CRM pointer after one OK, and stop here. Build nothing else.
- **Partly, or no:** carry on. A CRM that holds some groups becomes one of the sources.

## Step 2. Where each group lives

The student guides, Claude advises (`sources.md`, "Where each group lives"):
- For each group they picked, ask where those people are today. Offer the usual places as suggestions ("customers are often in your payment platform"), but read only what the student names.
- For each place, also ask where new people of that group will show up from now on. This becomes the weekly update plan: `auto`, `auto (app only)`, `you` or `you (when it happens)` (`sources.md`, "Will each source stay current?").
- Settle access per place, in the order in `sources.md`: connector, browser (read-only), export, paste.
- Groups that live only in their head (friends, family, some partners) are typed or pasted now, as emails or profile links, never names. They're `you (when it happens)`: no weekly reminder. LinkedIn is paste only.

Show the plan as one short table (source, groups, how we read it, who keeps it current) and get an OK before moving on.

## Step 3. Pick where it lives

Show the pros and cons table from `storage.md` and recommend, following its rules: Google Sheet for most students, Notion when their CRM is in Notion and they don't send from an email tool. Ask with AskUserQuestion.

Then check the connector: Google Sheets (and Drive) for a Sheet, Notion for Notion. If it's missing, say so and say where to turn it on. For a Sheet, offer the no-connector path in `storage.md` as a fallback.

## Step 4. Create the list

Follow `storage.md`:
- **Sheet:** create it with three tabs (`Do not contact`, `To review`, `Read me`) and the header rows.
- **Notion:** the `Do not contact` page with the two databases. Ask for the parent page, or use the GTM Hub if they have one.

Fill the `Business` line and the source plan (`Source | Groups | How we read it | Who | Last run`) from the plan the student approved in step 2. Last run stays empty until step 6.

## Step 5. Collect

- Start one `dnc-collector` agent per place the student named, in parallel. Each brief holds:
  - the source and how to get in;
  - the window (last 12 months for the inbox, all records for the CRM and platforms);
  - B2B or B2C;
  - which records to read, for the groups the student picked only.
- Run browser sources in the main conversation, one page at a time, since the browser is shared.
- Save the ROWS from every agent into one file, `~/do-not-contact/.private/new.csv`. Keep the UNSURE lists for step 6.
- Add rows for anything the student typed or pasted (friends, family, partners, competitors, LinkedIn links), with Source manual or LinkedIn.

## Step 6. Show and approve

Run:

```bash
python3 <skill folder>/scripts/dnc.py merge ~/do-not-contact/.private/new.csv [--existing ~/do-not-contact/.private/existing.csv] -o ~/do-not-contact/.private/add.csv
```

- `--existing` is only for a list that already has rows. Read its key columns first and pass the saved result (`storage.md`).
- The script cleans every key, drops duplicates and skips rows it can't use, with the reason. It still adds a row for a listed person when the reason is stronger or the row brings a new email or profile link.

Show:
- counts by reason and by source;
- five sample rows;
- anything the script skipped.

Then go through the unsure list with AskUserQuestion, up to 4 per question, each one "add" or "leave out". Add the yes's as rows to `new.csv` and run the merge again, so they're cleaned and deduped too. Show the new counts.

Ask once: "Save these <n> rows to your list?" On yes, write `add.csv` with the tools in `storage.md`, then confirm the new row count. Set Last run to today for every source read in step 5, and for every row that only starts with the weekly run.

## Step 7. Tell every system about it

- Show the pointer block from `storage.md` and write it into `~/.claude/CLAUDE.md` after one OK.
- If they have a GTM Hub or `gtm/README.md`, offer to add the one-line link there too.

## Step 8. Keep it growing

The update reads the same places the student named in step 2, following the plan they approved. Recommend a weekly update (Monday 08:00). Say in two lines each:
- **A scheduled task in the Claude app** (recommended): runs on their computer while the app is open, can use Claude in Chrome and read exports in `~/do-not-contact/.private/`. Create it with `create_scheduled_task`: taskId `do-not-contact-update`, cron `0 8 * * 1`, description "Weekly do-not-contact update", and the prompt below.
- **A cloud scheduled task:** runs even when the computer is off, connectors only. It can't use Claude in Chrome or read files on their computer, so "auto (app only)" and export sources become reminders in the summary. It needs this course marketplace added in Claude under Customize > Plugins, because cloud runs don't load plugins installed with `/plugin`. Create it with the `/schedule` skill.

Ask where to send the weekly summary: their own email or a Slack DM to themself. The prompt, for either kind:

```
Scheduled run of the do-not-contact update. Use the update-do-not-contact skill (do-not-contact plugin) in "scheduled run" mode.
List: <link> (<Google Sheet | Notion>). Business: <B2B | B2C>.
Send the summary to: <their email or "my Slack DM">. Send nothing to anyone else.
```

Create it only after they confirm the timing.

An unattended run can stall on a permission prompt the first time it writes to the Sheet or Notion, or sends the summary. So offer to run it once now, while they watch, and have them pick "always allow" for those tools. Or they add the tools to the allow list in their settings.

Last, if they send email from a sending tool: suggest switching on its global blocklist, and offer a first blocklist file now (check-do-not-contact, blocklist).

## Wrap up

- Delete the files in `~/do-not-contact/.private/`.
- Tell them in four lines:
  - where the list is and how many rows it has;
  - when it updates;
  - "Say 'add <email or profile link>, said no' any time someone says no on LinkedIn or a call";
  - "Before any campaign, say 'check this list against my do-not-contact list'".
