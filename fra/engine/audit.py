"""Runs the full audit: 20 points, areas, flags, First Three Actions, composite score,
Action Center. Rules: docs/council/r3_identity_audit.md §0–§5, r3_commercial_bureaus.md §2."""
from __future__ import annotations

from datetime import date
from typing import Optional

from fra import config as C
from fra.content import POINTS, ROOT_CAUSES
from fra.engine import bureaus as B
from fra.engine.guarantor import analyze_guarantor
from fra.engine.identity import address_candidates, build_matrix, email_is_free, root_domain
from fra.engine.products import evaluate as evaluate_products
from fra.engine.results import (Action, AreaRating, AuditResult, Composite, ConcentrationGroup, Finding, Flag,
                                Metric, ReviewItem)
from fra.states import state_code
from fra.models import STATUS_SEVERITY, Case, CommercialBureau, DocType, Status


def _research(case: Case, key: str):
    r = case.research.get(key)
    return (r.result, r.finding) if r else ("not_started", "")


def _has_doc(case: Case, *types: DocType) -> bool:
    return any(d.doc_type in types for d in case.documents) or any(
        any(t.value.split(" ")[0].lower() in s.source.lower() for t in types) for s in case.identity_sources)


def _src(case: Case, *needles: str):
    return [s for s in case.identity_sources if any(n.lower() in s.source.lower() for n in needles)]


def _row(matrix, field):
    return next((r for r in matrix if r.field == field), None)


def finding(n: int, status: Status, one_line: str, found: str, correction: str = "", plain: str = "",
            sources: Optional[list[str]] = None, tier: int = 7, insufficient: bool = False) -> Finding:
    p = POINTS[n]
    if not plain:
        plain = {
            Status.PASS: "This is in good shape — keep it consistent.",
            Status.NA: "This doesn't apply to your business.",
            Status.PEND: "We need one more document or check before we can rate this — it is not a negative finding.",
            Status.NI: "This works, but improving it could help your approval or limits.",
            Status.AR: "Fix this before you apply — a lender is likely to flag it.",
        }[status]
    return Finding(number=n, title=p["title"], status=status, one_line=one_line, found=found, why=p["why"],
                   correction=correction or ("None required." if status in (Status.PASS, Status.NA) else ""),
                   where_fix=p["where"], pass_standard=p["pass"], plain=plain, what_it_is=p["what"],
                   sources=sources or [], tier=tier, insufficient_data=insufficient)


def run_audit(case: Case, audit_date: Optional[date] = None) -> AuditResult:
    audit_date = audit_date or case.meta.report_date or date.today()
    it = case.intake
    res = AuditResult(audit_date=audit_date)
    goal = set(it.funding.product_types)

    # ---- Identity matrix and address --------------------------------------------------
    matrix, sources = build_matrix(case, audit_date)
    res.matrix, res.matrix_sources = matrix, sources
    res.address_candidates = address_candidates(case, audit_date)
    sev = {r.field: r.severity for r in matrix}
    master_name = (_row(matrix, "legal_name").controlling_value if _row(matrix, "legal_name") else "") or it.legal_name
    master_type = (_row(matrix, "entity_type").controlling_value if _row(matrix, "entity_type") else "") or it.entity_type
    master_ein = (_row(matrix, "ein").controlling_value if _row(matrix, "ein") else "") or it.ein
    master_addr = case.meta.master_address_designation
    if master_addr is None or master_addr.is_empty():
        master_addr = it.business_address if not it.business_address.is_empty() else None

    # ---- Guarantor ----------------------------------------------------------------------
    if case.consumer_credit:
        res.guarantor = analyze_guarantor(case.consumer_credit[0], it, audit_date)

    # ---- Bureau cards -------------------------------------------------------------------
    res.bureau_cards = B.build_cards(case, audit_date, master_name, master_type, master_addr, master_ein)

    F: dict[int, Finding] = {}

    # 01 EIN / IRS identity
    irs = _src(case, "IRS", "CP 575", "147C")
    ein_row = _row(matrix, "ein")
    conflict_srcs = [k for k, c in (ein_row.cells.items() if ein_row else []) if c.outcome == "CONFLICT"]
    if it.entity_type.lower().startswith("sole") and not it.ein:
        F[1] = finding(1, Status.NA, "Sole proprietor using an SSN", "No EIN is used; most business-credit products need one.")
    elif conflict_srcs:
        F[1] = finding(1, Status.AR, "Conflicting TIN on " + ", ".join(conflict_srcs),
                       f"The controlling EIN (from {ein_row.controlling_source}) ends in …{master_ein[-4:]}. A different nine-digit number appears on: {', '.join(conflict_srcs)}.",
                       "Obtain the account profile and current W-9 from the institution showing the different number; if the TIN on file differs from the IRS-issued EIN, have it corrected before any application. A Letter 147C is optional supporting evidence only.",
                       "One of your records shows a different tax ID — lenders' identity checks can stop on this, so it gets fixed first.",
                       sources=[ein_row.controlling_source] + conflict_srcs, tier=1)
    elif not irs:
        F[1] = finding(1, Status.PEND, "IRS EIN notice not yet on file",
                       "No IRS EIN document (CP 575 or Letter 147C) has been provided, so the EIN cannot be confirmed against the IRS record.",
                       "Provide the IRS CP 575 notice, or request a Letter 147C from the IRS Business & Specialty Tax Line.", tier=7)
    else:
        F[1] = finding(1, Status.PASS, "EIN documented and consistent across records",
                       f"The IRS EIN notice confirms the EIN ending …{master_ein[-4:] if master_ein else '????'}; no conflicting number was found on the records reviewed.",
                       sources=[s.source for s in irs])

    # 02 Secretary of State
    sos = _src(case, "Secretary of State", "SOS", "Certificate")
    r, txt = _research(case, "sos_status")
    if r == "found_issue":
        F[2] = finding(2, Status.AR, txt or "Entity not in active status", txt or "The live state record shows the entity is not active.",
                       "File the overdue annual report or reinstatement with the Secretary of State and obtain a current certificate of status.", tier=1)
    elif sev.get("formation") == "S1":
        F[2] = finding(2, Status.AR, "State or formation details conflict between documents", "Authoritative documents disagree on the state or formation details.", "Obtain the live state record and align the documents.", tier=1)
    elif not sos and r == "not_started":
        F[2] = finding(2, Status.PEND, "Formation documents and state search outstanding", "Neither formation documents nor a live state search are on file yet.",
                       "Provide the formation document; TLA will run the state search.", tier=7)
    elif r == "found_ok":
        F[2] = finding(2, Status.PASS, "Formed and active on the state record", (txt or "The live state record shows the entity as active with a complete filing chain."), sources=[s.source for s in sos] + ["SOS search"])
    else:
        F[2] = finding(2, Status.NI if sos else Status.PEND, "Formation documented; live status check pending",
                       "Formation documents are on file. A current status check on the live state record is still needed.",
                       "Obtain a current certificate of status near lender submission.", tier=7)

    # 03 Registered agent
    r, txt = _research(case, "registered_agent")
    F[3] = (finding(3, Status.PASS, "Current agent on file", txt or "A current registered agent with an in-state street address is on file.") if r == "found_ok" else
            finding(3, Status.AR, txt or "Registered agent issue", txt or "The state record shows a registered-agent problem.", "File a change of registered agent/office with the Secretary of State.", tier=2) if r == "found_issue" else
            finding(3, Status.PEND, "Confirm on the state record", "The registered agent will be confirmed with the Secretary of State search.", tier=7))

    # 04 NAICS / SIC
    naics_row, sic_row = _row(matrix, "naics"), _row(matrix, "sic")
    naics = naics_row.controlling_value if naics_row else ""
    blanks = [k for k, c in naics_row.cells.items() if c.outcome == "BLANK"] if naics_row else []
    if sev.get("naics") == "S2":
        F[4] = finding(4, Status.AR, "Industry codes conflict across records", naics_row.note, "Confirm the truthful primary NAICS and propagate it with the matching SIC to each bureau.", tier=2)
    elif not naics:
        F[4] = finding(4, Status.PEND if not case.commercial_reports else Status.AR, "No NAICS selected",
                       "No NAICS code has been selected or appears on the records reviewed.",
                       "Select the NAICS code that truthfully describes the primary revenue activity, then propagate it to each bureau.", tier=2)
    elif blanks:
        F[4] = finding(4, Status.AR, f"NAICS {naics} not yet on " + ", ".join(blanks),
                       f"NAICS {naics} is the selected classification, but the field is blank on: {', '.join(blanks)}.",
                       f"Confirm {naics} as the truthful primary classification and propagate it with the matching SIC to each bureau. TLA does not recommend changes to tax-return classification.", tier=2)
    else:
        F[4] = finding(4, Status.PASS, f"NAICS {naics} consistent", f"NAICS {naics} appears consistently on the records reviewed.")

    # 05 Licensing
    r, txt = _research(case, "licensing")
    has_lic = any(d.doc_type == DocType.BUSINESS_LICENSE for d in case.documents)
    F[5] = (finding(5, Status.NA, "No specialized license identified", txt or "TLA research found no specialized license requirement for the documented activity.") if r == "not_applicable" else
            finding(5, Status.PASS, "Current license on file", txt or "A current license matching the legal name is on file.") if r == "found_ok" or (has_lic and r == "not_started") else
            finding(5, Status.AR, txt or "Required license missing or mismatched", txt, "Obtain or renew the license in the exact legal name.", tier=1) if r == "found_issue" else
            finding(5, Status.PEND, "Licensing research not yet completed", "Licensing applicability for the documented activity has not yet been researched.", tier=7))

    # 06 Phone / 411
    r, txt = _research(case, "listing_411")
    phone_row = _row(matrix, "phone")
    phone_blank = [k for k, c in phone_row.cells.items() if c.outcome == "BLANK"] if phone_row else []
    if not it.business_phone:
        F[6] = finding(6, Status.AR, "No business phone provided", "No dedicated business phone number was provided.", "Establish a business number the company controls and list it under the exact legal name.", tier=6)
    elif r == "found_issue" or (r == "not_started" and phone_blank):
        F[6] = finding(6, Status.AR, "Number provided; 411 listing and bureau fields unverified",
                       f"The business number was provided by the client. {txt or 'The directory listing has not been confirmed.'}" + (f" The phone field is blank on: {', '.join(phone_blank)}." if phone_blank else ""),
                       "Confirm the business controls the number, list it under the exact legal name and master address, then add it to each bureau, the website and the Google profile.", tier=6)
    elif r == "found_ok" and not phone_blank:
        F[6] = finding(6, Status.PASS, "Listed and consistent", txt or "The number is listed under the legal name and appears on the bureau files.")
    elif r == "found_ok":
        F[6] = finding(6, Status.NI, "Listed; missing on some bureau files", f"{txt} The phone is blank on: {', '.join(phone_blank)}.", "Add the number to each bureau file.", tier=6)
    else:
        F[6] = finding(6, Status.PEND, "Directory listing check pending", "The business number was provided; the 411 listing check has not yet been run.", tier=7)

    # 07 Domain
    r, txt = _research(case, "domain")
    dom = root_domain(it.website) if it.website and "no website" not in it.website.lower() else ""
    F[7] = (finding(7, Status.AR, "No business domain", "The business has no domain.", "Register a domain matching the legal or trade name in the business name; enable auto-renew.", tier=6) if not dom else
            finding(7, Status.AR, txt or "Domain issue", txt, "Update the domain registration to the business or renew it.", tier=6) if r == "found_issue" else
            finding(7, Status.PASS, f"Active domain confirmed — {dom}", txt or f"The domain {dom} is active.") if r == "found_ok" else
            finding(7, Status.PEND, f"Domain {dom} to be verified", f"The client lists {dom}; registration has not yet been checked.", tier=7))

    # 08 Professional email
    if not it.business_email:
        F[8] = finding(8, Status.PEND, "No business email provided", "No business email was provided.", tier=7)
    elif email_is_free(it.business_email):
        F[8] = finding(8, Status.AR, "Using a free-mail address" + ("; domain already owned" if dom else ""),
                       "The business email is a free-mail address" + (f" even though the business owns {dom}." if dom else "."),
                       f"Create a mailbox such as info@{dom or 'yourdomain.com'} and use it on the bank, bureaus, applications and directories.", tier=6)
    elif dom and root_domain(it.business_email) != dom:
        F[8] = finding(8, Status.NI, "Email domain differs from website", "The email domain does not match the website domain.", "Use one domain for email and website.", tier=6)
    else:
        F[8] = finding(8, Status.PASS, "Domain email in use", "A domain-matched business email is used.")

    # 09 Website
    r, txt = _research(case, "website")
    F[9] = (finding(9, Status.AR, "No website", "The business has no website.", "Publish a site with the legal name, master address or service area, phone and a description matching the NAICS.", tier=6) if not dom else
            finding(9, Status.PASS, f"Active site — {dom}", txt or f"{dom} is live and represents the business.") if r == "found_ok" else
            finding(9, Status.NI, txt or "Site live but details inconsistent", txt, "Show the legal name, master address and phone consistently.", tier=6) if r == "found_issue" else
            finding(9, Status.PEND, f"{dom} to be reviewed", "The website has not yet been reviewed.", tier=7))

    # 10 Banking
    months = case.financials.bank_months
    if len({m.month for m in months}) < 3:
        rel = it.banking_relationships or it.primary_bank
        F[10] = finding(10, Status.PEND, "Relationships documented; statements outstanding" if rel else "Statements outstanding",
                        (f"Banking relationships reported: {rel}. " if rel else "") + "Three consecutive months of complete business bank statements have not yet been provided.",
                        "Provide three consecutive months of complete statements for every business account (six preferred).", tier=7)
    else:
        nsf = sum(m.nsf_count for m in months[-3:])
        neg = sum(m.negative_days for m in months[-3:])
        if it.banking_problems:
            F[10] = finding(10, Status.NI, "Prior banking problem disclosed", it.banking_problems_detail or "The client disclosed a prior banking problem.", "Keep documentation of the resolution in the funding file.", tier=3)
        elif nsf or neg:
            F[10] = finding(10, Status.NI, f"{nsf} NSF and {neg} negative days in 3 months", f"The last three statements show {nsf} NSF/returned items and {neg} negative-balance days.", "Keep a cushion so the account never goes negative for at least 90 days before applying.", tier=3)
        else:
            F[10] = finding(10, Status.PASS, "Three months of clean statements", "Three months of statements show no NSF or negative-balance activity.")

    # 11, 12, 13, 18, 19 (commercial)
    st, one, found, insuff = B.point_11(case, res.bureau_cards, audit_date, goal)
    F[11] = finding(11, st, one, found, "Correct identity fields at each bureau first, then build reporting accounts." if st != Status.PASS else "", tier=2 if st == Status.AR else 7, insufficient=insuff)
    st, one, found = B.point_12(case, audit_date)
    F[12] = finding(12, st, one, found, "After the identity corrections, add real vendor accounts that report to the business bureaus and pay them on time (aim for 3+ at each bureau)." if st != Status.PASS else "", tier=2 if st == Status.AR else 7)
    st, one, found, insuff = B.point_13(case, audit_date)
    F[13] = finding(13, st, one, found, "Order the LexisNexis business file." if st == Status.PEND else "", tier=7 if st == Status.PEND else 2, insufficient=insuff)
    r18, _ = _research(case, "ucc_search")
    st, one, found = B.point_18(case, audit_date, goal, r18 in ("found_ok", "found_issue", "not_found"))
    F[18] = finding(18, st, one, found, "Keep the filings and loan documents in the funding file; discuss collateral position with any prospective secured lender. Only the secured party can amend or terminate a filing." if st != Status.PASS else "", tier=4)
    r19, _ = _research(case, "duplicate_files")
    st, one, found = B.point_19(case, audit_date, r19)
    F[19] = finding(19, st, one, found, "Search each bureau under every name variant, EIN, address and phone, and record the identifiers." if st == Status.PEND else "", tier=1 if st == Status.AR else 7)

    # 14 Google Business Profile
    r, txt = _research(case, "gbp")
    no_master = sev.get("address") == "S1"
    F[14] = (finding(14, Status.NA, "Not eligible under Google's guidelines", txt) if r == "not_applicable" else
             finding(14, Status.PASS, "Verified profile consistent", txt or "A verified profile matches the master record.") if r == "found_ok" else
             finding(14, Status.AR, txt or "Profile shows wrong details", txt, "Claim and correct the profile using the exact legal name.", tier=6) if r == "found_issue" else
             finding(14, Status.PEND, "No profile documented", "No Google Business Profile has been documented. Creating one should wait until the master address is designated, because verification locks in the address.", "After designating the master address, create or claim and verify the profile.", tier=6))

    # 15 Proof of business address
    addr_row = _row(matrix, "address")
    active = [c for c in res.address_candidates if c.kind == "candidate"]
    has_proof = any(d.doc_type == DocType.PROOF_OF_ADDRESS for d in case.documents)
    if no_master:
        F[15] = finding(15, Status.AR, f"{len(active)} address candidates; no master address designated",
                        f"{len(active)} active addresses appear across the records and no master business address has been designated. See Section 06.",
                        "Choose one legitimate, supportable business address, provide proof, and propagate it to every record. TLA does not select the address.",
                        "Different records show different addresses — you choose one real address and we help you line every record up to it.", tier=1)
    elif addr_row and addr_row.severity in ("S1", "S2"):
        F[15] = finding(15, Status.AR, "Master address not yet propagated", addr_row.note, "Propagate the master address to each record using the checklist in Section 06.", tier=1)
    elif not has_proof:
        F[15] = finding(15, Status.PEND, "Proof of address not yet provided", "The address is consistent on the records reviewed, but proof (lease, utility or telecom bill in the legal name) has not been provided.", "Provide proof dated within 90 days.", tier=7)
    else:
        F[15] = finding(15, Status.PASS, "One master address with proof", "One address appears consistently with proof on file.")

    # 16 Foreign qualification
    r, txt = _research(case, "foreign_qualification")
    addr_state = (master_addr.state if master_addr else "") or it.business_address.state
    if r == "found_issue":
        F[16] = finding(16, Status.AR, txt or "Operating in a state where not registered", txt, "File a foreign registration in the operating state and appoint an in-state agent.", tier=1)
    elif r in ("found_ok", "not_applicable") or (it.formation_state and addr_state and state_code(it.formation_state) == state_code(addr_state)):
        F[16] = finding(16, Status.NA, "Domestic entity; no out-of-state nexus indicated", txt or f"The entity is formed in {it.formation_state} and operates there; no out-of-state nexus is indicated.")
    else:
        F[16] = finding(16, Status.PEND, f"Formed in {it.formation_state or '?'}, operating in {addr_state or '?'}", "The formation state differs from the operating address state; registration in the operating state needs to be checked.", tier=1)

    # 17 Legal name / DBA
    nm, et = _row(matrix, "legal_name"), _row(matrix, "entity_type")
    issues = [r_.note for r_ in (nm, et) if r_ and r_.severity in ("S1", "S2")]
    variants = [r_.note for r_ in (nm, et) if r_ and r_.severity == "S3"]
    if issues:
        bits = []
        for card in res.bureau_cards:
            for fld, shown, assess in card.identity_rows:
                if fld in ("Legal name", "Entity type") and assess not in ("MATCH", "FORMAT VARIANT"):
                    short = card.bureau.split(" ")[0]
                    bits.append(f"{short} {fld.lower()} {'blank' if assess == 'BLANK' else 'shown as ' + shown}")
        F[17] = finding(17, Status.AR, "; ".join(bits)[:120] if bits else "; ".join(issues)[:120], "The legal name or entity type does not match the controlling state filing on some records: " + "; ".join(issues) + ".",
                        "Use the Secretary of State spelling and entity type as controlling; correct each bureau with the formation document and status certificate.", tier=2)
    elif variants:
        F[17] = finding(17, Status.NI, "Minor name variants", "; ".join(variants), "Standardize to the exact state-filed name.", tier=6)
    elif not case.commercial_reports and not case.identity_sources:
        F[17] = finding(17, Status.PEND, "Records needed to compare", "No source documents or bureau files are available yet to compare the legal name.", tier=7)
    else:
        F[17] = finding(17, Status.PASS, "Legal name and entity type consistent", "The legal name and entity type match on every record reviewed.")

    # 20 Core consistency
    s1 = [r_ for r_ in matrix if r_.severity == "S1"]
    s2 = [r_ for r_ in matrix if r_.severity == "S2"]
    s3 = [r_ for r_ in matrix if r_.severity == "S3"]
    tier_c = sum(1 for s in sources if s in [c.value for c in CommercialBureau])
    if s1 or len(s2) >= 2:
        F[20] = finding(20, Status.AR, ", ".join(r_.label for r_ in (s1 + s2)[:5]) + " disagree",
                        "The records do not all describe the same company. Fields that disagree: " + "; ".join(f"{r_.label} — {r_.note}" for r_ in s1 + s2) + ".",
                        "Correct in this order: EIN → master address → name/type → codes, phone, website → revenue/employees → re-verify each bureau after 30–45 days → only then build credit depth.",
                        "Your records don't all describe the same company yet — fixing this resolves most of the audit.", tier=1)
    elif s2 or s3:
        F[20] = finding(20, Status.NI, "Minor inconsistencies", "; ".join(f"{r_.label} — {r_.note}" for r_ in s2 + s3), "Align the listed fields.", tier=2)
    elif tier_c < 2:
        F[20] = finding(20, Status.PEND, "Fewer than two bureau files to compare", "At least two commercial bureau files are needed to test record consistency.", tier=7)
    else:
        F[20] = finding(20, Status.PASS, "Records consistent", "All compared fields match.")

    # Analyst overrides (logged)
    for key, ov in case.overrides.items():
        n = int(key)
        if n in F and (ov.status or ov.finding):
            if ov.status:
                F[n].status = ov.status
            if ov.finding:
                F[n].one_line = ov.finding
            F[n].overridden = True
    res.findings = [F[n] for n in sorted(F)]
    res.status_counts = {s.value: sum(1 for f in res.findings if f.status == s) for s in Status}

    # ---- Products --------------------------------------------------------------------------
    res.products = evaluate_products(case, res.guarantor, audit_date)

    # ---- Review items -----------------------------------------------------------------------
    g = res.guarantor
    if g and g.identity_gate != "Clear":
        res.review_items.append(ReviewItem(id="HR-ID", title="Personal identity data needs review", reason="; ".join(case.consumer_credit[0].identity_flags), blocking=True))
    if not case.consumer_credit:
        res.review_items.append(ReviewItem(id="HR-01", title="No personal credit report", reason="Guarantor analysis and card/loan product fit need a current 3-bureau FICO report."))
    for d in case.documents:
        if d.extraction_status == "extracted" and d.extracted.get("_low_confidence"):
            res.review_items.append(ReviewItem(id="HR-06", title=f"Low extraction confidence: {d.filename}", reason="Verify the extracted values against the document.", blocking=True))
    for note in case.financials.consistency_notes:
        res.review_items.append(ReviewItem(id="HR-25", title="Financial-document consistency", reason=note))
    if it.funding.for_whom == "business" and any("gold" in (u.purpose or "").lower() or "invest" in (u.purpose or "").lower() for u in it.funding.uses):
        res.review_items.append(ReviewItem(id="HR-UOP", title="Use of proceeds outside ordinary operations", reason="Lenders require detailed documentation when funds leave the operating business."))

    # ---- Areas ------------------------------------------------------------------------------
    res.areas = rate_areas(res, case)

    condition_products(res, case)

    # ---- Flags, first three, concentration ----------------------------------------------------
    res.flags = build_flags(res)
    res.first_three, res.secondary = first_three(res)
    res.concentration = concentration(res)
    res.composite = composite(res, case, audit_date)
    res.actions = action_center(res, case)
    res.strengths = strengths(res, case)
    res.documents_reviewed = [(d.doc_type.value, d.filename, d.document_date.strftime("%m/%d/%Y") if d.document_date else "") for d in case.documents]
    return res


def _worst(statuses: list[Status]) -> Status:
    s = [x for x in statuses if x != Status.NA]
    return max(s, key=lambda x: STATUS_SEVERITY[x]) if s else Status.NA


def rate_areas(res: AuditResult, case: Case) -> list[AreaRating]:
    F = {f.number: f for f in res.findings}

    def rate(core: list[int], support: list[int], extra_core: list[Status] = (), s1: bool = False) -> Status:
        cs = [F[n].status for n in core] + list(extra_core)
        ss = [F[n].status for n in support]
        if Status.AR in cs or s1:
            return Status.AR
        if Status.AR in ss or Status.NI in cs or sum(1 for s in ss if s == Status.NI) >= 2:
            return Status.NI
        if Status.PEND in cs:
            return Status.PEND
        return Status.PASS

    s1 = any(r.severity == "S1" for r in res.matrix)
    legal = rate([1, 2, 15, 17, 20], [3, 5, 6, 7, 8, 9, 14, 16], s1=s1)
    credit = rate([11, 12, 19], [4, 13, 18], [c.status for c in res.bureau_cards[:2]])
    banking = rate([10], [18], [Status.NI] if case.financials.consistency_notes else [])
    g = res.guarantor
    guar = g.status if g else Status.PEND
    fg = case.intake.funding
    if not fg.amount_requested or not fg.uses:
        goal = Status.AR
    elif not fg.repayment_source or any(r.id == "HR-UOP" for r in res.review_items):
        goal = Status.NI
    elif any(p.fit in ("STRONG FIT", "POTENTIAL FIT") and p.in_goal for p in res.products) or not fg.product_types:
        goal = Status.PASS
    else:
        goal = Status.NI

    def narr(ok: list[int], bad: list[int]) -> str:
        okt = ", ".join(F[n].title for n in ok if F[n].status == Status.PASS)
        badt = "; ".join(F[n].one_line for n in bad if F[n].status in (Status.AR, Status.NI))
        pend = "; ".join(F[n].one_line for n in bad if F[n].status == Status.PEND)
        out = (f"{okt} pass. " if okt else "")
        if badt:
            out += f"What remains: {badt}."
        if pend:
            out += f" Pending: {pend}."
        return out.strip() or "No material issues found."

    return [
        AreaRating(key="legal", name="Business Legal / Identity", status=legal, narrative=narr([1, 2, 3, 15, 17], [1, 15, 17, 20])),
        AreaRating(key="credit", name="Business Credit", status=credit, narrative=narr([11, 12, 19], [11, 12, 4, 18])),
        AreaRating(key="banking", name="Banking / Financials", status=banking, narrative=narr([10], [10])),
        AreaRating(key="guarantor", name="Personal Guarantor", status=guar, narrative=(g.one_line + ". " + " ".join(g.flags[:2])) if g else "Personal credit report not yet provided."),
        AreaRating(key="goal", name="Funding Goal / Structure", status=goal, narrative=_goal_narrative(case)),
    ]


BUSINESS_LANES = {"BL", "BT", "SBA", "OL", "OT", "EQ", "FAC", "MCA", "BC"}
CASHFLOW_LANES = {"BL", "OL", "OT", "MCA", "FAC"}


def condition_products(res: AuditResult, case: Case) -> None:
    """Directional positioning is conditional on the audit findings (Section 13 of the report)."""
    areas = {a.key: a.status for a in res.areas}
    req = case.intake.funding.amount_requested
    g = res.guarantor
    for p in res.products:
        conds = []
        if p.code in BUSINESS_LANES and areas.get("legal") == Status.AR:
            conds.append("after the identity corrections in Sections 06–09")
        if p.code in CASHFLOW_LANES | {"SBA", "BT"} and len({m.month for m in case.financials.bank_months}) < 3:
            conds.append("subject to three months of bank statements")
        if any(r.id == "HR-UOP" for r in res.review_items) and p.code in BUSINESS_LANES:
            conds.append("subject to use-of-proceeds review")
        if conds and p.fit in ("STRONG FIT", "POTENTIAL FIT", "POTENTIAL FIT — AFTER FIXES"):
            p.fit = f"{p.fit.split(' — ')[0]} — " + ("AFTER CORRECTIONS" if "identity" in conds[0] else "SUBJECT TO REVIEW")
            p.reasons.append("Conditional: " + "; ".join(conds) + ".")
        # Ranges never exceed the request; capacity above the request is noted, not shown
        if req and p.range_high and p.range_high > req:
            p.reasons.append("Indicative capacity exceeds the amount requested; range shown up to the request.")
            p.range_high = req
            p.range_low = min(p.range_low or req, req)
        # Earliest-ready date for a recent late payment (BC/PC hard KO)
        if g and p.code in ("BC", "PC") and any("late payment within the last 12 months" in b for b in p.blockers):
            lates = [t.last_late_date for cc in case.consumer_credit for t in cc.tradelines if t.last_late_date and t.owner_type != "au"]
            if lates:
                last = max(lates)
                p.earliest_ready = date(last.year + 1, last.month, min(last.day, 28))


def _goal_narrative(case: Case) -> str:
    fg = case.intake.funding
    if not fg.amount_requested:
        return "The funding amount and use of proceeds have not been stated yet."
    uses = ", ".join(u.purpose for u in fg.uses) or "not yet documented"
    rep = fg.repayment_source or "not yet documented"
    rng = f"${fg.amount_minimum:,.0f}–${fg.amount_requested:,.0f}" if fg.amount_minimum and fg.amount_minimum != fg.amount_requested else f"${fg.amount_requested:,.0f}"
    return f"Request of {rng}. Use of proceeds: {uses}. Source of repayment: {rep}."


CONSEQUENCE = {
    1: "A tax-ID mismatch can fail lender identity verification regardless of financial strength.",
    2: "A lender cannot close with an entity that is not in good standing.",
    4: "Blank or conflicting industry codes misroute automated screening.",
    6: "An unverified phone weakens identity checks at card issuers and lenders.",
    8: "Free-mail on applications is a minor negative signal.",
    10: "Without statements, cash-flow lenders cannot evaluate the file.",
    11: "Wrong or thin bureau data routes applications to decline or manual review.",
    12: "Without reporting accounts, the business cannot generate a PAYDEX or depth.",
    13: "LexisNexis is used in lender identity screening.",
    14: "Google profile verification should wait for the master address.",
    15: "Conflicting addresses trigger manual review and document requests.",
    17: "Name or entity-type mismatches split bureau files.",
    18: "Existing filings constrain new secured borrowing.",
    19: "A duplicate file can hide payment history from lenders.",
    20: "Inconsistent records drive automated declines.",
}


def build_flags(res: AuditResult) -> list[Flag]:
    flags = []
    for f in res.findings:
        if f.status in (Status.AR, Status.NI, Status.PEND):
            flags.append(Flag(title=f"{f.title}: {f.one_line}", status=f.status, consequence=CONSEQUENCE.get(f.number, f.why.split(".")[0] + "."),
                              tier=f.tier if f.status != Status.PEND else 7, points=[f.number], ref=f"Point {f.number:02d}"))
    if res.guarantor:
        for msg in res.guarantor.flags:
            flags.append(Flag(title=f"Guarantor: {msg}", status=Status.NI, consequence="Advisory item on the personal credit file.", tier=5, ref="Section 12"))
    for r in res.review_items:
        flags.append(Flag(title=r.title, status=Status.AR if r.blocking else Status.NI, consequence=r.reason, tier=3, ref=r.id))
    rank = {Status.AR: 0, Status.NI: 1, Status.PEND: 2}
    return sorted(flags, key=lambda x: (x.tier, rank.get(x.status, 3)))


# Dependency edges: fixing the key unlocks these points (r3 identity §5.2)
DOWNSTREAM = {1: [11, 19, 20, 12], 15: [6, 14, 11, 20, 12], 17: [11, 20, 12], 20: [12, 11], 2: [1, 3, 15, 17, 20], 4: [11], 10: []}


def first_three(res: AuditResult) -> tuple[list[Action], list[tuple[str, Status, str]]]:
    cands = [f for f in res.findings if f.status == Status.AR]
    weight = {1: 3, 2: 2}

    def score(f: Finding) -> float:
        return weight.get(f.tier, 1) * (1 + len(DOWNSTREAM.get(f.number, [])))
    ranked = sorted(cands, key=lambda f: (-score(f), f.tier, f.number))
    chosen: list[Finding] = []
    bundle_points = {4, 6, 8, 9, 17, 20, 11}
    for f in ranked:
        if len(chosen) == 2 and f.number in bundle_points:
            # Third action is often the "lock the commercial identity" bundle
            chosen.append(f)
            break
        if len(chosen) < 3:
            chosen.append(f)
    actions = []
    for i, f in enumerate(chosen[:3], 1):
        actions.append(Action(priority=i, item=_action_title(f), what=f.correction or f.found, path="CLIENT ACTION", ref=f"Point {f.number:02d}"))
    if res.guarantor and len(actions) < 3 and res.guarantor.status == Status.AR:
        actions.append(Action(priority=len(actions) + 1, item="Address the personal credit blockers", what="; ".join(res.guarantor.flags[:2]), path="CLIENT ACTION", ref="Section 12"))
    chosen_nums = {f.number for f in chosen[:3]}
    secondary = [(f"{f.title}", f.status, f.one_line) for f in res.findings if f.status in (Status.AR, Status.NI, Status.PEND) and f.number not in chosen_nums]
    return actions, secondary


def _action_title(f: Finding) -> str:
    return {1: "Correct the lender-facing TIN record", 15: "Designate the Master Business Address", 20: "Lock the commercial business identity",
            17: "Align the legal name and entity type everywhere", 2: "Restore good standing with the state", 4: "Lock the industry classification",
            10: "Provide three months of business bank statements", 11: "Correct the business bureau files",
            12: "Build reporting payment history", 6: "Verify and list the business phone", 8: "Move to a domain email address"}.get(f.number, f.title)


def concentration(res: AuditResult) -> list[ConcentrationGroup]:
    F = {f.number: f for f in res.findings}
    out = []
    for name, pts, meaning in ROOT_CAUSES:
        bad = [p for p in pts if F[p].status in (Status.AR, Status.NI)]
        if bad:
            out.append(ConcentrationGroup(name=name, points=bad, meaning=f"{len(bad)} of the twenty points trace to this: {meaning}"))
    pend = [f.number for f in res.findings if f.status == Status.PEND]
    if pend:
        out.append(ConcentrationGroup(name="Documents / sources outstanding", points=pend, meaning="These points are waiting on a document or check — not negative findings."))
    return sorted(out, key=lambda g: -len(g.points))


def composite(res: AuditResult, case: Case, audit_date: date) -> Composite:
    F = {f.number: f for f in res.findings}
    unlocks = []
    s1 = [r for r in res.matrix if r.severity == "S1"]
    if s1:
        unlocks.append("Resolve the core identity conflict(s): " + ", ".join(r.label for r in s1))
    pend_core = [n for n in (1, 2, 10, 15, 20) if F[n].status == Status.PEND]
    if pend_core or sum(1 for f in res.findings if f.status == Status.PEND) > 2:
        unlocks.append("Complete the pending documents and checks: " + ", ".join(F[n].title for n in (pend_core or [f.number for f in res.findings if f.status == Status.PEND][:4])))
    for b in (CommercialBureau.EXPERIAN, CommercialBureau.DNB):
        if not B.fresh(B.get_report(case, b), audit_date):
            unlocks.append(f"Obtain a current {b.value} report")
    if not res.guarantor:
        unlocks.append("Provide a current 3-bureau personal credit report")
    elif res.guarantor.report_age_days and res.guarantor.report_age_days > C.CONSUMER_REPORT_PROVISIONAL_DAYS:
        unlocks.append("Re-pull the personal credit report (over 60 days old)")
    if len({m.month for m in case.financials.bank_months}) < 3:
        unlocks.append("Provide three months of business bank statements")
    fg = case.intake.funding
    if not fg.amount_requested or not fg.uses:
        unlocks.append("State the funding amount and use of proceeds")
    if any(r.blocking for r in res.review_items):
        unlocks.append("Clear the open review items")
    # Area scores (computed even when withheld, for internal display)
    def area_score(points):
        vals, wts = 0.0, 0.0
        for n in points:
            st = F[n].status
            if st.value in C.POINT_VALUES:
                w = 2 if n in C.CORE_POINTS else 1
                vals += C.POINT_VALUES[st.value] * w
                wts += w
        return vals / wts if wts else 0.0
    gf = res.guarantor.mid_score if res.guarantor else None
    guar = (100 if gf >= 740 else 85 if gf >= 680 else 60 if gf >= 620 else 25) if gf else 0
    if res.guarantor:
        guar = max(0, guar - 10 * len(res.guarantor.flags))
    best = max((p.score or 0 for p in res.products if p.in_goal and p.fit not in ("NOT YET", "NEEDS INFORMATION", "NOT RECOMMENDED")), default=0)
    areas = {"legal": area_score([1, 2, 3, 5, 6, 7, 8, 9, 14, 15, 16, 17, 20]), "credit": area_score([4, 11, 12, 13, 18, 19]),
             "banking": area_score([10]), "guarantor": float(guar), "goal": float(best)}
    if unlocks:
        return Composite(issued=False, unlocks=unlocks, area_scores=areas)
    score = sum(C.COMPOSITE_WEIGHTS[k] * v for k, v in areas.items())
    ar_core = any(F[n].status == Status.AR for n in C.CORE_POINTS)
    n_ar = sum(1 for f in res.findings if f.status == Status.AR)
    if n_ar >= 5:
        score = min(score, 64)
    elif ar_core:
        score = min(score, 79)
    return Composite(issued=True, score=round(score), tier=C.tier_for(score), area_scores=areas)


PHASE_OF = {1: 1, 15: 1, 2: 1, 20: 2, 17: 2, 4: 2, 6: 2, 8: 2, 9: 2, 7: 2, 3: 1, 16: 1, 5: 1, 10: 1, 11: 2, 14: 3, 13: 1, 19: 1, 18: 1, 12: 3}
PHASES = {1: "Weeks 0–2: Identity and documents", 2: "Weeks 2–6: Propagate corrections", 3: "Weeks 6–12: Verify and build depth", 4: "Months 3–6: Reassess and apply"}


def action_center(res: AuditResult, case: Case) -> list[Action]:
    acts = []
    i = 1
    for f in sorted(res.findings, key=lambda f: (PHASE_OF.get(f.number, 3), f.tier)):
        if f.status in (Status.PASS, Status.NA):
            continue
        third = f.number in (1, 2, 11, 13, 16, 18, 19)
        path = "CLIENT ACTION / THIRD-PARTY" if third else "CLIENT ACTION"
        if f.status == Status.PEND and f.number in (5, 13, 18, 19, 2, 3):
            path = "OPTIONAL IMPLEMENTATION"
        acts.append(Action(priority=i, item=f.title, what=f.correction or f.one_line, path=path,
                           position="AWAITING CLIENT" if f.status != Status.PEND else "PENDING DOCUMENT",
                           phase=PHASE_OF.get(f.number, 3), window=PHASES[PHASE_OF.get(f.number, 3)],
                           done_when=f.pass_standard, ref=f"Point {f.number:02d}"))
        i += 1
    if res.guarantor:
        for msg in res.guarantor.flags:
            acts.append(Action(priority=i, item="Personal guarantor", what=msg, path="CLIENT ACTION", phase=2, window=PHASES[2], ref="Section 12"))
            i += 1
    if case.intake.funding.amount_requested and any(r.id == "HR-UOP" for r in res.review_items):
        acts.append(Action(priority=i, item="Use-of-proceeds documentation", what="Document the exact allocation, structure, timeline, collateral and a source of repayment that does not depend on the investment performing.", path="CLIENT ACTION", phase=1, window=PHASES[1], ref="Section 13"))
        i += 1
    acts.append(Action(priority=i, item="Reassessment", what="Once the corrections are complete and bureaus have updated (30–45 days), request a reassessment to issue the composite Funding Readiness Score.", path="OPTIONAL IMPLEMENTATION", phase=4, window=PHASES[4], position="AFTER CORRECTIONS"))
    for f in res.findings:
        if f.status in (Status.PASS, Status.NA) and f.number in (5, 16, 18, 7, 9):
            acts.append(Action(priority=0, item=f.title, what=f.one_line, path="COMPLETED IN FRA", position="COMPLETE", phase=1, window="Completed", ref=f"Point {f.number:02d}"))
    return acts


def strengths(res: AuditResult, case: Case) -> list[Metric]:
    out = []
    trs = sorted(case.financials.tax_returns, key=lambda t: t.year)
    for t in trs[-2:]:
        if t.gross_receipts:
            margin = f" · ~{t.net_income / t.gross_receipts:.1%} margin" if t.net_income and t.gross_receipts else ""
            out.append(Metric(label=f"{t.year} revenue", value=_money(t.gross_receipts), sub=f"Tax-return verified{margin}"))
        if t.net_income is not None:
            out.append(Metric(label=f"{t.year} net business profit", value=_money(t.net_income), sub="Tax return"))
    f = case.financials
    if f.pnl_revenue:
        out.append(Metric(label="YTD revenue", value=_money(f.pnl_revenue), sub=f"Through {f.pnl_period_end:%m/%d/%Y}" if f.pnl_period_end else "P&L"))
    if f.personal_net_worth:
        out.append(Metric(label="Personal net worth", value=_money(f.personal_net_worth), sub="Personal financial statement"))
    g = res.guarantor
    if g and g.scores:
        out.append(Metric(label="Guarantor scores", value=" / ".join(str(v) for _, v, _ in g.scores), sub=" / ".join(b[:2].upper() for b, _, _ in g.scores)))
    if g and g.util_overall is not None:
        out.append(Metric(label="Revolving utilization", value=f"{g.util_overall:.1%}", sub="Primary accounts"))
    if g:
        out.append(Metric(label="Collections · public records", value=f"{g.collections} · {g.public_records}", sub="Personal file"))
    if case.intake.formation_date:
        out.append(Metric(label="Entity formed", value=case.intake.formation_date.strftime("%m/%d/%Y"), sub=f"{case.intake.formation_state} {case.intake.entity_type}".strip()))
    if case.intake.primary_bank:
        out.append(Metric(label="Primary bank", value=case.intake.primary_bank, sub=case.intake.bank_account_age or ""))
    return out


def _money(v: float) -> str:
    if abs(v) >= 1_000_000:
        return f"${v / 1_000_000:.2f}MM"
    if abs(v) >= 1000:
        return f"${v / 1000:,.0f}K"
    return f"${v:,.0f}"
