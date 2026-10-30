# Template: the student's scheduled update (GitHub)

The handover (`handover.md`, step 3) fills this in. It has two parts: the task prompt (between the task markers) becomes the `gtm-update` scheduled task, and the review guide (between the guide markers) goes into `gtm/updates/README.md`. How to fill it:
- Replace every `{{...}}` with the real values from `gtm/README.md` and the plan from handover step 1.
- Where a line says `PASTE`, paste the named part of the file from this skill's `references/` folder, word for word.
- Delete what the student doesn't have: lines for skipped sections or banks that live in a linked system, the example rows, and steps for source types they don't use (for example the Claude in Chrome step when no line is `auto, app only`, or the cloud lines for an app task).
- Keep their own theme and persona names where they use them.
- The email address or Slack member ID goes only on the task prompt's Alert line, never in a file.
- Leave out the markers themselves.

<!-- task starts -->
# Weekly GTM update for {{company}}

Made by the AI Growth Systems Bootcamp setup on {{YYYY-MM-DD}}. This prompt is the whole update. To change it, edit this task, or ask Claude to "change my GTM update settings".

Scheduled run of the GTM update. Do not ask questions. Alert: {{email to <address> | Slack DM to <member ID>}}. Git: {{commit yes|no · push yes|no}}. Enrich new customers: {{no | yes, with <tool>, up to <n> lookups per run}}.

Offers in scope: {{offer 1}} · {{offer 2}}. Tag every new row and quote with its offer.

## Where things live

- **Context:** the private repo `{{owner}}/gtm-context`, at `~/gtm-context` on this computer. {{cloud only: In a cloud run there's no `~/gtm-context`: the run's checked-out copy of the repo is the folder.}} Every `gtm/` path below is inside it.
- **Hub:** `gtm/README.md` links to every page and bank, and holds the best-customer rule and the "Last run" dates.
- **Pages:** `gtm/product.md`, `gtm/icp.md`, `gtm/messaging.md`
- **Banks:** `gtm/customers.csv` (contacts: {{kept | not kept}}), `gtm/objections.csv`, `gtm/competitors.csv` {{or, for a bank that lives in a linked system: "Customers: <system> · via: <how to query it> · filter: <...>"}}
- **CSV helper:** `scripts/gtm_csv.py` in the repo. Query and update the banks only with it, never read them whole: `query` with `--where`, `--any`, `--contains`; `upsert --rows <json file>` with the bank's key: customers `--key "Email|LinkedIn URL|Customer" --merge Offer`, objections `--key "Objection,Offer"`, competitors `--key Name`.
- **Reports:** `gtm/updates/`. Raw exports: `gtm/.private/` (gitignored).

## Where new information comes from

| Bucket | Source | How to get in | Who |
|---|---|---|---|
| {{bucket}} | {{source}} | {{connector, public page, Claude in Chrome, export or paste}} | {{auto, auto (app only), you (how often), none}} |
| Customers | Course dashboard, students page | Claude in Chrome, read-only | auto (app only) |
| Customers | Student list export | You drop a fresh CSV into `gtm/.private/` | you, monthly |

## Steps

Follow the update rules at the end: no questions, skip and log any source that fails, alert only the user.

1. **Load.** Read `gtm/README.md`: the best-customer rule and the "Last run" dates. Each bucket's window starts at its last run date, or 30 days ago. {{cloud only: First check out the `gtm-updates` branch (or create it from main), then merge main into it. If that merge conflicts, abort it, continue on the branch as it is, and note it in the report.}}
2. **Decide the scope.** It's a full check if the last full check was in an earlier calendar month. Otherwise it's a weekly run.
3. **Read, in parallel and in the background,** with the reading briefs below:
   - One agent per conversation source in the plan, with the window.
   - New customers since the window start, from the customer sources in the plan.
   - Full check only: one agent per product and proof source, in compare mode, with `gtm/product.md` as the baseline.
   - `auto (app only)` lines: read them yourself with Claude in Chrome, one page at a time, read-only. If Chrome isn't available, log the source under "Couldn't read".
   - `you` lines: read only a new file in `gtm/.private/` or pasted text. Otherwise, when one is due, add a reminder to the alert.
4. **Update the banks (automatic).** Put the rows in a JSON file in `gtm/.private/`, write them with one `upsert` per bank, then delete the JSON file.
   - **Customers:** write with `--key "Email|LinkedIn URL|Customer" --merge Offer`. If contacts are kept, one row per buyer with their name (in Customer), Company, Email and LinkedIn URL from the source; otherwise one row per company, its name in Customer. New rows get their Offer, Permission note `not asked yet` and Logo shareable `no`. A buyer (or company) already in the bank that bought another offer gets that offer added to its Offer cell, not a second row. If "Enrich new customers" is yes, fill buyer and company fields for the new rows only, within the lookup limit above (never look up emails or phone numbers). Set Best customer `yes` where the rule matches.
   - **Objections:** run one `--any` query for the themes in this batch and compare by meaning, not exact wording, within the same offer. A repeat (same meaning, same offer) reuses the existing Objection text, so `--key "Objection,Offer"` updates that row: Times seen increased and Last seen updated. The same objection about another offer is a new row. A new one gets Answer status `draft`.
   - **Quotes:** append the 5 to 10 strongest new quotes under a "New quotes (unreviewed, <date>)" heading at the end of `gtm/messaging.md`. Never edit the top of the page.
5. **Find what needs a decision (proposed updates only):** every difference the compare-mode readers returned, value props or word lists that new quotes contradict, ICP drift per offer (full check), and staleness (passed dates, old drafts).
6. **Write the report** to `gtm/updates/<YYYY-MM-DD>.md` in the format below. Then update the "Last refreshed" line and the "Last run" dates in `gtm/README.md`.
7. **Git**, only as allowed on the Git line above{{cloud only: (a cloud run always commits and pushes to `gtm-updates`)}}: stage only the files this run changed, never `git add -A`. Commit with `gtm: update <date>`, then push if allowed.
8. **Send the alert** in the format below, with the report's path (or its GitHub link if pushed), to the address on the Alert line above only. If sending fails, leave a draft and note it in the report.

## Reading briefs

Start one general-purpose agent per source, all in one message, in the background, and give each the brief below with the source, how to reach it, the window, and the offers in scope: {{each offer in scope, with a one-line summary}}. Tag every row with its offer. If agents aren't available in this run, read each source yourself with the same brief.

**Conversation source** (calls, email, DMs). Read external conversations about the offer in the window, then return customer language and objections.

PASTE `mining-playbook.md`: the sections "What to read", "What to extract", "Rules" and "Objection themes".

Return a LANGUAGE table (Type, Quote, Who, Offer, Times, Source), an OBJECTIONS table (Theme, Objection, Quote, Offer, Stage, Answer given, Moved forward, Times, Source), and up to 3 lines of notes on what you couldn't read.

**Product or proof source, compare mode** (full check only). Read the source, compare it with the baseline file you're given, and report only facts that differ. Ignore wording changes that don't change a fact. Return ADDED, REMOVED and CHANGED lines (`<bucket>: <field>: "<baseline value>" -> "<source value>" [source]`), one UNCHANGED line, and FLAGS for passed dates or contradictions. No personal data: role and company type only.

## Update rules

PASTE `update-playbook.md`: everything from "## What may change without the user" to the end.
<!-- task ends -->

<!-- guide starts -->
# GTM updates: how to review and change them

Each weekly update writes a report here. When the user says "review GTM updates" or follows an alert, in any Claude session:

## How to review GTM updates

1. {{cloud only: First offer to merge the `gtm-updates` branch into main, and do it only on a clear yes.}} Open the newest report in this folder, and any older ones with `open` items.
2. Show the summary. Then go through the open proposed updates in batches of up to 4, with one AskUserQuestion: apply, edit, or reject.
3. **Apply** each approved one: show the before and after, and change only the part of the page it names. Add a changelog line at the bottom of that page, and update its "Last updated" date in the `gtm/README.md` table. If ICP names change, ask before changing the ICP segment values in `customers.csv` (one `upsert` batch with `scripts/gtm_csv.py`).
4. **Draft objections:** `python3 ~/gtm-context/scripts/gtm_csv.py query ~/gtm-context/gtm/objections.csv --where "Answer status=draft"`. The user confirms or edits each answer. Set `works` only when they say it works.
5. **New customers** with Permission note `not asked yet`: ask which ones gave permission to show their logo. Set Logo shareable `yes` only on an explicit yes, and write how and when in Permission note.
6. **Quotes** under "New quotes": move the good ones into the right sections of `gtm/messaging.md`, the rest to "All quotes" at the bottom of the page.
7. Mark each item `applied` or `rejected` in the report, and set the "Last refreshed" line to 0 open updates. Ask before committing the review changes.

Every write is shown first. Contact details stay in `customers.csv`; everywhere else, role and company type only, never names, emails or profile URLs. Query banks with the helper, never read them whole.

## How to change the update settings

The settings live in the prompt of the scheduled task `gtm-update`.
- **Change the plan, alert, schedule or git permissions:** edit the task in the Claude app (Scheduled, then Weekly GTM update), or ask Claude in Claude Code, which reads the task file and changes it with `update_scheduled_task`. Show the diff first.
- **A new source:** decide whether it keeps updating on its own (a CRM, inbox, call recorder, dashboard) or was a one-off (a file, a pasted list). For a one-off, ask where that information will show up from now on. Then add one line to the "Where new information comes from" table: source, how to get in, and who gets it (auto, auto app only, you, none).
- **Also update** the "Updates" block in `gtm/README.md` when the schedule or alert channel changes.
- **Bigger changes** (a new ICP from scratch, a first competitor study, a new offer): install the course plugin again and run that section. Its handover then rewrites this task.
<!-- guide ends -->
