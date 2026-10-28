# Template: the student's update skill (Notion)

The handover (`handover.md`, step 3) fills this in and writes it as `SKILL.md` in the student's own plugin. How to fill it:
- Replace every `{{...}}` with the real links, data source IDs and filters from the Hub's "For agents" section, and the plan from handover step 1.
- Delete what the student doesn't have: database lines for skipped sections, the example rows, and steps for source types they don't use (for example the Claude in Chrome step when no line is `auto, app only`).
- Keep their own column, theme and persona names where a linked database uses them.
- Never write an email address or Slack member ID into the file. Those stay in the scheduled prompt.
- Copy everything between the two marker lines, without the markers.

<!-- skill starts -->
---
name: update-gtm-context
description: "Keep {{company}}'s GTM context in Notion up to date. Reads new customers, objections and buyer quotes from the sources in its plan, adds them to the GTM Hub's databases on its own, checks once a month that offers, prices and the website still match, and turns anything that needs a decision into proposed updates you approve. Three modes: scheduled run, review, and change settings. Use for \"update my GTM context\", \"run the GTM update\", \"review GTM updates\", \"what changed in my GTM context\", \"change my GTM update settings\", \"add a source to my GTM updates\", or when a scheduled run starts. Not for building a new section from scratch (install the course plugin again for that)."
---

# Update {{company}}'s GTM context

Made for {{company}} by the AI Growth Systems Bootcamp setup on {{YYYY-MM-DD}}. It's yours: say "change my GTM update settings", or edit this file in your `gtm-update` repo.

## References

- `references/update-playbook.md`: what may change on its own and what may not, the rules for unattended runs, and the report and alert formats. Read it first.
- `references/mining-playbook.md`: what counts as customer language and objections.
- `references/source-map.md`: how to get into a source, and how to plan a new one.

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

## Pick the mode

- **Scheduled run:** the prompt says "scheduled run", or the user says "run the GTM update" or "update now".
- **Review:** the user says "review GTM updates", or follows an alert.
- **Change settings:** the user wants to add or remove a source, or change the alert or the schedule.

## Scheduled run

Follow the unattended rules in `update-playbook.md`: no questions, skip and log any source that fails, alert only the user.

1. **Load.** Fetch the Hub and read its "For agents" section: the best-customer rule and the "Last run" dates. Each bucket's window starts at its last run date, or 30 days ago.
2. **Decide the scope.** It's a full check if the last full check was in an earlier calendar month, or the user asked for one. Otherwise it's a weekly run.
3. **Read, in parallel and in the background:**
   - One `language-miner` per conversation source in the plan, with the window and "extract: both".
   - New customers since the window start, from the customer sources in the plan.
   - Full check only: one `source-reader` per product and proof source, in compare mode, with the current Product & offer page as the baseline.
   - `auto (app only)` lines: read them yourself with Claude in Chrome, one page at a time. If Chrome isn't available, log the source under "Couldn't read".
   - `you` lines: read only a new file in `~/gtm-context/.private/` or pasted text. Otherwise, when one is due, add a reminder to the alert.
   - If the agents aren't available in this run, read each source yourself, one at a time.
4. **Update the banks (automatic):**
   - **Customers:** dedupe with one filtered query for this batch's company names. Create new rows at company level with Permission note `not asked yet`. Tick Best customer where the rule matches.
   - **Objections:** run one filtered query for the themes in this batch and compare by meaning, not exact wording. A repeat gets Times seen and Last seen updated (where those columns exist). A new one gets a row with Answer status `draft`.
   - **Quotes:** add the 5 to 10 strongest new quotes to a "New quotes (unreviewed, <date>)" section at the bottom of the Messaging page, with `insert_content` at the end. Never edit the top of the page.
5. **Find what needs a decision (proposed updates only):** every difference the compare-mode readers returned, value props or word lists that new quotes contradict, ICP drift (full check), and staleness (passed dates, old drafts).
6. **Write the report** as a child page of "Updates to review", titled `GTM update <date>`, in the playbook's format. Then update the Hub callout's "Last refreshed" line, and the "Last run" line in the "For agents" section (anchor the edit on its plain-text label).
7. **Send the alert** in the playbook's format, with the report link, to the address or DM in the scheduled prompt only (in a manual run, ask). If sending fails, leave a draft and note it in the report.

## Review

1. Open the newest report under "Updates to review", and any older ones with `open` items.
2. Show the summary. Then go through the open proposed updates in batches of up to 4, with one AskUserQuestion: apply, edit, or reject.
3. **Apply** each approved one: fetch the page, show the before and after, and change only the part it names with `notion-update-page` (`update_content`, anchored on plain text). Update that page's "Last updated" date in the Hub links table. If ICP names change, ask before changing the ICP segment values on customers.
4. **Draft objections:** query Objections for Answer status `draft`. The user confirms or edits each answer. Set `works` only when they say it works.
5. **New customers** with Permission note `not asked yet`: ask which ones gave permission to show their logo. Tick Logo shareable only on an explicit yes, and write how and when in Permission note.
6. **Quotes** under "New quotes": move the good ones into the right sections of the Messaging page, the rest to "More quotes".
7. Mark each item `applied` or `rejected` in the report, and set the "Last refreshed" line to 0 open updates.

## Change settings

- **A new or changed source:** plan it as in `references/source-map.md` ("Will each source stay current?"), then update the table above.
- **Save the change:** edit this file in `~/gtm-update` (if it's missing, `gh repo clone gtm-update ~/gtm-update`). Show the diff, then commit and push after one OK. The account copy follows on its own, or with **Check for updates** in Customize > Plugins.
- **Schedule or alert:** change the scheduled task (the Claude app's scheduled tasks, or claude.ai/code for a cloud task), and the "Updates" lines in the Hub's "For agents" section.
- **Bigger changes** (a new ICP from scratch, a first competitor study, a new offer): install the course plugin again and run that section. Its handover then refreshes this skill.

## Rules

- Only the sources in the plan. Only the user adds or removes sources.
- Unattended runs never change Product & offer, ICP or the top of the Messaging page. They only propose.
- Every write in review and change-settings mode is shown first. Nothing is sent to anyone but the user.
- No personal names, emails or profile URLs in the context: role and company type only.
- Don't name the enrichment tool: say "public company data".
<!-- skill ends -->
