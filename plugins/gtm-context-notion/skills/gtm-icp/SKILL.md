---
name: gtm-icp
description: "Define or refine your ideal customer profile (ICP) on the ICP page of your Notion GTM Hub, using your best existing customers, or your competitors' customers when you have none. Produces one section per ICP with hard filters, scoring signals, buying triggers, an anti-ICP and a one-line hook, checked for specificity before you approve it. Use for \"define my ICP\", \"who is my ideal customer\", \"refine my ICP\", \"my ICP is too broad\", \"who should I target\", or as part of build-gtm-context. Not for scoring a specific lead list (that is the outbound system's job)."
metadata:
  version: "0.1.0"
---

# ICP

The ICP is what every outbound and inbound agent checks a person against. It has to be checkable from public data (a LinkedIn profile, a website) and narrow enough that you could build a list of 50 real people from it.

## Reference files

- `references/icp-checks.md`: how to build an ICP from customers or competitors, its structure, and the checks to run. Read it before drafting.
- `references/page-template.md`: the page layout.
- `references/sections.md`: quality bar, and the B2B / B2C / agency differences.

## Before starting

1. Fetch the GTM Hub page: its link is in the "GTM context" block of Claude's memory. Its links table and "For agents" section hold every link you need. If no Hub link is known, run the build-gtm-context skill first, which sets up the Hub.
2. Fetch the Product & offer page and the ICP page by their links. If the ICP page has content, summarise it and ask what to change.

## Steps

### 1. Gather evidence

Use what exists, in this order of strength:

1. **Best customers:** query the Customers database with the filter Best customer = ticked. If none are marked, run gtm-customers part A3 first. It picks 3 names for a short B2B list, or a behaviour rule for B2C and long lists.
2. **All customers:** query by ICP segment and Size to see the spread. Use filtered queries, not a full read.
3. **Competitor evidence:** if the guide passed it on, use it. Otherwise fetch the Competitors page summary by link and read the "Who they sell to" line.
4. **Conversations:** if the guide already has language-miner results, use them for triggers, pains and anti-ICP signals.
5. **The user's own view:** only when the data above is thin (fewer than about 10 customers with details), ask once, in one batch:
   - "Describe the last 3 people who asked to buy, even if they didn't."
   - "Who do you never want as a customer again, and why?"
   - For agencies, consultants and B2B2C businesses: "Who are your clients' customers?" (if not already answered).

   With rich data, skip these questions: the review questions in step 4 below catch the same things with less effort.

If there are no customers and no competitor evidence, say the ICP will be a starting hypothesis, marked `(no data yet)`, and continue.

### 2. Find the pattern

Compare the best customers with each other and with the rest. Look for the 3 attributes they share that others don't: industry, size band, stage, role of the buyer, situation, tools, geography. For B2C, use situation and trigger instead of firmographics.

Then enrich, so the scoring works before first contact. Look up the best group and a similar-sized sample of the rest on the public attributes in `icp-checks.md` (headcount growth, funding, job postings, tech stack, time in role, LinkedIn activity and so on):
- With an enrichment connector available, use it, after telling the user how many lookups that is and getting their OK, because it uses credits.
- Without one, read company websites and public LinkedIn pages for a small sample (about 10), and say the result is lighter.
- Don't name the enrichment tool to the user or on any page. Say "public company data" instead.
- Look up small and large companies separately, matching on exact domain. A large company's domain also matches its subsidiaries and old brands, so keep the record with the most employees. Tiny firms (1 to 10 people) are often missing from company data: for them, the person's title and LinkedIn profile carry the signal.

Public attributes that clearly separate the best group become the hard filters and public scoring signals. What people only say on calls becomes conversation signals.

Write 1 primary ICP. Add a second or third only if the evidence clearly shows a separate group with a different buyer or reason to buy.

### 3. Draft and check

Fill the page template. Run every check in `icp-checks.md`. Fix what fails, then note in one line per check what changed.

### 4. Pause: show the draft

Show the draft and the check notes. Ask specifically:
- "Could you name 5 real people who match ICP 1 right now?"
- "Is anyone in the anti-ICP someone you'd actually take?"

Apply edits. Don't write on silence.

### 5. Write

- Replace the ICP page content with the approved draft (`notion-update-page`).
- If the ICP names changed, update the ICP segment options in the Customers database to match, and offer to re-tag customers. If the customers database is linked and already has its own segment or persona column, don't add a new one: write on the ICP page which of its values map to each ICP.
- Update the ICP row in the Hub links table.

## Rules

- At most 3 ICPs. Primary first.
- Hard filters and public scoring signals must be checkable from public data or company data. "Ambitious" or "growth-minded" is not a filter. Each public signal says where to check it.
- Every attribute shows its evidence: `(customers)`, `(from competitors, confirm)` or `(guess, confirm)`.
- Query with filters, never read whole databases. Fetch by link, never search Notion.
