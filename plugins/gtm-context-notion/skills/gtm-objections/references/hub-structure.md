# GTM Hub structure (Notion)

One GTM Hub page links to everything. Four short pages and three databases sit under it. The Hub page is also the map for agents: its links table and its collapsed "For agents" section hold every link, ID and setting, so skills never search Notion and no local file is needed. The Hub link itself lives in Claude's memory (the "GTM context" pointer block).

```
GTM Hub (page)
├── 📦 Product & offer (page)
├── 🎯 ICP (page)
├── 💬 Messaging & customer language (page)
├── ⚔️ Competitors (page: summary on top, then the Competitors database inline)
├── Objections bank (database)
├── Customers (database)
└── 🔄 Updates to review (page, added at the handover: the review guide, then one child page per update report)
```

## Reuse before you create

Many users already keep customers or objections in Notion. Copying them into the Hub would create a second source of truth, so always ask first:

- "Do you already keep your customers in a Notion database?" and "Do you already log objections somewhere in Notion?"
- **Yes:** they paste the link. Fetch its schema once and link it from the Hub (links table and "For agents" section) instead of creating a new database. Record the filter that selects the rows for the offers in scope (for example `Products paid contains "AI Growth Systems Bootcamp"`), and which column holds the offer.
- **Missing columns:** if the existing database lacks a column a skill needs (for customers: Best customer, Logo shareable, Permission note, and Email and LinkedIn URL when contacts are kept), show the list and add only those, with the user's OK (`notion-update-data-source`). Never rename or remove their columns.
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
- Read `notion://docs/notion-flavored-markdown-spec` once (with `notion-fetch`) before the first write, and follow `page-style.md` for how every page looks.
- Before a targeted edit of the Hub links table, fetch the Hub page and copy the row exactly. Notion stores bold as `<b>` tags, turns domains like `Acme.AI` into links, and rewrites a mention when its target moves to Trash. Mentions of databases often don't match even when copied from a fetch, so anchor the edit on the plain text after the mention (for example `Linked, not copied | 2026-10-26 |`), adding the start of the next row when that text appears twice.
- Fetching a database schema returns a lot of text. Fetch it once per run and reuse what you learned.

## Hub page

Title: `GTM Hub`, icon 🧭. Content, in this order (format in `page-style.md`):

1. A `blue_bg` callout with the summary, one bold label per line: what the business sells in one sentence, the primary ICP in one sentence, and the "say this" line. Updated by the guide at the end of each run. Once updates are scheduled, it ends with one more line, kept current by the student's scheduled update: `Last refreshed: <date> · <n> new customers, <n> objections, <n> quotes · <n> updates to review`.
2. A short paragraph: "Agents: read the page you need by its link below. Query the databases with a filter. Don't copy this content anywhere else."
3. A styled table with a gray header row: `Section | Link | One-line summary | Last updated`. Links are page and database mentions. Dates in gray. One row per child page and database. A new section shows "Not started" in the summary column. Extra resources the user shared (case studies, a deck, a pricing sheet) get one row each, named `Resource: <name>`, linked and never copied.
4. At the very bottom, the collapsed "For agents: links and settings" section (format below).

## Pages

Create each page with the title and icon above (icons in `page-style.md`) and a single line, `Not started. Run build-gtm-context or the matching section skill.` The section skills replace that line with their template.

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
| Offer | multi-select | the offer in scope it's about. One row per objection and offer: the same objection about another offer is its own row, with its own Times seen |
| Theme | select | price, timing, proof, fit, effort, existing-solution, approval, risk, other |
| What they said | text | verbatim quote, no names |
| Who | text | role and company type |
| Our answer | text | the answer that works best |
| Answer status | select | works, draft, unknown |
| Stage | select | first contact, call, proposal, renewal |
| Source | select | call, email, DM, form, webinar, pasted |
| Times seen | number | |
| Last seen | date | |
| Reference | text | source tag, for example [call 2026-09-14] |

**Customers**

| Column | Type | Notes |
|---|---|---|
| Customer | title | the buyer's name when contacts are kept; otherwise the company, or for B2C a segment ("New parents, Milan") |
| Company | text | the buyer's company; blank for an individual |
| Email | email | only when contacts are kept |
| LinkedIn URL | url | only when contacts are kept |
| Offer | multi-select | the offers in scope they bought. One row per buyer (or per company when contacts aren't kept): a second offer is added to this column, not a second row |
| Website | url | |
| ICP segment | select | the ICP names from the ICP page, plus "outside ICP" |
| Size | select | 1, 2-10, 11-50, 51-200, 201-1000, 1000+ |
| Industry | text | |
| Type | select | B2B, B2C |
| Buyer role | text | the buyer's title or function |
| Seniority | select | founder or owner, C-level, VP or director, manager, individual contributor |
| Best customer | checkbox | one of the ones the user would clone |
| Logo shareable | checkbox | ticked only with explicit permission |
| Permission note | text | how and when permission was given, or "not asked yet" |
| Quote | text | public testimonial, only if permission covers it |
| Result | text | a number or outcome, only if shareable |
| Case study | url | |
| Enriched | text | where company and buyer fields came from, for example "Clay, 2026-10-30" |
| <signal properties> | number or checkbox | optional, one per best-customer signal (for example Purchases, Reviews), added when the best-customer rule needs them (gtm-customers A3) |

## The "For agents" section (the map)

The Hub page is the only map of the context. Its links table lists every page and database. A collapsed section at the very bottom holds what agents need beyond that: data source IDs, filters, sources, the best-customer rule and the update settings. Settings only, never content.

Because the map lives in Notion, any session on any surface (Claude Code, Cowork, a cloud routine, another computer) needs only the Hub link: one fetch gives it everything. The Hub link itself sits in Claude's memory (the "GTM context" pointer block) and in every scheduled prompt.

Write it as a toggle heading, so people reading the Hub don't see it unless they open it:

```markdown
<toggle heading="h2">
For agents: links and settings

Read this instead of searching. Settings only, no content. Kept current by the GTM context skills.

**Databases**
- Objections bank: <mention of the database> · data source: collection://... · filter: <only if shared with other offers>
- Customers: <mention> · data source: collection://... · filter: <...>
- Competitors: <mention> · data source: collection://...

**Offers in scope:** <offer 1> · <offer 2> (the others are left out on purpose)

**Sources** (one line per item: where it was built from, how to get in, where new information comes from, and who brings it in)
- <item>: <built from: link or tool> · via: <connector name | Claude in Chrome | built-in browser | export file | pasted> · filter: <only if the source also holds other offers> · new info from: <source> · who: <auto | auto, app only | you (how often) | none>

**Customer contacts:** <kept in the Customers database | not kept> (decided <date>, gtm-customers A1)

**Best-customer rule:** <for example "came back for more, or left 2+ reviews">

**Updates** (added at the handover)
- Update task: gtm-update (its prompt holds the source plan; review guide on the Updates to review page)
- Runs: <Claude app scheduled task gtm-update | cloud scheduled task> · <cadence, for example every Monday 08:00>
- Full check: first run of each month
- Alert: <email to your own address | Slack DM to yourself> (the address or member ID is only in the scheduled prompt, never on the page)
- Last run: customers <date> · conversations <date> · full check <date>

Last updated: <YYYY-MM-DD>
</toggle>
```

Mark a linked database as `(linked, existing database)` after its name, so later skills know not to create rows in a format the user didn't choose. Leave out lines for skipped sections. When editing this section later, anchor on its plain-text labels (for example `Last run: customers`), as with the links table.

If a link stops working (page moved or deleted), ask the user for the new link. Don't search for it.

## Older setups: gtm-hub.md

Only build-gtm-context does this. Earlier versions kept this map in a local file, `gtm-hub.md`, in the project folder or in `~/gtm-context/`. If one is found (`gtm_home.py status` lists them), copy its database lines, sources and update settings into the "For agents" section, update the pointer in Claude's memory to the Hub link, and tell the user the file is no longer needed. Delete it only on their OK.
