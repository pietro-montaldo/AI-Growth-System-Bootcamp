# GTM Hub structure (Notion)

One GTM Hub page links to everything. Four short pages and three databases sit under it. The student's project folder holds only `gtm-hub.md`, a list of links, so skills never search Notion.

```
GTM Hub (page)
├── Product & offer (page)
├── ICP (page)
├── Messaging & customer language (page)
├── Competitors (page: summary on top, then the Competitors database inline)
├── Objections bank (database)
└── Customers (database)
```

## Reuse before you create

Many users already keep customers or objections in Notion. Copying them into the Hub would create a second source of truth, so always ask first:

- "Do you already keep your customers in a Notion database?" and "Do you already log objections somewhere in Notion?"
- **Yes:** they paste the link. Fetch its schema once and link it from the Hub and `gtm-hub.md` instead of creating a new database. Record the filter that selects the rows for this offer (for example `Products paid contains "AI Growth Systems Bootcamp"`).
- **Missing columns:** if the existing database lacks a column a skill needs (for customers: Best customer, Logo shareable, Permission note), show the list and add only those, with the user's OK (`notion-update-data-source`). Never rename or remove their columns.
- **Their vocabulary wins:** use their existing theme, persona and stage options instead of the defaults below. Map new rows onto them.
- Create a new database only for what doesn't exist yet.
- Don't create a page or database for a section the user skips (for example no competitors). Add a "Skipped" row to the Hub links table instead.

## Notion tools

Tool names vary slightly by connector version. Use the matching tool:

| Job | Tool |
|---|---|
| Read a page or a database schema by link | `notion-fetch` |
| Create pages or database rows | `notion-create-pages` (rows: parent is the data source ID) |
| Replace or edit page content, update a row | `notion-update-page` |
| Create a database | `notion-create-database` |
| Add columns to an existing database | `notion-update-data-source` |
| Move an empty database the skill created to Trash | `notion-delete-databases` (only with the user's OK) |
| Read matching rows only | `notion-query-data-sources`. SQL mode with a `WHERE` clause is the most flexible: multi-select columns are JSON text, so filter them with `LIKE '%value%'`. If that tool isn't available on the user's plan, use `notion-search` scoped to the database (its data source URL) with the filter value as the query. |

`notion-search` across the whole workspace is used once, and only if the user wants help finding a parent page. Never use it to find GTM Hub pages.

Editing tips that save a failed call:
- Read `notion://docs/notion-flavored-markdown-spec` once (with `notion-fetch`) before the first write.
- Before a targeted edit of the Hub links table, fetch the Hub page and copy the row exactly. Notion stores bold as `<b>` tags, turns domains like `Acme.AI` into links, and rewrites a mention when its target moves to Trash.
- Fetching a database schema returns a lot of text. Fetch it once per run and reuse what you learned.

## Hub page

Title: `GTM Hub`. Content, in this order:

1. A callout with the summary: what the business sells in one sentence, the primary ICP in one sentence, and the "say this" line. Updated by the guide at the end of each run.
2. A short paragraph: "Agents: read the page you need by its link below. Query the databases with a filter. Don't copy this content anywhere else."
3. A table: `Section | Link | One-line summary | Last updated`. One row per child page and database. A new section shows "Not started" in the summary column.

## Pages

Create each page with the title above and a single line, `Not started. Run build-gtm-context or the matching section skill.` The section skills replace that line with their template.

## Databases

Create only the ones the user doesn't already have (see "Reuse before you create"). New databases go under the Hub, except Competitors, which goes inside the Competitors page.

**Competitors**

| Column | Type | Notes |
|---|---|---|
| Name | title | |
| Website | url | |
| Headline | text | their main headline, verbatim |
| What they sell | text | one or two sentences |
| Who they sell to | text | |
| Price | text | or "not public" |
| Public customers | text | companies they show publicly |
| How we differ | text | |
| Threat | select | high, medium, low |
| Last checked | date | |

**Objections bank**

| Column | Type | Notes |
|---|---|---|
| Objection | title | short, in plain words |
| Theme | select | price, timing, proof, fit, effort, existing-solution, approval, risk, other |
| What they said | text | verbatim quote, no names |
| Who | text | role and company type |
| Our answer | text | the answer that works best |
| Answer status | select | works, draft, unknown |
| Stage | select | first contact, call, proposal, renewal |
| Source | select | call, email, DM, form, pasted |
| Times seen | number | |
| Last seen | date | |
| Reference | text | source tag, for example [call 2026-09-14] |

**Customers**

| Column | Type | Notes |
|---|---|---|
| Company | title | for B2C, a segment name instead, for example "New parents, Milan" |
| Website | url | |
| ICP segment | select | the ICP names from the ICP page, plus "outside ICP" |
| Size | select | 1, 2-10, 11-50, 51-200, 201-1000, 1000+ |
| Industry | text | |
| Type | select | B2B, B2C |
| Best customer | checkbox | one of the ones the user would clone |
| Logo shareable | checkbox | ticked only with explicit permission |
| Permission note | text | how and when permission was given, or "not asked yet" |
| Quote | text | public testimonial, only if permission covers it |
| Result | text | a number or outcome, only if shareable |
| Case study | url | |

## gtm-hub.md

Saved in the project folder. Links and IDs only, never content.

```markdown
# GTM Hub links

Only links live here. The context itself lives in Notion. Skills read pages by these links and never search.

- Hub: <url>
- Product & offer: <url>
- ICP: <url>
- Messaging & customer language: <url>
- Competitors page: <url>
- Competitors database: <url> | data source: <collection://...>
- Objections bank: <url> | data source: <collection://...> | filter: <only if the database is shared with other offers>
- Customers: <url> | data source: <collection://...> | filter: <only if the database is shared with other offers>

## Sources
Where the context was built from, and how to get back in. Refreshes reread these instead of asking again.
- <bucket>: <link or tool> | via: <connector name | Claude in Chrome | built-in browser | export file | pasted>

Last updated: <YYYY-MM-DD>
```

Mark a linked database as `(linked, existing database)` after its name, so later skills know not to create rows in a format the user didn't choose. Leave out lines for skipped sections.

If a link stops working (page moved or deleted), ask the user for the new link. Don't search for it.
