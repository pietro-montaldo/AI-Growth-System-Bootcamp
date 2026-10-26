---
name: build-gtm-context
description: "Build your whole go-to-market context layer in your own GitHub repo with you, no Notion needed. First it finds where your GTM information already lives (website, CRM, course or payment platform, docs, calls, email) and reads it, through a connector or by browsing. Then it drafts product and offer, customers, competitors, ICP, customer language, objections and shareable logos, and asks you only about real gaps. Everything lands in a gtm/ folder: short markdown pages plus CSV banks that agents query instead of reading whole. Resumes where you left off. Use for \"build my GTM context\", \"set up my GTM context in GitHub\", \"start the context layer\", \"help me define my ICP and messaging\", \"System 1\", or the first time you use this plugin. Not for refreshing one section only (use the matching gtm-* skill, for example gtm-objections)."
metadata:
  version: "0.2.0"
---

# Build your GTM context (GitHub)

This is the guide. It works in three moves: **find** what the user already has, **read** it all, then **draft** each section from it and ask only about gaps. The result is a `gtm/` folder in the user's repository that every later agent (outbound, inbound, content) reads first.

## Reference files

- `references/source-map.md`: the buckets, where they usually live, how to ask, and how to get into each source (connector, browser, export, paste).
- `references/repo-structure.md`: the `gtm/` folder, the hub file, page rules, CSV columns, the helper script, privacy and git rules.
- `references/sections.md`: what each section captures and the quality bar.
- `scripts/gtm_csv.py`: reads and updates the CSV banks without reading them whole. Call it by its full path in this skill's folder.

## Start

Explain in three lines:
- What they'll end up with: a `gtm/` folder in their repo with their product, ICP, competitors, customer language, objections and customers.
- How it works: "First tell me where this already lives. I'll read it and draft, and only ask you about what's missing." About 30 minutes of their time, less if a lot already exists. They can stop at any step.
- What you'll read only with their OK. Nothing is ever sent, nothing is pushed without asking, and no personal names are saved.

## Step 0. Check what exists

- **`gtm/README.md` exists:** read it. Show each section with its status. One AskUserQuestion: continue from the first unfinished section (recommended), update specific sections, or start over. The "Sources" list is reused, so don't ask for sources again unless the user wants to add some.
- **No `gtm/` folder:** go to step 1.

## Step 1. Map the sources

1. See which connectors exist from the tool names already listed in the session (for example `gmail`, `fathom`, `hubspot`, `notion`, `google_drive`). Don't run one broad keyword search across all tools: it returns huge tool definitions and can miss the ones you need. Load a tool only when you use it, with a `select:` query.
2. Show the bucket table from `source-map.md` and ask the user to reply in one message: for each bucket, a link, a tool name or "none". Add which offer this context is about, if they sell several.
3. For each pointer, settle access using the order in `source-map.md`: connector, browser, export, paste. When there's no connector for a tool, say so plainly and offer to browse there (Claude in Chrome for signed-in dashboards) or to read an export placed in `gtm/.private/`.
4. One AskUserQuestion to confirm: which conversation sources (email, call recorder, DMs, webinar recordings) you may read, and whether to use Claude in Chrome or the built-in browser for the sources that need browsing.

## Step 2. Set up the folder

Follow "Setting up the folder" in `repo-structure.md`:
1. Check it's a git repository, and that the remote isn't public. If it is public, stop and resolve that with the user first.
2. Customers or objections that already live in a connected system are linked under "Sources", not copied (see "Reuse before you create").
3. Create `gtm/README.md`, the three pages, and only the CSV banks that are needed, using the script's `init` with the exact columns from `repo-structure.md`. Add `gtm/.private/` to `.gitignore`.
4. Fill the "Sources" list: link and how to get in for each bucket.

## Step 3. Read everything

Start all of these at once, so the user waits only once:
- One `source-reader` agent per document, database, export or public page from step 1, in parallel, in the background.
- One `language-miner` agent per approved conversation source (brief: see gtm-messaging step 2), in the background.
- Sources that need a signed-in browser: read them yourself in the main conversation, one page at a time, while the agents run.

If conversation sources were already mined recently for the same window (the "Sources" list shows the date), reuse those results and mine only the new sources.

When everything is back, show a "What I found" table: bucket, sources read, found / partly / nothing.

Sources often disagree (session counts, prices, customer numbers). Settle them with one rule, said once: the source closest to the buyer wins (a live sales page beats an internal note, a database count beats a number in prose). Ask only about contradictions that rule can't settle, together with the other open questions, in one batch.

## Steps 4 to 10. The sections

Run each section skill with the Skill tool, skipping its "Before starting" setup check. Hand it the findings for its bucket. Each skill drafts from the findings first and asks only about what's missing or contradictory.

| Step | Skill | Pass forward |
|---|---|---|
| 4. Product & offer | `gtm-product` | the product summary (first lines of the page) |
| 5. Customers | `gtm-customers`, part A only | B2B or B2C, "no customers yet", the clients' customers answer, best-customer rule |
| 6. Competitors (optional) | `gtm-competitors`. If step 1 found none, ask once "Do buyers compare you with anyone?" and mark Skipped if not. With no customers either, recommend running it, because competitors' customers are then the only ICP evidence. | ICP evidence |
| 7. ICP | `gtm-icp` | ICP names, and the facts from steps 3, 5 and 6 |
| 8. Messaging | `gtm-messaging`, with the language-miner results from step 3 | the objections table |
| 9. Objections | `gtm-objections`, with the objections from steps 3 and 8 | |
| 10. Logo permission | `gtm-customers`, part B only. Skip if there are no customers. | |

Between steps, write one line: "Done: <section>. Next: <section>." Then continue. If the user says "skip", mark the section "Skipped" in the hub table and move on.

When the sources already answered most of product, ICP and messaging, draft those three together and show them in one review pass, with one approve-or-edit question per page. Going page by page is for when the user is answering from scratch.

## Step 11. Wrap up

1. Update the hub summary in `gtm/README.md`: what they sell, the primary ICP and the "say this" line, each in one sentence.
2. Show a short status:
   - Sections done and skipped, and which sources each came from.
   - How many items are still marked `(guess, confirm)` or `draft`, and where they are.
3. Run `git status` and show what changed. Ask once: "Commit this to your repo?" On yes, commit with `gtm: build context layer`. Then ask separately before pushing.
4. Tell them what comes next, in two lines: later course systems read `gtm/README.md` first and open only the files they need. Refresh objections every few weeks with gtm-objections, and the rest monthly. Refreshes reuse the saved sources.

## Rules

- Find and read before asking. A question the sources already answer is a wasted question.
- Use AskUserQuestion for choices (at most 4 options per question: list longer choices in the chat), and plain chat for links and free text.
- Every write is shown to the user first. Don't write on silence. Never commit or push without asking.
- Browsing is read-only. The user signs in themselves, and you never click anything that changes data or sends messages.
- Open files by the links in `gtm/README.md`. Query banks with the helper script, never read them whole.
- No personal names, emails or profile URLs in any file. Raw exports stay in `gtm/.private/` and get deleted when you're done.
- Don't name the enrichment tool to the user or in the files: say "public company data".
