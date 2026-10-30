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

Same buckets. Use the Sent Items folder. If there's no connector, have them export: Outlook desktop, then File, then Open & Export, then Import/Export, then export a .pst of Sent Items. A .pst needs a converter. The easier route is to select 150 sent emails and drag them into a folder. On a Mac that saves .eml files, which the `extract` command below reads. Outlook for Windows saves .msg files, which the script can't read. There, use the connector or the paste fallback below.

### Fallback: export

- Gmail: Google Takeout, then Mail, then only the "Sent" label. You get an .mbox file. Apple Mail exports .mbox too.
- Turn .mbox and .eml files into the JSONL with the script. Call it by its full path in the skill folder:

  ```bash
  python3 "<skill-folder>/scripts/voice_mine.py" extract Sent.mbox more-emails/ -o voice-mining/emails.jsonl --from jane@acme.com
  ```

  It reads plain text and HTML-only emails in any charset, prefers the plain text part, turns HTML into text, and drops the quoted thread and attachments. `--from` keeps only mail the person sent. Without it, the summary lists the top senders so you can check. Each row gets a `thread` hint: `reply` if it answers an earlier message, `first` if it starts a thread. Use it to set `kind` below: a `first` row is `cold` or `new`, a `reply` row is `reply` or `followup`. Never parse the files by hand: multipart and HTML mail need the script.
- Any client: the person forwards 50 sent emails to themselves or pastes them into a doc. That's slow but enough for a first version.

### JSONL format

One email per line:

```json
{"id": "18c2f...", "date": "2025-03-14", "to": "anna@acme.com", "subject": "Re: proposal", "kind": "reply", "body": "Hi Anna,\n\n..."}
```

`kind`, set by you. Use exactly these four for email. The script and the personal skill use the same words:

- `cold`: first message in a thread, to someone who has never written to them. Check the thread and their inbox for earlier contact.
- `followup`: they wrote again with no reply in between, a nudge or a bump.
- `reply`: answering someone who wrote to them.
- `new`: first message in a thread to someone they already know, like a client, partner or past lead.

Leave out emails to colleagues at their own company. They're a different register and would blur the numbers.

LinkedIn posts and DMs they confirmed they wrote can go in the same file with `kind` set to `post` or `dm`. With 5 or more of a kind, `fingerprint` measures them separately and `check` uses those numbers. With fewer, `check` skips the length and greeting checks for that kind and says so.

Dates are ISO `YYYY-MM-DD`. The pre-AI baseline depends on them, so never guess a date. If you can't find one, write `"date": null`. Undated emails are still scored, but they never count as pre-AI.

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

Save each call as `voice-mining/calls/YYYY-MM-DD-<type>.txt` (or keep the .vtt or .srt). The transcript command reads:

- `Name: text`, `[00:01:02] Name: text` and `Name (00:01): text` lines.
- WebVTT `<v Name>text</v>` (Teams) and `Name: text` cues (Zoom), and .srt files.
- Otter style: `Name  0:03` on its own line, then the text below.
- A name on its own line, then the text below, with a blank line between turns.

Files can be UTF-8 or Windows/Latin-1. `--speaker` must match the label exactly (case doesn't matter), so `Speaker 1` never picks up `Speaker 10`. If nothing matches, the command prints the labels it found. Lines like "Next step: ..." or "Nota bene: ..." are read as speech, not as a new speaker.

AI summaries, action items and "key takeaways" from recorders are AI-written. Never mine them. Only the person's own spoken words count.

## Posts and DMs (optional)

- LinkedIn connectors (AuthoredUp, LeadShark, or similar) can list their posts with performance. Pull the last 20 to 30.
- Ask which ones they wrote themselves, without AI. Only those count for wording. AI-assisted top performers can still show structure and topics.
- DMs they sent to prospects are gold for cold messages. Treat them like cold emails.
