"""Personal guarantor analysis (RULEBOOK §1–§4; r3 identity §4 guarantor rating)."""
from __future__ import annotations

from datetime import date
from statistics import median
from typing import Optional

from fra import config as C
from fra.engine.results import DerogItem, GuarantorResult
from fra.models import Bureau, ConsumerCredit, Intake, Status, Tradeline


def months_between(earlier: date, later: date) -> int:
    return (later.year - earlier.year) * 12 + (later.month - earlier.month) - (1 if later.day < earlier.day else 0)


def decay(months: Optional[int], steps) -> float:
    if months is None:
        return 1.0
    for upper, mult in steps:
        if months < upper:
            return mult
    return 0.0


def mid_score(values: list[int]) -> Optional[int]:
    """F-02: middle of three, lower of two, the single score if one."""
    if not values:
        return None
    vals = sorted(values)
    if len(vals) == 2:
        return vals[0]
    if len(vals) >= 3:
        return int(median(vals[:3])) if len(vals) == 3 else vals[len(vals) // 2]
    return vals[0]


def _is_revolver(t: Tradeline) -> bool:
    return t.account_type == "revolving" and not t.closed


def _primary(t: Tradeline) -> bool:
    return t.owner_type in ("primary", "joint")


def _derog_class(t: Tradeline) -> Optional[str]:
    s = t.status
    if s == "collection":
        if t.medical:
            return "medical_unpaid_500" if (t.balance or 0) >= 500 else "medical_small_or_paid"
        if (t.original_amount or t.balance or 0) < 100:
            return "collection_small"
        return "collection"
    if s == "paid_collection":
        return "medical_small_or_paid" if t.medical else "paid_collection"
    if s in ("chargeoff", "paid_chargeoff", "repo", "foreclosure"):
        return s
    return None


def analyze_guarantor(cc: ConsumerCredit, intake: Intake, audit_date: date) -> GuarantorResult:
    g = GuarantorResult(person=cc.person, report_date=cc.report_date)
    if cc.report_date:
        g.report_age_days = (audit_date - cc.report_date).days

    # Scores (F-01, F-02, F-05)
    fico = [s for s in cc.scores if s.fico_eligible]
    g.scores = [(s.bureau.value, s.value, s.model) for s in cc.scores]
    g.fico_available = bool(fico)
    use = fico or cc.scores
    g.mid_score = mid_score([s.value for s in use])
    if len(use) >= 2:
        g.bureau_spread = max(s.value for s in use) - min(s.value for s in use)

    # Utilization and depth (F-07..F-13), primary + joint only
    revs = [t for t in cc.tradelines if _is_revolver(t) and t.credit_limit]
    prim_revs = [t for t in revs if _primary(t)]
    g.total_revolving_limit = sum(t.credit_limit or 0 for t in prim_revs)
    g.total_revolving_balance = sum(t.balance or 0 for t in prim_revs)
    if g.total_revolving_limit:
        g.util_overall = g.total_revolving_balance / g.total_revolving_limit
        g.util_max_card = max((t.balance or 0) / t.credit_limit for t in prim_revs)
    all_lim = sum(t.credit_limit or 0 for t in revs)
    if all_lim:
        g.util_as_reported = sum(t.balance or 0 for t in revs) / all_lim
    g.highest_limit = max((t.credit_limit for t in prim_revs), default=None)
    g.n_primary_revolvers = len(prim_revs)
    prim = [t for t in cc.tradelines if _primary(t) and t.open_date and t.account_type != "collection"]
    if prim:
        ages = [months_between(t.open_date, audit_date) for t in prim]
        g.oldest_months = max(ages)
        g.aaoa_months = round(sum(ages) / len(ages))

    # AU-heavy (F-36)
    au_lim = sum(t.credit_limit or 0 for t in revs if t.owner_type == "au")
    if all_lim and au_lim / all_lim >= C.AU_HEAVY_LIMIT_SHARE:
        g.au_heavy = True
    oldest_any = max(
        (t for t in cc.tradelines if t.open_date and t.account_type != "collection"),
        key=lambda t: months_between(t.open_date, audit_date), default=None)
    if oldest_any and oldest_any.owner_type == "au":
        g.au_heavy = True

    # Inquiries per bureau (F-15, raw counts)
    for b in Bureau:
        for window, target in ((6, g.inquiries_6m), (12, g.inquiries_12m), (24, g.inquiries_24m)):
            target[b.value] = sum(
                1 for q in cc.inquiries if q.bureau == b and months_between(q.inquiry_date, audit_date) < window)

    # New accounts (F-18)
    for t in cc.tradelines:
        if not t.open_date or t.account_type == "collection":
            continue
        m = months_between(t.open_date, audit_date)
        if _primary(t):
            g.new_accounts_6m += m < 6
            g.new_accounts_12m += m < 12
        g.new_accounts_24m_all += m < 24

    # Lates and derogatories (F-19..F-21)
    for t in cc.tradelines:
        if t.owner_type == "au":
            continue
        if t.last_late_date:
            m = months_between(t.last_late_date, audit_date)
            if m < 12:
                g.lates_12m += 1
            if m < 24:
                g.lates_24m += 1
                g.recent_lates.append(f"{t.creditor}: {t.worst_late or 30}-day late, {t.last_late_date:%m/%Y}")
            base = C.DEROG_BASE.get(f"late{min(t.worst_late or 30, 120)}", 20)
            sev = base * decay(m, C.DECAY_STEPS)
            if sev > 0:
                g.derogs.append(DerogItem(description=f"{t.worst_late or 30}-day late — {t.creditor}", severity=round(sev, 1), months_since=m))
        cls = _derog_class(t)
        if cls:
            if cls.startswith(("collection", "medical", "paid_collection")):
                g.collections += 1
            ref = t.dofd or t.last_reported
            m = months_between(ref, audit_date) if ref else None
            sev = C.DEROG_BASE[cls] * decay(m, C.DECAY_STEPS)
            g.derogs.append(DerogItem(description=f"{cls.replace('_', ' ')} — {t.creditor}", severity=round(sev, 1), months_since=m))
    for pr in cc.public_records:
        g.public_records += 1
        kind = pr.kind
        if kind.startswith("bankruptcy") and pr.status in ("filed", "open", ""):
            kind = "bankruptcy_open"
        elif kind.startswith("bankruptcy") and pr.status == "dismissed":
            kind = "bankruptcy_dismissed"
        ref = pr.status_date or pr.filed
        m = months_between(ref, audit_date) if ref else None
        steps = C.BK_DECAY_STEPS if kind.startswith("bankruptcy") else C.DECAY_STEPS
        mult = 1.0 if kind == "bankruptcy_open" else decay(m, steps)
        g.derogs.append(DerogItem(description=kind.replace("_", " "), severity=round(C.DEROG_BASE.get(kind, 70) * mult, 1), months_since=m))
    sev = sorted((d.severity for d in g.derogs), reverse=True)
    if sev:
        g.derog_load = min(100.0, sev[0] + 0.5 * (sev[1] if len(sev) > 1 else 0) + 0.25 * sum(sev[2:]))

    # Monthly debt and DTI (F-22, F-24)
    for t in cc.tradelines:
        if t.owner_type == "au" or t.closed or t.account_type == "collection":
            continue
        bal = t.balance or 0
        if t.account_type == "revolving":
            if bal > 0:
                g.monthly_debt += max(t.payment or 0, 0.03 * bal, 25)
        else:
            g.monthly_debt += t.payment or 0
    if intake.personal_income:
        gmi = intake.personal_income / 12
        g.dti = (g.monthly_debt + (intake.housing_payment or 0)) / gmi if gmi else None

    # Identity gates (RULEBOOK §4) — the analyst records identity issues; the tool never infers origin
    if any(f.lower().startswith(("different ssn", "invalid ssn", "deceased", "ofac", "605b")) for f in cc.identity_flags):
        g.identity_gate = "Block"
    elif cc.identity_flags:
        g.identity_gate = "Review"

    # Flags (advisory review items)
    if g.bureau_spread is not None and g.bureau_spread >= C.BUREAU_SPREAD_REVIEW:
        g.flags.append(f"{g.bureau_spread}-point score gap between bureaus — confirm each bureau's data before applying.")
    heavy = [b for b, n in g.inquiries_6m.items() if n >= C.INQUIRY_ADVISORY_6M]
    if heavy:
        g.flags.append(f"Recent inquiry volume on {', '.join(heavy)} — {', '.join(str(g.inquiries_6m[b]) for b in heavy)} hard inquiries in 6 months.")
    if g.lates_12m:
        g.flags.append(f"{g.lates_12m} account(s) with a late payment in the last 12 months.")
    if g.util_overall is not None and g.util_overall > C.UTIL_FAIR:
        g.flags.append(f"Revolving utilization {g.util_overall:.0%} — above the 30% level most underwriters prefer.")
    if g.au_heavy:
        g.flags.append("Authorized-user accounts make up a large share of the credit file; lenders who review manually discount them.")
    if cc.fraud_alert:
        g.flags.append("Fraud alert on file — expect identity verification and possible delays. Keep the alert if the fraud was real.")
    if cc.freeze_bureaus:
        g.flags.append(f"Security freeze on {', '.join(b.value for b in cc.freeze_bureaus)} — must be lifted temporarily before applying to lenders that pull that bureau.")
    if len(set(a.strip().upper() for a in cc.addresses)) > 3:
        g.flags.append("Several different addresses are reported across bureaus — align the current address.")
    if not g.fico_available and cc.scores:
        g.flags.append("No FICO score on file (VantageScore only). Lenders mostly use FICO; obtain a FICO 3-bureau report.")
    if g.report_age_days is not None and g.report_age_days > C.CONSUMER_REPORT_STALE_DAYS:
        g.flags.append(f"Credit report is {g.report_age_days} days old — re-pull a current report before any card application.")

    # Strengths
    if g.mid_score and g.mid_score >= 720:
        g.strengths.append(f"Middle credit score {g.mid_score}")
    if g.util_overall is not None and g.util_overall <= C.UTIL_GOOD:
        g.strengths.append(f"Low revolving utilization ({g.util_overall:.1%})")
    if not g.collections and not g.public_records and not any(d.severity >= 35 for d in g.derogs):
        g.strengths.append("No collections, charge-offs or public records")
    if g.oldest_months and g.oldest_months >= 120:
        g.strengths.append(f"Credit history of {g.oldest_months // 12} years")
    if g.highest_limit and g.highest_limit >= 15000:
        g.strengths.append(f"Highest primary card limit ${g.highest_limit:,.0f}")

    # Area status (r3 identity §4 guarantor specifics)
    gf = g.mid_score
    if g.identity_gate == "Block" or (gf is not None and gf < C.GUARANTOR_AR_SCORE) or any(
            p.kind.startswith("bankruptcy") and p.status in ("filed", "open", "") for p in cc.public_records):
        g.status = Status.AR
    elif gf is None:
        g.status = Status.PEND
    elif gf < C.GUARANTOR_PASS_SCORE or g.flags or g.identity_gate == "Review":
        g.status = Status.NI
    else:
        g.status = Status.PASS

    util_txt = f"revolving utilization near {g.util_overall:.1%}" if g.util_overall is not None else "utilization not determined"
    g.one_line = f"Middle score {gf if gf else 'not available'}, {util_txt}, " + (
        "no collections or public records" if not (g.collections or g.public_records) else
        f"{g.collections} collection(s), {g.public_records} public record(s)")
    return g
