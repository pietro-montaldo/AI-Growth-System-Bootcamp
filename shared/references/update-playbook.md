# Update playbook: keeping the GTM context current

The first build is a snapshot. Prices change, cohorts start and end, new customers buy, and new objections and buyer phrases show up every week. An update reads the sources in the update task's plan ("Where new information comes from"), adds what's new to the banks, and proposes changes to the pages.

## What may change without the user, and what may not

| Thing | During a scheduled run |
|---|---|
| Customers bank: new customers | Added automatically, one row per buyer with their contact details when the hub says contacts are kept (otherwise one row per company), tagged with their offer, Permission note `not asked yet`. Enriched only if the task says so, within its lookup limit |
| Customers bank: best-customer tag | Applied automatically, using the saved rule |
| Objections bank: new objections | Added automatically, Answer status `draft` |
| Objections bank: repeats | Times seen and Last seen updated automatically |
| Messaging page: new quotes | Added automatically to a "New quotes (unreviewed, <date>)" section at the bottom |
| Product & offer page | Never changed. Differences become proposed updates |
| ICP page | Never changed. Drift becomes a proposed update |
| Messaging summary, value props, word lists | Never changed. Proposed updates only |
| Logo permission | Never set. New customers wait for the review |

Banks only ever grow or get counters updated. Nothing is deleted, and nothing curated is rewritten without the user.

Tag every row a scheduled run adds, so the review can find it: in a linked log, put "Added by GTM update <date>" in a notes column it already has (for example "How we know"); in a CSV bank, Answer status `draft` and the source tag do the job. A linked log without a count column can't record repeats: skip them and list them in the report instead.

## Rules for unattended runs

1. **Never ask a question.** Anything that needs a decision becomes a proposed update in the report.
2. **Never stop on one failure.** A source that can't be read (connector signed out, Chrome closed, page gone) is skipped, logged in the report under "Couldn't read", and named in the alert.
3. **Only the planned sources.** Read the sources in the update task's plan, and nothing else. Lines marked `auto, app only` are skipped and logged when Chrome isn't available. Lines marked `you` are read only if the user dropped a new export or pasted something; otherwise the alert reminds them when it's due. Don't go looking for new sources: only the user adds them, by changing the update settings.
4. **Only what's new.** Each bucket has a "last run" date in the hub's Updates settings (the Notion Hub's "For agents" section, or `gtm/README.md` in the GitHub version). Read conversations and customers since that date. If there's no date, use the last 30 days.
5. **Read-only browsing.** Same rules as the build: summary pages first, never click anything that changes data or sends messages, close tabs afterwards.
6. **Personal data only in the customer database.** When the hub says customer contacts are kept, new customer rows keep the buyer's name, email and LinkedIn URL from the source. Everywhere else (pages, quotes, objections, the report, the alert): role and company type, never names, emails or profile URLs.
7. **One message out, to the user only.** The alert goes to the address or Slack DM saved at setup, and nowhere else. Never send anything to customers or prospects.

## What to check per bucket

**Every run (weekly by default)**
- **Customers:** new customers since the last run, from the customer source. Upsert them (matched by email, then LinkedIn URL, then name; by company when contacts aren't kept) and apply the best-customer rule. If the sales platform shows totals (for example students per course on a dashboard), compare them with the count in the customer bank. A gap goes under "Stale" as something to check (often free seats or scholarships), never as rows guessed into the bank.
- **Objections:** read each conversation source for the window (the conversation brief). Dedupe objections with one query per batch for the themes in it, comparing by meaning, not exact wording.
- **Customer language:** take the new quotes from the same miner results. Merge repeats with quotes already on the page, keep the 5 to 10 strongest new ones, and add them to the "New quotes" section.
- **Staleness:**
  - Dates on the pages that have passed (next cohort, launch dates, "until" offers).
  - Sections older than their rhythm: banks weekly; product, ICP, competitors and messaging monthly.
  - Items still marked `draft` or `(guess, confirm)`.

**First run of each month (or when the user asks for a full check)**
- **Offer and website:** read each product source in compare mode (the compare-mode brief), with the current Product & offer page as the baseline. It returns only ADDED, REMOVED and CHANGED fields. Typical findings:
  - A new or retired offer.
  - A price, format, length or date change.
  - A new headline or claim.
  - A changed proof number, such as students trained or rating.
- **Proof:** the same check on testimonial and logo sources.
- **ICP drift, per offer:** compare the customers each offer added this month with that offer's ICP filters ("Find them"). Propose an ICP update when either is true:
  - More than about 30% of new customers fall outside every ICP.
  - A group outside the ICP shows up 3 or more times.

  Include the evidence.
- **Competitors** (if not skipped): reread each competitor's public site in compare mode, with its current row as the baseline, and report only changes.

When sources disagree, the source closest to the buyer wins (a live sales page beats an internal note), as in the build.

## Proposed updates

Each proposed update is one numbered item:

```markdown
### 3. Product & offer: price of the Bootcamp
- Now on the page: $999
- Source says: $1,199 (maven.com/..., read 2026-11-03)
- Suggested change: update the offers table and the summary line
- Status: open
```

Status is `open`, `applied` or `rejected`. Review mode sets it.

## The report

One report per run. Title: `GTM update <YYYY-MM-DD>`.

```markdown
> **Summary:** 3 new customers, 5 objections (2 new, 3 repeats), 8 new quotes, 4 proposed updates. 1 source couldn't be read.

## Added automatically
- Customers: <company (size, industry)>, ...
- Objections: <new ones, with theme>; repeats: <objection (now seen N times)>
- Quotes: <count> added to the messaging page

## Proposed updates
<numbered items as above>

## Stale
- <item>: <why>

## Couldn't read
- <source>: <reason>. <what to do, for example "open Chrome and sign in to Maven before Monday">
- <source>: hit the reading cap, <n> conversations not read (list their dates)
```

## The alert

Short, plain, and sent only to the user's own address or DM:

```
GTM update <date>: 3 new customers, 5 objections, 8 quotes added. 4 updates need your OK.
1 source couldn't be read: Maven (Chrome was closed).
Report: <link or path>
To review, open Claude anywhere and say "review GTM updates".
```

If nothing changed, still send a one-line alert ("No changes this week"), so the user knows the schedule works. If the send fails, leave an email draft instead, and note it in the report.
