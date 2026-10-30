# The gtm/ folder (GitHub only)

All the context lives in a `gtm/` folder inside a private repository called `gtm-context` on the student's GitHub, cloned at `~/gtm-context`. It's one fixed place, outside any project, decided for the student and never asked (see `context-home.md`). `gtm/README.md` is the hub: it links to everything, so skills open the exact file they need and never search. The repository must be private, because the banks hold customer and objection data. All `gtm/` paths in the skills are inside `~/gtm-context/`.

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
├── updates/           README.md (review guide) and one report per update run (added at the handover)
└── .private/          raw exports while you work (gitignored, delete when done)
```

## Reuse before you create

Ask first whether customers or objections already live somewhere with a connector (a CRM, a Notion or Airtable database, a Google Sheet). If they do, link that source under "Sources" in `gtm/README.md` with the filter that selects the right rows, query it there, and don't create the CSV. One source of truth beats a copy that goes stale.

Create a CSV bank when the data has no other home, or lives only in a platform without a connector (then read an export and keep company-level rows only). Don't create a file for a section the user skips. Add a "Skipped" row to the links table instead.

## Setting up the folder

1. Run `gtm_home.py status`. If `~/gtm-context` is already a git repository, use it and go to step 3.
2. Otherwise, say in one line: "I'll create a private repository called gtm-context on your GitHub and keep it at ~/gtm-context, so every project can use it." On OK:
   - **A `gtm-context` repo already exists on their GitHub** (`gh repo view gtm-context` works): if `~/gtm-context` is missing or empty, `gh repo clone gtm-context ~/gtm-context`. If the folder already has files (for example a `.private/` folder from the Notion version), clone won't work there: run `git init ~/gtm-context`, `git -C ~/gtm-context remote add origin <its URL>`, then `git -C ~/gtm-context pull origin main`.
   - **No repo yet:** `git init ~/gtm-context` (fine if the folder already exists). With the GitHub CLI signed in (`gh auth status`), also run `gh repo create gtm-context --private --source ~/gtm-context --remote origin`. That creates the empty private repo and links it. Nothing is pushed yet.
   - **No GitHub CLI:** keep the local repo, and say they can publish it as a private repo later (the guide's last step offers that).
3. Check the visibility (`gh repo view --json visibility -q .visibility`, run inside `~/gtm-context`). "No git remotes found" means it's local for now: fine. If it's `PUBLIC`, stop and say so: customer and objection data shouldn't be public. Offer to make it private (the user confirms the command).
4. Create `gtm/` and the files below. `.gitignore` gets `gtm/.private/` and `.private/`.
5. Never commit or push without the user's OK. At the end, offer one commit with a message like `gtm: build context layer` and ask before pushing. Scheduled updates commit or push only as the user allowed at the handover (recorded in the Updates block and in the task prompt).

## gtm/README.md (the hub)

```markdown
# GTM context

> **In short:** <what we sell, in one sentence>
> **Primary ICP:** <one sentence>
> **Say this:** "<one line>"
> **Last refreshed:** <date> · <n> new customers, <n> objections, <n> quotes · <n> updates to review   (added once updates are scheduled)

Agents: open only the file you need from the table below. Query the CSV banks with the helper script (filters, counts), never read them whole. Don't copy this content anywhere else.

| Section | File | One-line summary | Last updated |
| --- | --- | --- | --- |
| Product & offer | [product.md](product.md) | Not started | |
| ICP | [icp.md](icp.md) | Not started | |
| Messaging & customer language | [messaging.md](messaging.md) | Not started | |
| Competitors | [competitors.md](competitors.md), [competitors.csv](competitors.csv) | Not started | |
| Objections | [objections.csv](objections.csv) | Not started | |
| Customers | [customers.csv](customers.csv) | Not started | |
| Resource: <name> | <link> | one line on what it's for (one row per extra resource, linked, never copied) | |

## Sources
Where the context was built from, and how to get in.
- <bucket>: <link or tool> | via: <connector name | Claude in Chrome | built-in browser | export file | pasted> | filter: <if the source is shared with other offers>

## Best-customer rule
<for example: "came back for more, or left 2+ reviews">

## Updates
Added at the handover. Settings only, no content.
- Update task: gtm-update (its prompt holds the source plan; review guide in gtm/updates/README.md)
- Runs: <Claude app scheduled task gtm-update | cloud scheduled task, on branch gtm-updates> · <cadence, for example every Monday 08:00>
- Full check: first run of each month
- Alert: <email to your own address | Slack DM to yourself> (the address or member ID is only in the scheduled prompt, never in a file)
- Git: commit <yes|no> · push <yes|no>
- Reports: [updates/](updates/)
- Last run: customers <date> · conversations <date> · full check <date>

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

Each skill that touches a bank has `scripts/gtm_csv.py` in its own folder. Commands run from whatever project the user is in, so call the script by its full path (`<skill folder>` is the base directory shown when the skill loads) and give bank paths in full, under `~/gtm-context/gtm/`.

```bash
python3 <skill folder>/scripts/gtm_csv.py init ~/gtm-context/gtm/objections.csv --cols "Objection,Theme,What they said,Who,Our answer,Answer status,Stage,Source,Times seen,Last seen,Reference"
python3 <skill folder>/scripts/gtm_csv.py query ~/gtm-context/gtm/objections.csv --where Theme=price --cols "Objection,Our answer,Answer status"
python3 <skill folder>/scripts/gtm_csv.py query ~/gtm-context/gtm/customers.csv --where "Best customer=yes" --cols "Company,Size,Industry"
python3 <skill folder>/scripts/gtm_csv.py count ~/gtm-context/gtm/customers.csv --by Size
python3 <skill folder>/scripts/gtm_csv.py upsert ~/gtm-context/gtm/objections.csv --key Objection --rows ~/gtm-context/gtm/.private/new-objections.json
```

Filters: `--where COL=VALUE`, `--contains COL=TEXT`, `--any COL=A|B`, `--min COL=NUMBER`. They combine and are case-insensitive. `upsert` updates rows whose key matches (ignoring case) and appends the rest. It never changes the key itself, and it refuses unknown columns.

If Python 3 isn't available, use `grep` on the file for a single filter. Never read a whole bank into the conversation.
