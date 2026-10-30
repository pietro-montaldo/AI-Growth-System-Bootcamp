---
name: check-do-not-contact
description: "Check a lead list against your do-not-contact list before any outreach. Takes a CSV, an export, pasted rows or a Notion view, matches people by email or LinkedIn link and companies by domain, and gives back two files: who to keep and who to drop, with the reason. Also makes a blocklist file to upload to an email sending tool. Every other outreach system runs this before it contacts anyone. Use for \"check this list against do not contact\", \"remove people who said no\", \"clean this lead list before I send\", \"is it safe to contact these people\", \"make a blocklist for my sending tool\", or before any campaign. Not for adding people to the list (use update-do-not-contact) or building it (use build-do-not-contact)."
metadata:
  version: "1.0.0"
---

# Check a lead list against your do-not-contact list

Run this before every send, so the rule lives in one place. Other skills and agents call it with a lead list and use only the keep file.

## Reference files

- `references/storage.md`: how to read only the key columns of the Sheet, or query Notion by keys.
- `references/rules.md`: how matching works and what to say about leads that can't be checked.
- `scripts/dnc.py`: run with `python3` by its full path in this skill's folder.

Temporary files go in `~/do-not-contact/.private/`. Delete them at the end, except the keep and drop files the student asked for.

## Find the list

- Read the link from the `do-not-contact:start` block in `~/.claude/CLAUDE.md`. Never search for it.
- No block: say the list isn't set up yet, and offer build-do-not-contact. Don't send to an unchecked list without saying so.

## Check a lead list

1. **Get the leads into a CSV** in `~/do-not-contact/.private/leads.csv`:
   - a file: copy it there;
   - pasted rows: write them there;
   - a Notion view or Sheet tab: read only the email, LinkedIn and website columns.
2. **See which columns hold the keys:** `dnc.py keys leads.csv`. It guesses the email, LinkedIn and website columns and prints the cleaned keys. If a guess is wrong, rerun with `--email-col`, `--linkedin-col` or `--domain-col`.
3. **Get the matching part of the list:**
   - **Sheet:** read the key columns (`'Do not contact'!A:H`) into `list.csv`.
   - **Notion:** one filtered query per batch of up to 100 keys, using the keys from step 2 (`storage.md`), into `list.csv`, with the columns named as in `storage.md`.
4. **Run the check:**

   ```bash
   python3 <skill folder>/scripts/dnc.py check ~/do-not-contact/.private/leads.csv --list ~/do-not-contact/.private/list.csv --out-dir <where the student wants the result>
   ```

   It writes:
   - `keep.csv`: the original rows, unchanged;
   - `drop.csv`: the dropped rows, with `DNC reason` and `DNC match`.
5. **Tell the student in three lines:**
   - how many leads were kept and dropped, with the drops by reason;
   - how many leads had no email, LinkedIn link or website. They couldn't be checked, so they're in keep.csv but flagged. Suggest finding an email or profile link before contacting them;
   - where the files are.

   If `list_rows_with_unreadable_until` is above 0, add one line: that many list rows have an Until date the script can't read, so they still block. Suggest writing those dates as 2027-05-01.

When another skill or agent called this, return the same three lines and the path to `keep.csv`. Then that system works from keep.csv only.

## Make a blocklist for a sending tool

"Make a blocklist" or "export for my sending tool":

1. Read the whole key column range of the Sheet into `list.csv`, or for Notion, query all rows' `Email`, `Company domain`, `Scope`, `Reason` and `Until` columns. Reading every row is fine here, because the file is the point.
2. Run `dnc.py blocklist list.csv -o <folder>/blocklist.csv`. Expired "not now" rows are left out.
3. Tell them:
   - in their sending tool, open the global blocklist (often called blocklist, suppression list or do-not-contact), and import the file;
   - redo this whenever they load a new campaign, or weekly;
   - LinkedIn-only rows can't go in an email blocklist. They're still caught by this check.

## Rules

- Never change the list here. If the student says "they also said no", switch to update-do-not-contact.
- Never print the list's rows in the chat beyond the counts and a few sample drops.
