---
name: refresh-gtm-context
description: "Keep the GTM context in your repo up to date on a schedule. It rereads the same sources as your first build, adds new customers, objections and buyer quotes to your gtm/ folder on its own, checks once a month that your offers, prices and website still match, and turns anything that needs a decision into proposed updates you approve. Sends you a short email or Slack alert after each run, and commits only if you allowed it. Three modes: set up the schedule, run (what the schedule does), and review the proposed updates. Use for \"keep my GTM context updated\", \"set up automatic updates\", \"schedule the refresh\", \"refresh my GTM context\", \"what changed in my GTM context\", \"review GTM updates\", or at the end of build-gtm-context. Not for the first build (use build-gtm-context)."
metadata:
  version: "0.3.0"
---

# Refresh your GTM context (GitHub)

The build is a snapshot. This skill keeps it current: same sources, only what's new, and nothing curated changes without the user.

## Reference files

- `references/refresh-playbook.md`: what may change on its own and what may not, what to check per bucket, the rules for unattended runs, and the report and alert formats. Read it first.
- `references/source-map.md`: how to get into each source (connector, browser, export, paste).
- `references/mining-playbook.md`: what counts as customer language and objections.
- `scripts/gtm_csv.py`: query and update the CSV banks. Call it by its full path in this skill's folder.
- `references/context-home.md`: the fixed home `~/gtm-context` and the pointer in Claude's memory. `scripts/gtm_home.py` checks and sets them up.

## Pick the mode

- **Setup:** called at the end of build-gtm-context, or the user asks to set up or change automatic updates.
- **Scheduled run:** the prompt says "scheduled run", or the user says "refresh now" or "run the refresh".
- **Review:** the user says "review GTM updates", or follows an alert.

All modes start by reading `~/gtm-context/gtm/README.md`. Every `gtm/` path in this skill is inside `~/gtm-context/`, the student's private gtm-context repo (see `references/context-home.md`), never the current project. If it's missing, say the context isn't set up and point to build-gtm-context. In a cloud routine there is no `~/gtm-context`: the routine's checked-out copy of the `gtm-context` repo is the folder, and every `gtm/` path is inside it.

## Setup

1. **Confirm the sources.** Show the "Sources" list from `gtm/README.md` per bucket. Ask the user to reply in one message: keep, remove, or add a source (a link or a tool name). This is where they point the refresh in the right direction.
2. **Check what works without them.** Mark each source:
   - **Connector:** works.
   - **Claude in Chrome:** works only with an app scheduled task, while Chrome is open and signed in.
   - **Export or paste:** can't run alone. Offer a connector if one exists, or a monthly reminder in the alert to drop a fresh export into `gtm/.private/`.
3. **Where it runs.** Explain in two lines each, then ask with AskUserQuestion:
   - **Claude app scheduled task:** runs on their computer while the Claude app is open (a missed run happens at the next launch). Uses the local repo and can use Claude in Chrome. Created with the scheduled-tasks tool.
   - **Cloud routine:** runs even when the computer is off, on a copy of the GitHub repo, with cloud connectors only and no browser. Created with the `/schedule` skill. It needs the repo on GitHub (offer to publish it as private first if it has no remote), and it always commits and pushes to a `gtm-refresh` branch, never to main. Cloud runs don't load plugins, so setup copies this skill into the repo (step 7).
4. **When.** Default every Monday at 08:00 local time, and the user can pick another day or time. There's one task: the run itself decides when the monthly full check is due.
5. **Alert.** Ask: email or Slack.
   - Email: a Gmail or Outlook connector that can send, to their own address. Confirm the address.
   - Slack: a DM to themself. Find their own member ID with the Slack connector.
   - Offer one test message. Send it only on a clear yes. If the connector can only draft, say alerts will arrive as drafts.
6. **Git permissions.** App task: ask once, as two separate choices: "May scheduled runs commit their changes?" and, only if yes, "May they also push?" Defaults: commit yes, push no. Cloud routine: commit and push to `gtm-refresh` are required, or the run's work is lost, so say so instead of asking. Either way the repo must still be private (check as in `repo-structure.md`).
7. **Cloud routine only: put the skill in the repo.** A cloud run only sees what's committed in the repo's `.claude/` folder. After one OK, copy this skill folder and two agents in, then commit and push:
   - `mkdir -p ~/gtm-context/.claude/skills ~/gtm-context/.claude/agents`
   - `cp -R "<this skill folder>" ~/gtm-context/.claude/skills/refresh-gtm-context`
   - `cp "<this skill folder>/../../agents/language-miner.md" "<this skill folder>/../../agents/source-reader.md" ~/gtm-context/.claude/agents/`
   - Commit with `gtm: add refresh skill for cloud runs`, and push.

   Say in one line that running setup again after a plugin update refreshes these copies.
8. **Create the schedule.** The prompt must stand on its own, because each run starts with no memory:

```
Scheduled run of the GTM refresh. Use the gtm-context-github:refresh-gtm-context skill in "scheduled run" mode.   (cloud: Use the refresh-gtm-context skill in this repo's .claude/skills in "scheduled run" mode.)
Repository: <absolute path to ~/gtm-context, for example /Users/name/gtm-context>   (cloud: <owner>/gtm-context, work on branch gtm-refresh)
Do not ask questions. Follow refresh-playbook.md: update the banks, write proposed updates for anything else, write the report, then send the alert.
Alert: <email to address | Slack DM to member ID>. Commit: <yes|no>. Push: <yes|no>.
```

   App: `create_scheduled_task` with taskId `gtm-refresh`, a title like "Weekly GTM refresh" and the cron expression (for example `0 8 * * 1`). Cloud: run `/schedule` with the same prompt and timing, with the `gtm-context` repo selected and the email or Slack connector left on.
9. **Record it** in `gtm/README.md` under a `## Refresh` block (format in build-gtm-context's `repo-structure.md`). Create `gtm/updates/` if it doesn't exist.
10. Run `gtm_home.py status`. If the pointer isn't in Claude's memory yet, offer it (as in build-gtm-context step 2). For an app scheduled task, also offer `gtm_home.py allow`, so unattended runs can read and write `~/gtm-context` without a permission prompt.
11. Offer a first run now, so they see a real report. On yes, run the scheduled-run steps below and stay available for questions.

## Scheduled run

Follow the unattended rules in `refresh-playbook.md`: no questions, skip and log any source that fails, alert only the user.

1. **Load.** Read `gtm/README.md`, its Sources and its Refresh block. Each bucket's window starts at its last run date, or 30 days ago. A cloud routine first checks out the `gtm-refresh` branch (or creates it from main), then merges main into it, so it starts from what the user already reviewed. If that merge conflicts, abort it, continue on the branch as it is, and note it in the report.
2. **Decide the scope.** It's a full check if the last full check was in an earlier calendar month, or the user asked for one. Otherwise it's a weekly run.
3. **Read, in parallel and in the background:**
   - One `language-miner` per conversation source, with the window and "extract: both".
   - New customers since the window start, from the linked customer system or a new export in `gtm/.private/`.
   - Full check only: one `source-reader` per product and proof source, in compare mode, with `gtm/product.md` as the baseline.
   - Sources that need Claude in Chrome: read them yourself, one page at a time. If Chrome isn't available, log the source under "Couldn't read".
4. **Update the banks (automatic).** Put the rows in a JSON file in `gtm/.private/`, write them with one `upsert` per bank, then delete the JSON file.
   - **Customers** (`customers.csv`, or the linked system): new companies get Permission note `not asked yet` and Logo shareable `no`. Set Best customer `yes` where the saved rule matches.
   - **Objections:** dedupe with one `--any` query for the themes in this batch, comparing by meaning, not exact wording (as in gtm-objections step 3). New rows get Answer status `draft`. Repeats reuse the existing Objection key, with Times seen increased and Last seen updated.
   - **Quotes:** append the 5 to 10 strongest new quotes under a "New quotes (unreviewed, <date>)" heading at the end of `gtm/messaging.md`. Never edit the top of the page.
5. **Find what needs a decision (proposed updates only):**
   - Every difference the compare-mode readers returned.
   - Value props or word lists that new quotes contradict.
   - ICP drift (full check): new customers outside every ICP, as described in the playbook.
   - Staleness: passed dates, sections older than the rhythm, old drafts.
6. **Write the report** to `gtm/updates/<YYYY-MM-DD>.md` in the playbook's format. Then:
   - Update the "Last refreshed" line in `gtm/README.md`: date, counts, and the number of open updates.
   - Update the last run dates in the `## Refresh` block.
7. **Git**, only as allowed in the scheduled prompt (a cloud routine always commits and pushes to `gtm-refresh`): stage only the files this run changed (the banks, `gtm/messaging.md`, `gtm/README.md` and the new report), never `git add -A`, so the user's own unfinished edits stay out. Commit with `gtm: refresh <date>`, then push if pushing is allowed. Never push to main from a cloud routine.
8. **Send the alert** in the playbook's format, with the report's path (or its GitHub link if pushed), to the address or DM in the scheduled prompt only (in a manual run, ask the user). If sending fails, leave a draft and note it in the report.

## Review

1. Open the newest report in `gtm/updates/` (and any older ones with `open` items). On a cloud setup, first offer to merge the `gtm-refresh` branch, and do it only on a clear yes.
2. Show the summary. Then go through the open proposed updates in batches of up to 4, with one AskUserQuestion: apply, edit, or reject.
3. Apply each approved one with the matching section skill's write step: gtm-product, gtm-icp or gtm-messaging. Set its status to `applied` or `rejected` in the report.
4. Objections added as `draft`: ask the user to confirm or edit the answers (gtm-objections step 4).
5. New customers: run gtm-customers part B for logo permission.
6. Move reviewed quotes from "New quotes" into the right sections of `gtm/messaging.md`, or leave them under "More quotes".
7. Update the "Last refreshed" line to show 0 open updates. Ask before committing the review changes.

## Rules

- Same sources as the build. Only the user adds or removes sources, in setup or review.
- Unattended runs never change `product.md`, `icp.md` or the top of `messaging.md`. They only propose.
- Query banks with `gtm_csv.py`, never read them whole. Write only with `upsert`.
- The alert goes to the user only. Nothing is ever sent to anyone else.
- No personal names, emails or profile URLs in any file. Raw exports stay in `gtm/.private/`.
- Don't name the enrichment tool to the user: say "public company data".
