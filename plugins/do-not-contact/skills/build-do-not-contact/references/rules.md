# Rules for the do-not-contact list

## The contract every outreach system follows

1. **Before contacting anyone,** check the batch against the list with `check-do-not-contact`. This means one filtered lookup per batch, never the whole list.
2. **When someone says no, unsubscribes or bounces,** add them with `update-do-not-contact`. This applies on any channel. A no on LinkedIn also stops email, and the other way round.

Each outreach system may keep its own record of who it already contacted, if it needs one. This list is the only thing they all share.

## Keys and matching

- **A person** is matched by email or LinkedIn URL. One match is enough.
- **A company** row (Scope = company) blocks everyone whose email or website is on that domain.
- **Personal email providers** (gmail.com, outlook.com, yahoo and others) are never blocked company-wide. `dnc.py` refuses them.
- **Rows with a past Until date** no longer block anyone. They stay on the list as history.
- **Always clean keys with `dnc.py`** before comparing or writing. For example, `https://it.linkedin.com/in/Jane-Doe/?utm=x` and `linkedin.com/in/jane-doe` are the same person.
- **A lead with no email, LinkedIn URL or website can't be checked.** Say how many there were. Don't guess from the name.

## What is never deleted

- said no, unsubscribed, bounced and erasure request rows stay forever.
- Only the student can remove a row, in review mode, and only after one clear yes for that row.
- A customer who churned, or a deal that closed lost, is not removed automatically. The weekly run proposes it in `To review`, and the student decides. Some will want churned customers left alone anyway.

## Approval

- **During the build:** show counts by reason and source, five sample rows and the unsure list. Write after one OK.
- **Quick add:** the student asked for it, so write it and confirm in one line.
- **The weekly scheduled run** is authorised once, at setup. It may only:
  - add rows to the list;
  - add rows to `To review`;
  - update the Last run dates;
  - send one alert to the student's own email or Slack DM.

  It never removes or changes a row, and never contacts anyone else.

## Privacy

- **This list is the one place in the course where emails and profile links are kept on purpose.** That's because it has to identify people in order to protect them. Keep only the columns in `storage.md`: no names, no message text.
- **Never copy rows into the GTM context, a prompt file, a skill, or a public repo.** Other files only link to the list.
- **A Sheet is shared with the team only,** never "anyone with the link".
- **Temporary files** go in `~/do-not-contact/.private/` and are deleted at the end of every run.
- **An erasure request:** delete the person's data everywhere else, but keep their email on this list, with Reason "erasure request" and nothing else. That's what stops them being contacted again, and keeping a suppression record is usually allowed for exactly this purpose. Say that this isn't legal advice, and that they should check their own rules if they're unsure.

## For sending tools

- Most email sending tools have a global blocklist. Ask the student to switch it on.
- Upload the file from `dnc.py blocklist` every time a new campaign is loaded. Weekly is enough for most students.
- LinkedIn-only rows can't go in an email blocklist. They're still caught by `check-do-not-contact`.
