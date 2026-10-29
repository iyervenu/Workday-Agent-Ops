"""Worked examples: the same integration before and after, and agent build-vs-buy.

Run:  python -m tools.tco.example      (from the repo root)

Figures are a mid-size tenant: 25,000 employees, Extend and Prism owned, and the
one documented API baseline anchor (4.5M calls for the 10,000-29,999 band).
"""

from .model import AgentLoad, Estimate, IntegrationLoad, Tenant, compare_build_vs_delivered
from .rates import EVENT_TO_CALL_COST_RATIO

TENANT = Tenant(employees=25_000, api_baseline=4_500_000, skus=("extend", "prism"))

WORKERS = 25_000
CHANGES_PER_YEAR = 200_000


def today() -> Estimate:
    """The integration estimate as it is commonly built today."""
    return Estimate(
        tenant=TENANT,
        integrations=[
            # Nightly Studio sync: one detail call per worker, every night.
            # 365 runs -> 365 Integration Events, regardless of record count.
            IntegrationLoad(
                "nightly worker sync (per-row)",
                api_calls=(WORKERS + 1) * 365,
                runs_per_year=365,
            ),
            # Triggered per transaction: it RUNS 200,000 times, so 200,000 events.
            IntegrationLoad(
                "HR change notifications (per-transaction trigger)",
                api_calls=CHANGES_PER_YEAR * 2,
                runs_per_year=CHANGES_PER_YEAR,
            ),
        ],
        agents=[
            AgentLoad("recruiting.talent_rediscovery", units_per_year=600),  # 50/mo
            AgentLoad("recruiting.candidate_grading", units_per_year=24_000),  # 2k/mo
        ],
    )


def future() -> Estimate:
    """The same business outcomes, designed for the metered model."""
    return Estimate(
        tenant=TENANT,
        integrations=[
            # One WQL read per night instead of 25,000 detail calls.
            #
            # IMPORTANT: "bulk" has a floor. The REST `limit` parameter maxes at 100
            # records per call, so a paged-REST bulk read of 25,000 workers is
            # 250 calls per night = 91,250/yr, not one. WQL's ceiling is 1,000,000
            # rows, so the same read is a single call. That is why large reads should
            # use WQL or a report rather than paged REST.
            # See docs/research/extend-platform-limits.md.
            IntegrationLoad(
                "nightly worker sync (one WQL read)", api_calls=365, runs_per_year=365
            ),
            # Batched nightly, NOT hourly. Frequency is the cost driver here: hourly
            # would be 8,760 runs (2,190 credits) versus 365 runs (91 credits), for
            # the same data volume.
            IntegrationLoad(
                "HR change notifications (nightly batch)",
                api_calls=730,
                runs_per_year=365,
            ),
            # Analytics reads served from Prism rather than per-row REST.
            # Metering of Prism/Data Cloud reads is UNVERIFIED - see open-questions.md #0.
            IntegrationLoad("analytics reads via Prism", exempt=True),
        ],
        agents=[
            # Rediscovery replicated externally; grading kept delivered (cheap per unit).
            AgentLoad("recruiting.candidate_grading", units_per_year=24_000),
        ],
    )


def main() -> None:
    print("=" * 78)
    print("TODAY")
    print("=" * 78)
    print(today().report())
    print()
    print("=" * 78)
    print("FUTURE - same outcomes, designed for metered consumption")
    print("=" * 78)
    print(future().report())
    print()
    print("=" * 78)
    print("DELTA")
    print("=" * 78)
    t, f = today(), future()
    saved = t.billable_credits() - f.billable_credits()
    print(f"  billable credits   {t.billable_credits():>12,.0f} -> {f.billable_credits():>12,.0f}")
    print(f"  saved              {saved:>12,.0f} credits/yr"
          f"  (~${saved * t.usd_per_credit:,.0f} illustrative)")
    print(f"  API calls          {t.api_calls_total():>12,} -> {f.api_calls_total():>12,}")
    print()
    print(f"  An Integration Event costs {EVENT_TO_CALL_COST_RATIO:.0f}x an API call.")
    print()
    print("=" * 78)
    print("DELIVERED AGENT vs EXTERNAL REPLICATION")
    print("=" * 78)
    # Rediscovery: pull the pool in bulk, rank with your own model.
    print(compare_build_vs_delivered(
        "recruiting.talent_rediscovery",
        units_per_year=600,
        external_api_calls_per_unit=40,
        external_inference_usd_per_unit=0.35,
    ))
    print()
    # Grading: cheap per unit already.
    print(compare_build_vs_delivered(
        "recruiting.candidate_grading",
        units_per_year=24_000,
        external_api_calls_per_unit=3,
        external_inference_usd_per_unit=0.02,
    ))
    print()
    print(compare_build_vs_delivered(
        "contract_negotiation.redline",
        units_per_year=1_200,
        external_api_calls_per_unit=5,
        external_inference_usd_per_unit=0.60,
    ))


if __name__ == "__main__":
    main()
