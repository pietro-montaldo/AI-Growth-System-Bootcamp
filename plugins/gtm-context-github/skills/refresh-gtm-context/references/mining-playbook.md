# Mining playbook: customer language and objections

How to turn calls, emails and messages into customer language and objections. The language-miner agent follows these rules, and so does any skill that reads pasted text.

## What to read

- **External conversations only.** Prospects, customers, partners. Skip internal threads, newsletters, receipts, notifications, calendar invites and cold pitches sent to the user.
- **Where buyers talk most.** Discovery and sales calls first, then email threads where the other person wrote more than two lines, then DMs.
- **Window.** Last 90 days by default. Go back to 12 months if there are fewer than 10 useful conversations.
- **Transcripts over summaries.** Call summaries paraphrase. Read the transcript when you need exact words.

## What to extract

| Type | What it is | Example |
|---|---|---|
| pain | How they describe the problem | "we're drowning in leads we never follow up" |
| outcome | The result they want, in their words | "I just want three good calls a week" |
| objection | Anything that slows or stops the purchase | "I'm not technical enough for this" |
| praise | What they say after it worked | "first time our pipeline didn't depend on me" |
| words | Recurring terms, jargon, names for things | "my outbound", "the CRM mess" |
| trigger | What made them reach out now | "we just lost our only SDR" |

## Rules

1. **Verbatim.** Copy the exact words, up to 25 words. Never polish them. Typos and slang stay.
2. **Source tag on every line.** `[call 2026-09-14]`, `[email 2026-08-02]`, `[DM 2026-10-01]`, `[pasted]`.
3. **No personal data.** Replace names with role and company type: "Head of Growth, 40-person SaaS". No emails, phone numbers or LinkedIn URLs.
4. **Count repeats.** If the same idea shows up in several conversations, keep the best quote and record how many times it came up.
5. **Objections need context.** Record the stage (first call, after proposal, at renewal) and, if visible, what the user answered and whether the deal moved forward.
6. **Say what you could not read.** Report how many threads or calls you read and what you skipped, so the user knows how complete the result is.

## Objection themes

Group every objection under one theme, so the bank can be filtered:

`price` · `timing` · `proof` (does it work, for someone like me) · `fit` (my case is different) · `effort` (time, skills, too technical) · `existing-solution` (we already use X) · `approval` (boss, IT, procurement) · `risk` (safety, data, reputation) · `other`

Use the user's own theme names instead if they already have a list.
