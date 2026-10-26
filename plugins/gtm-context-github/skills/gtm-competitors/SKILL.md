---
name: gtm-competitors
description: "Research your core competitors and save them to gtm/competitors.md and gtm/competitors.csv in your repo: what each sells, to whom, at what price, which customers they show publicly, and how you differ. Runs one research agent per competitor in parallel. When you have no customers yet, their public customers become the evidence for your ICP. Optional: skip it if you have no notable competitors. Use for \"research my competitors\", \"who else sells this\", \"update my competitor list\", \"how are we different from X\", or as part of build-gtm-context. Not for ongoing monitoring or battle cards for sales calls."
metadata:
  version: "0.2.0"
---

# Competitors

A competitor here is someone who sells the same result to the same or similar buyers, not every company in the space. Two to five is enough. The output serves two jobs: a clear "how we differ" for messaging, and evidence of who buys this kind of thing, which feeds the ICP.

## Reference files

- `references/source-map.md`: where competitor notes usually live and how to get in.
- `scripts/gtm_csv.py`: query and update `gtm/competitors.csv`. Call it by its full path in this skill's folder.

## Before starting

1. Read `gtm/README.md`. If it's missing, run the build-gtm-context skill first, which sets up the folder.
2. You need the product summary (the first lines of `gtm/product.md`).

## Steps

### 1. Get the names

Inside build-gtm-context, start from any competitor names or battle cards it found. On its own, first ask whether a comparison doc or battle card already exists, and read it (see `references/source-map.md`).

Then ask only for what's missing: "Who are the 2 to 5 competitors your buyers compare you with? Names or websites." Remind them: the ones a buyer actually mentions, including the "do it ourselves" option or a freelancer if that's what they lose to.

If they don't know, offer to suggest some: run 2 or 3 web searches using the product summary ("<category> for <buyer>", "<problem> service", "alternatives to <known player>"). List up to 8 candidates in the chat, numbered, with one line and a link each. Then ask with a multiSelect AskUserQuestion offering the 4 strongest (the tool allows 4 options), and tell the user to type other numbers in "Other".

If the user says no one is notable, stop: mark the section Skipped in the `gtm/README.md` table, don't create the files, and move on. Don't push.

If a researcher reports that a competitor's page is gone (404, retired offer), tell the user in one line and ask whether to replace it or drop it.

### 2. Research in parallel

Start one `competitor-researcher` agent per competitor, all in one message so they run in parallel. Give each a complete brief, since it starts with no context:
- The competitor's name and website.
- The product summary.
- If the user has no customers yet: "Focus on public customers, case studies and who-it's-for pages. This is the main evidence for the ICP."

### 3. Merge

From the agents' results, build:
- One CSV row per competitor.
- **ICP evidence:** the segments and company types that show up across 2 or more competitors. Keep it as a short list with sources. Inside build-gtm-context, hand it to the ICP step.
- **How we differ:** one line per competitor, drafted from their positioning versus the product summary, marked `(draft, confirm)`.

### 4. Pause: show the result

Show the table and the differences in the chat. Ask the user to correct "How we differ" and to set the Threat level (high, medium, low). Their knowledge beats the web here: ask "Is there anything buyers say about them that the web doesn't show?"

### 5. Write

- If `gtm/competitors.csv` doesn't exist, create it with `init` and the columns from the guide's `repo-structure.md`.
- Write all rows with one `upsert` keyed on Name. Set Last checked to today.
- Write `gtm/competitors.md`:

```markdown
> **In short:** We mostly compete with <names>. Buyers choose us when <reason>. They choose others when <reason>.
> **Who they sell to:** <the segment that shows up most across competitors>
> Last updated: <YYYY-MM-DD>

Details per competitor: competitors.csv (query by Name or Threat).

## Changelog
- <YYYY-MM-DD>: <what changed>
```

- Update the Competitors row in the `gtm/README.md` table.

## Rules

- Public information only. Every customer listed needs a source URL.
- "How we differ" stays marked as a draft until the user confirms it.
- Query with filters, never read the whole bank. Write only with `upsert`.
