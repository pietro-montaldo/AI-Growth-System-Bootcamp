# Handover: the student's own update plugin

After the build, the student only needs to keep their context current. So the build ends by creating a plugin that belongs to them: one skill, `update-gtm-context`, written for their context, their tools and their sources. It lives in a private GitHub repo of theirs, is added to their Claude account as a marketplace, and runs on a schedule. Then the course plugin can go.

Every step below is shown first and done after one OK. The student can stop at any step and pick up later by saying "set up my GTM updates".

## What they end up with

```
~/gtm-update/                        local copy of the private repo <owner>/gtm-update
├── .claude-plugin/marketplace.json  marketplace "my-gtm" with one plugin
├── README.md                        two lines: what this is, how to change it
└── plugins/my-gtm-context/
    ├── .claude-plugin/plugin.json
    ├── agents/                      language-miner.md, source-reader.md
    └── skills/update-gtm-context/
        ├── SKILL.md                 filled in from references/update-skill-template.md
        ├── references/              update-playbook.md, mining-playbook.md, source-map.md
        └── scripts/gtm_csv.py       GitHub version only
```

The names are fixed for every student, like `~/gtm-context`: repo `gtm-update`, marketplace `my-gtm`, plugin `my-gtm-context`. Never ask.

## 1. Plan the updates

Follow "Will each source stay current?" in `source-map.md`. Start from the hub's "Sources" (what the build read) and propose, per bucket, where new information comes from and who gets it (`auto`, `auto, app only`, `you`, `none`). Ask only about snapshots and open lines, in one message.

Then settle, with AskUserQuestion where it's a choice:
- **Where it runs.** If any line is `auto, app only`, recommend a scheduled task in the Claude app (runs on their computer while the app is open, can use Claude in Chrome). Otherwise recommend a cloud scheduled task (runs even when the computer is off, connectors only). Two lines each, then ask.
- **When.** Default every Monday at 08:00 local time. One task: the run decides when the monthly full check is due.
- **Alert.** Email (a Gmail or Outlook connector that can send, to their own address) or Slack (a DM to themself; find their member ID with the Slack connector). Confirm the address. Offer one test message, sent only on a clear yes.
- **GitHub version only: git.** "May update runs commit?" and, only if yes, "May they also push?" A cloud task must commit and push to a `gtm-updates` branch, or its work is lost, so say so instead of asking.

## 2. Check GitHub

Run `gh auth status`. If the GitHub CLI is missing or signed out, say why it's needed (their update skill lives in a private repo on their GitHub) and ask them to install it and run `gh auth login` in their own terminal. They sign in themselves. Wait, then check again.

If `~/gtm-update` or a `gtm-update` repo already exists, this is a rerun: clone or pull it, read the current `SKILL.md`, and carry over its settings unless the user changes them. Show the diff before writing.

## 3. Write the plugin

1. Fill in `references/update-skill-template.md` (this skill's folder) as its header says, and write it to `skills/update-gtm-context/SKILL.md`. Show the user the "Where things live" and "Where new information comes from" sections before writing.
2. Copy into the plugin: `update-playbook.md`, `mining-playbook.md` and `source-map.md` from this skill's `references/`; `language-miner.md` and `source-reader.md` from `<this skill folder>/../../agents/`; GitHub version only, `gtm_csv.py` from this skill's `scripts/`. Quote the paths: they can contain spaces.
3. Write the two manifests:

```json
{ "name": "my-gtm",
  "owner": { "name": "<their company>" },
  "metadata": { "description": "My own GTM context update skill." },
  "plugins": [ { "name": "my-gtm-context", "source": "./plugins/my-gtm-context",
                 "description": "Keeps my GTM context up to date." } ] }
```

```json
{ "name": "my-gtm-context", "version": "1.0.0",
  "author": { "name": "<their company>" },
  "description": "My own GTM context update skill, made by the AI Growth Systems Bootcamp setup." }
```

4. Run `claude plugin validate ~/gtm-update` and fix anything it reports.

## 4. Publish it as a private repo

`git -C ~/gtm-update init`, commit with `my GTM update skill`, then `gh repo create gtm-update --private --source ~/gtm-update --remote origin --push`. Check it's private (`gh repo view gtm-update --json visibility -q .visibility`). On a rerun, commit and push to the existing repo instead.

## 5. Add it to their Claude account

Walk them through it, one step at a time, and wait for each:
1. In claude.ai or the Claude app, open **Customize > Plugins > Add > Add marketplace** and enter `<owner>/gtm-update`.
2. Because the repo is private, the dialog asks to **Connect GitHub** and to give the Claude GitHub App access to `gtm-update`. Give it access to that repo only.
3. Add the `my-gtm-context` plugin, and turn on **Sync automatically**, so changes they push reach their account.
4. Check it arrived: in Claude Code, `claude plugin list` shows `my-gtm-context@synced` after a restart or `/reload-plugins`. This needs Claude Code signed in with their Claude account (not an API key), version 2.1.273 or later.

## 6. Create the schedule

The prompt must stand on its own, because each run starts with no memory:

```
Scheduled run of the GTM update. Use the update-gtm-context skill (my-gtm-context plugin) in "scheduled run" mode.
Do not ask questions. Alert: <email to address | Slack DM to member ID>.
GitHub version only: Commit: <yes|no>. Push: <yes|no>.
```

- **App task:** `create_scheduled_task` with taskId `gtm-update`, a title like "Weekly GTM update" and the cron expression (for example `0 8 * * 1`).
- **Cloud task:** run the `/schedule` skill with the same prompt and timing. Select the repository: `gtm-context` in the GitHub version (the run writes there), `gtm-update` in the Notion version (a cloud task needs one; the run doesn't change it). Leave on the connectors the plan uses, plus the alert one.

Record it under "Updates" in the hub (format in `hub-structure.md` or `repo-structure.md`), and create the "Updates to review" page or `gtm/updates/` folder if it doesn't exist.

## 7. First run

Offer a first run now, so they see a real report: run `my-gtm-context:update-gtm-context` in scheduled-run mode. If the synced plugin isn't loaded yet, read `~/gtm-update/plugins/my-gtm-context/skills/update-gtm-context/SKILL.md` and follow it. Stay available for questions.

## 8. Remove the course plugin

Explain in one line: everything they need is now in their own plugin, and keeping both means two skills that do similar things.
- **Installed in Claude Code:** `claude plugin uninstall gtm-context-notion@ai-growth-system-bootcamp` (or `gtm-context-github@...`), after their OK.
- **Added in Customize:** they remove it there (open the plugin, menu, **Remove**).
- **The course marketplace:** keep it if they use other course plugins (voice-miner lives there too). Removing a marketplace removes every plugin installed from it, so offer `claude plugin marketplace remove ai-growth-system-bootcamp` only if they don't.

The pointer in Claude's memory stays: later course systems use it to find the context.

## 9. Tell them how to use it

Three lines:
- Updates run on their own, and an alert says what changed.
- "Review GTM updates" goes through the proposed changes. "Change my GTM update settings" adds a source or changes the alert or schedule.
- For a bigger change (a new ICP from scratch, a first competitor study), they install the course plugin again and run that section, then rerun this handover.
