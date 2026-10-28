---
name: refresh-gtm-context
description: "Keep your Notion GTM Hub up to date on a schedule. It rereads the same sources as your first build, adds new customers, objections and buyer quotes to the Hub on its own, checks once a month that your offers, prices and website still match, and turns anything that needs a decision into proposed updates you approve. Sends you a short email or Slack alert after each run. Three modes: set up the schedule, run (what the schedule does), and review the proposed updates. Use for \"keep my GTM context updated\", \"set up automatic updates\", \"schedule the refresh\", \"refresh my GTM hub\", \"what changed in my GTM context\", \"review GTM updates\", or at the end of build-gtm-context. Not for the first build (use build-gtm-context)."
metadata:
  version: "0.3.0"
---

# Refresh your GTM context (Notion)

The build is a snapshot. This skill keeps it current: same sources, only what's new, and nothing curated changes without the user.

## Reference files

- `references/refresh-playbook.md`: what may change on its own and what may not, what to check per bucket, the rules for unattended runs, and the report and alert formats. Read it first.
- `references/source-map.md`: how to get into each source (connector, browser, export, paste).
- `references/mining-playbook.md`: what counts as customer language and objections.
- `references/context-home.md`: the fixed home `~/gtm-context` and the pointer in Claude's memory. `scripts/gtm_home.py` checks and sets them up (full path in this skill's folder).

## Pick the mode

- **Setup:** called at the end of build-gtm-context, or the user asks to set up or change automatic updates.
- **Scheduled run:** the prompt says "scheduled run", or the user says "refresh now" or "run the refresh".
- **Review:** the user says "review GTM updates", or follows an alert.

All modes start by fetching the GTM Hub page. Its link is in the scheduled prompt, or in the "GTM context" block of Claude's memory (see `references/context-home.md`). The Hub's links table and its "For agents" section (sources, data source IDs, best-customer rule, refresh settings) are the whole map, so nothing local is needed and the same steps work in a cloud routine. If no Hub link is known, say the Hub isn't set up and point to build-gtm-context. If an old local `gtm-hub.md` turns up, follow "Older setups" in build-gtm-context's `hub-structure.md`.

## Setup

1. **Confirm the sources.** Show the "Sources" from the Hub's "For agents" section, per bucket. Ask the user to reply in one message: keep, remove, or add a source (a link or a tool name). This is where they point the refresh in the right direction.
2. **Check what works without them.** Mark each source:
   - **Connector:** works.
   - **Claude in Chrome:** works only with an app scheduled task, while Chrome is open and signed in.
   - **Export or paste:** can't run alone. Offer a connector if one exists, or a monthly reminder in the alert to drop a fresh export.
3. **Where it runs.** Explain in two lines each, then ask with AskUserQuestion:
   - **Claude app scheduled task:** runs on their computer while the Claude app is open (a missed run happens at the next launch). Can use Claude in Chrome. Created with the scheduled-tasks tool.
   - **Cloud routine:** runs even when the computer is off, but only with cloud connectors and no browser. Everything it needs is on the Hub page, so no local files are needed. Created with the `/schedule` skill.
4. **When.** Default every Monday at 08:00 local time, and the user can pick another day or time. There's one task: the run itself decides when the monthly full check is due.
5. **Alert.** Ask: email or Slack.
   - Email: a Gmail or Outlook connector that can send, to their own address. Confirm the address.
   - Slack: a DM to themself. Find their own member ID with the Slack connector.
   - Offer one test message. Send it only on a clear yes. If the connector can only draft, say alerts will arrive as drafts.
6. **Create the schedule.** The prompt must stand on its own, because each run starts with no memory:

```
Scheduled run of the GTM refresh. Use the gtm-context-notion:refresh-gtm-context skill in "scheduled run" mode.
GTM Hub: <Notion Hub link>  (its "For agents" section holds the sources, IDs and refresh settings)
Do not ask questions. Follow refresh-playbook.md: update the banks, write proposed updates for anything else, write the report, then send the alert.
Alert: <email to address | Slack DM to member ID>.
```

   App: `create_scheduled_task` with taskId `gtm-refresh`, a title like "Weekly GTM refresh" and the cron expression (for example `0 8 * * 1`). Cloud: run `/schedule` with the same prompt and timing.
7. **Record it** under "Refresh" in the Hub's "For agents" section (format in build-gtm-context's `hub-structure.md`). Create the "Updates to review" page under the Hub if it doesn't exist, and add its row to the Hub links table.
8. Run `gtm_home.py status`. If the pointer isn't in Claude's memory yet, offer it now (as in build-gtm-context step 2).
9. Offer a first run now, so they see a real report. On yes, run the scheduled-run steps below and stay available for questions.

## Scheduled run

Follow the unattended rules in `refresh-playbook.md`: no questions, skip and log any source that fails, alert only the user.

1. **Load.** Fetch the Hub and read its "For agents" section: Sources, data source IDs and Refresh settings. Each bucket's window starts at its last run date, or 30 days ago.
2. **Decide the scope.** It's a full check if the last full check was in an earlier calendar month, or the user asked for one. Otherwise it's a weekly run.
3. **Read, in parallel and in the background:**
   - One `language-miner` per conversation source, with the window and "extract: both".
   - New customers since the window start: query the linked customers database with a date filter, or the CRM connector.
   - Full check only: one `source-reader` per product and proof source, in compare mode, with the current Product & offer page as the baseline.
   - Sources that need Claude in Chrome: read them yourself, one page at a time. If Chrome isn't available, log the source under "Couldn't read".
4. **Update the banks (automatic):**
   - **Customers:** dedupe with one filtered query for this batch's company names. Create the new rows at company level with Permission note `not asked yet`. Tick Best customer where the saved rule matches.
   - **Objections:** dedupe exactly like gtm-objections step 3, with one query per batch. New rows get Answer status `draft`. Repeats get Times seen and Last seen updated, where the bank has those columns.
   - **Quotes:** add the 5 to 10 strongest new quotes to a "New quotes (unreviewed, <date>)" section at the bottom of the Messaging page. Use `insert_content` at the end, and never edit the top of the page.
5. **Find what needs a decision (proposed updates only):**
   - Every difference the compare-mode readers returned.
   - Value props or word lists that new quotes contradict.
   - ICP drift (full check): new customers outside every ICP, as described in the playbook.
   - Staleness: passed dates, sections older than the rhythm, old drafts.
6. **Write the report** as a child page of "Updates to review", titled `GTM refresh <date>`, in the playbook's format. Then:
   - Update the Hub callout's "Last refreshed" line: date, counts, and the number of open updates.
   - Update the "Last run" line in the Hub's "For agents" section (anchor the edit on its plain-text label).
7. **Send the alert** in the playbook's format, with the report link, to the address or DM in the scheduled prompt only. In a manual run, ask the user for it. If sending fails, leave a draft and note it in the report.

## Review

1. Open the newest report (and any older ones with `open` items).
2. Show the summary. Then go through the open proposed updates in batches of up to 4, with one AskUserQuestion: apply, edit, or reject.
3. Apply each approved one with the matching section skill's write step: gtm-product, gtm-icp or gtm-messaging. Set its status to `applied` or `rejected` in the report.
4. Objections added as `draft`: ask the user to confirm or edit the answers (gtm-objections step 4).
5. New customers: run gtm-customers part B for logo permission.
6. Move reviewed quotes from "New quotes" into the right sections of the Messaging page, or leave them under "More quotes".
7. Update the "Last refreshed" line to show 0 open updates.

## Rules

- Same sources as the build. Only the user adds or removes sources, in setup or review.
- Unattended runs never change the Product, ICP or messaging summary. They only propose.
- Fetch pages by the links on the Hub. Query banks with filters, never read them whole.
- The alert goes to the user only. Nothing is ever sent to anyone else.
- Don't name the enrichment tool to the user: say "public company data".
