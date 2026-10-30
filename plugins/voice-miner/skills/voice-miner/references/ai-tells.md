# AI tells to keep out

Last researched: 2026-10-26. These tells change with every model generation, so refresh this file roughly every 6 months. Between consecutive model versions, 55% to 72% of tells change ([Graphite](https://graphite.io/five-percent/research/ai-tells)).

## How to use this file

1. **The person's own habits win.** If the profile lists a word or mark as theirs, keep it at their rate. That includes em dashes, "honestly", bullets and exclamation marks. This list is about what *they* never do, not about what's banned for everyone.
2. **Hard ban** (section A): fix on a single occurrence.
3. **Density cap** (section B): fine once. A cluster of them is what gives text away.
4. **Content beats cosmetics.** Removing tells doesn't save a message that says nothing specific. What readers and LinkedIn's filters react to most is genericness: no real event, number, name or opinion ([LinkedIn](https://news.linkedin.com/2026/keeping-conversations-real-on-linkedin), [ACL 2025](https://arxiv.org/html/2501.15654v2)).
5. **Don't overcorrect** (section D). Text with zero dashes, zero contractions, sprinkled fragments and forced typos is a new AI signature.

## A. Hard ban: one occurrence is enough

### Chatbot residue
- "Certainly!", "Of course!", "Great question!", "You're absolutely right"
- "I hope this helps", "Let me know if you'd like me to...", "Want me to...?", "If you want, I can also..."
- "Here's a shorter version...", or any assistant preamble left in the text
- Unfilled placeholders in a sent email: "[Company]", "{{firstName}}". In a draft they are fine on purpose: `check` lists them under "fill in before sending" and doesn't score them.
- `utm_source=chatgpt.com` or `oaicite` left in a link

### Email openers and closers
- Openers: "I hope this email finds you well", "I hope you're doing well. I wanted to...", "I wanted to reach out", "I'm reaching out because", "I am writing to..."
- Closers: "Please don't hesitate to...", "Feel free to reach out", "Please let me know if you have any questions", "Thank you for your time and consideration", "Happy to help!"
- A sign-off longer than the email's main sentence.
- These only count when the person doesn't use them. Some people really do write "Hope you're well". If the pre-AI baseline shows it, it stays.

### Fake personalization (cold outreach)
- A generic compliment followed by a pivot: "I came across your impressive work at...", "truly inspired by your commitment to..."
- A template with a scraped fact dropped in: "I noticed [company] is in the software industry", "I saw you raised a Series B", "Congrats on the new role" used as a hook with nothing after it.
- "Saw your recent post about X, great insights!" without saying what the post actually said.
- Several generic observations piled up instead of one sharp one.
- Tests ([Lavender data](https://somethinginc.com/blog/cold-email-sounds-like-ai-lavender-data/), [Modern Inbound](https://moderninbound.com/blog/how-to-write-a-cold-email-that-doesnt-sound-like-ai-2026)):
  - Delete the personal line. If the email still works, the line was decoration.
  - Could this exact sentence go to 1,000 people?
  - Would the detail fit a competitor just as well?

### Staged structures ([humanizer](https://github.com/blader/humanizer), [Pew 2026](https://www.pewresearch.org/data-labs/2026/08/20/how-much-of-the-internet-is-written-with-ai.md))
- **Contrast reframes:** "It's not X, it's Y", "not just X but Y", "This isn't about X. It's about Y", "No X. No Y. Just Z."
  - Newer variants: "not simply", "rather than merely", "rather than relying on", "less like a X and more like a Y", "less X, more Y".
  - The newer variants are the most common AI move of 2025-2026, up to 160x the human rate.
- **Staged run-ups:** "Here's the thing", "Here's the kicker", "Here's the part that...", "The trap is", "The catch is", "The honest answer is", "Let me be direct", "Honestly?" as its own sentence.
- **Salience flags:** "This matters.", "X matters because...", "The distinction matters", "worth stating plainly", "full stop."
- **Arguing with no one:** pre-empting an objection nobody raised.
- **Aphorism closers:** "Let that sink in.", "Read that again.", a one-line moral at the end.
- **Fragment stacks** for drama: "Not a detail. A design decision."
- **"Without X" dodges:** "without requiring", "without sacrificing", "without losing".

### Mannered metaphors (Claude's own tells)
"load-bearing", "earns its keep", "doing the heavy lifting", "doing a lot of work", "carries the argument", "the message lands", "let that sit", "a dial worth turning".
When a literal phrase exists, use it. That's Anthropic's own guidance ([docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1)).

### Formatting in plain-text email and DMs
- Visible markdown: `**bold**` or `## headers`. Bold appears about 43x more in AI text than in human text ([Pangram](https://www.pangram.com/signs-of-ai-writing)).
- Bold inline-header bullets like "**Speed:** faster results".
- Functional emoji as bullets or markers: ✅ ✔️ ❌ 🚀 🧠 🔹 💡 👉 1️⃣. Emotional emoji like 😊 or ❤️ lean human, so those are fine if the person uses them.
- Symbols: → ≈ ⚠ ─.
- Title Case Headings. Use sentence case.

### LinkedIn post templates ([Hiration](https://www.hiration.com/blog/ai-slop-linkedin/), [Switcher](https://www.switcherstudio.com/whats-new/linkedin-ai-slop-button-creators))
- Openers: "I'm thrilled to announce", "Humbled and honored", "In today's fast-paced...", "Let's unpack this", "Unpopular opinion:", "Here's what nobody tells you about".
- The forced parable: a trivial moment inflated into a business lesson.
- Evenly spaced one-sentence lines building to a moral ("broetry").
- A "Key takeaways" bullet list, emoji bullets, a hashtag stack.
- Closers: "Agree?", "Thoughts?", "Repost if...". A closing question tied to a real tension in the post is fine.
- LinkedIn's slop filter now stops generic posts from spreading beyond first-degree connections, and readers can report them.

## B. Density cap: fine once, a tell in clusters

### Vocabulary
These co-occur. One is noise. Three in one email is a tell.

- **Classic (2023-2025):** delve, underscore, highlight, showcase, foster, garner, bolster, enhance, align with, navigate, leverage, utilize, facilitate, streamline, elevate, unlock, empower, resonate, crucial, pivotal, vital, vibrant, robust, seamless, comprehensive, intricate, multifaceted, profound, nuanced, valuable, tapestry, testament, landscape, realm, interplay, ecosystem, framework, paradigm, synergy, journey, "valuable insights", "diverse array", "game-changing", "cutting-edge", "supercharge".
- **Newer (2026, GPT-6, Opus 5, Gemini 3):** dependable, practical, steady, deliberate, prioritize, clearer, echoed, core, quietly, "every single", "single most", "arguably the most", enormously, immense, profound, incredibly, remarkably, "absolutely essential".
- **Stance adverbs that fake candor:** honestly, genuinely, quietly, personally, simply, and "actually" with no contrast. Their AI use rose as em dashes declined. Keep them only where the person actually uses them, at their rate.
- **Transitions as paragraph openers:** Additionally, Moreover, Furthermore, Notably, Ultimately. "Additionally" alone is common in human writing, so it only counts in a cluster.
- **Copula dodges:** "serves as", "stands as", "boasts", "represents" where "is" or "has" would do.

### Structure
- Lists of three (adjectives, benefits, pain points). AI uses them about 4x more than humans. One per piece at most.
- Trailing "-ing" analysis clauses: ", highlighting...", ", ensuring...", ", reflecting...".
- Inflated significance: "marks a pivotal moment", "reflects a broader shift", "setting the stage for".
- Vague attribution: "experts say", "industry reports show". Name the source, or say "I've seen".
- Balanced hedging: "While X is true, Y is also important." Stacked qualifiers: "could potentially".
- Template email bodies: intro, value, CTA, each 3 or 4 sentences. Every paragraph the same length.
- Colon or semicolon reveals: "X exists in theory; in practice, Y."
- An upbeat summary at the end. Humans just stop.
- Rhetorical question, then its answer.

### Punctuation
- **Em dashes:** no longer a reliable tell on their own. Wikipedia moved them to "historical indicators (2022 to September 2026)". The human average is about 3 per 1,000 words, with a wide range. Match the person's rate. If they never use them, don't. Three or more in one email is a tell either way.
- **Curly vs straight quotes:** weak on their own. Curly and straight mixed in the same email suggests pasted text.

## C. What makes text read human

From [Graphite](https://graphite.io/five-percent/research/ai-tells) and [ACL 2025](https://arxiv.org/html/2501.15654v2): first person, direct address, a real anecdote, a specific number or name, a disputable opinion, a parenthetical aside, an exclamation mark when the person uses them, varied sentence length, plain repetition of the right word rather than synonym cycling, and an ending that just stops.

These have to come from the person's profile and the facts you have. Never invent them.

## D. Overcorrection: the new tells

- Stripping every dash, contraction and exclamation mark reads like Gemini. Use the person's own rates.
- Sprinkling fragments to fake rhythm is a known Claude tic.
- Forced typos, deliberately repeated words, and quirks the person doesn't have just swap one pattern for another.
- Anchor everything on the person's real samples in `examples.md`, not on avoiding this list.

## E. Why it matters commercially

- Managers seen using heavy AI in email were rated sincere by only 40% to 52% of readers, against 83% for low AI use ([Coman & Cardon 2025](https://www.psypost.org/managers-who-use-ai-to-write-emails-seen-as-less-sincere-caring-and-confident/)).
- 47% of buyers say they're less likely to reply to an email they think is AI-written ([Hunter](https://hunter.io/blog/the-cold-email-confidence-gap-why-senders-fear-ai-more-than-decision-makers)). Most can't actually spot AI, though. What they react to is genericness.
- Signal-based personalization gets about 18% replies, against about 9% for generic templates ([Explorium](https://www.explorium.ai/blog/data-for-gtm/why-ai-personalized-cold-emails-still-get-ignored-2026-checklist-for-outbound-teams.md)). These figures are vendor-reported.
- Cold email length guidance varies: 25 to 50 words (Lavender), under 80 (Josh Braun), under 90 (Vendisys). The person's own cold-email numbers come first.
