---
name: build-gtm-context
description: "Build your whole go-to-market context layer in Notion with you. First it finds where your GTM information already lives (Notion, CRM, course or payment platform, website, calls, email) and reads it, through a connector or by browsing. Then it drafts product and offer, customers, competitors, ICP, customer language, objections and shareable logos, and asks you only about real gaps. Everything lands in one GTM Hub page. Resumes where you left off. Use for \"build my GTM context\", \"set up my GTM Hub\", \"start the context layer\", \"help me define my ICP and messaging\", \"System 1\", or the first time you use this plugin. Not for refreshing one section only (use the matching gtm-* skill, for example gtm-objections)."
metadata:
  version: "0.2.0"
---

# Build your GTM context

This is the guide. It works in three moves: **find** what the user already has, **read** it all, then **draft** each section from it and ask only about gaps. The result is one GTM Hub page in Notion that every later agent (outbound, inbound, content) reads first.

## Reference files

- `references/source-map.md`: the buckets, where they usually live, how to ask, and how to get into each source (connector, browser, export, paste).
- `references/hub-structure.md`: the Hub, its pages and database schemas, reusing existing databases, the Notion tools, and the "For agents" section that makes the Hub its own map.
- `references/sections.md`: what each section captures and the quality bar.
- `references/context-home.md`: how every session finds the context (the Hub link in Claude's memory, never asked), and older setups.
- `scripts/gtm_home.py`: checks the pointer, writes it, and finds old links files. Call it by its full path in this skill's folder.

## Start

Explain in three lines:
- What they'll end up with: one GTM Hub in Notion with their product, ICP, competitors, customer language, objections and customers.
- How it works: "First tell me where this already lives. I'll read it and draft, and only ask you about what's missing." About 30 minutes of their time, less if a lot already exists. They can stop at any step.
- What you'll read only with their OK. Nothing is ever sent, and no personal names are saved.

## Step 0. Check what exists

Find the Hub link: the "GTM context" block in Claude's memory, or `gtm_home.py status` (it reads the pointer). Never ask the user where anything is saved.

- **A Hub link is known:** fetch the Hub page. Its links table and "For agents" section are the whole map. Show each section with its status. One AskUserQuestion: continue from the first unfinished section (recommended), update specific sections, or start over. The "Sources" in the "For agents" section are reused, so don't ask for sources again unless the user wants to add some.
- **An old `gtm-hub.md` turns up** (`status` lists it, in the project folder or `~/gtm-context/`): follow "Older setups" in `hub-structure.md`. Move its contents onto the Hub page, then continue as above.
- **Neither:** go to step 1.

## Step 1. Map the sources

1. Check that a Notion connector is available. If not, stop and explain: connect Notion in Claude's connector settings, then run this skill again.
2. See which other connectors exist from the tool names already listed in the session (for example `gmail`, `fathom`, `hubspot`, `google_drive`). Don't run one broad keyword search across all tools: it returns huge tool definitions and can miss the ones you need. Load a tool only when you use it, with a `select:` query.
3. Show the bucket table from `source-map.md` and ask the user to reply in one message: for each bucket, a link, a tool name, or "none". Add which offer this context is about, if they sell several.
4. For each pointer, settle access using the order in `source-map.md`: connector, browser, export, paste. When there's no connector for a tool, say so plainly and offer to browse there (Claude in Chrome for signed-in dashboards) or to read an export.
5. One AskUserQuestion to confirm: which conversation sources (email, call recorder, DMs) you may read, and whether to use Claude in Chrome or the built-in browser for the sources that need browsing.

## Step 2. Set up the Hub

1. Ask: "Do you already have a GTM Hub page in Notion?"
   - **Yes:** they paste the link. Fetch it. If it's blank, use it as the Hub itself. If it has content, match what exists to `hub-structure.md` and create only what's missing.
   - **No:** ask for the link of the page it should live under. If they don't know, run one workspace search for likely parents ("wiki", "company", "marketing") and let them pick.
2. Customers or objections databases found in step 1 are linked, not copied. Follow "Reuse before you create" in `hub-structure.md`.
3. Create the Hub page, the four pages and any missing databases.
4. Write the collapsed "For agents: links and settings" section at the bottom of the Hub (format in `hub-structure.md`): data source IDs and filters, plus the "Sources" list (link and how to get in). Show the Hub link.
5. **Pointer in Claude's memory** (see `context-home.md`): show the block from `gtm_home.py pointer --notion-hub <Hub link> --print` and explain it in one sentence: every Claude session will know where the GTM context is, without searching. Write it with `gtm_home.py pointer --notion-hub <Hub link>` after one OK. Nothing else is saved on their computer.

## Step 3. Read everything

Start all of these at once, so the user waits only once:
- One `source-reader` agent per document, database, export or public page from step 1, in parallel, in the background.
- One `language-miner` agent per approved conversation source (brief: see gtm-messaging step 2), in the background.
- Sources that need a signed-in browser: read them yourself in the main conversation, one page at a time, while the agents run.

If conversation sources were already mined recently for the same window (the "Sources" in the Hub's "For agents" section show the date), reuse those results and mine only the new sources.

When everything is back, show a "What I found" table: bucket, sources read, found / partly / nothing.

Sources often disagree (session counts, prices, customer numbers). Settle them with one rule, said once: the source closest to the buyer wins (a live sales page beats an internal note, a database count beats a number in prose). Ask only about contradictions that rule can't settle, together with the other open questions, in one batch.

## Steps 4 to 10. The sections

Run each section skill with the Skill tool, skipping its "Before starting" Hub check. Hand it the findings for its bucket. Each skill drafts from the findings first and asks only about what's missing or contradictory.

| Step | Skill | Pass forward |
|---|---|---|
| 4. Product & offer | `gtm-product` | the product summary (first lines of the page) |
| 5. Customers | `gtm-customers`, part A only | B2B or B2C, "no customers yet", the clients' customers answer, best-customer signals |
| 6. Competitors (optional) | `gtm-competitors`. If step 1 found none, ask once "Do buyers compare you with anyone?" and mark Skipped if not. With no customers either, recommend running it, because competitors' customers are then the only ICP evidence. | ICP evidence |
| 7. ICP | `gtm-icp` | ICP names, and the facts from steps 3, 5 and 6 |
| 8. Messaging | `gtm-messaging`, with the language-miner results from step 3 | the objections table |
| 9. Objections | `gtm-objections`, with the objections from steps 3 and 8 | |
| 10. Logo permission | `gtm-customers`, part B only. Skip if there are no customers. | |

Between steps, write one line: "Done: <section>. Next: <section>." Then continue. If the user says "skip", mark the section "Skipped" in the Hub links table and move on.

When the sources already answered most of product, ICP and messaging, draft those three together and show them in one review pass, with one approve-or-edit question per page. Going page by page is for when the user is answering from scratch.

## Step 11. Wrap up

1. Update the Hub summary callout: what they sell, the primary ICP and the "say this" line, each in one sentence.
2. Show the Hub link and a short status:
   - Sections done and skipped, and which sources each one came from.
   - How many items are still marked `(guess, confirm)` or `draft`, and where they are.
3. Tell them in one line that later course systems find the Hub through Claude's memory and fetch only the pages they need.

## Step 12. Keep it fresh

The context goes stale within weeks: prices change, new customers buy, new objections show up. Explain that in one sentence, then ask: "Set up a weekly automatic refresh now? It takes about 3 minutes." On yes, run the refresh-gtm-context skill in setup mode. It reuses the sources from this build and only asks the user to confirm them, pick when it runs, and choose email or Slack for alerts. On no, say they can start it later by saying "set up automatic updates".

## Rules

- Find and read before asking. A question the sources already answer is a wasted question.
- Use AskUserQuestion for choices (at most 4 options per question: list longer choices in the chat), and plain chat for links and free text.
- Every write is shown to the user first. Don't write on silence.
- Browsing is read-only. The user signs in themselves, and you never click anything that changes data or sends messages.
- Fetch pages by the links on the Hub (links table and "For agents" section). Never search for them. The only searches are the source search in step 1 (if the user asks) and the parent-page search in step 2.
- Query databases with filters, never read them whole.
- The Hub link is the only thing saved outside Notion (in Claude's memory). Never copy context or personal data onto the user's computer.
