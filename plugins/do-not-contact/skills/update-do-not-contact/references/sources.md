# Who goes on the list, and where they are

The student decides who goes on the list. Claude interviews, advises and reads only the places the student names. It never goes looking through tools on its own.

## The interview

1. **Open question first.** "Who should your outreach never reach? Think of people you'd be embarrassed or sorry to cold-message." Let them answer in their own words. Don't show a form.
2. **Play it back as groups.** Turn their answer into groups from the table below, in their words where you can.
3. **Advise on what's missing.** Suggest the groups they didn't mention, one line each on why it matters. For example: "Customers: a cold pitch to someone who already pays you feels careless." They say yes or no to each. Never add a group they didn't confirm.
4. **B2B or B2C?** Ask once, only if it isn't obvious.
5. **The CRM check** (below).

## Groups people usually keep off-limits

| Group | Reason | Scope | Why it matters | Where they often are (suggestions only) |
|---|---|---|---|---|
| Customers | customer | company for B2B, person for B2C | A cold pitch to a paying customer feels careless | CRM, payment or course platform (Stripe, Maven, Shopify, Kajabi), invoices |
| Open deals | open deal | company for B2B, person for B2C | A cold email in the middle of a deal confuses the buyer | CRM pipeline |
| Friends and family | personal | person | Automated outreach to people close to you is awkward | Their head, phone contacts, a list they paste |
| Partners and investors | partner | person or company | They expect a personal message, not a sequence | Their head, a partners list, CRM tags |
| Competitors | competitor | company | Pitching them gives away your playbook | A competitors list, the GTM context |
| People who said no or asked to stop | said no | person | Contacting them again costs trust and can get you reported | Email replies, LinkedIn DMs, CRM notes, deals lost as "not interested" |
| "Not now, maybe later" | not now, Until = 6 months from the reply | person | They asked for time, so you wait | Email replies, DMs, CRM notes |
| Unsubscribes | unsubscribed | person | Required by law in most countries | Sending tool (Instantly, Smartlead, lemlist, Apollo and others), newsletter tool |
| Bounces | bounced | person | Sending again hurts deliverability | Sending tool, bounce notices in the inbox |
| Anyone who asked to have their data deleted | erasure request | person | A legal request | Inbox, support desk |

- B2B customers and open deals block the whole company domain, so no one at a customer gets a cold email.
- B2C buyers are blocked one person at a time.
- Anyone the student names who fits no group goes in with Reason `other` and a short Note.

## The CRM check

Ask about the groups they picked, by name: "Do you already keep all of these in a CRM: <their groups>?"

**When the CRM is the list.** If the answer is yes for every group they picked (bounces and unsubscribes can stay in the sending tool, as long as it checks the CRM before sending), the CRM already is their do-not-contact list. A second list would be a copy that drifts out of date. Say so plainly and build nothing. Instead, give these tips in a few lines:
- Mark every off-limits contact in the CRM with one clear status or tag, for example "Do not contact", with the reason.
- Connect the sending tool to the CRM, or switch on its own blocklist, so it skips those contacts before every send.
- Tell any new outreach system to check the CRM first.
- If some groups later live outside the CRM (a pasted list of friends, a separate sending tool), run this guide again.

Then offer the CRM version of the pointer (`storage.md`, "The pointer"), after one OK, so the check and update skills know the CRM is the list.

**When the CRM is only part of it.** Carry on. The CRM becomes one of the places in the next step, read for the groups it holds.

## Where each group lives

For each group the student picked, ask two things. They answer; Claude advises.
1. **Where are these people today?** Offer the usual places from the table as suggestions, never as assumptions. Read only the places the student names. "None" is a fine answer.
2. **Where will new ones show up from now on?** For example "new buyers appear in Stripe" or "I'll paste new partners when I sign them". This becomes the weekly update plan (see "Will each source stay current?").
   - If it's a different place from today's (customers in an old spreadsheet, new ones in Stripe), the new place gets its own plan row. The build reads only today's place. The weekly run reads the new place from the build day on.

Ask for an email, a profile link or a website, never just a name. "My cousin Marco" needs Marco's email or LinkedIn link. Names never go in the list or its Note.

Then settle access for each place, in the order below. Groups that live only in the student's head (friends, family, some partners) are typed or pasted now, and added later with "add <email>, friend".

If they use the GTM context kit, its Hub or `gtm/README.md` "Sources" may already name their CRM, inbox and platforms. Use it to make better suggestions, then let the student confirm.

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
- **you:** an export or a paste on a rhythm. The weekly alert reminds the student, for example "Export last week's unsubscribes from your sending tool into the private folder".
- **you (when it happens):** groups only the student knows about, like friends, family and partners. No reminder. They add people with "add <email>, friend" whenever it comes up.

A cloud scheduled task only reaches connectors. It can't use Claude in Chrome or read exports on the student's computer, so with a cloud task every "auto (app only)" and "you" source becomes a reminder in the weekly summary. "you (when it happens)" never does.

Write the plan, with the groups for each source, in the `Read me` tab (Sheet) or the `Sources` table (Notion).
