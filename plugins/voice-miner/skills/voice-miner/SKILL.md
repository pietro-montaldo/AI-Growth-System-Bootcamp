---
name: voice-miner
description: "Mine a person's real voice from their sent emails and sales call transcripts, filter out anything AI-written, and turn it into a personal \"<name>-voice\" skill that writes email replies, cold emails, follow-ups, LinkedIn posts and DMs that sound like them and not like AI. Use when someone says \"learn my voice\", \"clone my writing style\", \"make Claude write like me\", \"build my tone of voice\", \"mine my emails\", \"analyze how I talk on calls\", \"my drafts sound like ChatGPT\", \"set up my voice skill\", or wants Claude to answer emails or write posts and outreach as them. Also use to refresh an existing voice skill with new emails, calls or corrections. Not for company brand guidelines (use a brand voice skill) or for cleaning one draft (use a humanizer skill)."
metadata:
  version: "1.1.0"
---

# Voice miner

Build a voice from evidence, not adjectives. The output is a personal skill, `<firstname>-voice`, that the person installs once. From then on Claude writes their emails, posts and outreach in that voice.

Two sources, two registers:

- **Sent email** is how they write. It sets the rules for emails and DMs: length, greetings, sign-offs, punctuation, how direct they are.
- **Call transcripts** are how they think and sell out loud. They supply the content moves: how they explain the offer, handle objections, talk price, ask for the next step, and the comparisons and stories they repeat. Posts mostly borrow from this register.

The main risk is learning from text that AI already wrote. Since 2023 a lot of "sent" email was drafted by Gmail, Copilot, Superhuman or ChatGPT. Learning from it teaches Claude to sound like Claude. Step 3 filters it out.

## Before you start

Ask everything in one go (AskUserQuestion when available). Don't start pulling data before you have the answers.

1. Full name, role, and what they sell to whom. One line, like "I sell AI training to marketing teams at mid-size B2B companies".
2. Which email account to mine, and which call recorder they use (Fathom, Granola, Gong, Fireflies, Otter, Zoom, Teams, or files).
3. Languages they write business email in.
4. Which AI writing tools they have used for email since 2023 (Gmail "Help me write", Copilot, Superhuman AI, ChatGPT, Grammarly, Lavender, sequence tools). Also: does anyone else send from this inbox, like an assistant?
5. Optional: 3 to 5 LinkedIn posts or messages they wrote themselves and are proud of.

Then tell them what happens to the data. Raw emails and transcripts stay in a local working folder, `voice-mining/`, and are deleted at the end unless they want to keep them. The finished skill only holds short excerpts, with names, companies and numbers swapped for placeholders. They approve every excerpt before it goes in.

## Process

Run the script by its full path: `python3 "<skill-folder>/scripts/voice_mine.py"`, where `<skill-folder>` is the folder that holds this SKILL.md. Keep the quotes, since paths often have spaces.

### 1. Pull sent email

Read `references/sources.md` for how to do this with each connector or export. Targets:

- 150 to 300 sent emails. A mix of new emails and replies, mostly to people outside their company. Prospects and clients matter most.
- Older emails from before 30 November 2022, when ChatGPT launched, if the mailbox goes back that far. 20 or more of these give the person a pre-AI baseline: proof of how they wrote before any assistant existed. Aim for about a third of the sample.
- The last 12 months, so the voice is current.

Save the emails as JSONL in `voice-mining/emails.jsonl`. For .mbox or .eml exports, the script's `extract` command writes it; never parse mail by hand. Each email's `kind` is one of `cold`, `followup`, `reply` or `new`. `sources.md` explains how to tell them apart.

### 2. Clean

```bash
python3 "<skill-folder>/scripts/voice_mine.py" clean voice-mining/emails.jsonl -o voice-mining/clean.jsonl
```

The script removes quoted replies, forwards, signatures, calendar invites and auto-replies. It also drops templates: anything sent 3 or more times almost unchanged is a sequence or a snippet, not their voice. Look over the summary it prints. If it removed fewer than 20% or more than 70% of the emails, open a few and check why before going on.

### 3. Filter out AI-written emails

```bash
python3 "<skill-folder>/scripts/voice_mine.py" score voice-mining/clean.jsonl -o voice-mining/scored.jsonl
```

Every email after 30 November 2022 gets an AI score with reasons, and lands in one of three verdicts: `human`, `suspect` or `ai`. With 20 or more pre-AI emails, the script first learns the person's own habits. If they always used em dashes or "I hope you're well", those don't count against them.

Then check with the person:

- Show the top suspects: date, subject, the first two lines and the reasons. Ask "Did you write these yourself, or did a tool help?" Their answer beats the score.
- Edit `verdict` in `scored.jsonl`: `ai` for the emails they disown, `human` for the ones they claim. Only `human` and `human-preAI` emails go into the fingerprint.
- With no pre-AI baseline, be stricter. Treat every `suspect` they don't explicitly claim as AI.
- Some tools can't be detected from text. If they said they use one, ask which kinds of email it touched, like follow-ups or long proposals, and leave that kind out.

Tell them in one line how many emails survived. Fewer than 40 human emails is thin. Say so, and lean more on the calls.

### 4. Measure the written voice

```bash
python3 "<skill-folder>/scripts/voice_mine.py" fingerprint voice-mining/scored.jsonl -o voice-mining/fingerprint.json
```

This measures the voice in numbers, split by language and by kind of email: length range, sentence length, greetings, sign-offs, punctuation per 100 words, contractions, hedges, bullets, sentence starters and recurring phrases. These numbers become hard targets in the finished skill. Adjectives like "concise" can't be checked. "Median reply 48 words, never past 120" can.

Then redact. Phrases and sentence starters can hold client names, and the command prints the `possible names` it found. Ask the person which are clients, companies or people, then run `redact voice-mining/fingerprint.json -o voice-mining/fingerprint.redacted.json --term "<name>"` (repeat `--term`, add `--drop "<phrase>"` for anything else). It also swaps emails, links, phone numbers and amounts. Show them the list it prints and get a yes.

Then read 30 to 40 of the human emails yourself. Prioritize cold emails, follow-ups and replies to prospects. Use `references/analysis-guide.md`, part A. Numbers catch the form. Reading catches the moves: how they say no, how they push a deal forward, how warm they are with a client they've had for years compared with a stranger.

### 5. Mine the calls

Pull 5 to 10 recent commercial calls: discovery, demo, proposal walk-through, negotiation, onboarding. Add one webinar or talk if there is one; that's the best source for posts. Save the transcripts as text in `voice-mining/calls/`.

```bash
python3 "<skill-folder>/scripts/voice_mine.py" transcript voice-mining/calls/ --speaker "<name as labeled>" \
  -o voice-mining/speech.json --turns-out voice-mining/my-turns.txt
```

Check the speaker label first. Some recorders write "Speaker 1" instead of the name. The match is exact, and when nothing matches the script prints the labels it found. Read `my-turns.txt` using `references/analysis-guide.md`, part B. With more than 6 calls, split them across subagents. Each one returns part B's template for its batch, so your context holds conclusions instead of raw transcripts.

### 6. Optional: posts and DMs

If they shared posts or DMs, or a LinkedIn connector is available, include them. Posts from 2023 onward are often AI-assisted. Only use the ones they confirm they wrote, and run them through `check` first (step 8). Weight their best performers, but only for structure and topics, never for wording you haven't confirmed is theirs.

### 7. Write the profile

Copy `assets/voice-skill-template/` to `<firstname>-voice/`. Then fill it in:

- `references/profile.md` covers voice traits with evidence, numbers, commercial moves, words they use and never use, and how spoken habits translate to the page. Fill every placeholder. Where the evidence is thin, write "not enough evidence" instead of guessing.
- `references/formats.md` adapts the voice to cold email, follow-up, reply, new email, LinkedIn post, DM and comment.
- `references/examples.md` holds 6 to 10 real excerpts, redacted. Show the person the list and get a yes before saving.
- Copy `voice-mining/fingerprint.redacted.json` (saved as `fingerprint.json`, never the unredacted one), `scripts/voice_mine.py` and `references/ai-tells.md` into the new skill.
- `SKILL.md`: replace `{{FIRSTNAME}}`, `{{FIRSTNAME_LOWER}}`, `{{FULLNAME}}` and `{{OFFER}}` (one sentence: what they sell to whom, so Claude knows the context). Add any trigger phrases they actually use, like "answer Lucy" or "draft the bump". Keep `description` one double-quoted string and write every quote inside it as `\"`, or the skill won't load.

Rules for the profile:

- Every trait needs evidence: a quote, or a number from the fingerprint. No evidence, no trait.
- Describe what they do, not what kind of person they are. "Opens replies with the answer, no greeting, 40% of the time" is a rule Claude can follow. "Direct and friendly" isn't.
- Keep the two registers apart. A comparison they use on calls might fit a post, but it's out of place in a three-line email reply.
- Write "never" rules from what's missing too. If they wrote 200 emails and never once said "I hope this finds you well", that's a rule.

### 8. Blind test before handing over

Write 4 drafts with the new skill:

1. A reply to a real email they received recently.
2. A cold email to a real kind of prospect they target.
3. A follow-up after a call.
4. A LinkedIn post on a topic they talk about on calls.

Run each one through `check` before showing it, with `--kind` set to what it is (`post` for the post). Read its warnings: they say which checks were skipped.

```bash
python3 "<firstname>-voice/scripts/voice_mine.py" check draft.txt --fingerprint "<firstname>-voice/fingerprint.json" --kind cold
```

Mix in one real email they wrote, unlabeled, and ask: "Which of these didn't you write? Mark anything you'd never say." If they can't find the real one, the skill is ready. Otherwise, add every correction to `profile.md` as a rule and redraft until they would send the draft without editing it.

### 9. Package and hand over

Zip the `<firstname>-voice/` folder. Tell them how to install it in one or two lines. In the Claude app: Settings, then Capabilities, then Skills, then upload the zip. In Claude Code: copy the folder into `~/.claude/skills/`.

Delete `voice-mining/` unless they asked to keep it. End with the one sentence that triggers it, like "Reply to this in my voice".

## Refresh mode

When the person already has a `<firstname>-voice` skill, read its `profile.md` and the corrections log first. Then mine only what's new: emails since the last refresh, plus new calls. Rerun clean, score and fingerprint on the new batch, then compare. Update the numbers. Promote any repeated correction to a rule. Flag drift, like replies getting longer, and ask before changing a rule they approved.

If `references/ai-tells.md` is more than 6 months old, search the web for new AI writing tells first, since they change with every model release. Update the file, the word and phrase lists in `scripts/voice_mine.py`, and the copies inside the person's skill.

## Hard rules

- Never learn from an email that wasn't checked for AI. When in doubt, leave it out. A smaller clean sample is better than a bigger dirty one.
- Never put real names, companies, deal sizes or email addresses into the skill. Use placeholders like [client], [company] and [amount].
- Never invent traits, stories or results to fill a section.
- The person's corrections always beat the numbers.
- Never send email as the person. The finished skill writes drafts, and sending stays with the person.
