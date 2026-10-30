# Where the list lives: Google Sheet or Notion

The list has one job: every tool that contacts people checks it first. That includes an enrichment table, a sending tool, and a Claude agent that drafts DMs. So the best home is the one all of the student's tools can read, and where anyone can add a row in ten seconds, even from a phone.

## The choice (show this table, then recommend)

| | Google Sheet | Notion database |
|---|---|---|
| Enrichment and automation tools can look a person up before a send | Yes, most have a native Google Sheets lookup | Some can, many can't |
| Sending tools (email sequencers) | Export a blocklist file and upload it | Same |
| Claude agents can check it | Yes, with the Google Sheets connector | Yes, with a filtered query |
| Add someone from a phone | Easy | Easy |
| Already familiar | Everyone knows a spreadsheet | Familiar if the team lives in Notion |
| Best for | Most students, and anyone who will send email from a tool | Students whose CRM is in Notion and who do outreach through Claude |

How to recommend:
- **Default: Google Sheet.** It's the one format every tool in the chain can read, including tools they'll add later.
- **Recommend Notion** when their customers or deals already live in Notion and they don't plan to send from an email tool. Customers and deals are then one link away.
- **Not offered: a file in a GitHub repo.** Rows change because of events (a reply, an unsubscribe, a bounce). A commit for every change is too much friction, sending tools can't read it, and it would put emails into a repo.

Ask with AskUserQuestion: "Google Sheet (Recommended)" and "Notion", each with one line from the table.

## The columns (same in both homes)

| Column | Sheet | Notion type | Notes |
|---|---|---|---|
| Entry | not used | title | Notion only. The main key, so people can read the row: the email, else the LinkedIn URL, else the domain |
| Email | text | email | lowercase |
| LinkedIn URL | text | url | `linkedin.com/in/<name>` |
| Company domain | text | text | only for company-wide blocks, for example `acme.com` |
| Scope | text | select: person, company | company blocks everyone at that domain |
| Reason | text | select: said no, not now, unsubscribed, bounced, customer, open deal, partner, competitor, personal, erasure request, other | |
| Until | date | date | blank means forever |
| Source | text | select: inbox, CRM, sequencer, course platform, LinkedIn, manual, other | |
| Added | date | date | |
| Note | text | text | a few words, never the text of a message |

`dnc.py` uses exactly these column names (without Entry). When you export rows to check or merge, keep the names.

## Google Sheet

**Layout: three tabs.**
1. `Do not contact`: the list. Header row frozen. One row per person or company.
2. `To review`: the same columns plus `Why unsure` and `Proposed`. `Proposed` is either add or remove. The weekly run puts anything that needs a decision here, never straight into the list.
3. `Read me`, which holds:
   - three lines on what the list is for;
   - the rule "Before contacting anyone, check this list. When someone says no, add them";
   - a small table, `Source | How we read it | Who | Last run`, one row per source. "Who" is auto, auto (app only) or you. The weekly run updates `Last run`.

**Create it:**
- If the Google Drive connector can create a Google Sheet, create one called "Do not contact".
- Otherwise ask the student to open `sheets.new`, name it "Do not contact" and paste the link.
- Then add the three tabs and write the header rows with the Google Sheets connector.
- Format the `Until` and `Added` columns (F and H) of both list tabs as dates with the pattern `yyyy-mm-dd` (`update_spreadsheet`, `repeatCell` with `numberFormat` `{"type": "DATE", "pattern": "yyyy-mm-dd"}`). Then a date typed by hand in any country's style still reads back as `2027-05-01`, which `dnc.py` needs.
- Remind them to share it with their team only, never "anyone with the link".

**Read and write with the Google Sheets connector.** Tool names vary a little by connector version.

| Job | Tool |
|---|---|
| See the tabs and the number of rows | `get_spreadsheet` |
| Read only the key columns for a check or a merge | `get_values` on `'Do not contact'!A:H` (Email to Added, no Note) |
| Add rows | `append_values` to `'Do not contact'!A:I` |
| Change or clear a row (only in review mode, with an OK) | `update_values` on that row's range |
| Add a tab | `update_spreadsheet` (add sheet) |

- Save what you read as a CSV in `~/do-not-contact/.private/`, run `dnc.py`, then delete the file.
- Only the key columns are read. That's a few kilobytes even for thousands of rows.

**No Sheets connector?**
- Claude writes the new rows into `~/do-not-contact/.private/add.csv`.
- The student imports it: File > Import > Upload > "Append to current sheet".
- For a check, the student downloads the `Do not contact` tab as CSV (File > Download > CSV) into the same folder.

## Notion

**Layout: one page with two databases.** The page is called `Do not contact`. It goes under a page the student names, or under their GTM Hub if they have one. It holds:
- a short callout: what the list is for, and the rule;
- the `Sources` table (`Source | How we read it | Who | Last run`);
- the inline database `Do not contact list` (the columns above);
- the inline database `To review` (the same columns plus `Why unsure`, text, and `Proposed`, select: add, remove).

**Tools:**

| Job | Tool |
|---|---|
| Create the page | `notion-create-pages` |
| Create the databases | `notion-create-database`, with the columns above |
| Add rows | `notion-create-pages` with the data source ID as parent, in batches of up to 50. Write keys already cleaned by `dnc.py`. Dates are set as `date:Until:start` and `date:Added:start` |
| Check a batch of keys | `notion-query-data-sources` in SQL mode, keys passed as `params` (up to 100 per query, so split bigger batches). See the query below |
| Update a row (review mode only, with an OK) | `notion-update-page` |

The check query. One `?` per key, keys from `dnc.py keys`:

```sql
SELECT "Email", "LinkedIn URL", "Company domain", "Scope", "Reason", "date:Until:start" AS "Until"
FROM "collection://<data source id>"
WHERE lower("Email") IN (?, ?) OR lower("LinkedIn URL") IN (?) OR lower("Company domain") IN (?, ?)
```

Leave out an `IN` group that has no keys. Save the results as a CSV with these column names, then run `dnc.py`.

- Never read the database whole. For a merge, query the keys of the new rows the same way. That way the list can grow to any size.
- If `notion-query-data-sources` isn't available on their plan, use `notion-search` scoped to the database with one key per search. That's slower, so do it only for small batches.

## The pointer

Every later system has to find the list without asking. Add this block to `~/.claude/CLAUDE.md`. Show it first, then write it after one OK, because it changes their global settings. If the markers are already there, replace what's between them instead of adding a second block.

```
<!-- do-not-contact:start -->
## Do-not-contact list
- List: <Sheet link or Notion page link> (<Google Sheet | Notion>)
- Before contacting anyone, check them with the check-do-not-contact skill. When someone says no, unsubscribes or bounces, add them with update-do-not-contact.
<!-- do-not-contact:end -->
```

If they have a GTM Hub (Notion) or `~/gtm-context/gtm/README.md` (GitHub), offer to add one line there too: `Do-not-contact list: <link>`, in "For agents" or under "Sources". Only the link goes there, never the rows.
