"""Workday consumption rate card.

Every figure carries its provenance. VERIFIED means it was read from a primary or
reputable secondary source on the stated date; ASSUMED means it is an input we chose
and must be overridden with real tenant or contract data before any client use.

Sources: cio.com (Workday rate card figures), i8cloudconsulting.com (entitlement
mechanics, allotment table, overage rates), blog.workday.com (Flex Credits mechanics).
See docs/research/flex-credits-economics.md.
"""

VERIFIED_ON = "2026-10-26"

# ---------------------------------------------------------------------------
# Credit price
# ---------------------------------------------------------------------------
# Workday publishes NO dollar-per-credit rate. 0.10 is an illustrative figure used by
# partner analyses. Every dollar output is therefore directional only. Override with
# the client's actual contracted rate before showing money to anyone.
ILLUSTRATIVE_USD_PER_CREDIT = 0.10  # ASSUMED - not a Workday-published rate

# ---------------------------------------------------------------------------
# Complimentary annual agent credits, by employee count. VERIFIED 2026-10-26.
# Credits expire annually and do NOT roll over.
# ---------------------------------------------------------------------------
COMPLIMENTARY_CREDITS = [
    (100_000, 200_000),
    (30_000, 120_000),
    (10_000, 60_000),
    (3_500, 30_000),
    (0, 15_000),
]
PLANNING_SANA_ONLY_CREDITS = 5_000  # no HCM or Financials

# ---------------------------------------------------------------------------
# Platform Entitlement overage rates. VERIFIED 2026-10-26.
# Entitlements are the baseline allowances; exceeding them draws Flex Credits.
# ---------------------------------------------------------------------------
API_CREDITS_PER_10K_CALLS = 60
INTEGRATION_EVENT_CREDITS_PER_100 = 25
DOC_STORAGE_CREDITS_PER_GB_YEAR = 120

CREDITS_PER_API_CALL = API_CREDITS_PER_10K_CALLS / 10_000          # 0.006
CREDITS_PER_INTEGRATION_EVENT = INTEGRATION_EVENT_CREDITS_PER_100 / 100  # 0.25

# The single most actionable ratio in this file: an Integration Event costs ~42x an
# API call. Designs should count events far more carefully than calls.
EVENT_TO_CALL_COST_RATIO = CREDITS_PER_INTEGRATION_EVENT / CREDITS_PER_API_CALL

# ---------------------------------------------------------------------------
# SKU boosts. VERIFIED 2026-10-26.
# These lift the API-call baseline ONLY - not Integration Events, not storage.
# Additive against the baseline, NOT compounded with each other.
# ---------------------------------------------------------------------------
API_BASELINE_BOOSTS = {
    "extend": 0.50,
    "prism": 0.15,
    "financials": 0.15,
}

# Only one baseline datapoint is documented: a 10,000-29,999 employee org has a
# 4.5M annual API-call baseline. The full table by band is NOT published, so the
# baseline must be supplied per engagement from the client's own entitlement record.
KNOWN_API_BASELINE_ANCHOR = {"band": "10000-29999", "annual_api_calls": 4_500_000}

# ---------------------------------------------------------------------------
# Delivered agent rate card. VERIFIED 2026-10-26 unless noted.
# credits = cost per unit of work; unit names the thing being charged for.
# NOTE: skills inside ONE agent can differ by >100x. Govern at skill level.
# ---------------------------------------------------------------------------
AGENT_SKILLS = {
    "recruiting.candidate_grading": {
        "credits": 6,
        "unit": "resume screened and graded against a job opening",
        "source": "Workday rate card via cio.com",
    },
    "recruiting.talent_rediscovery": {
        "credits": 750,
        "unit": "requisition matched against existing talent pools",
        "source": "Workday rate card via cio.com",
    },
    "contract_negotiation.redline": {
        "credits": 500,
        "unit": "contract reviewed and redlined against a playbook",
        "source": "Workday rate card via cio.com",
    },
    "mobility.internal_talent_matching": {
        "credits": 750,
        "unit": "requisition matched internally",
        "source": "partner-reported",
    },
    "self_service.action": {
        "credits": 3,  # reported range 1-5; midpoint
        "unit": "self-service question or HR task",
        "source": "partner-reported range 1-5",
    },
    "business_process.optimize": {
        "credits": 1,
        "unit": "optimisation action",
        "source": "partner-reported",
    },
    "payroll_time.action": {
        "credits": 35,  # reported range 10-60; midpoint
        "unit": "payroll or time management action",
        "source": "partner-reported range 10-60",
    },
}

# ---------------------------------------------------------------------------
# What consumes metered entitlement, and what does not. VERIFIED 2026-10-26.
# This asymmetry drives build-vs-buy and productisation decisions.
# ---------------------------------------------------------------------------
CONSUMES_ENTITLEMENT = (
    "custom Studio integrations",
    "Orchestrations",
    "custom Workday Extend applications",
    "modified Workday-built integrations",
    "external AI agents calling the tenant",
    "certified Partner integrations (API requests)",
)

EXEMPT_FROM_ENTITLEMENT = (
    "Workday Core Connectors",
    "EIB (Integration Events only)",
    "Built-on-Workday partner applications",
    "sandbox and non-production activity",
)


def complimentary_credits(employees: int, planning_sana_only: bool = False) -> int:
    """Annual complimentary agent credits for an org of this size."""
    if planning_sana_only:
        return PLANNING_SANA_ONLY_CREDITS
    for threshold, credits in COMPLIMENTARY_CREDITS:
        if employees >= threshold:
            return credits
    return COMPLIMENTARY_CREDITS[-1][1]


def api_baseline_with_boosts(base_calls: int, skus: tuple[str, ...] = ()) -> int:
    """Apply SKU boosts to an API-call baseline.

    Boosts are additive against the baseline rather than compounded, so Extend plus
    Prism gives +65% of baseline, not 1.50 * 1.15.
    """
    uplift = sum(API_BASELINE_BOOSTS.get(s.lower(), 0.0) for s in skus)
    return int(round(base_calls * (1 + uplift)))
