# ICP page template

One block per offer in scope, with up to 5 ICP cards each, strongest first. Each card follows "Structure of one ICP: a battlecard" in `icp-checks.md`: the fixed labels, in that order, one table row each. Evidence goes once, at the bottom. The summary and the scoreboard at the top let an agent, or a person, pick the right card fast.

Write it in Notion's format, following `page-style.md`: the summary callout, a coloured scoreboard, one closed toggle per ICP with its label table, and tokens for filters. In the chat, show the same content as plain markdown.

```
<callout icon="🎯" color="blue_bg">
<b>In short:</b> <offer 1> sells best to <ICP 1 in one sentence>. <offer 2> sells best to <...>.<br /><b>We don't sell to:</b> <anti-ICP in a few words><br /><b>Built from:</b> <n best customers per offer / competitors' customers / no data yet><br /><span color="gray">Last updated: <YYYY-MM-DD></span>
</callout>

## Scoreboard

<table header-row="true" fit-page-width="true">
<tr color="gray_bg">
<td>Offer</td>
<td>ICP</td>
<td>Fit</td>
<td>Customers</td>
<td>Best</td>
<td>Why this score</td>
</tr>
<tr>
<td><offer 1></td>
<td>1. <short name></td>
<td color="green_bg">`5/5`</td>
<td><n></td>
<td><n></td>
<td><best-customer rate, came back for more, reviews></td>
</tr>
</table>

## Offer: <offer 1>

<one line: what this offer is and its price, as tokens: `USD 699`>

<toggle heading="h3">
ICP 1: <short name> (fit <score>/5)

<table header-column="true" fit-page-width="true">
<colgroup>
<col width="140" color="gray_bg" />
<col />
</colgroup>
<tr>
<td>Who</td>
<td><role + company type + situation, one sentence></td>
</tr>
<tr>
<td>Find them</td>
<td>`titles: <...>` `seniority: <...>` `headcount: <...>` `industry: <...>` `geo: <...>` `tech: <... or leave out>`</td>
</tr>
<tr>
<td>Score</td>
<td><span color="green">+2</span> <signal (where to check)><br /><span color="green">+1</span> <signal><br /><span color="red">-1</span> <signal><br /><span color="red">-2</span> <signal></td>
</tr>
<tr>
<td>Trigger</td>
<td><moment that makes them look now></td>
</tr>
<tr>
<td>Their words</td>
<td><i>"<verbatim pain quote>"</i></td>
</tr>
<tr>
<td>Lead with</td>
<td><value prop><br /><b>Proof:</b> <one result, number or customer type></td>
</tr>
<tr>
<td>Expect</td>
<td><top objection> → <answer that works></td>
</tr>
<tr>
<td>Not them</td>
<td><span color="red"><who looks like a fit but isn't, and why></span></td>
</tr>
<tr>
<td>Say this</td>
<td><b>"<one line in their words>"</b></td>
</tr>
</table>
</toggle>

<toggle heading="h3">
ICP 2: <short name> (fit <score>/5)

<same table, one card per distinct group in this offer's data, up to 5>
</toggle>

## Offer: <offer 2>

<same structure. If an ICP is the same as one above, its toggle holds one line, "Same as <offer 1>, ICP <n>: <name>", and a table with only the rows that differ (Lead with, Expect).>

---

## For agencies and B2B2C: your clients' customers

<who they are, and what your client needs you to reach them>

<toggle heading="h2">
Evidence

- <per offer and ICP: the best customers or competitor customers it's based on (company names only), with evidence tags: (customers), (from competitors, confirm), (guess, confirm)>
- <how the ICP names map to the Customers database's ICP segment values>
</toggle>
```

Fit colours on the scoreboard: `green_bg` for 5, `yellow_bg` for 3 and 4, `gray_bg` for 1 and 2. One offer only: drop the "Offer" headings and the Offer column.
