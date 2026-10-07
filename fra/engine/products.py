"""Funding product fit (RULEBOOK §6–§8). Produces directional positioning per product,
not approval predictions. Hard knock-outs → NOT YET; soft knock-outs cap the score."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from fra import config as C
from fra.engine.guarantor import months_between
from fra.engine.results import GuarantorResult, ProductFit
from fra.models import Case

PRODUCTS = {
    "BC": "Business 0% credit cards",
    "PC": "Personal 0% credit cards",
    "PL": "Personal unsecured loan",
    "OL": "Online / fintech line of credit",
    "BL": "Bank line of credit",
    "SBA": "SBA loan (7(a) / Express / Micro)",
    "BT": "Bank term loan",
    "OT": "Online term loan",
    "EQ": "Equipment financing",
    "FAC": "Invoice factoring",
    "MCA": "Revenue-based financing / MCA",
    "DSCR": "Rental property loan (DSCR)",
    "FF": "Fix-and-flip loan",
}
SEQUENCE = ["BL", "BT", "SBA", "EQ", "OL", "OT", "FAC", "BC", "PC", "PL", "DSCR", "FF", "MCA"]
COST_RANK = {"SBA": 1, "BT": 2, "BL": 2, "EQ": 3, "BC": 3, "PC": 3, "DSCR": 4, "PL": 4, "OL": 5, "OT": 6, "FAC": 6, "FF": 7, "MCA": 9}

PRIME_RATE = 0.07  # placeholder — staff verify monthly (RULEBOOK §6.0)


def pmt(rate_annual: float, months: int, principal: float) -> float:
    r = rate_annual / 12
    return principal * r / (1 - (1 + r) ** -months) if r else principal / months


def pv(rate_annual: float, months: int, payment: float) -> float:
    r = rate_annual / 12
    return payment * (1 - (1 + r) ** -months) / r if r else payment * months


def round_down(x: float) -> float:
    step = 1000 if x < 25000 else 5000
    return max(0.0, (x // step) * step)


@dataclass
class Ctx:
    case: Case
    g: Optional[GuarantorResult]
    audit_date: date
    goal: set[str]
    gf: Optional[int] = None
    tib_months: Optional[int] = None
    tmr: Optional[float] = None
    tmr_verified: bool = False
    income: Optional[float] = None
    income_verified: bool = False
    ebitda: Optional[float] = None
    existing_ads: float = 0.0
    positions: int = 0
    nsf_month: Optional[float] = None
    adb: Optional[float] = None
    notes: list[str] = field(default_factory=list)


def build_ctx(case: Case, g: Optional[GuarantorResult], audit_date: date, goal: set[str]) -> Ctx:
    it = case.intake
    ctx = Ctx(case=case, g=g, audit_date=audit_date, goal=goal, gf=g.mid_score if g else None)
    start = it.operations_start_date or it.formation_date
    if start:
        ctx.tib_months = months_between(start, audit_date)
    months = [m for m in case.financials.bank_months if m.deposits is not None]
    if months:
        last3 = sorted(months, key=lambda m: m.month)[-3:]
        ctx.tmr = sum(m.deposits for m in last3) / len(last3)
        ctx.tmr_verified = True
        ctx.nsf_month = sum(m.nsf_count for m in last3) / len(last3)
        adbs = [m.avg_daily_balance for m in last3 if m.avg_daily_balance is not None]
        ctx.adb = sum(adbs) / len(adbs) if adbs else None
    elif it.avg_monthly_deposits:
        ctx.tmr = it.avg_monthly_deposits * 0.8
    elif case.financials.tax_returns:
        gr = case.financials.tax_returns[-1].gross_receipts
        ctx.tmr = gr / 12 if gr else None
    elif it.revenue_last_year:
        ctx.tmr = it.revenue_last_year * 0.8 / 12
    if ctx.adb is None and it.avg_30day_balance:
        ctx.adb = it.avg_30day_balance
    if it.personal_income:
        ctx.income = it.personal_income * 0.8  # unverified haircut (F-23)
    if case.financials.tax_returns:
        t = sorted(case.financials.tax_returns, key=lambda r: r.year)[-1]
        if t.net_income is not None:
            ctx.ebitda = t.net_income + (t.interest or 0) + (t.depreciation or 0) + (t.amortization or 0)
    for d in it.debts:
        if d.payment:
            mult = {"daily": 21.67 * 12, "weekly": 4.33 * 12}.get(d.frequency, 12)
            ctx.existing_ads += d.payment * mult
        if d.kind.upper() in ("MCA", "REVENUE-BASED FINANCING") or d.frequency in ("daily", "weekly"):
            ctx.positions += 1
    return ctx


def _fit(code: str, ctx: Ctx) -> ProductFit:
    return ProductFit(code=code, name=PRODUCTS[code], fit="", in_goal=code in ctx.goal)


def _finish(p: ProductFit, hard: list[str], soft_cap: Optional[int], score: Optional[float], missing: list[str]) -> ProductFit:
    if missing:
        p.fit = "NEEDS INFORMATION"
        p.blockers = [f"Needed to assess: {m}" for m in missing] + hard
        p.range_low = p.range_high = None
        return p
    if score is not None:
        score = max(0, min(100, score))
        if soft_cap is not None:
            score = min(score, soft_cap)
        p.score = round(score)
    p.blockers = hard + p.blockers
    if hard:
        p.fit = "NOT YET"
        p.range_low = p.range_high = None
    elif p.score is not None and p.score >= 80:
        p.fit = "STRONG FIT"
    elif p.score is not None and p.score >= 65:
        p.fit = "POTENTIAL FIT"
    else:
        p.fit = "NOT YET" if (p.score or 0) < 50 else "POTENTIAL FIT — AFTER FIXES"
    return p


def _band(value, bands):
    for threshold, pts in bands:
        if value >= threshold:
            return pts
    return 0


def card_stack(ctx: Ctx, personal: bool = False) -> ProductFit:
    code = "PC" if personal else "BC"
    p = _fit(code, ctx)
    g = ctx.g
    if not g or g.mid_score is None:
        return _finish(p, [], None, None, ["a current 3-bureau FICO credit report"])
    hard, soft = [], None
    if g.mid_score < 660:
        hard.append(f"Middle score {g.mid_score} is below the 660 most card issuers need")
    elif g.mid_score < 680:
        soft = 64
        p.blockers.append("Middle score 660–679: fewer issuers approve")
    unpaid = [d for d in g.derogs if ("collection" in d.description or "chargeoff" in d.description) and "paid" not in d.description]
    if any(d.months_since is not None and d.months_since <= 24 for d in unpaid):
        hard.append("Unpaid collection or charge-off within 24 months")
    if g.lates_12m:
        hard.append("A 30-day or worse late payment within the last 12 months")
    if g.util_overall is not None and g.util_overall > C.UTIL_HIGH:
        soft = 64 if soft is None else min(soft, 64)
        p.blockers.append(f"Utilization {g.util_overall:.0%} — pay balances down below 10% before applying")
    worst_inq6 = max(g.inquiries_6m.values(), default=0)
    if worst_inq6 > 6 or max(g.inquiries_12m.values(), default=0) > 10:
        hard.append("Too many recent inquiries on at least one bureau")
    if g.n_primary_revolvers == 0:
        hard.append("No primary revolving account")
    if not personal and (g.oldest_months or 0) < 24:
        hard.append("Oldest primary account is under 2 years")
    if ctx.case.intake.personal_income is not None and ctx.case.intake.personal_income < 30000:
        hard.append("Individual income under $30,000")
    if not personal and ctx.case.intake.funding.willing_pg is False:
        hard.append("Business cards require a personal guarantee")
    if ctx.case.consumer_credit and ctx.case.consumer_credit[0].freeze_bureaus:
        soft = 64 if soft is None else min(soft, 64)
        p.blockers.append("A security freeze must be lifted temporarily before applying")

    s = _band(g.mid_score, [(760, 20), (740, 18), (720, 15), (700, 11), (680, 7), (660, 3)])
    u = g.util_overall
    s += 9 if u == 0 else _band(-(u or 0), [(-0.05, 12), (-0.09, 11), (-0.19, 8), (-0.29, 5), (-0.49, 2)]) if u is not None else 6
    s += _band(-(g.util_max_card or 0), [(-0.29, 5), (-0.49, 3), (-0.89, 1)]) if g.util_max_card is not None else 2.5
    s += {0: 8, 1: 7, 2: 5, 3: 3}.get(worst_inq6, 1 if worst_inq6 <= 6 else 0)
    w12 = max(g.inquiries_12m.values(), default=0)
    s += 4 if w12 <= 2 else 2 if w12 <= 4 else 0
    s += 3 if max(g.inquiries_24m.values(), default=0) <= 4 else 1 if max(g.inquiries_24m.values(), default=0) <= 8 else 0
    s += {0: 4, 1: 3, 2: 1}.get(g.new_accounts_6m, 0) + (3 if g.new_accounts_12m <= 1 else 2 if g.new_accounts_12m <= 3 else 0)
    s += 3 if g.new_accounts_24m_all <= 2 else 2 if g.new_accounts_24m_all <= 4 else 0
    hl = g.highest_limit or 0
    s += _band(hl, [(25000, 12), (15000, 10), (10000, 8), (5000, 5), (2000, 2)])
    s += _band(g.n_primary_revolvers, [(5, 5), (3, 4), (2, 2), (1, 1)])
    s += _band(g.oldest_months or 0, [(120, 5), (60, 4), (36, 3), (24, 1)])
    s += _band(g.aaoa_months or 0, [(84, 4), (48, 3), (24, 2), (12, 1)])
    s += 6 if not g.lates_24m else 1
    s += 3 if g.derog_load == 0 else 2 if g.derog_load < 20 else 1 if g.derog_load < 40 else 0
    inc = ctx.case.intake.personal_income or 0
    s += _band(inc, [(150000, 3), (100000, 2.5), (60000, 2), (40000, 1)])
    if inc == 0:
        s += 1.5

    # Range (RULEBOOK R5 / §6.1)
    if not hard and hl:
        m = 0.8 if g.mid_score >= 740 else 0.6 if g.mid_score >= 720 else 0.45 if g.mid_score >= 700 else 0.3 if g.mid_score >= 680 else 0.2
        n = 5 if s >= 80 else 3 if s >= 65 else 2 if s >= 50 else 1
        n -= (worst_inq6 > 2) + (g.new_accounts_12m >= 3) + (hl < 5000)
        n = max(1, min(n, 3) if personal else n)
        caps = [C.STACK_MAX_MULTIPLE_HL * hl, C.STACK_ABSOLUTE_CAP]
        if ctx.income:
            caps.append(C.STACK_MAX_INCOME_SHARE * ctx.income)
            gmi = ctx.income / 12
            pti = (0.45 * gmi - (ctx.case.intake.housing_payment or 0) - g.monthly_debt) / 0.015
            caps.append(max(0.0, pti))
        cap = min(caps)
        exp_ = min(hl * m * n, cap)
        cons = min(hl * m * max(n - 2, 1), cap)
        if personal:
            exp_, cons = exp_ * 0.8, cons * 0.8
        if hl < 2000 or g.n_primary_revolvers < 3:
            cons, exp_ = 3000, 8000
        p.range_low, p.range_high = round_down(cons), round_down(exp_)
        if p.range_high < 5000:
            soft = 64 if soft is None else min(soft, 64)
            p.blockers.append("Expected amount is too small to justify the inquiries yet")
        p.range_confidence = "Medium" if not ctx.case.intake.personal_income else "Medium" if not g.fico_available else "Medium"
        if g.report_age_days is not None and g.report_age_days > C.CONSUMER_REPORT_SUPPRESS_DAYS:
            p.range_low = p.range_high = None
    p.cost_note = "Personal liability; 0% promotional rates typically end after 12–21 months, then about 20–30% APR."
    if hl:
        p.reasons.append(f"Highest primary card limit ${hl:,.0f}; issuers anchor new limits on it")
    if g.util_overall is not None:
        p.reasons.append(f"Revolving utilization {g.util_overall:.1%}")
    return _finish(p, hard, soft, s, [])


def personal_loan(ctx: Ctx) -> ProductFit:
    p = _fit("PL", ctx)
    g = ctx.g
    if not g or g.mid_score is None or ctx.case.intake.personal_income is None:
        return _finish(p, [], None, None, [m for m, ok in (("a current FICO credit report", g and g.mid_score), ("individual income", ctx.case.intake.personal_income is not None)) if not ok])
    hard, soft = [], None
    if g.mid_score < 640:
        hard.append("Middle score below 640")
    elif g.mid_score < 660:
        soft = 64
    if (ctx.case.intake.personal_income or 0) < 36000:
        hard.append("Individual income under $36,000")
    gmi = (ctx.income or 0) / 12
    pay_max = 0.40 * gmi - (ctx.case.intake.housing_payment or 0) - g.monthly_debt
    if pay_max <= 0:
        hard.append("Debt-to-income would exceed 45% with a new payment")
    apr = 0.09 if g.mid_score >= 740 else 0.14 if g.mid_score >= 700 else 0.20 if g.mid_score >= 660 else 0.28
    if not hard:
        p.range_high = round_down(min(pv(apr, 60, pay_max), 0.35 * (ctx.income or 0), 50000))
        p.range_low = round_down(min(pv(apr, 36, pay_max), 0.25 * (ctx.income or 0)))
        p.range_confidence = "Medium"
    score = 50 + (g.mid_score - 660) * 0.5 - (g.dti or 0) * 40
    p.cost_note = f"Typical APR band for this score: about {apr:.0%}."
    return _finish(p, hard, soft, score, [])


def common_business_hard(ctx: Ctx, code: str) -> list[str]:
    it = ctx.case.intake
    h = []
    if it.tax_liens_or_judgments:
        h.append("Unresolved tax lien or judgment reported in intake")
    if it.funding.willing_pg is False and code in ("OL", "OT", "SBA", "MCA"):
        h.append("This product requires a personal guarantee")
    if not it.primary_bank:
        h.append("No business bank account in the legal name on file")
    return h


def online_loc(ctx: Ctx) -> ProductFit:
    p = _fit("OL", ctx)
    missing = [m for m, ok in (("time in business", ctx.tib_months is not None), ("monthly revenue / deposits", ctx.tmr), ("owner credit score", ctx.gf)) if not ok]
    if missing:
        return _finish(p, [], None, None, missing)
    hard, soft = common_business_hard(ctx, "OL"), None
    if ctx.tib_months < 6:
        hard.append("Under 6 months in business")
    elif ctx.tib_months < 12:
        soft = 79
    if ctx.tmr < 2500:
        hard.append("Monthly revenue under $2,500")
    elif ctx.tmr < 8333:
        soft = min(soft or 79, 79)
    if ctx.gf < 600:
        hard.append("Owner credit score below 600")
    elif ctx.gf < 625:
        soft = 64
    if ctx.positions >= 2:
        hard.append("Two or more daily/weekly-debit financings open")
    if ctx.nsf_month and ctx.nsf_month > 5:
        soft = 64
    k_lo, k_hi = 0.5, 1.0
    line_hi = ctx.tmr * k_hi
    pbr_room = 0.20 * ctx.tmr - ctx.existing_ads / 12
    line_cap = max(0.0, pbr_room / 0.05)  # ~5% of line per month on full draw
    line_hi = min(line_hi, line_cap) if pbr_room > 0 else 0
    if line_hi <= 0 and not hard:
        hard.append("Existing payments already use the affordable share of monthly revenue")
    if not hard:
        p.range_low, p.range_high = round_down(min(ctx.tmr * k_lo, line_hi)), round_down(line_hi)
        p.range_confidence = "High" if ctx.tmr_verified else "Low"
    score = 50 + min(ctx.tib_months, 36) / 36 * 20 + min(ctx.tmr / 50000, 1) * 15 + (ctx.gf - 600) / 200 * 15
    p.reasons.append(f"About {ctx.tib_months} months in business; monthly revenue basis ${ctx.tmr:,.0f}{'' if ctx.tmr_verified else ' (self-reported, reduced 20%)'}")
    p.cost_note = "Online lines typically cost more than bank lines; draws often repay weekly over 6–24 months."
    return _finish(p, hard, soft, score, [])


def dscr_value(ctx: Ctx, proposed_annual: float) -> Optional[float]:
    if ctx.ebitda is None:
        return None
    total = ctx.existing_ads + proposed_annual
    return ctx.ebitda / total if total else None


def bank_lane(ctx: Ctx, code: str) -> ProductFit:
    p = _fit(code, ctx)
    it = ctx.case.intake
    missing = []
    if ctx.gf is None:
        missing.append("owner credit score")
    if ctx.ebitda is None:
        missing.append("filed business tax returns (to compute debt service coverage)")
    if ctx.tib_months is None:
        missing.append("time in business")
    req = it.funding.amount_requested or 0
    if missing:
        p = _finish(p, [], None, None, missing)
        if ctx.ebitda is None and ctx.gf is not None:
            p.reasons.append("Banks and the SBA lend on documented cash flow from tax returns; without returns no range is shown.")
        return p
    hard, soft = common_business_hard(ctx, code), None
    floor = {"SBA": 620, "BT": 660, "BL": 660}.get(code, 640)
    if ctx.gf < floor:
        hard.append(f"Owner middle score {ctx.gf} below the typical lender minimum of {floor}" + (" (lender overlay, not an SBA rule)" if code == "SBA" else ""))
    elif code == "SBA" and ctx.gf < 680:
        soft = 79
    if code in ("BT", "BL") and ctx.tib_months < 24:
        hard.append("Under 2 years in business (route to SBA, equipment or online lenders)")
    if code == "SBA":
        if it.sba_citizenship_ok is False:
            hard.append("SBA requires all owners to be U.S. citizens or nationals residing in the U.S. (effective 3/1/2026)")
        if it.federal_debt_delinquent:
            hard.append("Delinquent federal debt reported in intake")
    g = ctx.g
    if g and any("bankruptcy open" in d.description for d in g.derogs):
        hard.append("Open bankruptcy")
    rate = {"SBA": PRIME_RATE + 0.03, "BT": PRIME_RATE + 0.02, "BL": PRIME_RATE + 0.015}[code]
    term = {"SBA": 120, "BT": 60, "BL": 12}[code]
    target = 1.15 if code == "SBA" else 1.25
    proposed = pmt(rate, term, req) * 12 if req else 0
    d = dscr_value(ctx, proposed)
    if d is not None:
        p.reasons.append(f"Debt service coverage with the requested amount ≈ {d:.2f}x (target {target:.2f}x)")
        floor_d = 1.10 if code == "SBA" else 1.00
        if d < floor_d:
            hard.append(f"Cash flow covers debt payments only {d:.2f}x — below {floor_d:.2f}x")
        elif d < target:
            soft = min(soft or 64, 64)
    max_pay = ctx.ebitda / target - ctx.existing_ads
    if max_pay > 0 and not hard:
        amt = pv(rate, term, max_pay / 12)
        if code == "BL":
            amt = min(amt, (ctx.tmr or 0) * 1.2)
        caps = {"SBA": 5_000_000, "BT": 1_000_000, "BL": 500_000}
        amt = min(amt, caps[code])
        p.range_low, p.range_high = round_down(amt * 0.7), round_down(amt)
        p.range_confidence = "Medium"
    score = 40 + (ctx.gf - 600) / 200 * 25 + (min(d, 2.0) - 1.0) * 30 if d is not None else 50
    score += min(ctx.tib_months, 60) / 60 * 10
    p.cost_note = {"SBA": "Lowest typical cost; longest process (often 30–90 days); SBA rules on use of proceeds apply.",
                   "BT": "Low cost; banks lend on tax-return cash flow and often want collateral.",
                   "BL": "Low cost revolving line; usually requires 2+ years in business and a deposit relationship."}[code]
    if code == "SBA":
        p.reasons.append("SBA eligibility also depends on use of proceeds, ownership and the lender's own overlays.")
    return _finish(p, hard, soft, score, [])


def online_term(ctx: Ctx) -> ProductFit:
    p = _fit("OT", ctx)
    missing = [m for m, ok in (("time in business", ctx.tib_months is not None), ("revenue", ctx.tmr), ("owner credit score", ctx.gf)) if not ok]
    if missing:
        return _finish(p, [], None, None, missing)
    hard, soft = common_business_hard(ctx, "OT"), None
    if ctx.tib_months < 12:
        hard.append("Under 12 months in business")
    if ctx.tmr * 12 < 100000:
        hard.append("Annual revenue under about $100,000")
    if ctx.gf < 600:
        hard.append("Owner credit score below 600")
    if ctx.positions >= 2:
        hard.append("Two or more daily/weekly-debit financings open")
    if not hard:
        room = 0.15 * ctx.tmr - ctx.existing_ads / 12
        amt = min(ctx.tmr * 1.5, pv(0.30, 18, room)) if room > 0 else 0
        if amt <= 0:
            hard.append("Existing payments already use the affordable share of monthly revenue")
        else:
            p.range_low, p.range_high = round_down(amt * 0.6), round_down(amt)
            p.range_confidence = "High" if ctx.tmr_verified else "Low"
    score = 50 + min(ctx.tib_months, 36) / 36 * 20 + (ctx.gf - 600) / 200 * 20
    p.cost_note = "Faster than banks but costlier; often weekly or daily payments."
    return _finish(p, hard, soft, score, [])


def equipment(ctx: Ctx) -> ProductFit:
    p = _fit("EQ", ctx)
    if ctx.gf is None or ctx.tib_months is None:
        return _finish(p, [], None, None, [m for m, ok in (("owner credit score", ctx.gf), ("time in business", ctx.tib_months is not None)) if not ok])
    hard, soft = [], None
    if ctx.gf < 550:
        hard.append("Owner credit score below 550")
    elif ctx.gf < 600:
        soft = 79
    if ctx.tib_months < 6:
        hard.append("Under 6 months in business")
    elif ctx.tib_months < 24:
        soft = min(soft or 79, 79)
        p.blockers.append("Under 2 years: non-bank lessors, typically 10–30% down")
    score = 55 + (ctx.gf - 550) / 250 * 30 + min(ctx.tib_months, 36) / 36 * 15
    p.reasons.append("The equipment itself is the collateral; amount depends on the quote (not yet provided).")
    p.cost_note = "Rates depend on lane (bank/captive vs non-bank) and equipment age."
    return _finish(p, hard, soft, score, [])


def factoring(ctx: Ctx) -> ProductFit:
    p = _fit("FAC", ctx)
    f = ctx.case.financials
    if f.ar_total is None:
        return _finish(p, [], None, None, ["accounts receivable aging (business-to-business invoices)"])
    hard = []
    if f.ar_total and f.ar_over_90 and f.ar_over_90 / f.ar_total > 0.5:
        hard.append("More than half of receivables are over 90 days")
    if not hard:
        eligible = f.ar_total - (f.ar_over_90 or 0)
        p.range_low, p.range_high = round_down(eligible * 0.70), round_down(eligible * 0.85)
        p.range_confidence = "Medium"
    score = 75 - ((f.dso_days or 45) - 30) * 0.3
    p.cost_note = "Typically 1–5% of invoice value per 30 days; customers usually pay the factor directly."
    return _finish(p, hard, None, score, [])


def mca(ctx: Ctx, others: list[ProductFit]) -> ProductFit:
    p = _fit("MCA", ctx)
    if ctx.tmr is None or ctx.tib_months is None:
        return _finish(p, [], None, None, [m for m, ok in (("monthly deposits", ctx.tmr), ("time in business", ctx.tib_months is not None)) if not ok])
    hard, soft = [], None
    if ctx.tib_months < 4:
        hard.append("Under 4 months in business")
    if ctx.tmr < 10000:
        hard.append("Monthly deposits under $10,000")
    if ctx.gf is not None and ctx.gf < 500:
        hard.append("Owner credit score below 500")
    if ctx.positions >= 4:
        hard.append("Four or more advances already open")
    if ctx.existing_ads / 12 > 0.35 * ctx.tmr:
        hard.append("Existing debits already exceed 35% of monthly revenue")
    req = ctx.case.intake.funding.amount_requested or 0
    cheaper = [o for o in others if o.code != "MCA" and o.range_high and req and o.range_high >= 0.5 * req]
    if not hard:
        exp_ = min(ctx.tmr * 1.0, max(0.0, (0.20 * ctx.tmr - ctx.existing_ads / 12) * 6 / 1.35))
        cons = min(ctx.tmr * 0.5, max(0.0, (0.15 * ctx.tmr - ctx.existing_ads / 12) * 6 / 1.35))
        p.range_low, p.range_high = round_down(cons), round_down(exp_)
        p.range_confidence = "High" if ctx.tmr_verified else "Low"
    p.cost_note = ("Most expensive option: a 1.35 factor repaid over about 6 months is roughly 100–140% estimated APR. "
                   "Request the state-required cost disclosure before signing.")
    score = 60
    p = _finish(p, hard, soft, score, [])
    if not hard and (cheaper or ctx.positions):
        p.fit = "NOT RECOMMENDED"
        p.blockers.append("Cheaper options cover at least half of the request" if cheaper else "Stacking another advance on an existing one is high-risk")
    elif not hard:
        p.fit = "LAST RESORT"
    return p


def evaluate(case: Case, g: Optional[GuarantorResult], audit_date: date) -> list[ProductFit]:
    goal = set(case.intake.funding.product_types)
    not_sure = not goal or "NOT_SURE" in goal
    ctx = build_ctx(case, g, audit_date, goal)
    business = case.intake.funding.for_whom != "personal"
    out: list[ProductFit] = []
    if business or "BC" in goal or not_sure:
        out.append(card_stack(ctx))
    if "PC" in goal or not business:
        out.append(card_stack(ctx, personal=True))
    if "PL" in goal or not business:
        out.append(personal_loan(ctx))
    if business:
        for code in ("BL", "BT", "SBA"):
            out.append(bank_lane(ctx, code))
        out.append(online_loc(ctx))
        out.append(online_term(ctx))
        if "EQ" in goal or not_sure:
            out.append(equipment(ctx))
        if "FAC" in goal or case.financials.ar_total:
            out.append(factoring(ctx))
        out.append(mca(ctx, out))
    for code in ("DSCR", "FF"):
        if code in goal:
            p = _fit(code, ctx)
            out.append(_finish(p, [], None, None, ["property details (price, rent or ARV, down payment, reserves)"]))
    order = {"STRONG FIT": 0, "POTENTIAL FIT": 1, "POTENTIAL FIT — AFTER FIXES": 2, "NEEDS INFORMATION": 3, "NOT YET": 4, "LAST RESORT": 5, "NOT RECOMMENDED": 6}
    return sorted(out, key=lambda p: (not p.in_goal and not not_sure, order.get(p.fit, 9), COST_RANK.get(p.code, 9)))
