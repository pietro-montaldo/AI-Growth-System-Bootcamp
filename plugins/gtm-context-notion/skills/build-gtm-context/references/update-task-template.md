# Template: the student's scheduled update (Notion)

The handover (`handover.md`, step 3) fills this in. It has two parts: the task prompt (between the task markers) becomes the `gtm-update` scheduled task, and the review guide (between the guide markers) goes onto the "Updates to review" page. How to fill it:
- Replace every `{{...}}` with the real links, data source IDs and filters from the Hub's "For agents" section, and the plan from handover step 1.
- Where a line says `PASTE`, paste the named part of the file from this skill's `references/` folder, word for word.
- Delete what the student doesn't have: database lines for skipped sections, the example rows, and steps for source types they don't use (for example the Claude in Chrome step when no line is `auto, app only`).
- Keep their own column, theme and persona names where a linked database uses them.
- The email address or Slack member ID goes only on the task prompt's Alert line, never on a page.
- Leave out the markers themselves.

<!-- task starts -->
# Weekly GTM update for {{company}}

Made by the AI Growth Systems Bootcamp setup on {{YYYY-MM-DD}}. This prompt is the whole update. To change it, edit this task, or ask Claude to "change my GTM update settings".

Scheduled run of the GTM update. Do not ask questions. Alert: {{email to <address> | Slack DM to <member ID>}}. Enrich new customers: {{no | yes, with <tool>, up to <n> lookups per run}}.

Offers in scope: {{offer 1}} · {{offer 2}}. Tag every new row and quote with its offer.

## Where things live

- **GTM Hub (Notion):** {{Hub link}}. Its links table lists every page. Its "For agents" section holds the best-customer rule and the "Last run" dates.
- **Updates to review:** {{link}}
- **Pages:** Product & offer {{link}} · ICP {{link}} · Messaging & customer language {{link}}
- **Customers:** {{database link}} · data source `{{collection://...}}` · filter: {{filter, or "none"}} · columns: {{only the names that differ from the standard ones, for example Best customer = "Top customer"}}
- **Objections:** {{database link}} · data source `{{collection://...}}` · filter: {{...}} · columns: {{...}}
- **Competitors:** {{database link}} · data source `{{collection://...}}`

Fetch pages by these links and never search Notion for them. Query databases with filters, never read them whole.

## Where new information comes from

| Bucket | Source | How to get in | Who |
|---|---|---|---|
| {{bucket}} | {{source}} | {{connector, public page, Claude in Chrome, export or paste}} | {{auto, auto (app only), you (how often), none}} |
| Customers | Course dashboard, students page | Claude in Chrome, read-only | auto (app only) |
| Customers | Student list export | You drop a fresh CSV into `~/gtm-context/.private/` | you, monthly |

## Steps

Follow the update rules at the end: no questions, skip and log any source that fails, alert only the user.

1. **Load.** Fetch the Hub and read its "For agents" section: the best-customer rule and the "Last run" dates. Each bucket's window starts at its last run date, or 30 days ago.
2. **Decide the scope.** It's a full check if the last full check was in an earlier calendar month. Otherwise it's a weekly run.
3. **Read, in parallel and in the background,** with the reading briefs below:
   - One agent per conversation source in the plan, with the window.
   - New customers since the window start, from the customer sources in the plan.
   - Full check only: one agent per product and proof source, in compare mode, with the current Product & offer page as the baseline.
   - `auto (app only)` lines: read them yourself with Claude in Chrome, one page at a time, read-only. If Chrome isn't available, log the source under "Couldn't read".
   - `you` lines: read only a new file in `~/gtm-context/.private/` or pasted text. Otherwise, when one is due, add a reminder to the alert.
4. **Update the banks (automatic):**
   - **Customers:** dedupe with one filtered query for this batch's company names. Create new rows at company level with their offer and Permission note `not asked yet`. If "Enrich new customers" is yes, fill company and buyer fields for the new rows only, within the lookup limit above (never emails or phone numbers). Tick Best customer where the rule matches.
   - **Objections:** run one filtered query for the themes in this batch and compare by meaning, not exact wording. A repeat gets Times seen and Last seen updated (where those columns exist). A new one gets a row with Answer status `draft`.
   - **Quotes:** add the 5 to 10 strongest new quotes to a "New quotes (unreviewed, <date>)" section at the bottom of the Messaging page, with `insert_content` at the end. Never edit the top of the page.
5. **Find what needs a decision (proposed updates only):** every difference the compare-mode readers returned, value props or word lists that new quotes contradict, ICP drift per offer (full check), and staleness (passed dates, old drafts).
6. **Write the report** as a child page of "Updates to review", titled `GTM update <date>`, in the format below. Then update the Hub callout's "Last refreshed" line, and the "Last run" line in the "For agents" section (anchor the edit on its plain-text label).
7. **Send the alert** in the format below, with the report link, to the address on the Alert line above only. If sending fails, leave a draft and note it in the report.

## Reading briefs

Start one general-purpose agent per source, all in one message, in the background, and give each the brief below with the source, how to reach it, the window, and the offers in scope: {{each offer in scope, with a one-line summary}}. Tag every row with its offer. If agents aren't available in this run, read each source yourself with the same brief.

**Conversation source** (calls, email, DMs). Read external conversations about the offer in the window, then return customer language and objections.

PASTE `mining-playbook.md`: the sections "What to read", "What to extract", "Rules" and "Objection themes".

Return a LANGUAGE table (Type, Quote, Who, Offer, Times, Source), an OBJECTIONS table (Theme, Objection, Quote, Offer, Stage, Answer given, Moved forward, Times, Source), and up to 3 lines of notes on what you couldn't read.

**Product or proof source, compare mode** (full check only). Read the source, compare it with the baseline page you're given, and report only facts that differ. Ignore wording changes that don't change a fact. Return ADDED, REMOVED and CHANGED lines (`<bucket>: <field>: "<baseline value>" -> "<source value>" [source]`), one UNCHANGED line, and FLAGS for passed dates or contradictions. No personal data: role and company type only.

## Update rules

PASTE `update-playbook.md`: everything from "## What may change without the user" to the end.
<!-- task ends -->

<!-- guide starts -->
## How to review GTM updates

When the user says "review GTM updates" or follows an alert, in any Claude session:

1. Open the newest report below, and any older ones with `open` items.
2. Show the summary. Then go through the open proposed updates in batches of up to 4, with one AskUserQuestion: apply, edit, or reject.
3. **Apply** each approved one: fetch the page, show the before and after, and change only the part it names (`notion-update-page`, `update_content`, anchored on plain text). Update that page's "Last updated" date in the Hub links table. If ICP names change, ask before changing the ICP segment values on customers.
4. **Draft objections:** query Objections ({{data source}}) for Answer status `draft`. The user confirms or edits each answer. Set `works` only when they say it works.
5. **New customers** with Permission note `not asked yet`: ask which ones gave permission to show their logo. Tick Logo shareable only on an explicit yes, and write how and when in Permission note.
6. **Quotes** under "New quotes": move the good ones into the right sections of the Messaging page, the rest to "More quotes".
7. Mark each item `applied` or `rejected` in the report, and set the Hub's "Last refreshed" line to 0 open updates.

Every write is shown first. No personal names, emails or profile URLs: role and company type only.

## How to change the update settings

The settings live in the prompt of the scheduled task `gtm-update`.
- **Change the plan, alert or schedule:** edit the task in the Claude app (Scheduled, then Weekly GTM update), or ask Claude in Claude Code, which reads the task file and changes it with `update_scheduled_task`. Show the diff first.
- **A new source:** decide whether it keeps updating on its own (a CRM, inbox, call recorder, dashboard) or was a one-off (a file, a pasted list). For a one-off, ask where that information will show up from now on. Then add one line to the "Where new information comes from" table: source, how to get in, and who gets it (auto, auto app only, you, none).
- **Also update** the "Updates" lines in the Hub's "For agents" section when the schedule or alert channel changes.
- **Bigger changes** (a new ICP from scratch, a first competitor study, a new offer): install the course plugin again and run that section. Its handover then rewrites this task.
<!-- guide ends -->
