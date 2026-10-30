# Product & offer page template

Fill this in Notion's format, following `page-style.md`. Keep it to one or two screens with the toggles closed. In the chat, show the same content as plain markdown. Delete any heading that doesn't apply.

```
<callout icon="📦" color="blue_bg">
<b>In short:</b> <what it is, for whom, and the result, in one sentence><br /><b>Offers in scope:</b> <name> `<price>` · <name> `<price>`<br /><b>Best proof:</b> <one result, client or number><br /><span color="gray">Last updated: <YYYY-MM-DD></span>
</callout>

## What it is

<2 to 4 sentences in plain buyer words. What they get, how it works, how long it takes.>

## The result for the buyer

<columns>
<column>
**Before**

- <their situation now, in their words if known>
</column>
<column>
**After**

- <what changes, as concretely as possible>
</column>
</columns>

## Offers and prices

<table header-row="true" fit-page-width="true">
<tr color="gray_bg">
<td>Offer</td>
<td>Price</td>
<td>Who it fits</td>
<td>What they get</td>
</tr>
<tr>
<td><name></td>
<td>`<price>`</td>
<td><who></td>
<td><what></td>
</tr>
</table>

<toggle heading="h3">
Offer: <name> · <price>

<table header-column="true" fit-page-width="true">
<colgroup>
<col width="140" color="gray_bg" />
<col />
</colgroup>
<tr>
<td>What it is</td>
<td><one or two sentences></td>
</tr>
<tr>
<td>Who it's for</td>
<td><buyer and situation></td>
</tr>
<tr>
<td>Result</td>
<td><the result they get></td>
</tr>
<tr>
<td>Price</td>
<td>`<price>` <terms, if any></td>
</tr>
<tr>
<td>Delivery</td>
<td>`<format>` `<length>` <who does the work, tools the buyer needs></td>
</tr>
</table>
</toggle>

<one toggle per offer in scope. Out-of-scope offers: one line each under the table, no toggle.>

## What it is not

- <span color="red"><what people confuse it with, or who should not buy it></span>

---

<toggle heading="h2">
Details and examples

<longer descriptions, extra offers, FAQs, links to decks or proposals>
</toggle>
```
