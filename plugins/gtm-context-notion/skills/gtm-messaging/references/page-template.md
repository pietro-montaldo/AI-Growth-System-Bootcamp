# Messaging & customer language page template

Top part: what a writing agent needs on every run. Bottom part: the longer evidence, collapsed. Write it in Notion's format, following `page-style.md`. In the chat, show the same content as plain markdown.

```
<callout icon="💬" color="blue_bg">
<b>In short:</b> Buyers describe the problem as <i>"<top pain quote>"</i>. They want <i>"<top outcome quote>"</i>.<br /><b>Lead with:</b> <value prop 1> (<offer 1>) · <value prop> (<offer 2>)<br /><b>Built from:</b> <n> calls, <n> email threads, <n> DMs, <date range><br /><span color="gray">Last updated: <YYYY-MM-DD></span>
</callout>

## Value props by offer

### <offer 1>

<table header-row="true" fit-page-width="true">
<tr color="gray_bg">
<td>Value prop</td>
<td>Pain → what we do → proof</td>
<td>Their words</td>
</tr>
<tr>
<td><b><short name></b></td>
<td><pain> → <what we do> → <proof></td>
<td><i>"<quote>"</i></td>
</tr>
</table>

### <offer 2>

<same table>

(One offer: drop the offer headings.)

## What they say

<columns>
<column>
**The problem, in their words**

- <i>"<quote>"</i> <span color="gray">(Founder, 8-person agency · <offer> · seen 4x · call 2026-09-14)</span>
</column>
<column>
**What they want**

- <i>"<quote>"</i> <span color="gray">(... · seen 3x · email 2026-08-02)</span>
</column>
</columns>

## Words to use and avoid

<table header-row="true" fit-page-width="true">
<tr color="gray_bg">
<td>They say (use)</td>
<td>We avoid</td>
</tr>
<tr>
<td><span color="green">"my outbound"</span></td>
<td><span color="red">"pipeline generation engine"</span></td>
</tr>
</table>

## Our voice

<table header-row="true" fit-page-width="true">
<tr color="gray_bg">
<td>Attribute</td>
<td>Means</td>
<td>Doesn't mean</td>
</tr>
<tr>
<td><b>Direct</b></td>
<td>short sentences, one ask</td>
<td>blunt or cold</td>
</tr>
</table>

---

<toggle heading="h2">
All quotes

<the full merged table: type, quote, who, offer, times, source>
</toggle>
```

The scheduled update adds a "New quotes (unreviewed, <date>)" section at the very bottom with `insert_content`. The review moves the good ones up into "What they say" and the rest into "All quotes".
