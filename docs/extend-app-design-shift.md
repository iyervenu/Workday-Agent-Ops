# How Extend app design changes

Drawn from auditing two real production apps (anonymised here as archetypes). The shift is not cosmetic:
the app stops being a **destination** and becomes a set of **capabilities** that a page is merely one
consumer of.

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

**The cost problem.** Eleven calls per page load, at 1,000 loads a day, is **~4.0 million API calls a year
from a single page** — most or all of a mid-size tenant's entire API entitlement, consumed by one screen.
(Caveat: some of those endpoints likely fire on action rather than load, so treat this as the ceiling and
measure the real figure in the Platform Consumption Console.)

**How it should be rebuilt:**

1. **Move the read path to Prism.** Reconciliation is a join across two datasets — exactly what Prism and
   Iceberg exist for. The page reads one pre-joined dataset instead of assembling it from eleven calls.
   Call volume per load collapses from 11 to ~1, an 11× reduction before any other change — and possibly to
   near-zero cost if Prism reads avoid the API entitlement (unverified, open question #0).
2. **Make the matching a tool, not page script.** "Reconcile this statement" becomes a callable capability.
   Same logic then serves the Workday page, a Teams prompt, and an agent, instead of being trapped in one
   PMD.
3. **Humans move from matching to exceptions.** The agent proposes; the human adjudicates only what failed.
   The page shrinks from a workbench to an exception queue.

**Net:** roughly seven pages and eleven endpoints become **two pages, one tool and one Prism dataset.**

## Archetype 2: the request-and-approval app

**As built:** twenty-nine pages, six business objects, seven orchestrations — and **every one of those
orchestrations contains loop constructs alongside API request nodes.** Several are pure business-rule
validators. One is a hand-built approval-routing integration.

**Three distinct problems:**

1. **Per-row loops.** Wherever an API node sits *inside* a loop, that is the expensive pattern. Worth
   auditing each flow individually — co-occurrence of loops and request nodes is a signal, not proof, since
   loops are also used for data shaping. Bulk the ones that are genuinely per-row.
2. **The hand-built approval routing is the piece most at risk of obsolescence.** Custom Agents now
   auto-register in ASOR, inherit user permissions, maintain audit trails and **pause for human approvals**
   natively. Hand-rolled approval orchestration is precisely what the platform absorbed. Do not rebuild it;
   plan to retire it.
3. **Twenty-nine pages is the real weight, and much of it exists only because a page was the only
   interface.** Validators like "validate this sponsor" or "validate this contact" are pure business rules
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
