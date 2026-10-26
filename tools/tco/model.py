"""Consumption and TCO model for Workday integrations and agents.

Answers three questions with arithmetic instead of adjectives:
  1. What does this integration footprint cost to run per year?
  2. Which agent skills are worth enabling, and which blow the allotment?
  3. Is replicating a delivered agent externally actually cheaper?

Dollar outputs are directional only - Workday publishes no price per credit.
See docs/research/flex-credits-economics.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import rates


@dataclass
class IntegrationLoad:
    """Annual metered volume for one integration."""

    name: str
    api_calls: int = 0
    integration_events: int = 0
    doc_storage_gb: float = 0.0
    exempt: bool = False  # Core Connector, EIB events, Built-on-Workday

    def credits(self) -> float:
        if self.exempt:
            return 0.0
        return (
            self.api_calls * rates.CREDITS_PER_API_CALL
            + self.integration_events * rates.CREDITS_PER_INTEGRATION_EVENT
            + self.doc_storage_gb * rates.DOC_STORAGE_CREDITS_PER_GB_YEAR
        )


@dataclass
class AgentLoad:
    """Annual volume for one agent skill."""

    skill: str
    units_per_year: int

    def credits(self) -> float:
        spec = rates.AGENT_SKILLS.get(self.skill)
        if spec is None:
            raise KeyError(
                f"Unknown skill {self.skill!r}. Known: {sorted(rates.AGENT_SKILLS)}"
            )
        return spec["credits"] * self.units_per_year


@dataclass
class Tenant:
    employees: int
    api_baseline: int  # from the client's entitlement record, not guessable
    skus: tuple[str, ...] = ()
    planning_sana_only: bool = False

    def api_entitlement(self) -> int:
        return rates.api_baseline_with_boosts(self.api_baseline, self.skus)

    def agent_allotment(self) -> int:
        return rates.complimentary_credits(self.employees, self.planning_sana_only)


@dataclass
class Estimate:
    tenant: Tenant
    integrations: list[IntegrationLoad] = field(default_factory=list)
    agents: list[AgentLoad] = field(default_factory=list)
    usd_per_credit: float = rates.ILLUSTRATIVE_USD_PER_CREDIT

    def api_calls_total(self) -> int:
        return sum(i.api_calls for i in self.integrations if not i.exempt)

    def api_overage_calls(self) -> int:
        return max(0, self.api_calls_total() - self.tenant.api_entitlement())

    def api_overage_credits(self) -> float:
        return self.api_overage_calls() * rates.CREDITS_PER_API_CALL

    def event_credits(self) -> float:
        return sum(
            i.integration_events * rates.CREDITS_PER_INTEGRATION_EVENT
            for i in self.integrations
            if not i.exempt
        )

    def storage_credits(self) -> float:
        return sum(
            i.doc_storage_gb * rates.DOC_STORAGE_CREDITS_PER_GB_YEAR
            for i in self.integrations
            if not i.exempt
        )

    def agent_credits(self) -> float:
        return sum(a.credits() for a in self.agents)

    def agent_overage_credits(self) -> float:
        return max(0.0, self.agent_credits() - self.tenant.agent_allotment())

    def billable_credits(self) -> float:
        """Credits that actually cost money, after entitlement and allotment."""
        return (
            self.api_overage_credits()
            + self.event_credits()
            + self.storage_credits()
            + self.agent_overage_credits()
        )

    def illustrative_usd(self) -> float:
        return self.billable_credits() * self.usd_per_credit

    def report(self) -> str:
        t = self.tenant
        lines = [
            "Workday consumption estimate",
            f"  rate card verified {rates.VERIFIED_ON}",
            "",
            f"Tenant: {t.employees:,} employees"
            + (f", SKUs: {', '.join(t.skus)}" if t.skus else ""),
            f"  API entitlement       {t.api_entitlement():>14,} calls/yr"
            + (f"  (baseline {t.api_baseline:,} + boosts)" if t.skus else ""),
            f"  Agent allotment       {t.agent_allotment():>14,} credits/yr"
            "  (expires annually, no roll-over)",
            "",
            "Integrations",
        ]
        for i in sorted(self.integrations, key=lambda x: -x.credits()):
            tag = "  [exempt]" if i.exempt else ""
            lines.append(
                f"  {i.name:<34} {i.api_calls:>12,} calls "
                f"{i.integration_events:>9,} events "
                f"{i.credits():>10,.0f} cr{tag}"
            )
        lines += [
            "",
            f"  API calls total       {self.api_calls_total():>14,}",
            f"  over entitlement      {self.api_overage_calls():>14,}"
            f"  -> {self.api_overage_credits():>10,.0f} credits",
            f"  Integration Events    {'':>14}  -> {self.event_credits():>10,.0f} credits",
            f"  Document storage      {'':>14}  -> {self.storage_credits():>10,.0f} credits",
            "",
            "Agents",
        ]
        for a in sorted(self.agents, key=lambda x: -x.credits()):
            spec = rates.AGENT_SKILLS[a.skill]
            lines.append(
                f"  {a.skill:<34} {a.units_per_year:>12,} x {spec['credits']:>4} cr "
                f"{a.credits():>10,.0f} cr"
            )
        lines += [
            "",
            f"  Agent credits         {self.agent_credits():>14,.0f}",
            f"  over allotment        {'':>14}  -> {self.agent_overage_credits():>10,.0f} credits",
            "",
            f"BILLABLE              {self.billable_credits():>14,.0f} credits/yr",
            f"  illustrative only   ~${self.illustrative_usd():>13,.0f}/yr"
            f"  at ${self.usd_per_credit:.2f}/credit (NOT a Workday-published rate)",
        ]
        return "\n".join(lines)


def compare_build_vs_delivered(
    skill: str,
    units_per_year: int,
    external_api_calls_per_unit: int,
    external_inference_usd_per_unit: float,
    usd_per_credit: float = rates.ILLUSTRATIVE_USD_PER_CREDIT,
) -> str:
    """Delivered agent vs replicating the same outcome outside Workday.

    Cost is only one input. Replicating externally also transfers to you: ASOR
    registration and audit, contextual security, Agent Passport attestation,
    ongoing maintenance, and - for hiring or contract decisions - regulatory
    exposure that a vendor agent arguably absorbs. Weigh those before acting on
    the number this returns.
    """
    spec = rates.AGENT_SKILLS[skill]
    delivered_credits = spec["credits"] * units_per_year
    delivered_usd = delivered_credits * usd_per_credit

    ext_calls = external_api_calls_per_unit * units_per_year
    ext_credits = ext_calls * rates.CREDITS_PER_API_CALL
    ext_workday_usd = ext_credits * usd_per_credit
    ext_inference_usd = external_inference_usd_per_unit * units_per_year
    ext_total = ext_workday_usd + ext_inference_usd

    ratio = delivered_usd / ext_total if ext_total else float("inf")
    verdict = (
        "external replication is materially cheaper - weigh the governance transfer"
        if ratio >= 5
        else "delivered agent is competitive - replication unlikely to repay build and risk"
    )
    return "\n".join(
        [
            f"{skill}  ({units_per_year:,} x {spec['unit']})",
            f"  delivered   {delivered_credits:>12,.0f} cr   ~${delivered_usd:>10,.0f}",
            f"  external    {ext_credits:>12,.0f} cr   ~${ext_workday_usd:>10,.0f} Workday"
            f" + ${ext_inference_usd:,.0f} inference  = ~${ext_total:,.0f}",
            f"  ratio       {ratio:>12,.1f}x",
            f"  -> {verdict}",
        ]
    )
