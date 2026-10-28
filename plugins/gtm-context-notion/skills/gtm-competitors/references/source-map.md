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

## How to ask

Show the table in the chat and ask the user to answer in one message: for each bucket, paste a link, name the tool, or say "none". Tell them a rough pointer is enough ("it's in my Maven dashboard", "somewhere in Notion"). Don't use AskUserQuestion for this: links don't fit multiple-choice options.

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
4. **Export a file.** Most platforms can export customers or students as CSV. Ask the user to export it into the project folder (or attach it). It's often faster than browsing many pages.
5. **Paste.** Always works.

## After reading

- Show a short "What I found" table: bucket, sources read, found / partly / nothing.
- Record each source in the hub's "Sources" list (the Notion Hub's "For agents" section, or `gtm/README.md` in the GitHub version): its link, and how to get in (connector, browser, export). This way a later refresh reads the same places without asking again. Links only, never the content.
- Every section skill then drafts from what was found and asks only about what's still missing.

## Privacy

- Read customer lists for patterns (roles, company types, sizes, engagement), not to copy people into the context. Personal names, emails and profile URLs stay where they are.
- Exported files with personal data stay out of any public repo.
