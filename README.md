# Workday Agent Ops

Exploring what's left for customers and implementers to own once Workday's agent platform handles the
basics. Deliberately **not** another agent-building project — 65+ partners are already doing that.

## Why this exists

As of 2026-10, Workday ships per-action agent governance natively: Custom Agents in Extend are
automatically registered in the Agent System of Record, inherit user permissions, maintain audit trails, and
pause for human approvals. Agent-Ready Tools (400+) expose governed business logic over MCP. Agent Passport
tests agents against OWASP LLM Top 10, NIST AI RMF and MITRE ATLAS.

Building a governance layer that duplicates any of that is wasted effort. See
[docs/research/](docs/research/) for the verified detail — and for what is demonstrably *not* covered.

## The gaps this repo targets

1. **Agent portfolio governance.** Workday governs what an agent *does*. Nobody governs *which agents should
   exist* — intake, ownership, duplication, testing standards, retirement, accountability when one
   misbehaves. Independent analysis calls this the real readiness test, and it is explicitly customer-owned.
2. **Domain-correctness evaluation.** Agent Passport verifies security and compliance posture against public
   standards. It does not answer *"does this agent correctly apply our institution's rules, and does it
   refuse when it should?"* That definition of correct belongs to the customer, so it stays customer-owned.
3. **Cross-perimeter audit.** Agents reach 1,000+ external systems through Pipedream connectors. Workday
   concedes governance "may leak outside Workday's control perimeter." Nothing stitches a single transaction
   across both sides.
4. **Zero-copy governance and cost.** Workday Data Cloud hands over Iceberg tables and states plainly that
   securing data *read out of* Workday is the customer's job — row/column security, access policy, lineage,
   retention, all on the partner platform. Add the metered Agent Gateway and a mandatory Flex Credits
   subscription, and combined cost observability is unowned too.

Gaps 1 and 2 are the same system at different maturities — uneven testing is one of the failure modes a
portfolio control plane exists to manage. Gap 4 is the deepest moat for anyone strong on both AWS and
Workday, but depends on Data Cloud entitlements.

## The wider frame

Workday is not moving alone. Salesforce and Oracle are building the same four layers — an agent registry,
metered AI consumption, zero-copy open-table data sharing, and MCP as the tool protocol. Each vendor governs
only its own perimeter, and nobody prices the whole estate in one currency. That cross-vendor gap is larger
than any single-vendor one, and it is the strategic position: see
**[docs/cross-vendor-thesis.md](docs/cross-vendor-thesis.md)**.

## Direction

Two assets in flight, both chosen because they produce evidence rather than claims:

- **Consumption and TCO modelling** — [tools/tco/](tools/tco/) turns the metered rate card into arithmetic
  for integration footprints, agent skill volumes, and delivered-vs-external agent decisions. Run
  `python -m tools.tco.example` for the worked before/after.
- **Cross-vendor agent identity and contextual security** — a reference implementation for reaching SaaS
  data from a cloud-hosted AI experience with user-level context and no SaaS login. This is the problem MCP
  explicitly declines to solve. Not yet built.

Then: domain-correctness evaluation (gap 2) growing into the portfolio control plane (gap 1).

## Layout

```
docs/research/              verified, source-cited platform notes + live open questions
docs/cross-vendor-thesis.md the strategic frame
docs/integration-patterns.md forward design rules, with worked before/after figures
tools/tco/                  consumption and TCO model
```

## Conventions

- **Verify, don't recall.** This space shipped major releases in June, September and October 2026. Claims
  carry a source and a date; anything inferred says so.
- **No client or tenant specifics in tracked files.** `CLAUDE.md` and `docs/engagement/` are gitignored for
  that reason. Research notes are drawn from public sources and are safe to share.
- Related: the `Extend-Local` repo is a separate, read-only precedent corpus of Extend apps. This repo does
  not depend on it.
