# AI Growth System Bootcamp

Claude skills from the AI Growth Systems Bootcamp by [Pietro Montaldo](https://www.linkedin.com/in/pietromontaldo/) (NotLinear). Built for non-technical operators who want Claude to do real GTM work.

## Skills

| Skill | What it does |
|---|---|
| [voice-miner](skills/voice-miner) | Learns your real voice from your sent emails and sales calls, and builds you a personal skill that writes emails, cold outreach and LinkedIn posts that sound like you, not like AI. |

---

## voice-miner

Most "write in my voice" setups describe you with adjectives like "friendly, direct, concise". Claude can't check adjectives, so it falls back on its own style. voice-miner takes evidence instead:

- **Your sent email** shows how you write: length, greetings, sign-offs, punctuation, how direct you are with a stranger compared with a client.
- **Your call recordings** show how you sell and explain: how you describe your offer, handle price and objections, and ask for the next step. They also hold the comparisons and opinions you repeat, which make the best posts.

The catch is that since 2023 a lot of sent email was drafted with AI. If Claude learns from it, it learns to sound like Claude. So before learning anything, voice-miner filters AI-written emails out.

### What it does

1. **Pulls your sent email** through Gmail or Outlook if connected, or from an export. It targets 150 to 300 emails.
2. **Cleans it.** It strips quoted replies, signatures, calendar invites, auto-replies and templates.
3. **Filters out AI-written email.** Every email after ChatGPT's launch (30 November 2022) gets a score with reasons. If you have older emails, those become your pre-AI baseline: if you always used em dashes or "Hope you're well", they don't count against you. You confirm the suspects yourself.
4. **Measures your voice in numbers**, split by language and by kind of email: median length, sentence length, greetings, sign-offs, punctuation, and the phrases you actually use.
5. **Mines your calls** (Fathom, Granola, Gong, Fireflies, Otter, Zoom or plain transcript files) for how you sell, explain and handle objections.
6. **Writes your personal skill**, `<firstname>-voice`, with your profile, per-format rules (reply, cold email, follow-up, recap, LinkedIn post, DM, comment) and real redacted examples.
7. **Runs a blind test.** It writes a few drafts and mixes in one real email of yours. If you can't spot the real one, the skill is ready. If you can, your corrections become rules.

Your personal skill then checks every draft before showing it to you:

```bash
python3 scripts/voice_mine.py check draft.txt --fingerprint fingerprint.json --kind cold
```

The check flags AI tells and anything off your own numbers. For example: "68 words, you rarely go past 41", "greeting 'Dear Anna,' isn't one you use", "too formal, you normally use contractions".

### Install

**Claude app (Cowork):** download this repo, zip the `skills/voice-miner` folder, then upload it under Settings > Capabilities > Skills.

**Claude Code:**

```bash
git clone https://github.com/pietro-montaldo/AI-Growth-System-Bootcamp.git
```

```bash
cp -R AI-Growth-System-Bootcamp/skills/voice-miner ~/.claude/skills/
```

Then ask Claude: "Learn my voice from my sent emails and sales calls."

### Requirements

- Python 3. The script uses only the standard library, so there's nothing to install.
- An email source: a Gmail or Outlook connector, or an export (.mbox, .eml).
- Optional but recommended: a call recorder connector, or transcript files (.txt, .vtt, .srt).

### Privacy

- Raw emails and transcripts stay in a local working folder and are deleted at the end unless you ask to keep them.
- The finished skill holds only short excerpts with names, companies and amounts replaced by placeholders, and you approve each one.
- Nothing is ever sent from your mailbox. The skills write drafts only.

### The AI tells list

`skills/voice-miner/references/ai-tells.md` is a sourced catalog of what makes text read as AI-written, as of October 2026. It draws on Wikipedia's "Signs of AI writing", corpus studies, model-by-model analyses and cold email practitioners. Two findings shaped the skill:

- **Em dashes are no longer a reliable tell.** Wikipedia moved them to "historical indicators". The newer tells are contrast reframes ("rather than merely"), salience flags ("this matters because"), mannered metaphors ("load-bearing", "earns its keep") and fake-candor adverbs ("honestly", "quietly").
- **Overcorrecting is its own tell.** Text with zero dashes, zero contractions and choppy fragments reads like a different model. That's why the skill anchors on your real samples, not on a ban list.

These tells change with every model release. The skill tells Claude to refresh the list when it's more than 6 months old.

### Structure

```
skills/voice-miner/
├── SKILL.md                      # the mining workflow
├── scripts/voice_mine.py         # clean, score, fingerprint, transcript, check
├── references/
│   ├── sources.md                # how to pull email and calls per tool
│   ├── analysis-guide.md         # what to read for in emails and calls
│   └── ai-tells.md               # sourced catalog of AI writing tells
└── assets/voice-skill-template/  # the personal skill it fills in for you
```

## License

MIT. Use it, adapt it, share it. See [LICENSE](LICENSE).
