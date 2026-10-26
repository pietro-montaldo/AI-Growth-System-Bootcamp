---
name: gtm-product
description: "Write or refresh the Product & offer page of the GTM Hub in Notion: what you sell, the result it gives, offers and prices, and what it is not. Starts from a website link, pasted text or a dictated description, drafts one screen, and writes it only after you approve. Use for \"describe my product\", \"update my offer\", \"we changed pricing\", \"product description for my GTM context\", or as step 1 of build-gtm-context. Not for the ICP (use gtm-icp) or competitor research (use gtm-competitors)."
metadata:
  version: "0.1.0"
---

# Product & offer

Every other section builds on this page: the ICP says who it's for, messaging says how to talk about it, objections say what stops people buying it. So it has to be short, concrete, and in plain words a buyer would use.

## Reference files

- `references/page-template.md`: the page layout to fill.
- `references/sections.md`: the quality bar for every GTM section.
- `references/source-map.md`: where this usually lives and how to get in (connector, browser, export, paste).

## Before starting

1. Read `gtm-hub.md` in the project folder. If it's missing, the Hub isn't set up yet: run the build-gtm-context skill first, which sets it up and then continues here.
2. Fetch the Product & offer page by its link. If it already has content, summarise it in three lines and ask what changed, then update only that part.

## Steps

### 1. Get the raw material

**Inside build-gtm-context:** use the product findings it hands you and go to step 2.

**On its own:** ask where it's already written down: a sales or course page, a deck, a proposal, a Notion or Google doc. Read every source they point to, using the access order in `source-map.md`. For a website, fetch the homepage, then the pricing, product or services, and about pages. Up to 5 pages per site.

Only if nothing is written down, ask them to dictate: talk freely for a minute about what they sell, who buys it and what changes for the buyer. Voice dictation works fine.

If they sell several things, ask which one this context is for. One GTM context per main offer keeps every later agent focused. Other offers can sit in the offers table.

### 2. Fill the gaps

Draft the page from the material. Then ask only for what is still missing, at most 4 questions in one batch. Typical gaps:
- The result for the buyer, as a number or a before/after ("from 2 calls a month to 2 a week").
- The price or price range, and how they charge (project, retainer, seat, one-off).
- What it is not, or who should not buy it.
- Their strongest proof: one result, one client, one number. Logos come later, in gtm-customers.

Mark anything you inferred and couldn't confirm with `(guess, confirm)`.

### 3. Pause: show the draft

Show the full page in the chat. Ask "What's wrong or missing?" Apply the edits. Repeat until the user approves. Don't write on silence.

### 4. Write to Notion

- Replace the page content with the approved draft using `notion-update-page`.
- Update the page's row in the Hub links table: one-line summary and today's date.

### 5. Confirm

One line with the page link. If running inside build-gtm-context, hand back the product summary (the first 3 lines of the page), because later steps need it.

## Rules

- One or two screens. Summary first, examples and details further down.
- Plain buyer words. No "leverage", "solutions", "empower", "seamless".
- Never invent prices, numbers or clients. Ask, or mark `(guess, confirm)`.
- Fetch by link, never search Notion. Never copy this content into the project folder.
