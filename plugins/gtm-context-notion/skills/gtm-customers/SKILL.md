---
name: gtm-customers
description: "Build or update the Customers database in your Notion GTM Hub: who already buys from you, which ICP segment each belongs to, which ones you would clone, and which logos you have permission to show publicly. Takes a pasted list, a CSV, a CRM, or a description. Use for \"add my customers\", \"which logos can I show\", \"update my customer list\", \"we have a new client\", \"customers I can share publicly\", or as part of build-gtm-context. Not for leads or prospects (those belong in a lead ledger or CRM) and not for the ICP itself (use gtm-icp)."
metadata:
  version: "0.1.0"
---

# Customers

Existing customers are the best evidence for the ICP, and shareable logos are the cheapest proof in outreach. This skill keeps one table of customers at company level, marks the best ones, and records logo permission explicitly.

It has two parts. Run both when used on its own. Inside build-gtm-context, part A runs early (step 5) and part B runs near the end (step 10).

## Reference files

- `references/source-map.md`: where customers usually live and how to get in (connector, browser, export, paste).

## Before starting

1. Fetch the GTM Hub page: its link is in the "GTM context" block of Claude's memory. Its links table and "For agents" section hold every link you need. If no Hub link is known, run the build-gtm-context skill first, which sets up the Hub.
2. Fetch the Customers database by its link once, to read its columns and select options. Don't read its rows yet.
3. **On its own** (not inside build-gtm-context): when you find this section's sources, also settle where new customers will come from and who brings it in (`auto`, `auto, app only`, `you`, `none`), as in "Where each item comes from, now and later" in `references/source-map.md`. Prefer an automatic route. Update its line in the hub's Sources list (the Hub's "For agents" section) after the user's OK.

## Part A. Collect customers

### A1. Find where the customers are

**Inside build-gtm-context:** use the customer findings it hands you. If the customers already live in a Notion database, it's already linked.

**On its own:** ask where customers live today, and read them using the access order in `references/source-map.md`:
- **A CRM or database** (Notion, Airtable, HubSpot, Attio, Pipedrive): read won deals or customer records only. If it's a Notion database, link it instead of copying (see "Reuse before you create" in build-gtm-context's `hub-structure.md`). Add only the missing columns (Best customer, Logo shareable, Permission note) with the user's OK, and use its existing segment or persona column as the ICP segment.
- **A course, shop or payment platform** (Maven, Stripe, Shopify, Kajabi, Teachable, Gumroad): there's usually no connector, so say so. Offer to browse the customer or student list with Claude in Chrome (the user is already signed in there), or ask for a CSV export into `~/gtm-context/.private/`.
- **A list or spreadsheet**: they paste it or upload it.
- **Only in their head**: they name them.
- **No customers yet**: stop here and say the ICP will be inferred from competitors instead.

If it isn't clear from the data, ask: "B2B, B2C, or both?" For B2C, don't list individuals. Create one row per customer segment ("New parents, Milan, about 120 customers"), or keep the linked database as it is.

If they are an agency, consultant or B2B2C business, ask one more question: "Who are your clients' customers?" Save the answer for the ICP step.

### A2. Fill and enrich

Use what the user gave first, then check what's missing. The ICP needs it, so the scoring works before first contact.

1. **Count the gaps** with one query or one pass over the batch:
   - **Company:** website, size, industry, location, stage or funding.
   - **Buyer:** role or title, seniority, function, time in role.

   Never collect emails, phone numbers or personal profile URLs.
2. **Derive before you pay.** Fill what the data already implies, at no cost: seniority from the title ("Founder", "VP", "Manager"), industry from the company website or the existing segment or persona column. Only what's still missing after that counts toward enrichment.
3. **Find the enrichment tool** from the tool names listed in the session: Clay first (the Clay connector or the Clay CLI), then any other enrichment connector, such as Apollo.
4. **Ask about credits before any lookup.** Say how many companies and buyers you'd look up, which fields each lookup fills, and what that costs in that tool's credits. Count unique companies, not rows: several students often share one company. Read the cost and the remaining balance from the tool when it reports them (Clay credits and quotas, Apollo credit usage); otherwise give an estimate and say it's one. If the balance is lower than the cost, say so and suggest the best customers first. Then one AskUserQuestion: enrich all rows, the best customers plus a similar sample, or skip.
5. **No enrichment tool connected:** check whether the data is already enough for the ICP: the best customers have size, industry and buyer role on most rows. If it is, continue without enrichment. Only if it isn't, say so in one line and offer to connect the Clay connector (Claude's connector settings), then continue once it's connected or the user says no. Without enrichment, read company websites for a small sample and mark anything uncertain `(guess)`.
6. **Match carefully.** Look up companies by exact domain. A large company's domain also matches its subsidiaries and old brands, so keep the record with the most employees. Tiny firms (1 to 10 people) are often missing from company data: for them, the buyer's title carries the signal.
7. **Write back.** Write company and buyer fields to the customers database. If it lacks a column you need (for example Seniority or Buyer role), show the list and add only those, with the user's OK (`notion-update-data-source`). For a linked database, use its own columns where they exist. Note where the data came from, for example "Clay, 2026-10-30".

Tag each customer with the offers they bought (offers in scope). In a linked database, reuse its own column (for example "Products paid"); add an Offer column only with the user's OK. Never store contact names, emails or phone numbers in the context.

### A3. Best customers

Best customers drive the ICP. "Best" means they paid well, got results, came back or referred others, and were easy to work with. How to find them depends on the business.

**B2B with a short list (up to about 30 customers):** run one filtered query for the engagement signals the data has (repeat purchases, came back for more, reviews, deal size) and suggest up to 4 candidates. Ask: "Which 3 would you clone if you could?" (multiSelect, "Other" for anyone else).

**B2C, or many individual buyers:** don't ask the user to pick names. With dozens of individuals it's hard and the pick is mostly memory. Define "best" by behaviour instead:
1. List the signals the data actually has, with counts. Examples: bought twice or more, came back with a bigger request, referred someone, left a review, finished or used the product a lot, spent the most, never refunded.
2. Ask (multiSelect): "Which of these mean a great customer to you?"
3. Apply that rule with one query. The best group is usually the top 10 to 20%. If the rule catches much more (common signals like "left a review" do), show the count for the rule as picked and for one or two tighter versions ("2 or more reviews", "both signals"), and let the user choose. Then show how the chosen group differs from everyone else (roles, company size, location, how they found you).
4. Leave out partners, co-instructors, team members and free seats, even when they match.
5. After approval, tick Best customer on the matching rows and record the rule itself ("came back for more or left 2+ reviews") under "Best-customer rule" in the Hub's "For agents" section, so it can be reapplied next month. Each row is a separate update, so above about 30 rows say so before starting.

With several offers in scope, check whether the best buyers differ by offer. If they do, define the rule per offer (for example "course: came back for more; team training: renewed or expanded") and record each one.

Either way, the result is a best group plus the reason it's best. The ICP step looks for what that group shares.

### A4. Pause, then write

Show the table in the chat. After approval:
- **Dedupe in one go:** query the database once with a filter matching all company names in this batch. Update rows that exist, create the rest.
- Set Permission note to `not asked yet` on new rows, Logo shareable unticked.
- Update the Customers row in the Hub links table.

## Part B. Logo permission

### B1. Ask about each customer

Query the database for rows where Logo shareable is unticked and Permission note is `not asked yet` (filtered, not the whole table).

Explain in one line: "A logo on your website or in outreach needs the customer's OK. Only tick the ones that have actually said yes."

Then one AskUserQuestion, multiSelect: "Which of these gave you permission to show their logo publicly?" Default: none. In the same batch, ask how permission was usually given (contract clause, email, verbal) and whether quotes or results can be shared too. If the user doesn't say how, record "Permission confirmed by the user on <date> (method not recorded)".

If the user's website already shows logos of companies in this list, ask where that permission came from. A company deal (for example a team contract) doesn't cover an individual buyer's row, so leave those unticked unless the user says otherwise.

### B2. Write

Tick Logo shareable and fill Permission note, Quote and Result for the approved rows. For the rest, set Permission note to `asked, no` or leave `not asked yet` if the user wants to check first.

## Rules

- Companies only in a database this skill creates. In a linked database, read people's rows for patterns and leave personal data where it is.
- Browsing a platform is read-only. The user signs in themselves.
- Never tick Logo shareable on a guess, a public website mention, or "they probably won't mind".
- Query with filters, never read the whole database. Fetch by link, never search Notion.
