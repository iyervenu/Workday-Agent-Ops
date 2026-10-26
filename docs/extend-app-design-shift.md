# How Extend app design changes

Drawn from auditing two real production apps (anonymised here as archetypes). The shift is not cosmetic:
the app stops being a **destination** and becomes a set of **capabilities** that a page is merely one
consumer of.

## Read this first: tool-ification is not a run-cost saving

An easy and expensive confusion to make — including in an earlier draft of this document.

**Moving logic from a page into a tool does not by itself reduce run cost.** The savings in the archetypes
below come from two *independent* changes: moving analytical reads to Prism, and bulking per-row call
patterns. Both are worth doing whether or not anything becomes a tool.

Three different meters are in play and they differ by orders of magnitude:

| Path | What is metered | Order of cost |
|---|---|---|
| Human uses a Workday page | API calls at 0.006 credits each | effectively free |
| Your own agent calls your own tool | **Assumed** API/entitlement consumption, plus your own cloud inference | pennies |
| Work routed through a **delivered Workday agent** | Rate card, 1–750 credits *per action* | $0.10 – $75 per action |

The expensive path is the third one — using Workday's delivered agents — not exposing your own logic as
callable. In fact, tool-ification is the *mechanism* for the arbitrage described in
[integration-patterns.md](integration-patterns.md): expose your logic as a tool, drive it with your own
agent on your own cloud, and the AI cost lands on your infrastructure bill where it is roughly two orders of
magnitude cheaper than Workday's per-action rate.

**But that entire argument rests on one unverified assumption:** that invoking a *custom* tool is metered as
API consumption rather than at delivered-agent rates. The published rate card prices Workday's own AI agents
doing AI work — there is no obvious reason Workday would charge inference rates for your business logic, and
"external AI agents calling the tenant" is described as entitlement consumption. But it is **not
documented**. See open question #2. If custom tool invocations turn out to be rate-card priced, the
economics invert and most of this document's advice changes.

**So the honest reason to build a tool is reach, not cost:** one implementation serving several front doors
instead of being trapped behind one page, and no duplicate build to keep in sync. If humans working inside
Workday are the only consumer a capability will ever have, **leave it as a page.**

Cost figures use the rate card in [research/flex-credits-economics.md](research/flex-credits-economics.md)
and the per-run Integration Event model in [integration-patterns.md](integration-patterns.md).

## The shift in one table

| | Today's Extend app | Future |
|---|---|---|
| **Front doors** | One — the Workday UI | Several — Workday UI, Teams/Slack, a cloud-hosted AI experience, an agent |
| **Where logic lives** | Page scripts and orchestrations, reachable only from inside the app | Tools (Custom Agent Actions / MCP-exposed orchestrations), reachable from anywhere |
| **Read path** | REST per request, often per row | Prism / Data Cloud for anything analytical; REST reserved for transactional writes |
| **Call pattern** | Per-row loops | Bulk-first, and run-frequency-aware |
| **Approval & audit** | Hand-built in orchestrations and pages | Delegated to the platform — Custom Agents auto-register, inherit permissions, audit, and pause for approval |
| **Business objects** | The app's private database | The data contract a tool reads and writes, potentially also visible from the lakehouse |
| **Page count** | Many — because a page was the only way to interact | Few — reserved for genuinely visual and exception work |

## Archetype 1: the reconciliation workbench

**As built:** seven pages, two business objects, five WQL queries, no orchestrations. The main workbench
page carries **eleven endpoint references**. Matching logic lives in page script. A human eyeballs the
matches and resolves exceptions.

**The cost problem — and be careful how this is stated.** What is *measured* is that the page file contains
eleven endpoint references. Everything beyond that is modelled:

- **Measured:** 11 endpoint references in the page definition.
- **Not known:** how many fire per page load. Some will be action-triggered rather than load-triggered, so
  11 is a ceiling, not an observed per-load figure.
- **Assumed:** a usage rate. At an illustrative 1,000 page loads a day, an 11-call load would be ~4.0M API
  calls a year — which would be most of a mid-size tenant's entire entitlement from one screen. **That
  number is an illustration of the shape of the risk, not a measurement.** The real figure comes from the
  Platform Consumption Console.

The defensible claim is narrow and still useful: *a page carrying double-digit endpoint references has a
consumption profile nobody has measured, and under metered pricing that is now worth measuring.* Do not
present the 4M figure as this app's actual consumption.

**How it should be rebuilt:**

1. **Move the read path to Prism.** Reconciliation is a join across two datasets — exactly what Prism and
   Iceberg exist for. The page reads one pre-joined dataset instead of assembling it from eleven calls.
   Call volume per load drops by roughly the number of endpoints collapsed — and *possibly* to near-zero
   cost, but only if Prism reads avoid the API entitlement, which is **unverified** (open question #0).
   Do not promise the saving before that is confirmed.
2. **Make the matching a tool, not page script.** "Reconcile this statement" becomes a callable capability.
   Same logic then serves the Workday page, a Teams prompt, and an agent, instead of being trapped in one
   PMD.
3. **Humans move from matching to exceptions.** The agent proposes; the human adjudicates only what failed.
   The page shrinks from a workbench to an exception queue.

**Net:** roughly seven pages and eleven endpoints become **two pages, one tool and one Prism dataset.**

## Archetype 2: the request-and-approval app

**As built:** twenty-nine pages, six business objects, seven orchestrations. Several of the orchestrations
are pure business-rule validators; one is a hand-built approval-routing integration.

**On the loops — what is and is not known.** A text scan shows loop constructs and API-request nodes
co-occurring in all seven flows. That is *not* evidence of per-row API calls: loops are also used for data
shaping, and the scan cannot tell whether a request node sits inside a loop or beside it. The defensible
statement is that **all seven warrant an individual audit**, not that all seven are inefficient.

**Three distinct problems:**

1. **Per-row loops.** Wherever an API node sits *inside* a loop, that is the expensive pattern. Worth
   auditing each flow individually — co-occurrence of loops and request nodes is a signal, not proof, since
   loops are also used for data shaping. Bulk the ones that are genuinely per-row.
2. **The hand-built approval routing is the piece most at risk of obsolescence.** Custom Agents now
   auto-register in ASOR, inherit user permissions, maintain audit trails and **pause for human approvals**
   natively. Hand-rolled approval orchestration is precisely what the platform absorbed. Do not rebuild it;
   plan to retire it.
3. **Twenty-nine pages is the real weight, and much of it exists only because a page was the only
   interface.** Validators of the "check this party record against our rules" kind are pure business logic
   and ideal tool candidates — expose them and they become reachable from a chat prompt, an email, or an
   external agent. Conversational intake plus platform-native approval removes the need for a large share of
   the page estate.

**Net:** the centre of gravity moves from **pages → tools + business objects**, with pages retained for the
genuinely visual steps.

## The design checklist for new builds

1. **What is the capability, independent of any screen?** Name it as a tool first. Build the page second.
2. **Is this read analytical or transactional?** Analytical → Prism or Data Cloud. Transactional → REST.
   Never assemble an analytical view from per-row REST.
3. **How many metered calls per interaction?** Estimate before building. A page with double-digit endpoints
   is a cost defect, not a design detail.
4. **How often must this run, really?** Run frequency costs ~42 API calls per run just to exist. Nightly
   beats hourly beats per-transaction unless freshness genuinely demands otherwise.
5. **Am I about to hand-build approval, audit or agent registration?** Stop — the platform does these now.
6. **Will this pattern repeat across clients?** Then certifying it as Built-on-Workday makes it exempt from
   client entitlement consumption entirely, which is a real argument for productising over rebuilding.

## What to verify before committing to this

- Whether **Prism and Data Cloud reads avoid the API entitlement** (open question #0) — gates points 1 and 2
- Whether **Extend app REST traffic raises billable Integration Events** or is call-metered only
  (open question #3b) — swings interactive app economics materially
- Whether a **custom Extend orchestration can be exposed as a Custom Agent Action** at all, which is still
  undocumented (open question #2) — gates the "logic becomes a tool" move
