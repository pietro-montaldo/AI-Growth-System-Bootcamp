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

### A2. Fill company details

For each company, fill Website, Size, Industry and Type. Use what the user gave first. For gaps, look up the company website (WebFetch) or use an enrichment connector if one is connected (without naming it to the user). Mark anything uncertain `(guess)`. Store companies only: no contact names, emails or LinkedIn profiles.

### A3. Best customers

Best customers drive the ICP. "Best" means they paid well, got results, came back or referred others, and were easy to work with. How to find them depends on the business.

**B2B with a short list (up to about 30 customers):** run one filtered query for the engagement signals the data has (repeat purchases, came back for more, reviews, deal size) and suggest up to 4 candidates. Ask: "Which 3 would you clone if you could?" (multiSelect, "Other" for anyone else).

**B2C, or many individual buyers:** don't ask the user to pick names. With dozens of individuals it's hard and the pick is mostly memory. Define "best" by behaviour instead:
1. List the signals the data actually has, with counts. Examples: bought twice or more, came back with a bigger request, referred someone, left a review, finished or used the product a lot, spent the most, never refunded.
2. Ask (multiSelect): "Which of these mean a great customer to you?"
3. Apply that rule with one query. The best group is usually the top 10 to 20%. If the rule catches much more (common signals like "left a review" do), show the count for the rule as picked and for one or two tighter versions ("2 or more reviews", "both signals"), and let the user choose. Then show how the chosen group differs from everyone else (roles, company size, location, how they found you).
4. Leave out partners, co-instructors, team members and free seats, even when they match.
5. After approval, tick Best customer on the matching rows and record the rule itself ("came back for more or left 2+ reviews") under "Best-customer rule" in the Hub's "For agents" section, so it can be reapplied next month. Each row is a separate update, so above about 30 rows say so before starting.

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
