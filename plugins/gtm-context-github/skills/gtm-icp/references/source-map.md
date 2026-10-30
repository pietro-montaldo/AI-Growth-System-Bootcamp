# Source map: find what already exists before asking

Most users already have a lot of their GTM context somewhere: a sales page, a CRM, a course platform, an old ICP doc, a spreadsheet of objections. Asking them to retype it wastes their time and produces a worse result. So every build starts by finding those sources, reading them, and drafting from them. Questions come last, and only for real gaps.

## The buckets and where they usually live

| Bucket | Where it often lives |
|---|---|
| Product & offer | Website, sales or course page (Maven, Gumroad, Kajabi, Teachable), deck, proposal, a Notion or Google doc |
| Customers | CRM (HubSpot, Attio, Pipedrive, a Notion or Airtable database), payment or course platform (Stripe, Maven, Shopify, Teachable, Kajabi, Gumroad), invoices, a spreadsheet |
| Competitors | A battle card or comparison doc, sales notes, the user's head |
| Customer language | Call recorder (Fathom, Granola, Gong, Fireflies), recordings of free webinars and live sessions (the audience's questions), email, LinkedIn DMs, reviews (G2, Trustpilot, Google, course platform reviews), surveys, testimonials |
| Objections | An objections doc or database, call notes, an FAQ page, refund or cancellation reasons in the platform, the support inbox |
| Proof and shareable customers | Logos and case studies on the website, testimonial pages, review platforms |
| Anything else | Case studies, pitch decks, sales one-pagers, pricing sheets, battle cards, brand or tone guides, webinar slides, FAQ pages |

## How to ask

Show the table in the chat and ask the user to answer in one message: for each bucket, paste a link, name the tool, or say "none". Tell them a rough pointer is enough ("it's in my Maven dashboard", "somewhere in Notion"). Don't use AskUserQuestion for this: links don't fit multiple-choice options.

End the message with one open question: "Is there any other GTM context you'd like included that isn't in this list? For example case studies, a pitch deck or a pricing sheet." Extras are linked from the hub, never copied: one row each in the hub's links table (`Resource: <name>`, the link, one line on what it's for). Read them like any other source, and use what fits a section: a case study feeds proof and the customers bank (Result, Case study), a deck or pricing sheet feeds Product & offer, a battle card feeds Competitors.

If they say "it's somewhere in my Notion / Drive" and that connector is available, run one plain search per bucket ("ICP", "customers", "objections", "case study"), show what you found, and let them confirm which ones to use.

## How to get into each source (in this order)

1. **A connector is available** (Notion, Google Drive, Gmail, HubSpot, Fathom and so on): use it.
2. **No connector for that tool:** say it plainly, for example "There's no Maven connector in this session." Then offer the options below. If a connector exists for the tool but isn't enabled, tell them where to turn it on (Claude's connector settings) and wait.
3. **Browse to it.** Many sources are dashboards without a connector (Maven, Stripe, Kajabi, Shopify admin). Use a browser tool:
   - **Claude in Chrome** uses the user's own Chrome, where they're usually already signed in. This is best for private dashboards.
   - **The app's built-in browser** works for public pages, and for private ones once the user signs in there.
   - The user signs in themselves. Never type a password. Read only: go to the page they named, read it, and don't click anything that changes data, sends messages, issues refunds or changes settings.
   - Read one page at a time in the main conversation, because the browser is shared.
   - Start with summary pages (dashboard, product list, sales and student counts). Open individual customer records only if no database already holds them.
   - Close the tabs you opened when you're done.
4. **Export a file.** Most platforms can export customers or students as CSV. Ask the user to attach it or export it into the private folder for raw exports (`~/gtm-context/.private/` in the Notion version, `~/gtm-context/gtm/.private/` in the GitHub version). Don't keep it in the project folder. It's often faster than browsing many pages.
5. **Paste.** Always works.

## Offers: one or several?

Before anything is drafted, list every offer the sources show: courses, services, products, workshops, retainers, with a one-line description and price where known. Then ask with AskUserQuestion (multiSelect): "Which of these should your GTM context cover?" Offer the full list (up to 4 options; list more in the chat), with "All of them" first.

The answer is the **offers in scope**. Record it in the hub summary and in the hub's settings ("Offers in scope"), and pass it to every section and every reading agent. Every section then covers each offer in scope: the product page has one section per offer, customers and objections are tagged with their offer, the ICP page has one block per offer, and messaging has value props per offer. Offers left out get one line each on the product page, nothing more.

## Where each item comes from, now and later

The build reads each source once. Updates later need to know, item by item, how the information was collected, where new information will come from, and who brings it in. Settle this right after access (build step 1.6), for every item: products and offers, customers, objections, customer language, proof and logos, competitors, and every extra resource. The goal is that you can keep most items current yourself.

For each item, settle three things, using judgement instead of asking about the obvious ones:
1. **How it was collected.** Read the source's description, columns and notes. For example: "objections log filled by hand from Fathom calls and Gmail", "customers database built from Maven exports", "case studies written once on the website".
2. **Where new information will come from.** A **live** source keeps changing on its own (a CRM, an inbox, a call recorder, a course or payment dashboard, the website, a database the team keeps adding to): read it again later. A **snapshot** was true on the day it was shared (an uploaded or exported file, a pasted list, a one-off doc, a log nobody adds to anymore): go to its origin. For example: "You gave me a customer list as a file. Where do new customers show up from now on: a payment dashboard, the CRM, an email when someone buys?" Or: "Does your team still add to this objections log? If not, I'll read new objections straight from your calls and email."
3. **Who brings it in:**
   - **auto:** a connector, or a public page. Works in any scheduled run.
   - **auto, app only:** needs a signed-in browser (Claude in Chrome or the app's built-in browser), so it works only in a scheduled task in the Claude app, while the computer is on.
   - **you (how often):** no way to get it unattended. The user drops a fresh export or pastes it, and each update alert reminds them when it's due.
   - **none:** it doesn't change (a past case study). Never reread.

A local folder (screenshots, a proof index, files on the user's computer) can only be read when that computer is connected: link it from the hub as a `Resource:` row, mark its line `auto, app only`, and keep any upkeep of the folder itself as its own separate task.

Prefer automatic. For every line that would be `you`, first look for an automatic route and propose it: a connector for the same tool, notification emails the platform sends (new sale, new enrolment, new review) read through the email connector, a public page, or the origin of a hand-kept log. Only leave it as `you` when nothing else works.

Show the whole plan as one table (item, how it was collected, new information from, who), with your proposal on every line, and ask only about the lines you couldn't settle, in one message. Record each line in the hub's Sources list:
`- <item>: <built from> · via: <how to get in> · new info from: <source> · who: <auto | auto, app only | you (how often) | none>`

## After reading

- Show a short "What I found" table: bucket, sources read, found / partly / nothing.
- Every source is already in the hub's "Sources" list from step 1.6 (the Notion Hub's "For agents" section, or `gtm/README.md` in the GitHub version): what the build read, how to get in, where new information comes from and who brings it in. Links only, never the content.
- Every section skill then drafts from what was found and asks only about what's still missing.

## Privacy

- Read customer lists for patterns (roles, company types, sizes, engagement), not to copy people into the context. Personal names, emails and profile URLs stay where they are.
- Exported files with personal data stay out of any public repo.
