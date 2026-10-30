---
name: update-do-not-contact
description: "Keep your do-not-contact list current. Adds one person or company in seconds (\"add jane@acme.com, said no\"), runs the weekly update that finds new no's, unsubscribes, bounces, customers and open deals since the last run, and walks you through anything that needs a decision. Works with the Google Sheet or Notion list made by build-do-not-contact. Use for \"add <email or LinkedIn link> to do not contact\", \"they said no\", \"don't contact them again\", \"update my do-not-contact list\", \"review do-not-contact\", \"change my do-not-contact sources\", or when the scheduled run starts. Not for building the list the first time (use build-do-not-contact) or checking a lead list (use check-do-not-contact)."
metadata:
  version: "1.2.0"
---

# Update your do-not-contact list

## Reference files

- `references/storage.md`: the columns, tabs or databases, tools and pointer.
- `references/sources.md`: the groups on the list and where they are, how to get in, what counts as a no.
- `references/rules.md`: matching, what is never deleted, what a scheduled run may do.
- `scripts/dnc.py`: run with `python3` by its full path in this skill's folder.

Temporary files go in `~/do-not-contact/.private/`. Delete them at the end of every run.

## Find the list

- Read the link from the `do-not-contact:start` block in `~/.claude/CLAUDE.md`, or from the scheduled prompt. Never search for it.
- No block and no link: say the list isn't set up yet and offer build-do-not-contact.
- The block says the CRM is the list: there's no separate list to update. For a quick add, offer to mark the person in the CRM with the status named in the block, after one OK, if the CRM connector can write. Otherwise tell them where to mark it. Stop there.
- Then read the source plan: the `Read me` tab (Sheet) or the `Sources` table on the page (Notion).

Pick the mode from how you were called.

## Mode 1: quick add

The student names a person or company: "add jane@acme.com, said no", "never contact anyone at acme.com, they're a partner", or a LinkedIn link.

1. `dnc.py clean <value>` gives the key. Work out the reason from their words (`storage.md` lists them; "friend" or "family" is personal, "investor" is partner), and the scope: company if they said "anyone at", otherwise person. If the reason is unclear, use "said no".
2. Put the row in `new.csv`. Source is one of the values in `storage.md`: a payment or course platform is "course platform", a sending tool is "sequencer", a call or anything else is "manual". Read the key columns (Sheet) or query that key (Notion) into `existing.csv`, and run `dnc.py merge new.csv --existing existing.csv -o add.csv`. Never compare by hand.
3. `add.csv` empty: say it's already listed, in one line, with its reason. Otherwise write the row and confirm in one line. A stronger reason is added as a new row, for example "unsubscribed" for someone listed as "not now". The old row stays.

Several at once (a pasted list): put them in a CSV, run `dnc.py merge` with the key columns as `--existing`, show the counts, and write after one OK.

## Mode 2: scheduled run (unattended)

Never ask anything. One failed source never stops the run: note it and go on.

1. For each source in the plan, the window runs from its Last run date to today. If there's no date, use the last 30 days.
2. **auto sources:** start one `dnc-collector` agent per source, in parallel, with the window, B2B or B2C (the plan's Business line), and that source's Groups from the plan. The agent returns rows for those groups only. Never add a group the plan doesn't list for that source.
   - **CRM with customers or open deals in its Groups:** also ask for CHANGES: customers who churned and deals closed lost for any reason. A won deal comes back as a new customer row, and the merge adds it.
3. **auto (app only) sources:** read them only if Claude in Chrome is connected. Otherwise note "skipped, needs the app".
4. **you sources:** if a new export is in `~/do-not-contact/.private/`, read it. If not, add a reminder to the summary. **you (when it happens)** sources: skip, no reminder.
5. **Merge.** Save all ROWS to `new.csv` and all CHANGES to `changes.csv`. Read the list's key columns (Sheet) or query the keys of both files (Notion) into `existing.csv`. Then run:
   - `dnc.py merge new.csv --existing existing.csv -o add.csv`;
   - `dnc.py check changes.csv --list existing.csv --out-dir <private folder>/changes`. Its `drop.csv` holds the changes that concern rows already on the list.
6. **Write:**
   - every row of `add.csv` to the list;
   - every UNSURE item to `To review`, with Proposed "add";
   - every row of `changes/drop.csv` to `To review`, with Proposed "remove", the listed reason, and the change as why. For example "customer churned 2026-10". Changes are never applied in a scheduled run: don't change or delete the row itself (`rules.md`).
7. Update Last run for each source that was read.
8. **Send the summary** to the address in the prompt, and only there:

   ```
   Do-not-contact update, <date>
   Added: <n> (<n> said no, <n> unsubscribed, <n> bounced, <n> customers, <n> open deals ...)
   To review: <n>. Say "review do-not-contact" to go through them.
   Couldn't read: <sources and why, or "none">
   Skipped rows: <n, with the reasons from the merge, or "none">
   Reminder: <any "you" source that is due, or nothing>
   List: <link>
   ```

## Mode 3: review

"Review do-not-contact" or "check what's waiting".

1. Read the `To review` tab or database.
2. Go through it with AskUserQuestion, up to 4 items per question.
   - Show each item's key, reason, why it's there and what's proposed.
   - "add" items: add to the list, or leave out.
   - "remove" items: remove from the list, keep, or change the reason. For example, a lost deal can stay as "said no".
3. Apply each answer right away, then clear the answered rows from `To review`.
4. Never remove a said no, unsubscribed, bounced or erasure request row in review either, unless the student says that exact row was added by mistake.

## Mode 4: change settings

"Add a source", "change where the summary goes", "change the schedule".
- **Sources:** ask which group the new place holds and where new people of that group will show up (`sources.md`, "Where each group lives"), then update the plan table. For a new source, offer a first collection from it now (mode 2 steps for that source only, then show and approve as in build-do-not-contact step 6).
- **Schedule or summary address:** update the scheduled task (`update_scheduled_task`, or the `/schedule` skill for a cloud task), after one OK.
- **Moving between Sheet and Notion:**
  - say what will happen (new home, row count, pointer and scheduled prompt changed) and ask once. Do nothing before a yes;
  - create the new home (`storage.md`);
  - copy all rows over, then compare the row counts;
  - show the new pointer block and prompt, and write them after one OK;
  - leave the old list in place until the student deletes it themselves.

## Wrap up

Delete the files in `~/do-not-contact/.private/` (but never a fresh export the run didn't read). In interactive modes, confirm in one or two lines what changed.
