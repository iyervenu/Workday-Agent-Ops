# Workday agent & data platform research corpus

Distilled, source-cited notes on Workday's agent and data platform, maintained because **this space moves
faster than any model's training data** — releases landed in June, September and October 2026 alone, and
assertions made from memory have already proved wrong here more than once.

## Contents

| File | Covers |
|---|---|
| [workday-agent-platform.md](workday-agent-platform.md) | ASOR, Agent Gateway, tenant MCP endpoint, Agent-Ready Tools, Custom Agents, Custom Agent Actions, Pipedream, Agent Passport, A2A, partner landscape |
| [workday-data-cloud.md](workday-data-cloud.md) | Data Cloud, Data Connect, Live Data Query, Data Lake, Prism, Iceberg zero-copy, the AWS integration |
| [open-questions.md](open-questions.md) | The live watch list — unresolved questions, each with how to verify |

## Conventions

- **Every claim is dated and sourced.** `VERIFIED <date>` means it was read from a primary source on that
  date. Anything else must be labelled `INFERENCE`.
- **Never fill a gap from training data.** If a source doesn't say it, record that the source is silent —
  "not addressed" is a finding, not a failure.
- **Prefer practitioner channels alongside official docs.** Workday's own developer posts on dev.to and the
  community forums have repeatedly carried technical detail (endpoint shapes, auth flows, filter parameters)
  that product and marketing pages omit entirely.
- **Treat everything as decaying.** Re-verify before acting on anything older than roughly a quarter.

## Maintenance

Intended cadence: a weekly sweep of the sources listed at the bottom of each file, updating only what
changed, and moving items out of [open-questions.md](open-questions.md) as they get answered.

Nothing in this corpus is client-specific or tenant-specific — it is all drawn from public sources and is
safe to share. Tenant details, engagement context and anything client-identifying stay out of it by design.
