# ICP checks

Run these checks on every ICP draft before showing it to the user. Fix what fails, then show the draft with a one-line note per check that changed something.

## How to build the ICP

**From customers (preferred).** Start from the best group: 3 named customers for a small B2B list, or a behaviour rule for B2C and long lists ("bought twice or more, or came back for more"). Look at what the best group shares that the rest doesn't, then check the rest of the customer list against it. The ICP is the pattern in the best customers, not the average of all customers.

Look for that pattern in **public attributes**, not only in what customers said. Enrich the best group, and a sample of the rest, with the attributes in "Public signals" below. Use an enrichment connector if one is connected, otherwise their website and LinkedIn. Enrichment can cost credits, so say how many lookups you plan and get the user's OK first. Don't name the enrichment tool to the user or on the pages: call it "public company data".

**From competitors (when there are no customers yet).** Use competitors' public case studies, logos, testimonials and "who it's for" copy. Look for the segment that shows up across 2 or more competitors. Mark every attribute that came from competitors as `(from competitors, confirm)`, because the user's own buyers may differ.

**From the user's head (last resort).** Ask "describe the last 3 people who asked you about this, even if they didn't buy". Mark the result `(no data yet)`.

## Structure of one ICP

- **Who, in one sentence.** Role + company type + situation. Example: "Founder-CEO of a 5 to 30 person B2B services firm who still runs sales personally."
- **Hard filters.** Must all be true, and must be checkable from a LinkedIn profile, a website or an enrichment tool: geography, company size band, industry, role. 3 to 5 lines.
- **Public scoring signals.** Make a lead better or worse before anyone has talked to them. Use +2 / +1 / -1 / -2, and for each one say where to check it (LinkedIn profile, company site, job board, or company data). Examples: "+2 company has an open SDR or marketing role (job postings)", "+1 headcount grew in the last 12 months", "-2 already uses a direct competitor (tech stack)". Aim for 4 to 8, mostly public.
- **Conversation signals.** What they say once they reply ("I'm the only one doing sales"). Useful for inbound and follow-ups, but an outbound agent can't see them in advance, so keep them separate and short.
- **Buying triggers.** The moments that make them look for a solution now: a new funding round, a new role, a lost key client, a failed hire.
- **Anti-ICP.** Who looks like a fit but isn't, and why. This saves more time than the ICP itself.
- **Say this.** One line that would make this person stop scrolling, written in their words.

## Public signals

Attributes that company data usually includes, or that can be read from a public profile or website. Build hard filters and scoring signals from these first, because the outbound agent can check them automatically.

| About the person | About the company |
|---|---|
| Job title, seniority, function | Industry, B2B or B2C |
| Time in current role, recent job change | Headcount and headcount growth (6 or 12 months) |
| Past companies and roles | Headquarters location, countries served |
| Location | Founded year, funding stage, last round and date |
| Posts on LinkedIn in the last 90 days, and their topics | Estimated revenue |
| Followers, headline keywords | Tech stack (CRM, email tool, website tools) |
| Groups, communities, events they attend | Open job postings (for example SDR, marketing, RevOps) |
| | Recent news: launch, funding, new office, leadership change |

A signal that can't be found anywhere public ("ambitious", "data-driven", "frustrated with their CRM") is not a scoring signal. Turn it into something visible, for example "posted about CRM problems in the last 90 days", or move it to conversation signals.

## The checks

1. **Three defining attributes.** Can you name the 3 attributes that separate this ICP from everyone else? If you need more than 5, it is two ICPs. If you can name only 1, it is too broad.
2. **Specificity test.** Could you build a list of 50 real people from the hard filters alone, using LinkedIn or a database? If not, the filters are too vague.
3. **Reachability.** Is there one uniform way to reach them (a community, a job title search, an event, a newsletter)? If every lead needs a different channel, narrow it.
4. **Value test.** Does this ICP get a clearly better result from the product than the next-best option? If the honest answer is "about the same", it is not the primary ICP.
5. **Findability.** Can every hard filter, and most scoring signals, be checked in public data or an enrichment tool, without talking to the person? Count them, and rewrite the ones that can't.
6. **Evidence.** Is each attribute backed by customers, competitors or calls? Mark anything else `(guess, confirm)`.
7. **Count.** At most 3 ICPs. Put the primary one first. A solo business usually needs 1.

## Common mistakes to flag

- Describing demographics instead of a situation ("marketers aged 30 to 45" instead of "marketing lead who just lost their only SDR").
- Picking the biggest market instead of the most winnable one.
- Mixing the buyer and the user when they are different people.
- Hard filters or scoring signals that can't be checked from public data ("ambitious", "data-driven").
- Scoring that relies only on what people say on calls, so an outbound agent has nothing to score with before first contact.
- No anti-ICP.
