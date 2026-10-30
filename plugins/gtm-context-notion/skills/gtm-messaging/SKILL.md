---
name: gtm-messaging
description: "Mine how your buyers really talk from your call recordings, emails and DMs, then write the Messaging & customer language page of your Notion GTM Hub: their pains and desired outcomes in their own words, value props, words to use and avoid, and your voice. Runs one mining agent per connected source in parallel, and works from pasted text when nothing is connected. Use for \"find my customer language\", \"how do my buyers describe the problem\", \"update my messaging\", \"mine my calls\", \"voice of customer\", or as part of build-gtm-context. Not for writing a specific email or post."
metadata:
  version: "0.1.0"
---

# Messaging & customer language

The best copy uses the buyer's own words. This skill finds those words in real conversations and turns them into a short page every writing agent reads first. The objections found along the way go to the Objections bank.

## Reference files

- `references/mining-playbook.md`: what to read, what to extract, privacy rules and objection themes.
- `references/page-template.md`: the page layout.
- `references/source-map.md`: where buyer language usually lives and how to get in.

## Before starting

1. Fetch the GTM Hub page: its link is in the "GTM context" block of Claude's memory. Its links table and "For agents" section hold every link you need. If no Hub link is known, run the build-gtm-context skill first, which sets up the Hub.
2. Fetch the Product & offer and ICP pages by their links. You need the product summary and the ICP names.
3. Fetch the Messaging page by its link. If it has content, summarise it and ask what to refresh.
4. **On its own** (not inside build-gtm-context): when you find this section's sources, also settle where new customer language will come from and who brings it in (`auto`, `auto, app only`, `you`, `none`), as in "Where each item comes from, now and later" in `references/source-map.md`. Prefer an automatic route. Update its line in the hub's Sources list (the Hub's "For agents" section) after the user's OK.

## Steps

### 1. Pick the sources

Inside build-gtm-context, the sources were approved in its step 1 and the miners started in its step 3: skip to step 3 here and collect their results, together with any quotes the source-reader agents found (reviews, testimonials, surveys).

On its own: see which connectors exist from the tool names already listed in the session (email, call recorder, DMs). Don't run one broad keyword search across all tools. Then one AskUserQuestion, multiSelect: "Which of these can I read for buyer conversations?" List the connected ones, plus:
- **Paste transcripts or emails**: always offered. Good for anyone whose company blocks connectors.
- **Customer reviews**: a link to G2, Trustpilot, Google reviews or testimonials on their site.

Say clearly what will be read: "external conversations from the last 90 days, nothing is sent, and no names end up in Notion."

### 2. Mine in parallel

Start one `language-miner` agent per source, all in one message so they run in parallel. Give each a complete brief, since it starts with no context:
- The source and how to reach it (connector name, or the pasted text, or the review URL).
- The window: last 90 days.
- The product summary, the offers in scope (one line each), and ICP names if known. Ask the agent to tag each row with the offer it's about.
- What to extract: `both` (language and objections).
- Search hints for that source (keywords for each offer, typical buyer questions), so the agent finds buyer threads among newsletters and notifications.

Run them in the background so the conversation can continue.

For pasted text over about 3,000 words, also use an agent, so the main conversation stays light.

### 3. Merge

Combine the agents' tables. Merge repeats across sources and add up the counts. Keep rows about the offers in scope; rows about other offers stay only if the speaker matches an ICP, and the page summary says so. Group pains, outcomes and value props by offer; voice and words are shared. Then draft the page:
- **Pains** and **outcomes**: the 5 to 8 strongest quotes, most repeated first.
- **Value props**: per offer in scope, up to 3, each built from a pain, the offer's answer and a proof point. Each one must trace to quotes.
- **Words they use / words to avoid**: from the `words` rows, plus any jargon in the product page that buyers never say.
- **Voice**: 3 attributes with "means / doesn't mean", taken from how the user writes in the threads that worked. Mark it `(draft, confirm)`.

Keep the objections table aside. Inside build-gtm-context, hand it to the objections step. When this skill runs on its own, offer to run gtm-objections with it next.

### 4. Pause: show the draft

Show the page and a coverage line ("Read 34 email threads and 9 calls from Jul 28 to Oct 26"). Ask: "Which quotes sound most like your best customers? Anything here you'd never say?" Apply edits.

### 5. Write

- Replace the Messaging page content with the approved draft (`notion-update-page`).
- Update the Messaging row in the Hub links table.

## Rules

- Quotes stay verbatim with a source tag. No names, emails or profile URLs, only role and company type.
- If a source can't be read, say so and continue with the others. If none can, use pasted text. Never invent quotes.
- Fetch by link, never search Notion. Never copy this content into a project.
