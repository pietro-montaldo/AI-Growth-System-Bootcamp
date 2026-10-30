# ICP page template

One block per offer in scope, with up to 5 ICP cards each, strongest first. Each card follows "Structure of one ICP: a battlecard" in `icp-checks.md`: fixed labels, about 12 to 15 lines. Evidence goes once, at the bottom. The summary and score table at the top let an agent pick the right card fast.

```markdown
> **In short:** <offer 1> sells best to <ICP 1 in one sentence>. <offer 2> sells best to <...>. We don't sell to <anti-ICP in a few words>.
> **Built from:** <n best customers per offer / competitors' customers / no data yet>
> Last updated: <YYYY-MM-DD>

| Offer | ICP | Fit | Customers | Best | Why this score |
|---|---|---|---|---|---|
| <offer 1> | 1. <short name> | 5/5 | <n> | <n> | <best-customer rate, came back for more, reviews> |

## Offer: <offer 1>

### ICP 1: <short name> (fit <score>/5)
Who: <role + company type + situation, one sentence>
Find them: titles: <...> | seniority: <...> | headcount: <...> | industry: <...> | geo: <...> | tech: <... or leave out>
Score: +2 <signal> · +2 <signal> · +1 <signal> · -1 <signal> · -2 <signal>
Trigger: <moment that makes them look now>
Their words: "<verbatim pain quote>"
Lead with: <value prop> · proof: <one result, number or customer type>
Expect: <top objection> → <answer that works>
Not them: <who looks like a fit but isn't, and why>
Say this: "<one line in their words>"

### ICP 2 to 5: <short name> (fit <score>/5)
<same card, one per distinct group in this offer's data>

## Offer: <offer 2>
<same structure. If an ICP is the same as one above, write "Same as <offer 1>, ICP <n>: <name>" and only what differs (Lead with, Expect).>

---

## For agencies and B2B2C: your clients' customers
<who they are, and what your client needs you to reach them>

## Evidence
<per offer: the best customers or competitor customers each ICP is based on (company names only), and evidence tags: (customers), (from competitors, confirm), (guess, confirm)>
```
