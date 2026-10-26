# Flex Credits and consumption economics

Researched 2026-10-26. **Read the provenance key before quoting any figure externally.**

## Provenance key

Not all figures here are equally solid. This matters if any of it is going in front of a vendor or client.

| Tier | Meaning | Safe to assert? |
|---|---|---|
| **W** | Stated in Workday's own published material | Yes, with the source |
| **R-A** | Reported by reputable press as Workday's own figures (e.g. CIO quoting Workday's rate card) | Yes, attributed as reported |
| **R-B** | Reported by a **single partner/consultancy blog**, not confirmed against Workday material | **Attribute explicitly, never as fact** |
| **CALC** | Our arithmetic from tier W/R figures | Yes, if the inputs are stated |
| **ASSUM** | Our assumption or placeholder | **Never assert — label as an assumption** |

What this means in practice: the **mechanics** (tier W) are solid; the **specific entitlement numbers,
overage rates, SKU boosts and allotment tables are tier R-B** — a single partner source that we have not
been able to confirm against Workday's own published material. Treat them as a modelling starting point to
be replaced by the client's actual contract and entitlement record, not as published pricing.

**Workday publishes no dollar-per-credit rate at all.** Every dollar figure anywhere in this repo is tier
ASSUM.

**Why this file matters more than it looks.** Custom Extend apps and Orchestrations now draw metered
platform consumption. That turns run-cost from an invisible subscription detail into a recurring,
attributable bill — which changes how solutions should be designed, how builds should be proposed, and what
advisory work is worth selling.

> **Name collision warning.** Salesforce Agentforce also has a product called "Flex Credits." Figures like
> "$0.10 per action" and "1 million Flex Credits per org" circulating online are **Salesforce's**, not
> Workday's. Do not mix them. Workday has published **no dollar-per-credit rate** at all.

## Mechanics

- A **fungible credit currency** applied against metered capabilities; different capabilities cost different
  amounts.
- Included in the base subscription as an **annual allotment**, reset annually, expandable by purchase.
- **Metered on completed action** — not per query, not per token.
- **Credits expire after one year and do not roll over.** Use-it-or-lose-it.
- **No hard stop at zero.** Overages are permitted and reconciled at year-end — so budget overruns happen
  silently. Extra credits can be bought mid-year, prorated.
- **Non-production is free.** Sandbox activity is visible in the Platform Consumption Console for
  information only. Caveat: pre-production counts are reportedly **aggregate only**, which limits how
  precisely you can forecast before go-live.
- **Platform Consumption Console (PCC)** shows balance, burn rate, usage by agent and component, and rate
  card history, with threshold alerts at **80% / 90% / 100%**.

## Platform Entitlements vs Flex Credits

**Everything in this section is tier R-B** — one partner source, unconfirmed against Workday material.
Attribute it as such, and replace it with the client's own entitlement record before modelling anything
that matters.

Two distinct layers, easy to confuse:

**Platform Entitlements** — baseline, non-expiring allowances for **API calls**, **Integration Events** and
**Document Storage**. Exceeding them **draws down Flex Credits**.

Overage rates: **API 60 credits per 10,000 calls** · **Integration Events 25 credits per 100 events** ·
**Document Storage 120 credits per GB per year**.

**SKU boosts apply to API calls only**, calculated against the baseline and **additive, not stacked**:

| SKU | API-call boost |
|---|---|
| Workday Extend | **+50%** |
| Prism Analytics | **+15%** |
| Workday Financials | **+15%** |

Worked example: a 10,000–29,999-employee org with a 4.5M API-call baseline plus Extend reaches **6.75M calls
annually**. Integration Events and Document Storage are unaffected by these boosts.

## Complimentary agent credits by org size

| Employees | Annual credits |
|---|---|
| ≥ 100,000 | 200,000 |
| 30,000 – 99,999 | 120,000 |
| 10,000 – 29,999 | 60,000 |
| 3,500 – 9,999 | 30,000 |
| < 3,500 | 15,000 |

Planning / Sana Enterprise without HCM or Financials: 5,000 across all sizes.

## What consumes, and what doesn't

**Draws down credits / entitlements:**
- **Custom Studio integrations and Orchestrations**
- **Workday Extend (custom) applications**
- Modified Workday-built integrations
- External AI agents calling the tenant
- Certified Partner integrations (API requests)
- Agent use above the complimentary allotment

**Does not consume entitlements:**
- Workday Core Connectors
- EIB (Integration Events only)
- **Built-on-Workday (partner) applications**
- Sandbox / non-production activity

That asymmetry is the single most consequential fact here: **bespoke Extend and Orchestration cost to run;
Workday's own connectors and certified Built-on-Workday apps do not.**

## Published agent rates (Workday's own rate card)

**Tier R-A** — CIO reporting these as figures from Workday's own rate card. The strongest numbers in this
file, and safe to quote with that attribution:

- **Recruiting Agent — 6 credits** to screen and grade each résumé against a job opening
- **Recruiting Agent — 750 credits per requisition** to identify leads in existing talent pools
- **Contract Negotiation Agent — 500 credits** to review and redline a contract against a playbook

Partner-reported ranges (consistent with the above): Self-Service Agent 1–5 credits per action; Business
Process Optimize 1 credit; Payroll/Time 10–60 credits; Internal Talent Matching 750 credits per requisition.

**Critical:** *"The same agent may contain multiple skills with very different credit costs."* Candidate
grading at ~6 credits sits in the same agent as talent rediscovery at 750 — a **125× spread inside one
agent**. Cost control therefore has to operate at **skill level, not agent level**.

## Illustrative cost scenarios

`ILLUSTRATIVE` — these assume ~$0.10 per credit, which is a **partner's stated assumption, not a
Workday-published rate**. Treat the credit counts as sound and the dollar figures as directional only.

| Scenario | Credits/year | Illustrative $ |
|---|---|---|
| Talent rediscovery, 50 requisitions/month | 450,000 | ~$45,000 |
| Contract review, 100 documents/month | 600,000 | ~$60,000 |
| Self-Service Agent, 5,000 interactions/month | 150,000 | ~$15,000 |

For scale: 450,000 credits/year is **more than double** the top-tier 200,000 complimentary allotment.

## Risks worth repeating to a client

- Only **35% of CIOs** report full visibility into AI operating costs.
- *"A pilot can quietly consume a year's worth of Flex Credits within weeks without strong telemetry."*
- No cross-vendor standard unit — every vendor defines its own, so comparisons are meaningless.
- Burn rates vary enormously by task, and **no dollar pricing is published** — Workday Rising 2026 was
  characterised as selling agents on credits with no published price.

## What this changes for implementers `INFERENCE`

1. **Run-cost becomes a design constraint and a deliverable.** A per-row REST loop inside an Orchestration
   now has a recurring bill attached. Call efficiency is priced, not merely tidy.
2. **Good architecture becomes quantifiable.** "This refactor removes 2.4M API calls per year" converts to
   credits and then to money. Optimisation becomes a sellable engagement with measurable ROI — something
   that was previously an abstract quality argument.
3. **New advisory lines:** consumption baselining and TCO modelling before rollout; integration-footprint
   audit with consumption attribution; PCC governance setup (owner, thresholds, monthly cadence,
   business-unit chargeback); credit-efficient design standards; skill-level enablement policy.
4. **Prism and Data Cloud may become cost arbitrage, not just analytics choices.** Moving a read path off
   per-row REST and onto Prism tables or zero-copy Iceberg could cut metered API consumption with no
   functional change. **Unverified — how Prism and Data Cloud query volume is metered is not documented.**
   See open question.
5. **Build-vs-buy tilts toward productisation.** Built-on-Workday apps don't consume client entitlements but
   bespoke Extend does, so a pattern repeated across clients is structurally cheaper to run as a certified
   product than as five bespoke builds.
6. **Testing economics invert.** Non-production is free, so load-test and measure consumption in sandbox
   before go-live — constrained by pre-production counts being aggregate only.
7. **Proposals change shape.** A build quote without a projected run-cost is now incomplete; and an
   inefficient build becomes visible on the client's bill, which shifts accountability onto the builder.

## Sources

`blog.workday.com` (introducing Flex Credits; usage-based AI pricing) · `cio.com` (unpacking Workday's
agentic AI pricing — carries the rate-card figures) · `i8cloudconsulting.com` (entitlements, allotment
tables, overage rates; dollar figures are its own assumption) · `netnetweb.com` · `beri.net` (Rising 2026) ·
`panorama-consulting.com`
