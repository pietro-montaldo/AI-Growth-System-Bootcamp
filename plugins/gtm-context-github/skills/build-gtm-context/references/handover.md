# Handover: the student's own scheduled update

After the build, the student only needs to keep their context current. So the build ends with one scheduled task that belongs to them: its prompt holds the whole update, written for their context, their tools and their sources. Nothing else is installed. Then the course plugin can go.

A task prompt can do the full job because a skill is just instructions: in the Claude app a scheduled task is itself stored as a skill file (`~/.claude/scheduled-tasks/gtm-update/SKILL.md`), and each run reads all of it.

Every step below is shown first and done after one OK. The student can stop at any step and pick up later by saying "set up my GTM updates".

## What they end up with

- **The scheduled task `gtm-update`:** its prompt is `references/update-task-template.md` (this skill's folder), filled in. It does the scheduled run only.
- **The review guide:** how to review an update report and how to change the settings. On the "Updates to review" page (Notion) or in `gtm/updates/README.md` (GitHub).
- **One more line in the pointer** in Claude's memory, so "review GTM updates" works from any project.
- **GitHub version only:** `gtm_csv.py` committed to `~/gtm-context/scripts/`, so runs can query and update the CSV banks.

The task is named "Weekly GTM update", with the ID `gtm-update`. Never ask. If that ID is taken (a deleted task can leave its folder behind), `create_scheduled_task` names a free one, such as `gtm-update-2`: use it, and write the real ID wherever the task is named (the hub's Updates block and the review guide).

## 1. Plan the updates

The item-by-item plan was settled in build step 1 and is in the hub's "Sources" list: for every item, where new information comes from and who brings it in. Show it as one table and confirm it. If a line is missing or still open (for example a section run on its own later), settle it as in "Where each item comes from, now and later" in `source-map.md`, preferring an automatic route.

Then settle, with AskUserQuestion where it's a choice:
- **Where it runs.** If any line is `auto, app only`, recommend a scheduled task in the Claude app (runs on their computer while the app is open, can use Claude in Chrome). Otherwise offer both: the app task, or a cloud scheduled task (runs even when the computer is off, connectors only). Two lines each, then ask.
- **When.** Default every Monday at 08:00 local time. One task: the run decides when the monthly full check is due.
- **Alert.** Email (a Gmail or Outlook connector that can send, to their own address) or Slack (a DM to themself; find their member ID with the Slack connector). Confirm the address. Offer one test message, sent only on a clear yes.
- **Enrich new customers?** Only if an enrichment tool is connected (Clay first). Say what it would cost per week (new customers per week from the build's numbers, times the credits per lookup) and ask once: yes with a weekly lookup limit, or no. Default no.
- **GitHub version only: git.** "May update runs commit?" and, only if yes, "May they also push?" A cloud task must commit and push to a `gtm-updates` branch, or its work is lost, so say so instead of asking.

## 2. Prepare the hub

- Create the "Updates to review" page under the Hub (Notion) or the `gtm/updates/` folder (GitHub), if it doesn't exist. Its link goes into the task prompt.
- Add the "Last refreshed" line to the end of the hub summary (the Hub callout, or the summary block in `gtm/README.md`), so every run has a line to update.
- **GitHub version only, when any bank is a CSV file:** copy `gtm_csv.py` from this skill's `scripts/` to `~/gtm-context/scripts/gtm_csv.py`. It's committed with the rest at the end of the handover. Skip it when every bank lives in a linked system (Notion, a CRM).

## 3. Write the task prompt and the review guide

Fill in `references/update-task-template.md` as its header says. Paste the playbook sections as they are, headings included: the report and alert formats inside them must stay word for word. It has two parts:
- **The task prompt** (between the task markers): where things live, where new information comes from, the run steps, the reading briefs, and the update rules pasted in from `update-playbook.md` and `mining-playbook.md`.
- **The review guide** (between the guide markers): how to review a report and how to change the settings.

Show the user the "Where things live" and "Where new information comes from" sections before writing anything. Never put an email address or Slack member ID anywhere except the task prompt's Alert line.

Write the review guide onto the "Updates to review" page (Notion, below its first line) or into `gtm/updates/README.md` (GitHub).

## 4. Create the schedule

- **App task:** `create_scheduled_task` with taskId `gtm-update`, title "Weekly GTM update", the cron expression (for example `0 8 * * 1`) and the filled task prompt.
- **Cloud task:** run the `/schedule` skill with the same prompt and timing. Select a repository: `gtm-context` in the GitHub version (the run writes there). In the Notion version a cloud task still needs one repository; any repo of theirs works, because the run doesn't change it. Leave on the connectors the plan uses, plus the alert one.

Check for a rerun with `list_scheduled_tasks` (a task titled "Weekly GTM update"), not by looking at task folders: a deleted task can leave its folder behind. If one exists, read its current prompt, carry over its settings unless the user changes them, show the diff, and update it (`update_scheduled_task`, or `/schedule` for a cloud task). If the hub's Updates block names a task that no longer exists, say so and create a new one.

**Older setups:** if the hub's Updates block names an update plugin (`my-gtm-context`, from a `gtm-update` repo), carry its settings over from that plugin's `SKILL.md` (`~/gtm-update/plugins/my-gtm-context/skills/update-gtm-context/SKILL.md`): links, source plan, run steps for their own databases, alert and git settings. Afterwards, tell the user the plugin is no longer needed: they remove it in Customize > Plugins and can delete the `gtm-update` repo themselves.

Record it under "Updates" in the hub (format in `hub-structure.md` or `repo-structure.md`).

## 5. Pointer: how to review

Update the pointer in Claude's memory with the review guide's location, after one OK:
- Notion: `gtm_home.py pointer --notion-hub <Hub link> --updates <Updates to review link>`
- GitHub: `gtm_home.py pointer --repo <owner>/gtm-context` (once `gtm/updates/README.md` exists, it adds the review line on its own)

GitHub version: then commit the handover's changes in `~/gtm-context` (`gtm/README.md`, `gtm/updates/README.md`, `scripts/gtm_csv.py`) after one OK, and push only if they allow it.

## 6. First run

Offer a first run now, so they see a real report: `run_scheduled_task` with `gtm-update` for an app task, or the run-now option for a cloud task. It starts a fresh session with the task prompt, exactly like a scheduled run. Stay available for questions.

## 7. Remove the course plugin

Explain in one line: everything they need is now in their context, their scheduled task and the review guide.
- **Installed in Claude Code:** `claude plugin uninstall gtm-context-notion@ai-growth-system-bootcamp` (or `gtm-context-github@...`), after their OK.
- **Added in Customize:** they remove it there (open the plugin, menu, **Remove**).
- **The course marketplace:** keep it if they use other course plugins (voice-miner and do-not-contact live there too). Removing a marketplace removes every plugin installed from it, so offer `claude plugin marketplace remove ai-growth-system-bootcamp` only if they don't.

The pointer in Claude's memory stays: later course systems use it to find the context.

## 8. Tell them how to use it

Three lines:
- Updates run on their own, and an alert says what changed.
- "Review GTM updates" goes through the proposed changes. "Change my GTM update settings" adds a source or changes the alert or schedule. Both work in any Claude Code session, because the pointer says where the guide is.
- For a bigger change (a new ICP from scratch, a first competitor study), they install the course plugin again and run that section, then rerun this handover.
