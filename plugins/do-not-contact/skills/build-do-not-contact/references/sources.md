# Where the people on the list come from

Most of the list already exists, spread across the student's tools. The build finds it there instead of asking the student to remember names.

## What to collect, and from where

| Who | Reason | Scope | Where they usually are |
|---|---|---|---|
| People who said no or asked to stop | said no | person | Email replies, LinkedIn DMs, CRM notes, deals marked lost with "not interested" |
| "Not now, maybe later" | not now, Until = 6 months from the reply | person | Email replies, DMs, CRM notes |
| Unsubscribes | unsubscribed | person | Sending tool (Instantly, Smartlead, lemlist, Apollo and others), newsletter tool |
| Bounces | bounced | person | Sending tool, bounce notices in the inbox |
| Customers | customer | company for B2B, person for B2C | CRM, payment or course platform (Stripe, Maven, Shopify, Kajabi), invoices |
| Open deals | open deal | company for B2B, person for B2C | CRM pipeline |
| Partners, investors, friends | partner or personal | person or company | The student's head, a partners list, CRM tags |
| Competitors | competitor | company | A competitors list or the GTM context |
| Anyone who asked to have their data deleted | erasure request | person | Inbox, support desk |

**B2B or B2C?** Ask once if it isn't obvious.
- B2B customers and open deals block the whole company domain, so no one at a customer gets a cold email.
- B2C buyers are blocked one person at a time.

## How to ask

Show the table and ask the student to answer in one message: for each row, name the tool, paste a link, or say "none". A rough pointer is enough.

If they use the GTM context kit, read its Hub or `gtm/README.md` "Sources" first. The CRM, inbox and platforms are already listed there, so only confirm them.

## How to get into each source (in this order)

1. **A connector is available** (Gmail, Outlook, HubSpot, Notion, Attio, Stripe and others): use it.
2. **No connector:** say so plainly, for example "There's no Instantly connector in this session." Then offer the next options.
3. **Browse, read only.**
   - Use Claude in Chrome for signed-in dashboards. The student signs in themselves. Never type a password.
   - Read summary and export pages only. Never click anything that sends, deletes or changes settings.
   - Close the tabs you opened.
4. **Export a file.** Almost every sending tool and CRM can export unsubscribes, bounces, customers or deals as CSV. Ask the student to save it in `~/do-not-contact/.private/`. Delete it once read.
5. **Paste.** Always works.

**LinkedIn is paste only.** Never read the LinkedIn inbox with an automation or a scraper: it can get the student's account limited. The student pastes the profile links of people who said no, or adds them one at a time later with "add <profile link>, said no on LinkedIn".

## What counts as a no in an email reply

Only replies the person wrote to the student, in the window (default: last 12 months for the build, since the last run after that).

| Add as | When the reply says something like |
|---|---|
| said no | "not interested", "please stop", "remove me", "don't contact me", "no thanks", "we're not looking", a clear no in any language |
| unsubscribed | "unsubscribe", "take me off your list" |
| not now (Until = reply date + 6 months) | "not right now", "maybe next year", "reach out in Q3", "too busy at the moment" |
| erasure request | "delete my data", "GDPR request", "forget me" |
| bounced | an automatic bounce notice ("address not found", "mailbox unavailable") for an address the student sent to |
| unsure, not added | anything else that might be a no: "we already have someone for this", "send me more info" followed by silence, a sarcastic reply, a reply from an assistant |

- An out-of-office reply is not a no. A "no" about one offer is still a no to cold outreach. Add it.
- When in doubt, put it under unsure. The student decides. Adding someone wrongly costs one lost lead. Missing a real no costs trust.

## Will each source stay current?

The build reads each source once. The weekly update needs to know where new no's will come from. For each source, settle one line:
- **auto:** a connector. Works in any scheduled run.
- **auto (app only):** needs Claude in Chrome, so it only runs as a scheduled task in the Claude app, while the computer is on.
- **you:** an export or a paste. The weekly alert reminds the student, for example "Export last week's unsubscribes from your sending tool into the private folder".

Write the plan in the `Read me` tab (Sheet) or the `Sources` table (Notion).
