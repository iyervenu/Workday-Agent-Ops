# Workday agent platform

`VERIFIED 2026-10-25` unless marked otherwise.

## Component map

| Component | Status | What it is |
|---|---|---|
| **Trusted Agent Platform** | announced 2026-10-13 | Umbrella brand: *"headless access to HR and Finance, letting customers build and run lawful AI agents."* |
| **ASOR** (Agent System of Record) | GA | Registry, identity, lifecycle and observability for Workday, partner and third-party agents: find, add, register, configure, activate, deactivate, monitor. |
| **AgentSkills** | v1.2 | Open format for agent definitions. A Skill is *"a discrete, well-defined capability or function that an agent can perform."* Fields include `id`, `name`, `description`, `outputModes`, `tags`; bound to Workday resources via `workdayConfig.skillId`. Documented at `github.com/Workday/asor`. |
| **Agent Gateway** | GA | Single unified **regional** endpoint and control point; **meters all agent interactions**. Third-party agents register here and are issued an **Agent System User (ASU)** token. |
| **Tenant MCP endpoint** | GA | `https://{agentGatewayRegionEndpoint}/{tenantName}/mcp` — MCP **JSON-RPC 2.0**, **OAuth 2.1 with PKCE only**. Discovery filters: `toolType` (`AGENT_READY` \| `AGENT`), `operationType` (`CREATE` \| `PATCH` \| `VIEW`), `protocol=MCP`. Discovery is automatic for Workday Custom Agents; **third-party agents must enumerate permitted tools in their agent definition**. |
| **Agent-Ready Tools** | GA, 400+ | *"Pre-built headless API patterns"* — curated business logic rather than raw APIs, explicitly to cut hallucination and latency. Categories: **Basic** (read), **Advanced** (write), **Prompt** (read the valid options for a write). |
| **Custom Agents** | GA | Authored in Extend via **Developer Agent**, defined in AgentSkills, run in the **Workday Agent Harness**. *"Automatically registered in the Workday Agent System of Record, inheriting user permissions, maintaining strict audit trails, and pausing for human approvals when needed."* |
| **Custom Agent Actions** | named, **undocumented** | The mechanism for turning *your own* workflows and third-party services into tools *"that carry the same guardrails."* Deferred to a Part 2 post that had not published as of 2026-10-25. |
| **Pipedream** | GA (partnership) | Pre-built connectors across 1,000+ third-party systems; the documented path for custom agent actions reaching outside Workday. |
| **Agent Passport** | EA H2 2026, GA by end 2026 | *"Tests, verifies, and continuously monitors every AI agent"* — but **only against pre-defined public standards**: OWASP LLM Top 10, NIST AI RMF, MITRE ATLAS. Not domain correctness. |
| **A2A** (Agent2Agent) | documented | Separate path for connecting external agents. Workday documents both A2A and MCP and does **not** explain when to choose which. |

**Confirmed absences.** No API to register your own tool. No API to read agent activity or audit telemetry
(only *"visibility in ASOR Hub"*). No `CUSTOM` toolType in MCP discovery.

## What this commoditized

A per-action governance pipeline — identity check, risk tiering, proposal-before-write, approval gate,
segregated audit, kill switch — is **no longer differentiating**. Custom Agents get registration, permission
inheritance, audit trails and human-approval pauses automatically, and Workday has taken the
"headless / lawful agents" framing as product branding.

## What remains open

Per independent analysis (erp.today, *"Gatekeeping Enterprise AI? Workday Redraws the Build-vs-Buy Line"*):

> *"The next readiness test is not whether a company can build agents, but whether it can decide **which ones
> deserve to exist, who supports them, and when they get retired**."*
> *"Faster agent creation can produce useful automation, but it can also create duplicative agents, unclear
> ownership, uneven testing, and workflows that are hard to support."*

So: per-**action** governance is Workday's; per-**portfolio** governance — intake, ownership, duplication
control, testing standards, retirement, accountability — is customer-owned and explicitly unsolved. Specific
weak points documented:

- **Agent Passport accountability** — Workday is reportedly still working through *"questions of
  accountability if a tested agent later misbehaves"*; **one** attestation partner (Cisco); revocation
  mechanics unclear.
- **Pipedream perimeter leak** — actions reaching thousands of third-party systems mean governance *"may
  leak outside Workday's control perimeter."* Anything past Workday's edge is outside ASOR's audit.
- **Domain correctness is nobody's** — Agent Passport covers security/compliance standards, not *"is this the
  right answer under our policy."*

## Competitive field

**65+ global partners** already connect agents to ASOR, including Accenture, Deloitte, KPMG, PwC, IBM,
Kainos, Microsoft, Google Cloud, AWS, Adobe, Glean, Auditoria.AI, Compa, Paradox and WorkBoardAI.
**Building agents is not a differentiator.** No competing third-party agent-governance platform was named
in any coverage reviewed.

## Wider ecosystem `INFERENCE where noted`

- **MCP went stateless in the 2026-07-28 spec**, with identity and durable execution deliberately left
  *outside* the protocol — precisely the space ASOR and the Agent Gateway occupy. `INFERENCE:` expect that
  division to hold — thin protocol, platform owns identity, durability and governance.
- Adoption: ~97M monthly MCP SDK downloads (Mar 2026), ~78% of enterprise AI teams using it in production.
  It is infrastructure, not an experiment.
- A2A vs MCP is settling into "MCP gives agents reach, A2A gives agents peers, orchestration gives the
  system discipline."
- **WebMCP** (proposed web standard, Google I/O 2026) would let browser agents invoke structured tools.
- `INFERENCE:` the platform's direction is **raw APIs → curated tools**. Value shifts from building human
  UIs to authoring **tool contracts**, where the tool *description* is a real engineering artifact because
  it is what the model reads to decide whether to call it.
- `INFERENCE:` because the Gateway **meters** interactions, tool efficiency likely becomes a commercial
  concern, not just latency. Design for minimal round-trips.

## Sources

`doc.workday.com/admin-guide` (workday-ai/agents) · `blog.workday.com` (custom-agents,
trusted-agent-platform, workday-agentic-era-paths-build, managing-ai-powered-future-of-work) ·
`newsroom.workday.com` (2026-06-02, 2026-09-16, 2026-10-13) · `github.com/Workday/asor` ·
`dev.to/workdaydevelopers` ("Lawful Agents" series) · `erp.today` (build-vs-buy governance; workflow control)
