# Forward integration patterns under metered consumption

What changes in how we design Workday integrations and agents now that consumption is metered, with a
worked before/after. Figures from [research/flex-credits-economics.md](research/flex-credits-economics.md),
`VERIFIED 2026-10-26`. Reproduce with `python -m tools.tco.example`.

> Dollar figures assume ~$0.10/credit, which is an **illustrative partner assumption, not a
> Workday-published rate**. Workday publishes none. Treat credit counts as sound and dollars as
> directional.

## What actually changed

Custom Studio integrations, Orchestrations and custom Extend apps **draw down metered platform
consumption**. Workday's own Core Connectors, EIB (Integration Events only), Built-on-Workday partner apps,
and all sandbox activity **do not**. Run-cost moved from invisible to attributable.

Two layers, often confused:

- **Platform Entitlements** — baseline allowances for API calls, Integration Events, document storage.
  Exceeding them draws Flex Credits.
- **Flex Credits** — the agent rate card, plus entitlement overage. Expire annually, no roll-over, no hard
  stop at zero (overages reconcile at year-end, so overruns are silent).

## The two design rules that fall out

**Rule 1 — count calls *and* events, not just calls.**

| Unit | Rate | Credits per unit |
|---|---|---|
| API call | 60 credits / 10,000 | 0.006 |
| Integration Event | 25 credits / 100 | 0.25 |

> **Provenance, before this goes to a vendor.** The two overage rates below come from a **single partner
> blog**, not from Workday's own published material, and we could not confirm them. The per-run Integration
> Event model matches standard Workday vocabulary and practitioner experience but is **not confirmed for
> billing purposes** (open question #3b). Use these to shape a design conversation; replace them with the
> client's actual entitlement record and contract before putting numbers in writing.

**An Integration Event costs ~42× an API call**, and — crucially — **one Integration Event appears to be
raised per integration *run*, not per record.** A nightly integration raises 365 events a year whether it moves 10
records or 10 million. An integration *triggered per transaction* runs once per transaction, so it raises
one event per transaction.

Two consequences:

- **An integration run costs about 42 API calls simply to exist.** Below ~42 calls per run the event
  dominates the bill; above it, the calls do. Small, frequent integrations are mostly paying for existing.
- **Run frequency is a first-class cost driver, independent of data volume.** Hourly instead of nightly is
  8,760 runs versus 365 — about 2,190 credits versus 91 — for exactly the same data. Ask "how fresh does
  this genuinely need to be?" before "how do I move this efficiently?"

Per-transaction triggering is therefore the single most expensive pattern available: 200,000 transactions
becomes 200,000 runs becomes 50,000 credits, before a single API call is counted.

**Rule 2 — the SKU boosts only lift API calls.** Extend +50%, Prism +15%, Financials +15% — additive against
the baseline, not compounded, and they do **nothing** for Integration Events or storage.

## Worked example: nightly worker sync + change notifications

Mid-size tenant: 25,000 employees, Extend and Prism owned, 4.5M API-call baseline → **7,425,000** with
boosts. Agent allotment **60,000** credits/year.

### Today

| Integration | Volume | Credits |
|---|---|---|
| Nightly worker sync — one detail call per worker per night | 9,125,365 calls + 365 runs | 54,843 |
| HR change notifications — triggered per transaction | 400,000 calls + **200,000 runs** | 52,400 |
| Recruiting: talent rediscovery, 50 requisitions/month | 600 × 750 cr | 450,000 |
| Recruiting: candidate grading, 2,000 résumés/month | 24,000 × 6 cr | 144,000 |

Billable after entitlement and allotment: **596,693 credits/yr** (~$59,700 illustrative), of which
**62,693 is integration** and the rest is agent credits. The sync alone exceeds the entire API entitlement
by 2.1M calls, leaving nothing for anything else; the per-transaction trigger contributes 50,000 credits in
Integration Events before any call is counted.

### Future — same business outcomes

| Integration | Volume | Credits |
|---|---|---|
| Nightly worker sync — **one WQL read** per night | 365 calls + 365 runs | 93 |
| HR change notifications — **nightly batch**, not per transaction | 730 calls + 365 runs | 96 |
| Analytics reads served from Prism | — | 0 (metering unverified) |
| Recruiting: candidate grading, kept delivered | 24,000 × 6 cr | 144,000 |
| Recruiting: talent rediscovery, replicated externally | — | ~144 cr + own inference |

Billable: **84,182 credits/yr** (~$8,400). Integration cost alone falls from **62,693 credits to 182** — a
**344× reduction** — and API calls from 9,525,365 to 1,460. What remains is almost entirely agent credits,
not integration traffic.

Note what did the work: the sync got cheaper by going **bulk** (call pattern), while the notifications got
cheaper by going **batch** (run frequency). Two different levers, and the second one is invisible if you
only count API calls.

### The point for the team

**The saving is not Studio → Orchestrate. It is per-row → bulk.** You could capture most of it without
changing platform at all. Orchestrate is still the right target — maintainability, observability,
supportability — but do not sell it as the cost story, because a lift-and-shift that preserves a per-row
call pattern saves nothing. The business case belongs on the call pattern.

## Decision ladder for new integrations

1. **Count the metered units first** — projected API calls and Integration Events per year, before design.
   This is now a required estimate, not an afterthought.
2. **Can it be bulk — and via what?** One call returning N records beats N calls, the biggest single lever
   by orders of magnitude. **But "bulk" has a documented floor:** the REST `limit` parameter maxes at **100
   records per call**, so a paged-REST read of 25,000 records is **250 calls, not one**. WQL's ceiling is
   **1,000,000 rows**. So for large reads, **use WQL or a report, not paged REST** — same data, 250× fewer
   calls. See [research/extend-platform-limits.md](research/extend-platform-limits.md).
3. **Can GraphQL collapse round-trips?** One query replacing several REST calls is one metered call instead
   of several. Caveats: Workday's GraphQL object coverage is partial, and *we have not verified how GraphQL
   is metered* — assume per-query, confirm before relying on it.
4. **Can the read move to Prism or Data Cloud zero-copy?** Potentially the biggest structural lever, because
   it may avoid the API entitlement entirely. **Unverified** — see
   [research/open-questions.md](research/open-questions.md) #0. Verify before building a business case on it.
5. **Only then consider materialising into an Extend BO.** This is where the instinct to "spool the data"
   needs care: writing to and reading from an Extend BO happens over `/apps/<refId>/v1/<collection>`, which
   is tenant API traffic and **almost certainly metered too**. Spooling does not escape metering — it
   reshapes it, trading one expensive fan-out for many cheap reads. It wins when the same data is read many
   times between refreshes; it loses when it just adds a hop. Prism is the better materialisation target if
   step 4 confirms favourable metering.
6. **Prefer exempt paths where they fit** — Core Connectors and EIB for what they do well. And for a pattern
   repeated across clients, certifying it as Built-on-Workday makes it exempt from client entitlement
   entirely, which is a genuine argument for productising rather than rebuilding bespoke.

## Delivered agents vs external replication

The same question, answered with the rate card. 600 requisitions/year, 24,000 résumés/year, 1,200 contracts:

| Skill | Delivered | External | Ratio |
|---|---|---|---|
| Talent rediscovery (750 cr/req) | 450,000 cr (~$45,000) | ~$224 | **200×** |
| Contract redline (500 cr/doc) | 600,000 cr (~$60,000) | ~$724 | **83×** |
| Candidate grading (6 cr/résumé) | 144,000 cr (~$14,400) | ~$523 | **28×** |

Note the third row: even at 6 credits per unit, **volume makes it material**. Per-unit rate alone is not the
decision input — rate × volume is.

**But cost is not the whole decision.** Replicating externally transfers to you: ASOR registration and
audit, contextual security enforcement, Agent Passport attestation coverage, ongoing maintenance as Workday
improves the delivered agent, and — critically — **regulatory exposure**. For résumé screening and hiring
decisions, automated-employment-decision rules create bias-audit obligations that a vendor-attested agent
arguably absorbs and a homegrown screener does not. A 28× cost gap may still be the wrong trade there.

**Working rule:** replicate externally when credits-per-action is high, volume is real, the task is generic
rather than dependent on deep Workday context, and regulatory exposure is low. Contract redlining fits well.
Talent rediscovery fits on cost but deserves a legal conversation. Résumé screening is the one to leave
delivered despite the arithmetic.

**One pattern to avoid:** having an external agent *call* the delivered agent to get its functionality more
cheaply. That does not work — you pay the rate-card credits for the delivered action *and* the consumption
of the external agent calling the tenant. The arbitrage only exists in replicating the *outcome* from cheap
data reads, never in re-wrapping the delivered agent.

## Verify before client use

- The client's **actual API-call baseline** from their entitlement record — only one band's figure is public
- Their **contracted price per credit** — replaces the illustrative $0.10 everywhere
- **How Prism and Data Cloud reads are metered** (open question #0) — gates steps 4 and 5 above
- **How GraphQL is metered** — assumed per-query
- Whether **Studio is formally deprecated** — do not assert a deprecation path without a source
