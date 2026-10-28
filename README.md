# AI Growth System Bootcamp

Claude skills from the AI Growth Systems Bootcamp by [Pietro Montaldo](https://www.linkedin.com/in/pietromontaldo/) (NotLinear). Built for non-technical operators who want Claude to do real GTM work.

## Skills

| Skill | What it does |
|---|---|
| [voice-miner](plugins/voice-miner/skills/voice-miner) (plugin) | Learns your real voice from your sent emails and sales calls, and builds you a personal skill that writes emails, cold outreach and LinkedIn posts that sound like you, not like AI. |
| [GTM context](#gtm-context) (plugin) | Builds your go-to-market context layer with you: what you sell, your ideal customer, competitors, how your buyers talk, objections and shareable customers. It reads what you already have first, then asks only about gaps. Lives in Notion or in your own GitHub repo. |

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

voice-miner is a plugin in this repo's marketplace.

**Claude Code:** add this repo as a plugin marketplace once, then install it:

```
/plugin marketplace add pietro-montaldo/AI-Growth-System-Bootcamp
```

```
/plugin install voice-miner@ai-growth-system-bootcamp
```

**Claude app (Cowork):** add `pietro-montaldo/AI-Growth-System-Bootcamp` as a plugin marketplace in the app's plugin settings, then install Voice Miner from it. If you'd rather upload just the skill: download this repo, zip the `plugins/voice-miner/skills/voice-miner` folder, and upload it under Settings > Capabilities > Skills.

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

`plugins/voice-miner/skills/voice-miner/references/ai-tells.md` is a sourced catalog of what makes text read as AI-written, as of October 2026. It draws on Wikipedia's "Signs of AI writing", corpus studies, model-by-model analyses and cold email practitioners. Two findings shaped the skill:

- **Em dashes are no longer a reliable tell.** Wikipedia moved them to "historical indicators". The newer tells are contrast reframes ("rather than merely"), salience flags ("this matters because"), mannered metaphors ("load-bearing", "earns its keep") and fake-candor adverbs ("honestly", "quietly").
- **Overcorrecting is its own tell.** Text with zero dashes, zero contractions and choppy fragments reads like a different model. That's why the skill anchors on your real samples, not on a ban list.

These tells change with every model release. The skill tells Claude to refresh the list when it's more than 6 months old.

### Structure

```
plugins/voice-miner/
├── .claude-plugin/plugin.json        # plugin manifest
└── skills/voice-miner/
    ├── SKILL.md                      # the mining workflow
    ├── scripts/voice_mine.py         # clean, score, fingerprint, transcript, check
    ├── references/
    │   ├── sources.md                # how to pull email and calls per tool
    │   ├── analysis-guide.md         # what to read for in emails and calls
    │   └── ai-tells.md               # sourced catalog of AI writing tells
    └── assets/voice-skill-template/  # the personal skill it fills in for you
```

---

## GTM context

Every system you build with Claude (outbound, inbound, content) needs to know what you sell, who it's for, and how your buyers talk. Good context is the difference between an agent that writes "Hi {first_name}, I help companies grow" and one that sounds like you talking to your best customer.

This plugin builds that context with you. Most people already have a lot of it somewhere: a sales page, a CRM, a course platform, a few docs, months of calls and email. So it starts by asking where things live, reads them, and drafts. You only answer what your sources can't.

### Pick your version

| | Notion + GitHub | GitHub only |
|---|---|---|
| Your context lives in | Notion, under one GTM Hub page | Markdown pages and CSV tables in your own private repo |
| Good if | your team already works in Notion | you don't use Notion, or want everything in one place |
| You need | a Notion connector in Claude | a GitHub repo (private) |
| Plugin | `gtm-context-notion` | `gtm-context-github` |

Both work the same way and produce the same six sections. Only where the result is stored differs.

### Install

In Claude Code, add this repo as a plugin marketplace once:

```
/plugin marketplace add pietro-montaldo/AI-Growth-System-Bootcamp
```

Then install your version and start it:

| Notion + GitHub | GitHub only |
|---|---|
| `/plugin install gtm-context-notion@ai-growth-system-bootcamp` | `/plugin install gtm-context-github@ai-growth-system-bootcamp` |
| `/gtm-context-notion:build-gtm-context` | `/gtm-context-github:build-gtm-context` |

### What happens when you run it

About 30 minutes of your time, less if a lot already exists. You can stop at any step and pick up later.

1. **Tell Claude where things already live.** Your website, a Notion page, your CRM, your course or payment platform, your call recorder, your inbox, plus anything else you'd like included, like case studies or a pitch deck. A rough pointer is enough. Where there's no connector (for example a Maven or Stripe dashboard), Claude says so and offers to browse there read-only with Claude in Chrome, or to read an export.
2. **Set up where it lives.** In Notion, one GTM Hub page that links to everything. In GitHub, a private `gtm-context` repo. Either way, Claude remembers where it is (see below), so you're never asked where to save. Customer and objection lists you already keep somewhere connected are linked, not copied.
3. **Claude reads everything at once,** with parallel agents, then shows you what it found per section.
4. **Product & offer,** drafted from your pages and docs.
5. **Customers.** For long lists or B2C, "best customers" come from behaviour you choose (bought again, came back for more, left reviews) instead of picking names.
6. **Competitors,** optional. Claude researches each one in parallel.
7. **ICP,** built from your best customers, or from your competitors' customers if you have none yet. Signals are ones you can check in public company and profile data (headcount growth, job postings, time in role), so your outbound agent can score people before you talk to them.
8. **Customer language.** With your OK, Claude reads recent calls, webinars, emails and DMs and pulls out how buyers describe the problem in their own words.
9. **Objections,** grouped by theme with the answers that work.
10. **Logo permission:** which customers you may show publicly. Only the ones that said yes.
11. **Your own update skill,** so it stays current (see below).

You see every draft before anything is written. Nothing is ever sent, and in the GitHub version nothing is committed or pushed without asking. While the course plugin is installed, you can also run any section on its own, for example `/gtm-context-github:gtm-objections` to redo objections from last month's calls.

### Keep it fresh: your own update skill

Context goes stale within weeks: prices change, new customers buy, new objections show up. After the first build you only need to keep it current, so the build ends by handing you your own update skill and removing the course plugin:

1. **Plan where new information comes from.** For every source you gave, Claude works out whether it keeps updating on its own (a CRM, your inbox, your call recorder, a dashboard) or was a one-off (an uploaded file, a pasted list). For one-offs it asks where new customers or objections will show up from now on, and whether it can fetch them or you'll send them.
2. **Pick where and when it runs.** A scheduled task in the Claude app (on your computer, can read dashboards like Maven through Claude in Chrome) or in the cloud (runs even when your computer is off, connectors only). Weekly by default, plus an email or Slack alert to yourself.
3. **Claude writes your update skill** and saves it in a private `gtm-update` repo on your GitHub.
4. **You add it to your Claude account** in Customize > Plugins > Add marketplace, so it works in Claude Code, Cowork and scheduled runs.
5. **First run, then the course plugin goes.** You see a real report, then Claude helps you remove the course plugin (other course plugins, like voice-miner, stay).

Every run:
- **Adds what's new to your banks on its own:** new customers, new and repeat objections, and new buyer quotes on the messaging page.
- **Once a month, checks your offers, prices and website** against your Product & offer page, and whether new customers still match your ICP.
- **Never rewrites your pages.** Anything that needs a decision becomes a numbered "proposed update" in a report.
- **Sends you a short alert** with what changed, a link to the report, and a reminder when a file from you is due.

Say "review GTM updates" to go through the proposed updates, or "change my GTM update settings" to add a source or change the alert or schedule. For a bigger change, like a new ICP from scratch, install the course plugin again and run that section.

### Where your context lives

Your GTM context isn't tied to any one project, so every project, every later course system (outbound, inbound, content) and every scheduled update finds the same context. You're never asked where to save it.

| Notion version | GitHub version |
|---|---|
| Everything lives in Notion. The GTM Hub page is the map: it links to every page and database, and a collapsed "For agents" section holds the settings. Nothing is saved on your computer. | Everything lives in your private `gtm-context` repo on GitHub, cloned at `~/gtm-context`, with the context in `gtm/` inside. |

During setup, Claude also adds a few lines to its global memory (`~/.claude/CLAUDE.md`) saying where your context is: the Hub link, or the repo. Any Claude session can then use it without searching. You see the lines first and approve them. In the GitHub version, if you use Cowork, share the `~/gtm-context` folder with it once.

### How it's organised

```
Notion version                      GitHub version (inside ~/gtm-context)
GTM Hub (page)                      gtm/
├── Product & offer                 ├── README.md       the hub
├── ICP                             ├── product.md
├── Messaging & customer language   ├── icp.md
├── Competitors (+ database)        ├── messaging.md
├── Objections bank (database)      ├── competitors.md + .csv
├── Customers (database)            ├── objections.csv
└── Updates to review               ├── customers.csv
                                    └── updates/          update reports
```

Three rules keep it fast and cheap for agents to read:

1. **One hub links to everything.** Skills open the exact page they need by link and never search.
2. **Short pages, summary at the top.** One or two screens each, long examples further down.
3. **Query banks, don't read them whole.** Objections, competitors and customers are databases or CSV files, read with filters. The GitHub version ships a small helper script for that, so you never edit the CSV files by hand.

### Privacy

- Claude reads your email, calls and DMs only if you choose those sources, and only for this build.
- Quotes are saved with role and company type ("Founder, 8-person agency"), never names, emails or profile links.
- Customer logos are marked shareable only when you confirm the customer gave permission.
- In the GitHub version, raw exports go in `gtm/.private/`, which git ignores, and are deleted once read.

### Structure

```
.claude-plugin/marketplace.json   # the plugin marketplace for this repo
plugins/gtm-context-notion/       # Notion + GitHub version
plugins/gtm-context-github/       # GitHub-only version
shared/                           # text, agents and the helper scripts both versions use
scripts/sync-shared.sh            # copies shared/ into the plugins
```

Inspired by Corey Haines' [product-marketing skill](https://github.com/coreyhaines31/marketingskills/tree/main/skills/product-marketing) and Lenny's [defining-icp skill](https://github.com/RefoundAI/lenny-skills/tree/main/skills/defining-icp).

## License

MIT. Use it, adapt it, share it. See [LICENSE](LICENSE).
