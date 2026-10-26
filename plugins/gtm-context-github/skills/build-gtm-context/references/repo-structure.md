# The gtm/ folder (GitHub only)

All the context lives in a `gtm/` folder in the student's own repository. `gtm/README.md` is the hub: it links to everything, so skills open the exact file they need and never search. The repository should be private, because the banks hold customer and objection data.

```
gtm/
├── README.md          hub: summary, links table, sources, column guide
├── product.md         Product & offer
├── icp.md             ICP
├── messaging.md       Messaging & customer language
├── competitors.md     summary on top (only if competitors aren't skipped)
├── competitors.csv    bank
├── objections.csv     bank
├── customers.csv      bank
└── .private/          raw exports while you work (gitignored, delete when done)
```

## Reuse before you create

Ask first whether customers or objections already live somewhere with a connector (a CRM, a Notion or Airtable database, a Google Sheet). If they do, link that source under "Sources" in `gtm/README.md` with the filter that selects the right rows, query it there, and don't create the CSV. One source of truth beats a copy that goes stale.

Create a CSV bank when the data has no other home, or lives only in a platform without a connector (then read an export and keep company-level rows only). Don't create a file for a section the user skips. Add a "Skipped" row to the links table instead.

## Setting up the folder

1. Check this is a git repository (`git rev-parse --is-inside-work-tree`). If not, explain in one line and offer to run `git init`.
2. Check the remote, if there is one (`gh repo view --json visibility -q .visibility`). "No git remotes found" just means the repo is local for now: fine, and when they create the GitHub repo later, it should be private. If it's `PUBLIC`, stop and say so: customer and objection data shouldn't go in a public repository. Offer to make it private (the user confirms the command) or to keep the banks out of git.
3. Create `gtm/` and the files below. Add `gtm/.private/` to `.gitignore`.
4. Never commit or push without the user's OK. At the end, offer one commit with a message like `gtm: build context layer` and ask before pushing.

## gtm/README.md (the hub)

```markdown
# GTM context

> **In short:** <what we sell, in one sentence>
> **Primary ICP:** <one sentence>
> **Say this:** "<one line>"

Agents: open only the file you need from the table below. Query the CSV banks with the helper script (filters, counts), never read them whole. Don't copy this content anywhere else.

| Section | File | One-line summary | Last updated |
| --- | --- | --- | --- |
| Product & offer | [product.md](product.md) | Not started | |
| ICP | [icp.md](icp.md) | Not started | |
| Messaging & customer language | [messaging.md](messaging.md) | Not started | |
| Competitors | [competitors.md](competitors.md), [competitors.csv](competitors.csv) | Not started | |
| Objections | [objections.csv](objections.csv) | Not started | |
| Customers | [customers.csv](customers.csv) | Not started | |

## Sources
Where the context was built from, and how to get back in. Refreshes reread these instead of asking again.
- <bucket>: <link or tool> | via: <connector name | Claude in Chrome | built-in browser | export file | pasted> | filter: <if the source is shared with other offers>

## Best-customer rule
<for example: "came back for more, or left 2+ reviews">

Last updated: <YYYY-MM-DD>
```

## Pages

`product.md`, `icp.md` and `messaging.md` use the templates in each section skill's `references/page-template.md`. Each page:
- Starts with the summary block, then the details. One or two screens, long examples at the bottom.
- Ends with a short changelog: `## Changelog` then one line per change, newest first: `- 2026-10-26: built from website, CRM and 12 calls`.

## CSV banks

Rules for every bank:
- UTF-8, comma separated, header row exactly as below. Dates `YYYY-MM-DD`. Yes/no columns hold `yes` or `no`. Several values in one cell are separated by `; `.
- Select columns only take the listed values, so filters work.
- Write and update with the helper script's `upsert`, never by hand, so quotes and commas stay valid.
- Companies and roles only. No personal names, emails, phone numbers or profile URLs.

**customers.csv**

| Column | Values |
|---|---|
| Company | company name; for B2C a segment ("New parents, Milan") |
| Website | url |
| ICP segment | the ICP names from icp.md, or `outside ICP` |
| Size | `1`, `2-10`, `11-50`, `51-200`, `201-1000`, `1000+` |
| Industry | text |
| Type | `B2B`, `B2C` |
| Best customer | `yes`, `no` |
| Logo shareable | `yes` only with explicit permission, else `no` |
| Permission note | how and when, or `not asked yet` |
| Quote | public testimonial, only if permission covers it |
| Result | a number or outcome, only if shareable |
| Case study | url |

**objections.csv**

| Column | Values |
|---|---|
| Objection | short, plain words |
| Theme | `price`, `timing`, `proof`, `fit`, `effort`, `existing-solution`, `approval`, `risk`, `other` (or the user's own themes, listed in the hub) |
| What they said | verbatim quote |
| Who | role and company type |
| Our answer | the answer that works best |
| Answer status | `works`, `draft`, `unknown` |
| Stage | `first contact`, `call`, `proposal`, `renewal` |
| Source | `call`, `email`, `DM`, `form`, `webinar`, `pasted` |
| Times seen | number |
| Last seen | date |
| Reference | source tag, for example `[call 2026-09-14]` |

**competitors.csv**

| Column | Values |
|---|---|
| Name | |
| Website | url |
| Headline | their main headline, verbatim |
| What they sell | one or two sentences |
| Who they sell to | text |
| Price | text, or `not public` |
| Public customers | companies they show publicly |
| How we differ | text |
| Threat | `high`, `medium`, `low` |
| Last checked | date |

## The helper script

Each skill that touches a bank has `scripts/gtm_csv.py` in its own folder. Commands run from the project folder, so call the script by its full path: `<skill folder>` is the base directory shown when the skill loads.

```bash
python3 <skill folder>/scripts/gtm_csv.py init gtm/objections.csv --cols "Objection,Theme,What they said,Who,Our answer,Answer status,Stage,Source,Times seen,Last seen,Reference"
python3 <skill folder>/scripts/gtm_csv.py query gtm/objections.csv --where Theme=price --cols "Objection,Our answer,Answer status"
python3 <skill folder>/scripts/gtm_csv.py query gtm/customers.csv --where "Best customer=yes" --cols "Company,Size,Industry"
python3 <skill folder>/scripts/gtm_csv.py count gtm/customers.csv --by Size
python3 <skill folder>/scripts/gtm_csv.py upsert gtm/objections.csv --key Objection --rows gtm/.private/new-objections.json
```

Filters: `--where COL=VALUE`, `--contains COL=TEXT`, `--any COL=A|B`, `--min COL=NUMBER`. They combine and are case-insensitive. `upsert` updates rows whose key matches (ignoring case) and appends the rest. It never changes the key itself, and it refuses unknown columns.

If Python 3 isn't available, use `grep` on the file for a single filter. Never read a whole bank into the conversation.
