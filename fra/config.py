"""Editable thresholds. Every number here is a council default (docs/RULEBOOK.md
and docs/council/r3_*.md) that the team can tune. Keep comments pointing at the
rule each value comes from so changes stay traceable."""

# --- Report staleness (RULEBOOK §1.5; r3 bureaus §2) ---
CONSUMER_REPORT_STALE_DAYS = 30        # revolving products: "re-pull before applying"
CONSUMER_REPORT_PROVISIONAL_DAYS = 60  # readiness provisional
CONSUMER_REPORT_SUPPRESS_DAYS = 90     # funding ranges suppressed
COMMERCIAL_REPORT_MAX_AGE_DAYS = 90    # older business report counts as missing
BANK_STATEMENT_MAX_AGE_DAYS = 45       # R19
TAX_RETURN_MAX_AGE_MONTHS = 18         # R19

# --- Derogatory severity (RULEBOOK §3.1) ---
DEROG_BASE = {
    "late30": 20, "late60": 35, "late90": 50, "late120": 60,
    "collection": 60, "collection_small": 10, "paid_collection": 35,
    "medical_unpaid_500": 25, "medical_small_or_paid": 0,
    "chargeoff": 75, "paid_chargeoff": 55,
    "repo": 80, "surrender": 75, "foreclosure": 90,
    "judgment": 70, "tax_lien": 85,
    "bankruptcy7": 90, "bankruptcy13": 80, "bankruptcy13_active": 95,
    "bankruptcy_dismissed": 95, "bankruptcy_open": 100,
}
# Decay by months since DOFD/event (RULEBOOK §3.2): (upper bound in months, multiplier)
DECAY_STEPS = [(6, 1.00), (12, 0.85), (24, 0.65), (36, 0.45), (60, 0.30), (84, 0.15)]
BK_DECAY_STEPS = [(12, 1.00), (24, 0.80), (48, 0.55), (84, 0.35), (120, 0.20)]

# --- Guarantor area (r3 identity §4) ---
GUARANTOR_PASS_SCORE = 680
GUARANTOR_AR_SCORE = 620
BUREAU_SPREAD_REVIEW = 40              # HR: score gap between bureaus
INQUIRY_ADVISORY_6M = 4                # per bureau, advisory
UTIL_GOOD = 0.10
UTIL_FAIR = 0.30
UTIL_HIGH = 0.50
AU_HEAVY_LIMIT_SHARE = 0.30            # F-36

# --- Commercial bureaus (r3 bureaus §2) ---
INTELLISCORE_V2_PASS = 76
INTELLISCORE_V3_PASS = 721
PAYDEX_PASS = 80
DNB_CLASS_PASS = 2                     # Failure / Delinquency class <= 2
EQUIFAX_BUSINESS_PASS = 556
TRADES_PASS_PER_BUREAU = 3
TRADES_PASS_TOTAL = 5
COMMERCIAL_UTIL_PASS = 0.50

# --- Identity matrix (r3 identity §1.4) ---
REVENUE_MISMATCH_PCT = 0.30            # bureau revenue vs tax return (R10 pair)

# --- Composite score (r3 identity §5.4) ---
COMPOSITE_WEIGHTS = {
    "legal": 0.25, "credit": 0.20, "banking": 0.25, "guarantor": 0.20, "goal": 0.10,
}
POINT_VALUES = {"PASS": 100, "NEEDS IMPROVEMENT": 60, "ACTION REQUIRED": 20}
CORE_POINTS = {1, 2, 15, 17, 20}

# --- Tiers (RULEBOOK R17) ---
TIERS = [(80, "Fund-Ready"), (65, "Near-Ready"), (50, "Needs Work"), (0, "Not Ready")]

# --- Card stack cap (RULEBOOK R5) ---
STACK_MAX_MULTIPLE_HL = 4
STACK_MAX_INCOME_SHARE = 0.5
STACK_ABSOLUTE_CAP = 100_000

# --- AI ---
AI_MODEL = "claude-opus-5-5"
AI_EFFORT_EXTRACT = "medium"
AI_EFFORT_NARRATIVE = "high"
# USD per million tokens (input, output) for the cost meter
AI_PRICES = {"claude-opus-5-5": (4.00, 20.00), "claude-sonnet-5-5": (2.00, 10.00)}


def tier_for(score: float) -> str:
    for floor, name in TIERS:
        if score >= floor:
            return name
    return "Not Ready"
