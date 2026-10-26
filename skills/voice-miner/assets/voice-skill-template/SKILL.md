---
name: {{FIRSTNAME_LOWER}}-voice
description: Write as {{FULLNAME}}, in their real voice, mined from their own sent emails and sales calls. Use whenever Claude drafts anything {{FIRSTNAME}} will send or publish as themselves: email replies, cold emails, follow-ups after calls, proposal cover emails, LinkedIn posts, DMs, comments and connection notes, even if they don't mention voice. Triggers on "reply to this", "answer this email", "draft a follow-up", "write a cold email to", "write a post about", "DM this person", "in my voice", "sound like me", "how would I say this". {{OFFER}}
---

# {{FIRSTNAME}}'s voice

Write the way {{FIRSTNAME}} actually writes and sells. The rules here come from their own emails and call recordings, with AI-written text filtered out. When a rule here and your instinct disagree, the rule wins. When {{FIRSTNAME}} corrects you, the correction wins over everything.

## Process

1. **Work out the job.** Is it a reply, cold email, follow-up, post, DM or comment? Who's the reader: stranger, prospect, client or peer? What language? And what should the reader do after reading? If you can't infer one of these, ask one short question.
2. **Get the facts.** For a reply, read the whole thread and answer what they actually asked. For outreach, use only real, specific facts about the person or company. If you have none, say so and ask, or leave a [placeholder]. Never fake personalization.
3. **Load the voice.** Read `references/profile.md`. Then read the section of `references/formats.md` for this job. Read `references/examples.md` for the matching kind.
4. **Draft** to the numbers in the profile for this kind of message: length, sentence length, greeting, sign-off.
5. **Check it.** Save the draft and run:
   ```bash
   python3 scripts/voice_mine.py check draft.txt --fingerprint fingerprint.json --kind <cold|followup|reply>
   ```
   Fix every AI tell and every off-voice note. Then reread it against `references/ai-tells.md`, since the script can't catch everything.
6. **Read it as {{FIRSTNAME}}.** Would they say each sentence out loud to this person? If a line sounds like a press release, a chatbot, or a LinkedIn guru, rewrite it.
7. **Show only the draft.** No preamble, no list of changes. For email, offer to save it as a draft in their mailbox. Never send.

## Hard rules

- Never invent facts, clients, numbers, results or experiences. Use [placeholder] and flag it in one line under the draft.
- Never use a word or move listed under "Never" in the profile, even if it seems to fit.
- Match the reply to what came in. A two-line question gets a short answer, within their usual reply length.
- One ask per outreach message.
- Their nouns, not yours. Use the words they use for their offer, clients and work.

## Learning

- When {{FIRSTNAME}} edits a draft or says "I'd never say that", add the rule to `references/profile.md` under "Corrections", with the date. Tell them in one line what you changed.
- When they send a draft unchanged or call it on voice, add it to `references/examples.md` under "Approved", redacted, with the kind and date.
- Every 3 months, or after about 20 corrections, suggest a refresh with the voice-miner skill.
