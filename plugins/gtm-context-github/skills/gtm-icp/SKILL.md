---
name: gtm-icp
description: "Define or refine your ideal customer profile (ICP) in gtm/icp.md in your repo, using your best existing customers, or your competitors' customers when you have none. Produces one section per ICP with hard filters, public scoring signals you can check before any contact, conversation signals, buying triggers, an anti-ICP and a one-line hook, checked for specificity before you approve it. Use for \"define my ICP\", \"who is my ideal customer\", \"refine my ICP\", \"my ICP is too broad\", \"who should I target\", or as part of build-gtm-context. Not for scoring a specific lead list (that is the outbound system's job)."
metadata:
  version: "0.2.0"
---

# ICP

The ICP is what every outbound and inbound agent checks a person against. It has to be checkable from public data (a LinkedIn profile, a website, company data) and narrow enough that you could build a list of 50 real people from it.

## Reference files

- `references/icp-checks.md`: how to build an ICP from customers or competitors, its structure, public signals, and the checks to run. Read it before drafting.
- `references/page-template.md`: the page layout.
- `references/sections.md`: quality bar, and the B2B / B2C / agency differences.
- `scripts/gtm_csv.py`: query the customers and competitors banks. Call it by its full path in this skill's folder.

## Before starting

1. Read `gtm/README.md`. If it's missing, run the build-gtm-context skill first, which sets up the folder.
2. Read `gtm/product.md` and `gtm/icp.md`. If the ICP page has content, summarise it and ask what to change.

## Steps

### 1. Gather evidence

Use what exists, in this order of strength:

1. **Best customers:** query `gtm/customers.csv` with `--where "Best customer=yes"`, or the connected customer system listed under "Sources". If none are marked, run gtm-customers part A3 first. It picks 3 names for a short B2B list, or a behaviour rule for B2C and long lists.
2. **All customers:** use `count --by Size`, `--by Industry` and `--by "ICP segment"` to see the spread. Don't read the whole bank.
3. **Competitor evidence:** if the guide passed it on, use it. Otherwise read the "Who they sell to" line in `gtm/competitors.md`.
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
- Don't name the enrichment tool to the user or in any file. Say "public company data" instead.
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

- Write `gtm/icp.md` with the approved draft. Add a changelog line at the bottom.
- If the ICP names changed, update the ICP segment values in `gtm/customers.csv` with one `upsert` batch, after asking. If customers live in a connected system with its own segment or persona field, don't add a new one: write on the ICP page which of its values map to each ICP.
- Update the ICP row in the `gtm/README.md` table.

## Rules

- At most 3 ICPs. Primary first.
- Hard filters and public scoring signals must be checkable from public data or company data. "Ambitious" or "growth-minded" is not a filter. Each public signal says where to check it.
- Every attribute shows its evidence: `(customers)`, `(from competitors, confirm)` or `(guess, confirm)`.
- Query with filters, never read whole banks.
