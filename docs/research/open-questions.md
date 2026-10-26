# Open questions

The live watch list. Each item has **how to verify** so it can actually be closed rather than carried
forever. Move answered items into the relevant research file with a `VERIFIED <date>` marker.

Opened 2026-10-25.

## Highest value

**0. How are Prism and Data Cloud query volumes metered?** `added 2026-10-26`
Potentially the most commercially useful unknown. Custom Extend apps and Orchestrations draw down metered
API calls, with overages at 60 credits per 10,000 calls. If reads served from Prism tables or zero-copy
Iceberg are metered differently — or not at all against the API entitlement — then moving a read path off
per-row REST becomes a pure cost reduction with no functional change, and "credit-efficient architecture"
becomes a sellable engagement with arithmetic behind it. No source consulted documents this.
*Verify:* the Platform Consumption Console's usage-by-component breakdown in a tenant with Prism; whether
Data Cloud / Live Data Query consumption appears as API calls, a separate component, or a Flex Credit draw;
the Data Cloud admin guide's consumption section if one exists. See
[flex-credits-economics.md](flex-credits-economics.md).

**1. Is agent / ASOR telemetry exposed in the Data Cloud Catalog?**
Decides whether agent-portfolio governance and observability can be built on real data rather than a manual
registry. Every source checked is silent on agent, audit and telemetry objects; object availability is
defined by the Data Cloud Catalog, which the setup page points to but does not reproduce.
*Verify:* inspect the Data Cloud Catalog in-tenant; check whether ASOR's *"telemetry for every one of those
calls into that same repository"* is reachable from Prism, Data Lake, Live Data Query or a report.

**2. Can a custom Extend orchestration become an agent-callable tool directly?**
Or is Pipedream the only sanctioned route? The mechanism is named — **Custom Agent Actions** — but was
undocumented as of 2026-10-25.
*Verify:* watch for "Lawful Agents" Part 2 on `dev.to/workdaydevelopers`; check whether
`doc.workday.com/admin-guide/workday-ai/agents` gains a Custom Agent Actions page.

**3. Is Data Cloud licensed in the development tenant?**
Gates anything built on zero-copy. Requires a separate SKU plus a mandatory Flex Credits subscription and a
partner-platform contract.
*Verify:* check tenant entitlements and whether the *"Data Cloud: Manage Data Lake Access Policies"* domain
exists.

## Platform mechanics

**3b. Exactly what raises a billable Integration Event?** `added 2026-10-26`
The whole consumption model hinges on this. An Integration Event is raised per integration **run** (not per
record), which is standard Workday vocabulary and is what practitioner experience confirms — but it is not
established which execution types raise a *billable* event under the entitlement meter. Classic integrations
(EIB, Studio, Core Connector, Orchestrate for Integrations) clearly do. **Unknown:** whether an
Orchestration invoked via `/launch` raises one, and whether ordinary Extend app REST traffic raises one at
all or is purely API-call metered. If Extend/Orchestration traffic is call-metered only, interactive app
designs are far cheaper than this model assumes; if each invocation raises an event, they are far more
expensive.
*Verify:* the Platform Consumption Console's usage-by-component breakdown after running each execution type
once in a tenant; the entitlement definitions in the contract or admin guide.

**4. How does Workday's security model actually travel into AWS?**
Workday claims *"the permission model, business logic, and audit controls travel with the data"* but gives no
mechanism — no credential exchange, IAM mapping or OAuth detail. Meanwhile it explicitly makes
partner-platform security the customer's responsibility. These two statements need reconciling.
*Verify:* the Data Cloud admin guide's zero-copy setup pages; AWS-side Lake Formation / Glue catalogue
behaviour once a share exists.

**5. When should MCP be used versus A2A on Workday?**
Workday documents both and explains neither choice.
*Verify:* `doc.workday.com` A2A pages; watch for guidance in the "Lawful Agents" series.

**6. Does ASOR gain an activity/audit read API?**
Would re-open third-party analytics on ASOR directly, independent of Data Cloud.
*Verify:* `github.com/Workday/asor` commits and release notes.

**7. Does `wdcli --app-type` gain an agent-specific value?**
`wdcli app upload --help` already references *"Custom Agent (External Framework)"* apps. Possibly related to
the `Agent registration failed` warning seen on an `EXTEND`-type deploy on 2026-10-23.
*Verify:* `wdcli app create --help` across CLI releases; try listing valid `--app-type` values.

## Roadmap watch

**8. Does Agent Passport's scope widen beyond public standards?**
Today it validates against OWASP LLM Top 10, NIST AI RMF and MITRE ATLAS only — **not** customer-defined
correctness. If that changes, the domain-evaluation opportunity narrows significantly. Also watch the
attestation ecosystem (Cisco-only today) and how revocation behaves in practice.

**9. Does anything govern agent actions that exit Workday via Pipedream?**
Currently nothing appears to. If Workday closes this perimeter, the cross-boundary audit gap closes with it.

**10. Does the AWS integration reach GA, and which AWS services land?**
Only Bedrock is named so far; GA was *"planned for later this year"* (2026).
