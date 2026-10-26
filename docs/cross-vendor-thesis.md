# Cross-vendor positioning: why the stack converges

The strategic frame for the team conversation. Workday findings are
`VERIFIED 2026-10-26`; Salesforce is partially verified; **Oracle is not yet researched at all** and is
marked accordingly. Do not present the Oracle column to a client until it has had the same treatment.

## The thesis

Every major enterprise SaaS vendor is building the same four things at the same time. That convergence —
not any single vendor's roadmap — is what the tech stack is becoming. A partner positioned across Workday,
Salesforce, Oracle *and* the cloud layer can design what spans them. A single-vendor partner structurally
cannot.

## The convergence, by layer

| Layer | Workday `VERIFIED` | Salesforce `PARTIAL` | Oracle `NOT RESEARCHED` |
|---|---|---|---|
| **Agent registry / governance** | Agent System of Record (GA) — register, configure, activate, deactivate, observe; Custom Agents auto-register with audit trails and human-approval pauses | Agentforce with its own agent management | — |
| **Metered AI pricing** | **Flex Credits** — fungible, metered on completed action, annual allotment, no roll-over, no hard stop; **no published $/credit** | **Also called "Flex Credits"** — reported ~$0.10/action, Agentforce editions reported to include 1M credits/org/year plus 2.5M Data Services Credits | — |
| **Zero-copy / open-table data** | Data Cloud on **Apache Iceberg** — GA to Snowflake, BigQuery, Salesforce Data 360; EA to Databricks and Amazon SageMaker | Data Cloud zero-copy (and is itself a Workday federation target) | — |
| **Agent protocol** | Tenant **MCP** endpoint, JSON-RPC 2.0, OAuth 2.1 + PKCE, Agent System User tokens; A2A documented separately | Reported to be **metering agentic MCP and API calls** | — |

Two independent vendors landing on the same product name for metered AI consumption is not coincidence —
it is convergent design under the same economics.

## Where the cross-vendor gaps actually are

This is the substance of the position, and each one is larger than its single-vendor equivalent.

**1. Governance stops at each vendor's perimeter.** Workday audits what an agent does inside Workday.
Salesforce audits Salesforce. **Nobody governs one agent executing one business process across all three.**
Workday already concedes that actions reaching outside via Pipedream connectors "may leak outside Workday's
control perimeter" — and that is just one vendor's edge. A hire-to-onboard or quote-to-cash flow crossing
three platforms has three partial audit trails and no whole one.

**2. There is no common unit of cost.** Each vendor meters in its own currency, and independent analysis
notes vendors "are each defining their own units" with "no common measurement across platforms." A CFO
asking what the agent estate costs has to reconcile incompatible meters — and only ~35% of CIOs report full
visibility into AI operating costs today. Normalising this is tractable, valuable, and unowned.

**3. Agent identity is deliberately out of scope for the protocol.** MCP went **stateless** in the
2026-07-28 spec, with identity and durable execution left outside it on purpose. That is exactly the space
each vendor is filling proprietarily (Workday's ASU tokens, for instance). So an agent needing
user-contextual access across three platforms has to reconcile three identity models — and no standard will
do it for you.

**4. Iceberg makes a genuine cross-vendor lakehouse newly possible.** Everyone converging on Apache Iceberg
means Workday people data, Salesforce pipeline data and Oracle financials can sit in one catalog on AWS or
Azure without ETL. That is a real, newly available architecture — and it rewards **cloud-platform depth over
SaaS-configuration depth**, which inverts the traditional partner skill profile.

## What this means for positioning

The pitch is not "we know Workday better." It is: **the stack is converging on MCP plus Iceberg plus metered
consumption across every vendor you run, each vendor governs only its own perimeter, and nobody prices the
whole estate in one currency. We work across all of them plus the cloud layer, so we can design what spans
them and tell you what it actually costs.**

Concretely, that makes three things sellable that a single-vendor partner cannot offer:

- **Cross-vendor agent governance** — one inventory, one ownership model, one audit view, spanning
  perimeters that each vendor leaves open at its edge
- **Normalised consumption economics** — one currency across Workday credits, Salesforce credits, Oracle
  metering and cloud inference spend, with forecasting and chargeback
- **Cross-vendor agent identity and contextual security** — the problem MCP explicitly declines to solve

## Honest gaps before this is client-ready

- **Oracle is unresearched.** The column above is empty and must not be bluffed.
- **Salesforce is only partially verified** — the credit figures are from secondary sources and need
  confirming against Salesforce's own published material.
- **Cloud-provider agent layers are not covered here** — Bedrock AgentCore, Azure AI Foundry and Vertex all
  have their own agent and identity models that belong in this picture.
- **No cross-vendor reference architecture exists yet.** The thesis is sound; the diagram and a working
  proof are what would make it credible, and neither is built.

## Sources

Workday: see [research/workday-agent-platform.md](research/workday-agent-platform.md),
[research/workday-data-cloud.md](research/workday-data-cloud.md),
[research/flex-credits-economics.md](research/flex-credits-economics.md).
Salesforce and MCP ecosystem: secondary reporting — vantagepoint.io (Salesforce metering MCP and API calls),
supered.io and aquiva.com (Agentforce pricing), dev.to (MCP 2026-07-28 stateless spec; A2A versus MCP).
