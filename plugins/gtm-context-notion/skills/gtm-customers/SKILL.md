---
name: gtm-customers
description: "Build or update the Customers database in your Notion GTM Hub: who already buys from you, which ICP segment each belongs to, which ones you would clone, and which logos you have permission to show publicly. Takes a pasted list, a CSV, a CRM, or a description. Use for \"add my customers\", \"which logos can I show\", \"update my customer list\", \"we have a new client\", \"customers I can share publicly\", or as part of build-gtm-context. Not for leads or prospects (those belong in a lead ledger or CRM) and not for the ICP itself (use gtm-icp)."
metadata:
  version: "0.4.0"
---

# Customers

Existing customers are the best evidence for the ICP, and shareable logos are the cheapest proof in outreach. This skill keeps one table of customers (one row per buyer with their contact details, or per company if the user prefers), marks the best ones, and records logo permission explicitly.

It has two parts. Run both when used on its own. Inside build-gtm-context, part A runs early (step 5) and part B runs near the end (step 10).

## Reference files

- `references/source-map.md`: where customers usually live and how to get in (connector, browser, export, paste).
- `references/hub-structure.md`: the Customers database columns, and "Reuse before you create" for a database the user already has.

## Before starting

1. Fetch the GTM Hub page: its link is in the "GTM context" block of Claude's memory. Its links table and "For agents" section hold every link you need. If no Hub link is known, run the build-gtm-context skill first, which sets up the Hub.
2. Fetch the Customers database by its link once, to read its columns and select options. Don't read its rows yet.
3. **On its own** (not inside build-gtm-context): when you find this section's sources, also settle where new customers will come from and who brings it in (`auto`, `auto, app only`, `you`, `none`), as in "Where each item comes from, now and later" in `references/source-map.md`. Prefer an automatic route. Update its line in the hub's Sources list (the Hub's "For agents" section) after the user's OK.

## Part A. Collect customers

### A1. Find where the customers are

**Inside build-gtm-context:** use the customer findings it hands you. Its readers return patterns, not rows: read the rows themselves from the source, filtered to the offers in scope. If the customers already live in a Notion database, it's already linked.

**On its own:** ask where customers live today, and read them using the access order in `references/source-map.md`:
- **A CRM or database** (Notion, Airtable, HubSpot, Attio, Pipedrive): read won deals or customer records only. If it's a Notion database, link it instead of copying (see "Reuse before you create" in `references/hub-structure.md`). Add only the missing columns (Best customer, Logo shareable, Permission note) with the user's OK, and use its existing segment or persona column as the ICP segment.
- **A course, shop or payment platform** (Maven, Stripe, Shopify, Kajabi, Teachable, Gumroad): there's usually no connector, so say so. Offer to browse the customer or student list with Claude in Chrome (the user is already signed in there), or ask for a CSV export into `~/gtm-context/.private/`.
- **A list or spreadsheet**: they paste it or upload it.
- **Only in their head**: they name them.
- **No customers yet**: stop here and say the ICP will be inferred from competitors instead.

If it isn't clear from the data, ask: "B2B, B2C, or both?" For B2C without contact details (A1b), create one row per customer segment ("New parents, Milan, about 120 customers"), or keep the linked database as it is.

If they are an agency, consultant or B2B2C business, ask one more question: "Who are your clients' customers?" Save the answer for the ICP step.

### A1b. Keep contact details?

When the source has people (names, emails, LinkedIn URLs), ask once, with AskUserQuestion, before writing any row: "Keep each buyer's name, email and LinkedIn URL in your Customers database?"
- **Keep them (Recommended):** one row per buyer, with their contact details. Say why in one line: the export gets deleted after reading, so without them that information is lost, and people can't be enriched later (A2).
- **Company level only:** one row per company (B2B) or per segment (B2C), no names. Say what gets lost.

Record the answer as "Customer contacts" in the Hub's "For agents" section, so updates follow it. Contact details go only in the Customers database, never on a page, in a quote or in an objection. If customers already live in a CRM or Notion database that holds contacts, they stay there: just record "kept".

### A2. Fill and enrich

Use what the user gave first, then check what's missing. The ICP is the pattern in the best customers, so it can only be inferred and scored when their rows say who the buyer is and what company they're in.

1. **Count the gaps** with one query or one pass over the batch:
   - **Buyer** (matters most): role or title, seniority, function, time in role.
   - **Company:** website, size, industry, location, stage or funding.

   Don't look up emails or phone numbers: the ICP doesn't need them. Contact details only come from the user's own sources (A1b).
2. **Derive before you pay.** Fill what the data already implies, at no cost: seniority from the title ("Founder", "VP", "Manager"), industry from the company website or the existing segment or persona column. Only what's still missing after that counts toward enrichment.
3. **Is it enough for the ICP?** Enough means the best customers, and a similar sample of the rest, have the buyer's role and seniority (plus size and industry for B2B) on most rows. If it is, enrichment is optional: offer it once and move on. If it isn't, enrichment is needed. Say so in one line: "Without the buyers' roles I can't tell what your best customers share, so the ICP would be a guess."
4. **Find the enrichment tool** from the tool names listed in the session: Clay first (the Clay connector or the Clay CLI), then any other enrichment connector, such as Apollo.
5. **Ask about credits before any lookup.** Say how many people and companies you'd look up, which fields each lookup fills, and what that costs in that tool's credits. People are found by email or LinkedIn URL when contacts are kept, otherwise by name and company, which matches less often. Count unique companies, not rows: several buyers often share one company. Read the cost and the remaining balance from the tool when it reports them (Clay credits and quotas, Apollo credit usage); otherwise give an estimate and say it's one. If the balance is lower than the cost, say so and suggest the best customers first. Then one AskUserQuestion: enrich all rows, the best customers plus a similar sample, or skip. When the data isn't enough (step 3), the enrich options come first and "skip" says the ICP will be marked low confidence.
6. **No enrichment tool connected:** if the data is enough, continue without enrichment. If it isn't, say so in one line and offer to connect the Clay connector (Claude's connector settings), then continue once it's connected. If the user says no, look up the best customers' public profiles yourself (name and company, read-only web search) for a small sample, read company websites, mark anything uncertain `(guess)`, and say the ICP will be lower confidence.
7. **Match carefully.** Look up people by email or LinkedIn URL; a match on name alone counts only if the company matches too. Look up companies by exact domain. A large company's domain also matches its subsidiaries and old brands, so keep the record with the most employees. Tiny firms (1 to 10 people) are often missing from company data: for them, the buyer's title carries the signal.
8. **Write back.** Write buyer and company fields to the customers database, and the LinkedIn URL the lookup found when contacts are kept. If it lacks a column you need (for example Seniority, Buyer role or Enriched), show the list and add only those, with the user's OK (`notion-update-data-source`). For a linked database, use its own columns where they exist. Note where the data came from in Enriched, for example "Clay, 2026-10-30".

Tag each customer with the offers they bought (offers in scope). In a linked database, reuse its own column (for example "Products paid"); add an Offer column only with the user's OK. Contact details go only in the Customers database, and only when the user chose to keep them (A1b).

### A3. Best customers

Best customers drive the ICP. "Best" means they paid well, got results, came back or referred others, and were easy to work with. How to find them depends on the business.

**B2B with a short list (up to about 30 customers):** run one filtered query for the engagement signals the data has (repeat purchases, came back for more, reviews, deal size) and suggest up to 4 candidates. Ask: "Which 3 would you clone if you could?" (multiSelect, "Other" for anyone else).

**B2C, or many individual buyers:** don't ask the user to pick names. With dozens of individuals it's hard and the pick is mostly memory. Define "best" by behaviour instead:
1. List the signals the data actually has, with counts. Examples: bought twice or more, came back with a bigger request, referred someone, left a review, finished or used the product a lot, spent the most, never refunded.
2. Ask (multiSelect): "Which of these mean a great customer to you?"
3. Apply that rule with one query. If a chosen signal isn't a column of the database yet, add it first (a number or checkbox, with `notion-update-data-source`, after the user's OK) and fill it from the source, then query. The best group is usually the top 10 to 20%. If the rule catches much more (common signals like "left a review" do), show the count for the rule as picked and for one or two tighter versions ("2 or more reviews", "both signals"), and let the user choose. Then show how the chosen group differs from everyone else (roles, company size, location, how they found you).
4. Leave out partners, co-instructors, team members and free seats, even when they match.
5. After approval, tick Best customer on the matching rows and record the rule itself ("came back for more or left 2+ reviews") under "Best-customer rule" in the Hub's "For agents" section, so it can be reapplied next month. Each row is a separate update, so above about 30 rows say so before starting.

With several offers in scope, check whether the best buyers differ by offer. If they do, define the rule per offer (for example "course: came back for more; team training: renewed or expanded") and record each one.

Either way, the result is a best group plus the reason it's best. The ICP step looks for what that group shares.

### A4. Pause, then write

Show the table in the chat. After approval:
- **Dedupe in one go:** query the database once with a filter matching this batch's emails (or company names when contacts aren't kept). Update rows that exist, create the rest. One row per buyer (or company): when one already there bought another offer, add that offer to its Offer values and keep the ones it has.
- Set Permission note to `not asked yet` on new rows, Logo shareable unticked.
- Delete the raw export from `~/gtm-context/.private/` once the rows are in, and say so. If contacts weren't kept, say their contact details go with it.
- Update the Customers row in the Hub links table.

## Part B. Logo permission

### B1. Ask about each customer

Query the database for rows where Logo shareable is unticked and Permission note is `not asked yet` (filtered, not the whole table).

Explain in one line: "A logo on your website or in outreach needs the customer's OK. Only tick the ones that have actually said yes." Ask per company: with one row per buyer, apply the answer to every row of that company.

Then one AskUserQuestion, multiSelect: "Which of these gave you permission to show their logo publicly?" Default: none. In the same batch, ask how permission was usually given (contract clause, email, verbal) and whether quotes or results can be shared too. If the user doesn't say how, record "Permission confirmed by the user on <date> (method not recorded)".

If the user's website already shows logos of companies in this list, ask where that permission came from. A company deal (for example a team contract) doesn't cover an individual buyer's row, so leave those unticked unless the user says otherwise.

### B2. Write

Tick Logo shareable and fill Permission note, Quote and Result for the approved rows. For the rest, set Permission note to `asked, no` or leave `not asked yet` if the user wants to check first.

## Rules

- Contact details (name, email, LinkedIn URL) only in the Customers database, and only after the user's yes (A1b). Never on a page, in a quote, an objection or a report.
- Browsing a platform is read-only. The user signs in themselves.
- Never tick Logo shareable on a guess, a public website mention, or "they probably won't mind".
- Query with filters, never read the whole database. Fetch by link, never search Notion.
