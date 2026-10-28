---
name: gtm-customers
description: "Build or update your customers bank for the GTM context in your repo: who already buys from you, which ICP segment each belongs to, which ones are your best customers, and which logos you have permission to show publicly. Reads customers from wherever they live (CRM, Notion or Airtable, course or payment platform, spreadsheet) and links a connected system instead of copying it. Use for \"add my customers\", \"which logos can I show\", \"update my customer list\", \"we have a new client\", \"customers I can share publicly\", or as part of build-gtm-context. Not for leads or prospects (those belong in a lead ledger or CRM) and not for the ICP itself (use gtm-icp)."
metadata:
  version: "0.2.0"
---

# Customers

Existing customers are the best evidence for the ICP, and shareable logos are the cheapest proof in outreach. This skill keeps customers at company level, marks the best ones, and records logo permission explicitly.

It has two parts. Run both when used on its own. Inside build-gtm-context, part A runs early (step 5) and part B runs near the end (step 10).

## Reference files

- `references/source-map.md`: where customers usually live and how to get in (connector, browser, export, paste).
- `scripts/gtm_csv.py`: query and update `gtm/customers.csv`. Call it by its full path in this skill's folder. Columns and allowed values are in the guide's `repo-structure.md`, and the first line of the file is the header.

## Before starting

1. Read `~/gtm-context/gtm/README.md`. Every `gtm/` path in this skill is inside `~/gtm-context/`, the student's private gtm-context repo, whatever project they are in. If it's missing, run the build-gtm-context skill first, which sets up the folder.
2. Check the "Sources" list: if customers live in a connected system (CRM, Notion, Airtable, Sheets), work there and don't create `gtm/customers.csv`. Otherwise use the CSV.

## Part A. Collect customers

### A1. Find where the customers are

**Inside build-gtm-context:** use the customer findings it hands you.

**On its own:** ask where customers live today, and read them using the access order in `references/source-map.md`:
- **A CRM or database with a connector** (HubSpot, Attio, Pipedrive, a Notion or Airtable database, a Google Sheet): read won deals or customer records only, link it under "Sources" with the filter that selects this offer's customers, and keep working there. Ask before adding any column to their system.
- **A course, shop or payment platform** (Maven, Stripe, Shopify, Kajabi, Teachable, Gumroad): there's usually no connector, so say so. Offer to browse the customer list read-only with Claude in Chrome (the user is already signed in there), or ask for a CSV export into `gtm/.private/`. Build `gtm/customers.csv` from it at company level.
- **A list or spreadsheet**: they paste it or put it in `gtm/.private/`.
- **Only in their head**: they name them.
- **No customers yet**: stop here and say the ICP will be inferred from competitors instead.

If it isn't clear from the data, ask: "B2B, B2C, or both?" For B2C, don't list individuals. Create one row per customer segment ("New parents, Milan, about 120 customers").

If they are an agency, consultant or B2B2C business, ask one more question: "Who are your clients' customers?" Save the answer for the ICP step.

### A2. Fill company details

For each company, fill Website, Size, Industry and Type. Use what the user gave first. For gaps, look up the company website or use an enrichment connector if one is connected (without naming it to the user). Mark anything uncertain `(guess)`. Companies only: no contact names, emails or LinkedIn profiles.

### A3. Best customers

Best customers drive the ICP. "Best" means they paid well, got results, came back or referred others, and were easy to work with. How to find them depends on the business.

**B2B with a short list (up to about 30 customers):** look at the engagement signals the data has (repeat purchases, came back for more, reviews, deal size) and suggest up to 4 candidates. Ask: "Which 3 would you clone if you could?" (multiSelect, "Other" for anyone else).

**B2C, or many individual buyers:** don't ask the user to pick names. With dozens of individuals it's hard and the pick is mostly memory. Define "best" by behaviour instead:
1. List the signals the data actually has, with counts. Examples: bought twice or more, came back with a bigger request, referred someone, left a review, finished or used the product a lot, spent the most, never refunded.
2. Ask (multiSelect): "Which of these mean a great customer to you?"
3. Apply that rule (with the helper's `count` and `--min` filters, or a query in the connected system). The best group is usually the top 10 to 20%. If the rule catches much more, show the count for the rule as picked and for one or two tighter versions ("2 or more reviews", "both signals"), and let the user choose. Then show how the chosen group differs from everyone else (roles, company size, location, how they found you).
4. Leave out partners, co-instructors, team members and free seats, even when they match.
5. After approval, mark Best customer on the matching rows in one `upsert` batch (or in the connected system), and write the rule itself under "Best-customer rule" in `gtm/README.md` so it can be reapplied next month.

Either way, the result is a best group plus the reason it's best. The ICP step looks for what that group shares.

### A4. Pause, then write

Show the table in the chat. After approval:
- Write all rows with one `upsert` keyed on Company. It updates existing companies and adds the rest.
- Set Permission note to `not asked yet` and Logo shareable to `no` on new rows.
- Delete the raw export from `gtm/.private/` once the rows are in, and say so.
- Update the Customers row in the `gtm/README.md` table.

## Part B. Logo permission

### B1. Ask about each customer

Query only the rows where Logo shareable is `no` and Permission note is `not asked yet`.

Explain in one line: "A logo on your website or in outreach needs the customer's OK. Only mark the ones that have actually said yes."

Then one AskUserQuestion, multiSelect: "Which of these gave you permission to show their logo publicly?" Default: none. In the same batch, ask how permission was usually given (contract clause, email, verbal) and whether quotes or results can be shared too. If the user doesn't say how, record "Permission confirmed by the user on <date> (method not recorded)".

If the user's website already shows logos of companies in this list, ask where that permission came from. A company deal (for example a team contract) doesn't cover an individual buyer's row, so leave those as `no` unless the user says otherwise.

### B2. Write

Set Logo shareable to `yes` and fill Permission note, Quote and Result for the approved rows. For the rest, set Permission note to `asked, no`, or leave `not asked yet` if the user wants to check first.

## Rules

- Companies only in `customers.csv`. In a linked system, read people's rows for patterns and leave personal data where it is.
- Browsing a platform is read-only. The user signs in themselves.
- Never mark Logo shareable on a guess, a public website mention, or "they probably won't mind".
- Query with filters, never read the whole bank. Write only with `upsert`.
