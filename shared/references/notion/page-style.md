# How GTM pages look in Notion

Agents read these pages first and people read them second. Both work when the structure is fixed and the formatting means something. Agents find facts by their labels (Who, Find them, Lead with...), so labels and their order never change. Formatting changes only how the page looks.

Read `notion://docs/notion-flavored-markdown-spec` once (with `notion-fetch`) before the first write. In the chat, show drafts as plain markdown, because Notion tags don't display there. Use the Notion format below only when writing.

## Rules

1. **A summary callout at the top of every page.** Use `blue_bg` with the page's icon. Each item is one line with a bold label (`<b>In short:</b>`), with `<br />` between lines. The last line is `Last updated: <YYYY-MM-DD>`.
2. **Repeating cards are toggles.** One ICP or one offer is a `<toggle heading="h3">` whose title holds the key fact, for example `ICP 1: Solo experts (fit 5/5)` or `Offer: Bootcamp · USD 999`. The page then reads like a list a person can open, and `notion-fetch` still returns everything inside, so agents lose nothing.
3. **Long parts are collapsed.** Use a `<toggle heading="h2">` for each of these: Evidence, All quotes, Details and examples, and Changelog. With every toggle closed, a page fits on one or two screens.
4. **Cards are two-column tables.** Put the label in the first column and the value in the second, one row per label, using `header-column="true"`. Table cells are inline only: use `<br />` for a new line, never a list.
5. **Tokens for values a tool will reuse.** Wrap filter values, prices, scores and select values in inline code, one token per value: `headcount: 20-250` `industry: agencies` `USD 699` `5/5`. Prospecting filters can then be copied straight into Clay or Apollo. Never put a sentence in a token.
6. **Colour has one meaning each.** Green means fit 5 or a positive signal. Yellow means fit 3 to 4, or "check this". Red means a negative signal or "Not them". Gray means labels, sources and dates. Colour a cell with `<td color="green_bg">` and words with `<span color="green">`. Leave everything else uncoloured.
7. **Columns only for pairs.** Use them for things a reader compares side by side, such as before and after, words they use and words to avoid, or why buyers choose us and why they choose others. Two columns at most, and only for short content. Use a table for anything an agent filters or counts.
8. **Quotes stay verbatim.** In tables, write them in italics inside quotation marks. Put the source tag in gray after the quote: `<span color="gray">(Founder, 8-person agency · call 2026-09-14)</span>`.
9. **Link with mentions.** Refer to Hub pages and databases with `<mention url="...">`, not raw URLs.
10. **Header rows** of styled tables are `<tr color="gray_bg">`.

## Editing a page safely

- Fetch the page first. Anchor `update_content` on plain text, such as a label cell (`Find them`) or a heading title. Don't anchor on tokens, coloured spans or mentions, because Notion rewrites them on readback.
- To change one card, replace its whole toggle, from `<toggle` to `</toggle>`, copied exactly from the fetch.
- Add new material at the bottom with `insert_content` (for example "New quotes"). Never rebuild a page to add one item.

## Building blocks

Summary callout:

```
<callout icon="🎯" color="blue_bg">
<b>In short:</b> <one sentence><br /><b>Built from:</b> <sources><br /><span color="gray">Last updated: <YYYY-MM-DD></span>
</callout>
```

A card (toggle with a label table):

```
<toggle heading="h3">
ICP 1: <short name> (fit 5/5)

<table header-column="true" fit-page-width="true">
<colgroup>
<col width="140" color="gray_bg" />
<col />
</colgroup>
<tr>
<td>Who</td>
<td><one sentence></td>
</tr>
<tr>
<td>Find them</td>
<td>`titles: Founder, CEO` `headcount: 20-250` `industry: agencies`</td>
</tr>
</table>
</toggle>
```

Score table cell colours: `<td color="green_bg">` for `5/5`, `<td color="yellow_bg">` for `3/5` and `4/5`, `<td color="gray_bg">` for `1/5` and `2/5`.

Signals, one per line: `<span color="green">+2</span> posts about AI (LinkedIn)<br /><span color="red">-2</span> Copilot mandate (job posts)`.

Two columns:

```
<columns>
<column>
**Before**

- <their situation now>
</column>
<column>
**After**

- <what changes>
</column>
</columns>
```

Collapsed section:

```
<toggle heading="h2">
Evidence

- <one line per source>
</toggle>
```

## Page icons

GTM Hub 🧭 · Product & offer 📦 · ICP 🎯 · Messaging & customer language 💬 · Competitors ⚔️ · Updates to review 🔄. Set the icon when creating the page.
