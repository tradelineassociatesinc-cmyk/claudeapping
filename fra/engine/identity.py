"""Master Business Identity Matrix and address candidates (r3 identity §1–§2)."""
from __future__ import annotations

import re
from datetime import date
from typing import Optional

from fra import config as C
from fra.engine.results import AddressCandidate, MatrixCell, MatrixRow
from fra.models import Address, Case, IdentitySource

TIER_ORDER = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4}

SUFFIX_CLASSES = [
    ("LLC", ["LLC", "L L C", "LIMITED LIABILITY COMPANY", "LTD LIABILITY CO", "LIMITED LIABILITY CO"]),
    ("PLLC", ["PLLC", "P L L C", "PROFESSIONAL LIMITED LIABILITY COMPANY"]),
    ("INC", ["INC", "INCORPORATED"]),
    ("CORP", ["CORP", "CORPORATION"]),
    ("CO", ["CO", "COMPANY"]),
    ("LP", ["LP", "LIMITED PARTNERSHIP"]),
    ("LLP", ["LLP"]),
    ("PC", ["PC", "P C", "PROFESSIONAL CORPORATION"]),
]

ENTITY_TYPE_MAP = {
    "LLC": "LLC", "LIMITED LIABILITY COMPANY": "LLC", "L.L.C.": "LLC", "SINGLE MEMBER LLC": "LLC",
    "PLLC": "PLLC", "PROFESSIONAL LIMITED LIABILITY COMPANY": "PLLC",
    "CORPORATION": "CORP", "CORP": "CORP", "C-CORP": "CORP", "INC": "CORP", "INCORPORATED": "CORP",
    "S-CORP": "CORP", "PROFESSIONAL CORPORATION": "PC", "PROFESSIONAL CORPOATION": "PC", "PC": "PC",
    "PARTNERSHIP": "PARTNERSHIP", "LP": "LP", "LLP": "LLP", "SOLE PROPRIETOR": "SOLE PROP",
    "SOLE PROPRIETORSHIP": "SOLE PROP",
}
# Tax classifications that are compatible with an LLC legal type (not a mismatch)
TAX_CLASSIFICATIONS = {"DISREGARDED ENTITY", "S CORPORATION", "S-CORP", "C CORPORATION", "PARTNERSHIP"}

STREET_ABBR = {
    "STREET": "ST", "AVENUE": "AVE", "ROAD": "RD", "DRIVE": "DR", "LANE": "LN", "BOULEVARD": "BLVD",
    "COURT": "CT", "CIRCLE": "CIR", "PLACE": "PL", "PARKWAY": "PKWY", "HIGHWAY": "HWY", "SUITE": "STE",
    "TERRACE": "TER", "TRAIL": "TRL", "WAY": "WAY", "NORTH": "N", "SOUTH": "S", "EAST": "E", "WEST": "W",
    "APARTMENT": "APT", "BUILDING": "BLDG", "FLOOR": "FL", "UNIT": "UNIT",
}

FREE_MAIL = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com", "icloud.com", "live.com", "msn.com", "proton.me", "protonmail.com"}


# ---------------------------------------------------------------------------
# Normalizers
# ---------------------------------------------------------------------------

def _clean(s: str) -> str:
    s = s.upper().replace("&", " AND ")
    s = re.sub(r"[.,'\"]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return re.sub(r"^THE ", "", s)


def split_name(name: str) -> tuple[str, str]:
    """Return (core name, suffix class)."""
    s = _clean(name)
    for cls, variants in SUFFIX_CLASSES:
        for v in sorted(variants, key=len, reverse=True):
            if s.endswith(" " + v) or s == v:
                return s[: -len(v)].strip(), cls
    return s, ""


def compare_names(a: str, b: str) -> str:
    if not a or not b:
        return "BLANK"
    if a.strip() == b.strip():
        return "MATCH"
    core_a, suf_a = split_name(a)
    core_b, suf_b = split_name(b)
    if core_a != core_b:
        # IRS name control: first four significant characters
        return "CONFLICT"
    if suf_a == suf_b:
        return "EQUIVALENT"
    if {suf_a, suf_b} == {"INC", "CORP"} or "" in (suf_a, suf_b):
        return "VARIANT"
    return "CONFLICT"


def norm_entity(t: str) -> str:
    u = _clean(t).replace("“", "").replace("”", "")
    for key, val in ENTITY_TYPE_MAP.items():
        if u == _clean(key) or u.startswith(_clean(key) + " "):
            return val
    if "LIMITED LIABILITY" in u or "LLC" in u:
        return "PLLC" if "PROFESSIONAL" in u else "LLC"
    if "CORP" in u:
        return "CORP"
    return u


def compare_entity(controlling: str, other: str) -> str:
    if not other:
        return "BLANK"
    a, b = norm_entity(controlling), norm_entity(other)
    if a == b:
        return "MATCH" if _clean(controlling) == _clean(other) else "EQUIVALENT"
    if a == "LLC" and _clean(other) in TAX_CLASSIFICATIONS:
        return "EQUIVALENT"
    return "CONFLICT"


def norm_address(addr: Address) -> str:
    def toks(s: str) -> str:
        words = _clean(s).replace("#", " # ").split()
        return " ".join(STREET_ABBR.get(w, w) for w in words)
    return f"{toks(addr.line1)}|{toks(addr.line2)}|{addr.zip[:5]}"


def address_flags(addr: Address) -> list[str]:
    s = _clean(f"{addr.line1} {addr.line2}")
    flags = []
    if "PMB" in s.split():
        flags.append("Private mailbox (PMB/CMRA) — must be disclosed; not a physical office")
    if s.startswith("PO BOX") or " PO BOX" in s or s.startswith("P O BOX"):
        flags.append("PO box — never accepted as a physical business address")
    if "C/O" in s or s.startswith("CO "):
        flags.append("Care-of address")
    return flags


def compare_address(a: Address, b: Address) -> str:
    if b is None or b.is_empty():
        return "BLANK"
    na, nb = norm_address(a), norm_address(b)
    if na == nb:
        return "MATCH" if a.one_line().upper() == b.one_line().upper() else "EQUIVALENT"
    sa, sb = na.split("|"), nb.split("|")
    if sa[0] == sb[0] and sa[2] == sb[2]:
        return "VARIANT"  # same street, different/missing suite
    return "CONFLICT"


def norm_digits(s: str) -> str:
    return re.sub(r"\D", "", s or "")


def compare_simple(a: str, b: str) -> str:
    if not b:
        return "BLANK"
    if a == b:
        return "MATCH"
    return "EQUIVALENT" if a.strip().lower() == b.strip().lower() else "CONFLICT"


def root_domain(s: str) -> str:
    s = (s or "").lower().strip()
    s = re.sub(r"^https?://", "", s)
    s = s.split("/")[0]
    if "@" in s:
        s = s.split("@", 1)[1]
    return re.sub(r"^www\.", "", s)


# ---------------------------------------------------------------------------
# Source assembly
# ---------------------------------------------------------------------------

def intake_source(case: Case) -> IdentitySource:
    it = case.intake
    owners = "; ".join(f"{o.full_name} ({o.ownership_pct:g}%)" if o.ownership_pct is not None else o.full_name
                       for o in it.owners if o.full_name)
    return IdentitySource(
        source="Intake (client-stated)", tier="E", legal_name=it.legal_name or None, dba=it.dba or None,
        entity_type=it.entity_type or None, formation_state=it.formation_state or None,
        formation_date=it.formation_date, ein=it.ein or None,
        address=None if it.business_address.is_empty() else it.business_address,
        phone=it.business_phone or None, email=it.business_email or None, website=it.website or None,
        naics=it.naics if it.naics and "know" not in it.naics.lower() else None,
        sic=it.sic if it.sic and "know" not in it.sic.lower() else None,
        revenue=it.revenue_last_year, employees=it.employees, owners=owners or None,
    )


def all_sources(case: Case, audit_date: date) -> list[IdentitySource]:
    srcs = list(case.identity_sources)
    for rep in case.commercial_reports:
        if rep.file_found and not rep.insufficient_data:
            s = rep.identity.model_copy()
            s.source = rep.bureau.value
            s.tier = "C"
            s.as_of = rep.report_date
            srcs.append(s)
    srcs.append(intake_source(case))
    return sorted(srcs, key=lambda s: TIER_ORDER.get(s.tier, 9))


def _fmt(src: IdentitySource, field: str) -> Optional[str]:
    if field == "formation":
        parts = [src.formation_state or "", src.formation_date.strftime("%m/%d/%Y") if src.formation_date else ""]
        v = " · ".join(p for p in parts if p)
        return v or None
    v = getattr(src, field, None)
    if v is None or (isinstance(v, str) and not v.strip()):
        return None
    if isinstance(v, Address):
        return v.one_line()
    if field == "revenue":
        return f"${v:,.0f}"
    if field == "years_in_business":
        return f"{v:g}"
    return str(v)


CONTROLLING_HINT = {
    "legal_name": ("Secretary of State", "SOS", "Certificate", "IRS"),
    "entity_type": ("Secretary of State", "SOS", "Certificate"),
    "formation": ("Secretary of State", "SOS", "Certificate"),
    "ein": ("IRS", "CP 575", "147C"),
    "owners": ("Operating agreement", "Bylaws", "Membership"),
    "revenue": ("tax return", "Tax return", "1120", "1065", "Schedule C"),
}


def _controlling(field: str, srcs: list[IdentitySource]) -> Optional[IdentitySource]:
    # Bureau files (tier C) are what we test, never the controlling record
    with_val = [s for s in srcs if _fmt(s, field) and s.tier != "C"]
    if not with_val:
        return None
    hints = CONTROLLING_HINT.get(field)
    if hints:
        for h in hints:
            for s in with_val:
                if h.lower() in s.source.lower():
                    return s
    if field == "revenue":
        docs = [s for s in with_val if s.tier in ("A", "B")]
        if docs:
            return min(docs, key=lambda s: s.revenue or 0)  # lower-of rule (R10)
    return with_val[0]


def build_matrix(case: Case, audit_date: date) -> tuple[list[MatrixRow], list[str]]:
    srcs = all_sources(case, audit_date)
    names = [s.source for s in srcs]
    master = case.meta.master_address_designation
    rows: list[MatrixRow] = []
    fields = [
        ("legal_name", "Legal name"), ("entity_type", "Entity type"), ("formation", "State / formation date"),
        ("ein", "EIN / TIN"), ("address", "Business address"), ("phone", "Phone"), ("email", "Email"),
        ("website", "Website / domain"), ("naics", "NAICS"), ("sic", "SIC"), ("revenue", "Annual revenue"),
        ("employees", "Employees"), ("owners", "Owners / management"), ("years_in_business", "Years in business"),
    ]
    for field, label in fields:
        row = MatrixRow(field=field, label=label)
        ctl = _controlling(field, srcs)
        ctl_val = _fmt(ctl, field) if ctl else None
        if field == "address" and master and not master.is_empty():
            ctl_val, row.controlling_source = master.one_line(), "Client designation"
        elif ctl:
            row.controlling_source = ctl.source
        if field == "years_in_business" and ctl_val is None and _entity_age_years(case, audit_date):
            age = _entity_age_years(case, audit_date)
            ctl_val, row.controlling_source = f"{age:.1f}", "Formation date"
        row.controlling_value = ctl_val or ""
        conflicts, blanks_c, variants, docs_conflict = [], [], [], []
        for s in srcs:
            val = _fmt(s, field)
            if val is None:
                # Bureaus carry every field; a None on a bureau is a blank. Other sources simply don't show it.
                bureau_field = s.tier == "C" and field not in ("email", "owners", "formation")
                cell = MatrixCell(value="Blank" if bureau_field else "—",
                                  outcome="BLANK" if bureau_field else "NOT AVAILABLE")
                if bureau_field:
                    blanks_c.append(s.source)
                row.cells[s.source] = cell
                continue
            if ctl_val is None or (ctl is s and row.controlling_source == s.source):
                row.cells[s.source] = MatrixCell(value=val, outcome="CONTROLLING" if ctl_val else "MATCH")
                continue
            if field == "legal_name":
                out = compare_names(ctl_val, val)
            elif field == "entity_type":
                out = compare_entity(ctl_val, val)
            elif field == "address":
                ref = master if (master and not master.is_empty()) else ctl.address
                out = compare_address(ref, getattr(s, "address"))
            elif field == "ein":
                out = "MATCH" if norm_digits(val) == norm_digits(ctl_val) else "CONFLICT"
            elif field == "phone":
                out = "MATCH" if norm_digits(val)[-10:] == norm_digits(ctl_val)[-10:] else "CONFLICT"
            elif field in ("website", "email"):
                out = "MATCH" if root_domain(val) == root_domain(ctl_val) else "CONFLICT"
            elif field == "revenue":
                a, b = ctl.revenue or 0, s.revenue or 0
                out = "MATCH" if a and abs(a - b) / a <= 0.05 else ("UNDERSTATED" if b < a else "CONFLICT")
                if a and abs(a - b) / a <= C.REVENUE_MISMATCH_PCT and out != "MATCH":
                    out = "VARIANT"
            elif field == "formation":
                out = "MATCH" if (s.formation_state or "") == (ctl.formation_state or "") and (
                    not s.formation_date or not ctl.formation_date or abs((s.formation_date - ctl.formation_date).days) <= 183) else "CONFLICT"
            elif field == "years_in_business":
                age = _entity_age_years(case, audit_date)
                out = "UNDERSTATED" if (s.years_in_business or 0) < age - 1 else "MATCH"
            elif field == "owners":
                out = "MATCH" if _owner_names(val) == _owner_names(ctl_val) else "CONFLICT"
            else:
                out = compare_simple(ctl_val, val)
            row.cells[s.source] = MatrixCell(value=val, outcome=out)
            if out in ("CONFLICT", "UNDERSTATED"):
                conflicts.append(s)
            elif out == "VARIANT":
                variants.append(s.source)

        # Severity (r3 identity §1.4)
        sev = ""
        if field == "ein" and conflicts:
            sev = "S1"
        elif field == "legal_name" and any(s.tier in ("A", "B") for s in conflicts):
            sev = "S1"
        elif field == "formation" and any(s.tier == "A" for s in conflicts):
            sev = "S1"
        elif field in ("legal_name", "entity_type") and (conflicts or (field == "legal_name" and blanks_c)):
            sev = "S2"
        elif field == "address" and conflicts:
            sev = "S2"
        elif field == "revenue" and conflicts:
            sev = "S2"
        elif field == "naics" and conflicts:
            sev = "S2"
        elif field == "owners" and conflicts:
            sev = "S2"
        elif field == "years_in_business" and any(s.tier == "C" and s.years_in_business == 0 for s in srcs) and _entity_age_years(case, audit_date) >= 1:
            sev = "S2"
            row.note = "A bureau shows 0 years in business for an entity more than a year old."
        elif conflicts:
            sev = "S3"
        elif blanks_c and field in ("phone", "website", "naics", "sic", "employees", "address", "entity_type"):
            sev = "S2" if field in ("address", "entity_type") else "S3"
        elif variants:
            sev = "S3"
        row.severity = sev
        if conflicts and not row.note:
            row.note = "Differs on: " + ", ".join(s.source for s in conflicts)
        if blanks_c and not row.note:
            row.note = "Blank on: " + ", ".join(blanks_c)
        rows.append(row)

    # Address decision S1: no designation while ≥2 distinct candidates exist
    cands = address_candidates(case, audit_date)
    active = [c for c in cands if c.kind == "candidate"]
    if (not master or master.is_empty()) and len(active) >= 2:
        for r in rows:
            if r.field == "address":
                r.severity = "S1"
                r.note = f"{len(active)} active address candidates and no master address designated."
    return rows, names


def _owner_names(s: str) -> set[str]:
    names = set()
    for part in re.split(r"[;,]", s or ""):
        words = [w for w in re.sub(r"\(.*?\)", "", part).upper().split() if len(w) > 1 and w not in ("JR", "SR", "II", "III")]
        if words:
            names.add(words[0] + " " + words[-1])
    return names


def _entity_age_years(case: Case, audit_date: date) -> float:
    fd = case.intake.formation_date or next((s.formation_date for s in case.identity_sources if s.formation_date), None)
    return (audit_date - fd).days / 365.25 if fd else 0


def address_candidates(case: Case, audit_date: date) -> list[AddressCandidate]:
    seen: dict[str, AddressCandidate] = {}
    owner_homes = {norm_address(o.home_address) for o in case.intake.owners if not o.home_address.is_empty()}
    for s in all_sources(case, audit_date):
        if not s.address or s.address.is_empty():
            continue
        key = norm_address(s.address)
        cand = seen.get(key)
        if not cand:
            cand = AddressCandidate(address=s.address.one_line())
            cand.notes.extend(address_flags(s.address))
            if key in owner_homes:
                cand.notes.append("Also the owner's home address (residential)")
            seen[key] = cand
        cand.seen_on.append(s.source)
    for key, cand in seen.items():
        if any("registered agent" in src.lower() for src in cand.seen_on) and len(cand.seen_on) == 1:
            cand.kind = "registered_agent"
        elif any("PMB" in n or "PO box" in n for n in cand.notes):
            cand.kind = "mailbox"
        elif all(src in [r.bureau.value for r in case.commercial_reports] for src in cand.seen_on):
            # appears only on bureau files: a bureau correction unless the client claims it
            cand.kind = "stale"
            cand.notes.append("Appears only on bureau files — likely a bureau correction, not a candidate")
    return sorted(seen.values(), key=lambda c: (c.kind != "candidate", -len(c.seen_on)))


def email_is_free(email: str) -> bool:
    return root_domain(email) in FREE_MAIL
