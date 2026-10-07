"""Commercial bureau cards and points 11, 12, 13, 18, 19 (r3 commercial bureaus §2–§5)."""
from __future__ import annotations

from datetime import date
from typing import Optional

from fra import config as C
from fra.content import BUREAU_CHANNELS, BUREAU_EXPLAIN
from fra.engine.identity import compare_address, compare_entity, compare_names, norm_digits
from fra.engine.results import BureauCard, Metric
from fra.models import Case, CommercialBureau, CommercialReport, Status

BANK_LANE = {"BL", "BT", "SBA", "EQB", "OL"}
LIEN_PRODUCTS = {"BL", "BT", "SBA", "EQB", "EQA", "FAC", "OL"}


def fresh(rep: Optional[CommercialReport], audit_date: date) -> bool:
    return bool(rep and rep.report_date and (audit_date - rep.report_date).days <= C.COMMERCIAL_REPORT_MAX_AGE_DAYS)


def get_report(case: Case, bureau: CommercialBureau) -> Optional[CommercialReport]:
    reps = [r for r in case.commercial_reports if r.bureau == bureau]
    return max(reps, key=lambda r: r.report_date or date.min) if reps else None


def score(rep: CommercialReport, *names: str):
    for s in rep.scores:
        if any(n.lower() in s.name.lower() for n in names):
            return s
    return None


def _class_num(risk_class: str) -> Optional[int]:
    digits = [int(ch) for ch in risk_class if ch.isdigit()]
    return digits[0] if digits else None


def identity_defects(rep: CommercialReport, case: Case, master_name: str, master_type: str, master_addr, master_ein: str):
    """Return (rows, critical, material) comparing a bureau's identity block to the master record."""
    idn = rep.identity
    rows, critical, material = [], [], []

    def add(field, shown, assessment, crit):
        rows.append((field, shown or "Blank", assessment))
        if assessment not in ("MATCH", "FORMAT VARIANT", "—"):
            (critical if crit else material).append(f"{field}: {assessment.lower()} ({shown or 'blank'})")

    if master_name:
        out = compare_names(master_name, idn.legal_name or "")
        add("Legal name", idn.legal_name, {"MATCH": "MATCH", "EQUIVALENT": "FORMAT VARIANT"}.get(out, out), True)
    if master_type:
        out = compare_entity(master_type, idn.entity_type or "")
        add("Entity type", idn.entity_type, {"MATCH": "MATCH", "EQUIVALENT": "FORMAT VARIANT"}.get(out, out), True)
    if master_addr is not None:
        out = compare_address(master_addr, idn.address) if idn.address else "BLANK"
        shown = idn.address.one_line() if idn.address else ""
        add("Address", shown, {"MATCH": "MATCH", "EQUIVALENT": "FORMAT VARIANT", "VARIANT": "VERIFY", "CONFLICT": "STALE"}.get(out, out), True)
    if master_ein and idn.ein:
        add("Tax ID", f"…{norm_digits(idn.ein)[-4:]}", "MATCH" if norm_digits(idn.ein) == norm_digits(master_ein) else "CONFLICT", True)
    for field, val in (("Phone", idn.phone), ("NAICS", idn.naics), ("SIC", idn.sic), ("Website", idn.website)):
        add(field, val, "MATCH" if val else "BLANK", False)
    rev_doc = min((t.gross_receipts for t in case.financials.tax_returns[-1:] if t.gross_receipts), default=None)
    if idn.revenue is not None or rev_doc:
        if rev_doc and (idn.revenue or 0) < rev_doc * (1 - C.REVENUE_MISMATCH_PCT):
            add("Sales revenue", f"${idn.revenue:,.0f}" if idn.revenue else "", "UNDERSTATED", False)
        else:
            add("Sales revenue", f"${idn.revenue:,.0f}" if idn.revenue else "", "MATCH" if idn.revenue else "BLANK", False)
    if idn.years_in_business is not None:
        add("Years in business", f"{idn.years_in_business:g}", "UNDERSTATED" if idn.years_in_business == 0 else "MATCH", False)
    if idn.employees is not None:
        add("Employees", str(idn.employees), "UNDERSTATED" if idn.employees == 0 else "MATCH", False)
    return rows, critical, material


def build_cards(case: Case, audit_date: date, master_name: str, master_type: str, master_addr, master_ein: str) -> list[BureauCard]:
    cards = []
    for bureau in (CommercialBureau.EXPERIAN, CommercialBureau.DNB, CommercialBureau.EQUIFAX, CommercialBureau.LEXISNEXIS):
        rep = get_report(case, bureau)
        card = BureauCard(bureau=bureau.value, status=Status.PEND, plain=BUREAU_EXPLAIN.get(bureau.value, ""),
                          channel=BUREAU_CHANNELS.get(bureau.value, ""))
        if not rep:
            card.metrics = [Metric(label="Status", value="Not obtained", sub="Report to be ordered")]
            card.corrections = [f"Obtain the {bureau.value} report."]
            cards.append(card)
            continue
        card.file_id = f"…{rep.file_id[-4:]}" if rep.file_id else ""
        card.report_date = rep.report_date
        if not rep.file_found or rep.insufficient_data:
            card.metrics = [Metric(label="Finding", value="INSUFFICIENT DATA", sub="No score or conclusion generated")]
            card.corrections = ["Result was too thin to score — not a negative finding. Build identity first, then reporting accounts."]
            cards.append(card)
            continue

        crit_bad, nice = [], []
        if bureau == CommercialBureau.EXPERIAN:
            s = score(rep, "intelliscore")
            fsr = score(rep, "stability", "fsr")
            if s and s.value is not None:
                v3 = s.value > 100
                card.metrics.append(Metric(label=f"Intelliscore Plus {'V3' if v3 else 'V2'}", value=f"{s.value:g}", sub=f"Scale {'300–850' if v3 else '1–100'}"))
                if (not v3 and s.value <= 25) or (v3 and s.value <= 660):
                    crit_bad.append("Intelliscore in the high-risk band")
                elif (not v3 and s.value < C.INTELLISCORE_V2_PASS) or (v3 and s.value < C.INTELLISCORE_V3_PASS):
                    nice.append("Intelliscore below the low-risk band")
            if fsr and fsr.value is not None:
                card.metrics.append(Metric(label="Financial Stability", value=f"{fsr.value:g}", sub=f"Risk — {fsr.risk_class}" if fsr.risk_class else ""))
        elif bureau == CommercialBureau.DNB:
            p = score(rep, "paydex")
            fs = score(rep, "failure", "stress")
            dq = score(rep, "delinquency")
            card.metrics.append(Metric(label="PAYDEX", value=f"{p.value:g}" if p and p.value is not None else "—",
                                       sub="Not generated" if not p or p.value is None else "80 = pays on time"))
            if p and p.value is not None:
                if p.value < 70:
                    crit_bad.append("PAYDEX below 70")
                elif p.value < C.PAYDEX_PASS:
                    nice.append("PAYDEX below 80")
            else:
                nice.append("No PAYDEX generated yet")
            for sc, label in ((fs, "Failure score"), (dq, "Delinquency score")):
                if sc:
                    card.metrics.append(Metric(label=label, value=f"{sc.value:g}" if sc.value is not None else "—", sub=sc.risk_class))
                    cls = _class_num(sc.risk_class)
                    if cls and cls >= 4:
                        crit_bad.append(f"{label} class {cls}")
                    elif cls and cls > C.DNB_CLASS_PASS:
                        nice.append(f"{label} class {cls}")
        elif bureau == CommercialBureau.EQUIFAX:
            s = score(rep, "credit risk", "bcrs")
            pi = score(rep, "payment index")
            if s and s.value is not None:
                card.metrics.append(Metric(label="Business Credit Risk", value=f"{s.value:g}", sub="Scale 101–992"))
                if s.value < 450:
                    crit_bad.append("Equifax risk score below 450")
                elif s.value < C.EQUIFAX_BUSINESS_PASS:
                    nice.append("Equifax risk score below 556")
            if pi and pi.value is not None:
                card.metrics.append(Metric(label="Payment Index", value=f"{pi.value:g}", sub="90+ = paid as agreed"))
        else:
            card.metrics.append(Metric(label="Identities linked", value=str(1 + sum(1 for i in rep.internal_inconsistencies if "identity" in i.lower()))))

        if bureau != CommercialBureau.LEXISNEXIS:
            card.metrics.append(Metric(label="Reporting tradelines", value=str(len(rep.tradelines))))
            util = _util(rep)
            if util is not None:
                card.metrics.append(Metric(label="Utilization", value=f"{util:.0%}"))
            card.metrics.append(Metric(label="UCC filings", value=str(len(rep.ucc_filings))))

        rows, critical, material = identity_defects(rep, case, master_name, master_type, master_addr, master_ein)
        card.identity_rows = rows
        for c in critical + material:
            card.corrections.append(f"Correct {c} — submit with the supporting document through the channel below.")
        for i in rep.internal_inconsistencies:
            card.corrections.append(f"Internal inconsistency to verify: {i} If inaccurate, submit a supported dispute. Accurate information should not be disputed.")
        if rep.derogatories:
            crit_bad.extend(rep.derogatories)
        else:
            card.clean.append("No bankruptcies, judgments, liens or collections reported")
        if not rep.inquiries_count:
            card.clean.append("No commercial inquiries")
        stale = not fresh(rep, audit_date)
        if stale:
            card.corrections.insert(0, f"Report dated {rep.report_date:%m/%d/%Y} is older than 90 days — re-pull.")
        if crit_bad or critical:
            card.status = Status.AR
        elif stale:
            card.status = Status.PEND
        elif nice or material or not rep.tradelines:
            card.status = Status.NI
        else:
            card.status = Status.PASS
        cards.append(card)
    return cards


def _util(rep: CommercialReport) -> Optional[float]:
    hc = sum(t.high_credit or 0 for t in rep.tradelines if t.high_credit)
    bal = sum(t.balance or 0 for t in rep.tradelines if t.high_credit)
    return bal / hc if hc else None


def point_11(case: Case, cards: list[BureauCard], audit_date: date, goal: set[str]) -> tuple[Status, str, str, bool]:
    req = ["Experian Business", "Dun & Bradstreet"] + (["Equifax Business"] if goal & BANK_LANE else [])
    by = {c.bureau: c for c in cards}
    statuses = [by[b].status for b in req if b in by]
    insufficient = any(by[b].metrics and by[b].metrics[0].value == "INSUFFICIENT DATA" for b in req if b in by)
    parts, short = [], []
    for b in req + ["Equifax Business"]:
        c = by.get(b)
        if not c or (b == "Equifax Business" and b not in req and not c.report_date):
            continue
        if b in [p.split(":")[0] for p in parts]:
            continue
        m = ", ".join(f"{x.label} {x.value}" for x in c.metrics[:3])
        parts.append(f"{b}: {m}")
        first = c.metrics[0] if c.metrics else None
        if first and first.value in ("INSUFFICIENT DATA", "Not obtained"):
            short.append(f"{b.split(' ')[0]} {first.value.lower()}")
        elif b == "Dun & Bradstreet" and first and first.value == "—":
            short.append("no PAYDEX")
        elif first:
            short.append(f"{first.label.replace('Intelliscore Plus', 'Intelliscore')} {first.value}")
    one = "; ".join(short)
    if Status.AR in statuses:
        st = Status.AR
    elif Status.PEND in statuses:
        st = Status.PEND
    elif Status.NI in statuses:
        st = Status.NI
    else:
        st = Status.PASS
    found = "Each bureau was reviewed separately. " + ". ".join(parts) + "."
    return st, one, found, insufficient


def point_12(case: Case, audit_date: date) -> tuple[Status, str, str]:
    exp = get_report(case, CommercialBureau.EXPERIAN)
    dnb = get_report(case, CommercialBureau.DNB)
    if not (exp and fresh(exp, audit_date)) or not (dnb and fresh(dnb, audit_date)):
        return Status.PEND, "Experian and D&B reports needed to count reporting accounts", "One or both of the Experian and D&B reports are missing or older than 90 days, so reporting payment experiences cannot be counted."
    trades = [t for r in (exp, dnb, get_report(case, CommercialBureau.EQUIFAX)) if r for t in r.tradelines]
    n_exp, n_dnb, n_all = len(exp.tradelines), len(dnb.tradelines), len(trades)
    worst_dbt = max((t.dbt or 0 for t in trades), default=0)
    util = _util(exp)
    found = f"Experian shows {n_exp} reporting tradeline(s); D&B shows {n_dnb} payment experience(s)."
    if worst_dbt:
        found += f" The worst reported payment is {worst_dbt} days beyond terms."
    if util is not None:
        found += f" Commercial utilization at Experian is about {util:.0%}."
    if n_all <= 1 or worst_dbt > 60 or (util is not None and util >= 0.9 and len(exp.tradelines) >= 2):
        st = Status.AR
    elif n_exp >= C.TRADES_PASS_PER_BUREAU and n_dnb >= C.TRADES_PASS_PER_BUREAU and n_all >= C.TRADES_PASS_TOTAL and worst_dbt == 0 and (util is None or util < C.COMMERCIAL_UTIL_PASS):
        st = Status.PASS
    else:
        st = Status.NI if n_all > 1 else Status.AR
    one = f"{n_exp} tradeline(s) at Experian, {n_dnb} at D&B" + (f"; {worst_dbt} DBT reported" if worst_dbt else "")
    return st, one, found


def point_13(case: Case, audit_date: date) -> tuple[Status, str, str, bool]:
    rep = get_report(case, CommercialBureau.LEXISNEXIS)
    if not rep or not fresh(rep, audit_date):
        return Status.PEND, "File not yet obtained", "The LexisNexis business file has not been obtained for this audit.", False
    if not rep.file_found:
        return Status.PEND, "No record found", "LexisNexis returned no record for the business.", True
    issues = rep.internal_inconsistencies + rep.derogatories
    if issues:
        return Status.AR, issues[0], "LexisNexis shows: " + "; ".join(issues) + ".", False
    return Status.PASS, "One business identity; no unexplained records", "The LexisNexis file shows one business identity with no unexplained records.", False


def point_18(case: Case, audit_date: date, goal: set[str], research_done: bool) -> tuple[Status, str, str]:
    filings = [f for r in case.commercial_reports for f in r.ucc_filings]
    uniq = {}
    for f in filings:
        uniq[(f.secured_party.upper(), f.filing_number or f.filing_date)] = f
    filings = [f for f in uniq.values() if f.status == "active"]
    debt_lenders = {d.lender.upper() for d in case.intake.debts if d.lender}
    if not research_done and not filings:
        return Status.PEND, "UCC debtor search not yet completed", "The state UCC debtor search has not yet been completed, and no filings appear on the bureau files reviewed."
    if not filings:
        return Status.PASS, "No open UCC filings or public records found", "No open UCC filings, judgments or liens were found in the searches and files reviewed."
    unmatched = [f for f in filings if debt_lenders and not any(f.secured_party.upper()[:6] in d or d[:6] in f.secured_party.upper() for d in debt_lenders)]
    mca = [f for f in filings if f.collateral_class == "mca_factor"]
    desc = "; ".join(f"{f.secured_party} ({f.collateral_class or 'collateral not classified'})" for f in filings)
    found = f"{len(filings)} open filing(s): {desc}."
    if mca or unmatched:
        what = "an MCA/factor filing" if mca else "a filing not matched to the disclosed debt schedule"
        return Status.AR, f"{len(filings)} open filing(s), including {what}", found + f" This includes {what}; confirm with the client and the secured party."
    broad = [f for f in filings if f.collateral_class in ("blanket", "accounts")]
    if broad and goal & LIEN_PRODUCTS:
        return Status.NI, f"{len(filings)} legitimate filing(s), broad collateral", found + " These are legitimate filings and not a defect; they constrain new secured borrowing."
    if not research_done:
        return Status.PEND, f"{len(filings)} filing(s) on bureau files; SOS search pending", found + " The state UCC debtor search is still needed to confirm the full picture."
    return Status.PASS, f"{len(filings)} filing(s), all understood", found


def point_19(case: Case, audit_date: date, research_result: str) -> tuple[Status, str, str]:
    reps = [r for r in case.commercial_reports if r.bureau != CommercialBureau.LEXISNEXIS]
    ids: dict[str, set] = {}
    for r in reps:
        if r.file_id:
            ids.setdefault(r.bureau.value, set()).add(r.file_id)
    dup = [b for b, s in ids.items() if len(s) > 1]
    if dup:
        return Status.AR, f"More than one file at {', '.join(dup)}", f"More than one file identifier was found at {', '.join(dup)}."
    if research_result == "found_issue":
        return Status.AR, "Duplicate file confirmed by search", "The analyst's search confirmed a second business file."
    if research_result == "found_ok":
        return Status.PASS, "One file per bureau confirmed", "Searches under every name variant, EIN, address and phone confirmed one file per bureau."
    return Status.PEND, "Explicit duplicate search not yet completed", "No duplicate file has been confirmed. An explicit search at each bureau under every name variant, EIN and address is still needed before this point can pass."
