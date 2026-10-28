# Template: the student's update skill (GitHub)

The handover (`handover.md`, step 3) fills this in and writes it as `SKILL.md` in the student's own plugin. How to fill it:
- Replace every `{{...}}` with the real values from `gtm/README.md` and the plan from handover step 1.
- Delete what the student doesn't have: lines for skipped sections or banks that live in a linked system, the example rows, and steps for source types they don't use (for example the Claude in Chrome step when no line is `auto, app only`, or the cloud lines for an app task).
- Keep their own theme and persona names where they use them.
- Never write an email address or Slack member ID into the file. Those stay in the scheduled prompt.
- Copy everything between the two marker lines, without the markers.

<!-- skill starts -->
---
name: update-gtm-context
description: "Keep {{company}}'s GTM context in the gtm-context repo up to date. Reads new customers, objections and buyer quotes from the sources in its plan, adds them to the gtm/ banks on its own, checks once a month that offers, prices and the website still match, and turns anything that needs a decision into proposed updates you approve. Commits only as you allowed. Three modes: scheduled run, review, and change settings. Use for \"update my GTM context\", \"run the GTM update\", \"review GTM updates\", \"what changed in my GTM context\", \"change my GTM update settings\", \"add a source to my GTM updates\", or when a scheduled run starts. Not for building a new section from scratch (install the course plugin again for that)."
---

# Update {{company}}'s GTM context

Made for {{company}} by the AI Growth Systems Bootcamp setup on {{YYYY-MM-DD}}. It's yours: say "change my GTM update settings", or edit this file in your `gtm-update` repo.

## References

- `references/update-playbook.md`: what may change on its own and what may not, the rules for unattended runs, and the report and alert formats. Read it first.
- `references/mining-playbook.md`: what counts as customer language and objections.
- `references/source-map.md`: how to get into a source, and how to plan a new one.
- `scripts/gtm_csv.py`: query and update the CSV banks. Call it by its full path in this skill's folder.

## Where things live

- **Context:** the private repo `{{owner}}/gtm-context`, at `~/gtm-context` on this computer. In a cloud run there's no `~/gtm-context`: the run's checked-out copy of the repo is the folder. Every `gtm/` path below is inside it.
- **Hub:** `gtm/README.md` links to every page and bank, and holds the best-customer rule and the "Last run" dates.
- **Pages:** `gtm/product.md`, `gtm/icp.md`, `gtm/messaging.md`
- **Banks:** `gtm/customers.csv`, `gtm/objections.csv`, `gtm/competitors.csv` {{or, for a bank that lives in a linked system: "Customers: <system>, <how to query it>, filter <...>"}}
- **Reports:** `gtm/updates/`. Raw exports: `gtm/.private/` (gitignored).
- **Git:** {{commit yes|no · push yes|no, as allowed at setup}}. {{cloud only: a cloud run always commits and pushes to the `gtm-updates` branch, never to main.}}

## Where new information comes from

| Bucket | Source | How to get in | Who |
|---|---|---|---|
| {{bucket}} | {{source}} | {{connector, public page, Claude in Chrome, export or paste}} | {{auto, auto (app only), you (how often), none}} |
| Customers | Course dashboard, students page | Claude in Chrome, read-only | auto (app only) |
| Customers | Student list export | You drop a fresh CSV into `gtm/.private/` | you, monthly |

## Pick the mode

- **Scheduled run:** the prompt says "scheduled run", or the user says "run the GTM update" or "update now".
- **Review:** the user says "review GTM updates", or follows an alert.
- **Change settings:** the user wants to add or remove a source, or change the alert, the schedule or the git permissions.

## Scheduled run

Follow the unattended rules in `update-playbook.md`: no questions, skip and log any source that fails, alert only the user.

1. **Load.** Read `gtm/README.md`: the best-customer rule and the "Last run" dates. Each bucket's window starts at its last run date, or 30 days ago. A cloud run first checks out `gtm-updates` (or creates it from main), then merges main into it, so it starts from what the user already reviewed. If that merge conflicts, abort it, continue on the branch as it is, and note it in the report.
2. **Decide the scope.** It's a full check if the last full check was in an earlier calendar month, or the user asked for one. Otherwise it's a weekly run.
3. **Read, in parallel and in the background:**
   - One `language-miner` per conversation source in the plan, with the window and "extract: both".
   - New customers since the window start, from the customer sources in the plan.
   - Full check only: one `source-reader` per product and proof source, in compare mode, with `gtm/product.md` as the baseline.
   - `auto (app only)` lines: read them yourself with Claude in Chrome, one page at a time. If Chrome isn't available, log the source under "Couldn't read".
   - `you` lines: read only a new file in `gtm/.private/` or pasted text. Otherwise, when one is due, add a reminder to the alert.
   - If the agents aren't available in this run, read each source yourself, one at a time.
4. **Update the banks (automatic).** Put the rows in a JSON file in `gtm/.private/`, write them with one `upsert` per bank, then delete the JSON file.
   - **Customers:** new companies get Permission note `not asked yet` and Logo shareable `no`. Set Best customer `yes` where the rule matches.
   - **Objections:** run one `--any` query for the themes in this batch and compare by meaning, not exact wording. A repeat reuses the existing Objection key, with Times seen increased and Last seen updated. A new one gets Answer status `draft`.
   - **Quotes:** append the 5 to 10 strongest new quotes under a "New quotes (unreviewed, <date>)" heading at the end of `gtm/messaging.md`. Never edit the top of the page.
5. **Find what needs a decision (proposed updates only):** every difference the compare-mode readers returned, value props or word lists that new quotes contradict, ICP drift (full check), and staleness (passed dates, old drafts).
6. **Write the report** to `gtm/updates/<YYYY-MM-DD>.md` in the playbook's format. Then update the "Last refreshed" line and the "Last run" dates in `gtm/README.md`.
7. **Git**, only as allowed above: stage only the files this run changed (the banks, `gtm/messaging.md`, `gtm/README.md` and the new report), never `git add -A`. Commit with `gtm: update <date>`, then push if allowed.
8. **Send the alert** in the playbook's format, with the report's path (or its GitHub link if pushed), to the address or DM in the scheduled prompt only (in a manual run, ask). If sending fails, leave a draft and note it in the report.

## Review

1. If runs happen in the cloud, first offer to merge the `gtm-updates` branch into main, and do it only on a clear yes.
2. Open the newest report in `gtm/updates/`, and any older ones with `open` items. Show the summary. Then go through the open proposed updates in batches of up to 4, with one AskUserQuestion: apply, edit, or reject.
3. **Apply** each approved one: show the before and after, and change only the part of the page it names. Add a changelog line at the bottom of that page, and update its "Last updated" date in the `gtm/README.md` table. If ICP names change, ask before changing the ICP segment values in `customers.csv` (one `upsert` batch).
4. **Draft objections:** query `objections.csv` with `--where "Answer status=draft"`. The user confirms or edits each answer. Set `works` only when they say it works.
5. **New customers** with Permission note `not asked yet`: ask which ones gave permission to show their logo. Set Logo shareable `yes` only on an explicit yes, and write how and when in Permission note.
6. **Quotes** under "New quotes": move the good ones into the right sections of `gtm/messaging.md`, the rest to "More quotes".
7. Mark each item `applied` or `rejected` in the report, and set the "Last refreshed" line to 0 open updates. Ask before committing the review changes.

## Change settings

- **A new or changed source:** plan it as in `references/source-map.md` ("Will each source stay current?"), then update the table above.
- **Save the change:** edit this file in `~/gtm-update` (if it's missing, `gh repo clone gtm-update ~/gtm-update`). Show the diff, then commit and push after one OK. The account copy follows on its own, or with **Check for updates** in Customize > Plugins.
- **Schedule, alert or git permissions:** change the scheduled task (the Claude app's scheduled tasks, or claude.ai/code for a cloud task), the "Updates" block in `gtm/README.md`, and the "Git" line above.
- **Bigger changes** (a new ICP from scratch, a first competitor study, a new offer): install the course plugin again and run that section. Its handover then refreshes this skill.

## Rules

- Only the sources in the plan. Only the user adds or removes sources.
- Unattended runs never change `product.md`, `icp.md` or the top of `messaging.md`. They only propose.
- Query banks with `gtm_csv.py`, never read them whole. Write only with `upsert`.
- Every write in review and change-settings mode is shown first. Nothing is sent to anyone but the user.
- No personal names, emails or profile URLs in any file. Raw exports stay in `gtm/.private/`.
- Don't name the enrichment tool: say "public company data".
<!-- skill ends -->
