# Pulling the sources

Use whatever connector is available. Search for the tools by keyword (gmail, outlook, fathom, granola, gong, fireflies, otter, zoom) before asking the person to export anything. If nothing is connected, the fallbacks at the bottom of each section work everywhere.

## Sent email

### What to pull

| Bucket | How many | Why |
|---|---|---|
| Pre-AI: sent before 2022-11-30 | 50 to 100 if available | Baseline. Proves how they wrote with no assistant. |
| Last 12 months, to external people | 100 to 200 | Current voice. |
| Cold emails and first follow-ups | All you can find, up to 40 | Matter most for outreach. Hardest to get right. |

Skip newsletters, mass mails, calendar traffic, and threads where they only forwarded something.

### Gmail

Search queries (pass to the search threads tool):

- Current: `in:sent newer_than:12m -subject:(invitation OR accepted OR declined) -label:chats`
- Pre-AI baseline: `in:sent before:2022/11/30 after:2019/01/01`
- Likely cold or first-touch: `in:sent newer_than:24m -in:inbox -subject:re:` and then keep threads where the person sent the first message

For each thread, open it and keep only the messages the person sent. Take the body as plain text. The clean step strips the quoted history, but take the newest part when you can.

Work in batches of 20 to 30 threads and append to the JSONL as you go, so a long run doesn't hold everything in context.

### Outlook / Microsoft 365

Same buckets. Use the Sent Items folder. If there's no connector, have them export: Outlook desktop, then File, then Open & Export, then Import/Export, then export a .pst of Sent Items. A .pst needs a converter. The easier route is to select 150 sent emails, drag them into a folder, and save them as .msg or .eml files, which Claude can parse.

### Fallback: export

- Gmail: Google Takeout, then Mail, then only the "Sent" label. You get an .mbox file. Parse it with Python's `mailbox` module and convert to JSONL. Use `message.get_payload(decode=True)` and prefer the text/plain part.
- Any client: the person forwards 50 sent emails to themselves or pastes them into a doc. That's slow but enough for a first version.

### JSONL format

One email per line:

```json
{"id": "18c2f...", "date": "2025-03-14", "to": "anna@acme.com", "subject": "Re: proposal", "kind": "reply", "body": "Hi Anna,\n\n..."}
```

`kind`, set by you:

- `cold`: first message in a thread, to someone who has never written to them. Check the thread and their inbox for earlier contact.
- `followup`: they wrote again with no reply in between, a nudge or a bump.
- `reply`: answering someone outside the company.
- `internal`: a colleague at the same domain. Used for contrast only, not for the profile's main numbers.

Dates are ISO `YYYY-MM-DD`. The pre-AI baseline depends on them, so never guess a date.

## Call transcripts

### What to pull

5 to 10 calls from the last 6 months where the person talks a lot and is selling or advising:

- Discovery, demo, proposal walk-through, negotiation, renewal, onboarding or kickoff.
- Plus 1 webinar, workshop or podcast if there is one. Long monologues are the best source for posts.
- Skip internal standups and calls where they barely speak. The transcript command reports `talk_share` per call, so drop any under 0.25.

### By tool

- **Fathom**: list or search meetings, then get the transcript per recording. Speaker labels are usually the real name.
- **Granola**: list meetings, then get the meeting transcript. Notes are AI summaries, so never mine the notes, only the transcript.
- **Gong**: calls by date range, then transcript per call. Speakers are IDs, so map them to names with the call's party list.
- **Fireflies, Otter, tl;dv, Zoom, Teams**: if there's no connector, export the transcript as .txt or .vtt and drop the files into `voice-mining/calls/`.
- **No recorder**: ask for 2 or 3 voice memos where they explain their offer and answer a typical objection, and transcribe them. Or ask for a YouTube or podcast link where they speak. Even 20 minutes is useful.

Save each call as `voice-mining/calls/YYYY-MM-DD-<type>.txt`, with lines like `Name: text` or `[00:01:02] Name: text`. The transcript command also reads WebVTT `<v Name>` lines.

AI summaries, action items and "key takeaways" from recorders are AI-written. Never mine them. Only the person's own spoken words count.

## Posts and DMs (optional)

- LinkedIn connectors (AuthoredUp, LeadShark, or similar) can list their posts with performance. Pull the last 20 to 30.
- Ask which ones they wrote themselves, without AI. Only those count for wording. AI-assisted top performers can still show structure and topics.
- DMs they sent to prospects are gold for cold messages. Treat them like cold emails.
