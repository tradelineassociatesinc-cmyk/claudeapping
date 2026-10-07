"""AI drafting of the report's narrative fields from the engine's output (never from raw documents).
Rules: r3_report_spec.md §4–§5 and RULEBOOK §12. Every draft is checked before it can be used."""
from __future__ import annotations

import json
import re
from typing import Optional

from pydantic import BaseModel, Field

from fra import config as C
from fra.ai.client import structured_call
from fra.content import FORBIDDEN_PHRASES
from fra.engine.results import AuditResult
from fra.models import Case, Status

SYSTEM = """You write the narrative sections of a Funding Readiness Audit (FRA) report for Tradeline Associates Inc., a funding-readiness consulting firm. The reader is a small-business owner, not a finance expert.

Voice: direct, respectful, calm. No blame, no alarm words ("serious", "critical", "red flag"), no hype. Plain English at about an 8th-grade reading level for the "plain" fields; clear professional prose elsewhere. Use "you" and "your business".

Hard rules — breaking any of these makes the draft unusable:
1. Use ONLY facts, numbers, dates and names in the FACT SHEET. Never invent or estimate a figure. If a fact is missing, say it is pending.
2. Never guarantee or predict approval, funding, amounts, rates or terms. Ranges are "indicative" and are never added together.
3. Never suggest disputing accurate information, removing accurate negative items, "609 letters", pay-for-delete, CPNs, new credit identities, or any misrepresentation (income, time in business, addresses, revenue).
4. Never recommend buying authorized-user tradelines or aged/shelf companies to appear older.
5. When two documents disagree, state the disagreement; do not decide which is right. TLA does not select the client's master address.
6. No legal, tax or accounting conclusions. Refer those to the client's professional.
7. Do not repeat full tax IDs or account numbers; the fact sheet already masks them.
8. Do not mention SBSS scores.
Respect each field's length limit."""


class PlainLine(BaseModel):
    point: int
    text: str = Field(description="One sentence, ≤30 words, ≤8th-grade reading level: what this finding means for the client")


class ProductLine(BaseModel):
    code: str
    text: str = Field(description="≤60 words: why this product fits or not yet, using only fact-sheet facts")


class NarrativeDraft(BaseModel):
    cover_assessment: str = Field(description="≤25 words: overall assessment for the cover page")
    glance_meaning: str = Field(description="2–3 sentences, 8th-grade level: what this whole audit means for the client")
    central_story: str = Field(description="90–140 words: the central underwriting story — strengths first, then the root cause of what remains")
    area_legal: str = Field(description="≤60 words")
    area_credit: str = Field(description="≤60 words")
    area_banking: str = Field(description="≤60 words")
    area_guarantor: str = Field(description="≤60 words")
    area_goal: str = Field(description="≤60 words")
    action_1: str = Field(description="≤45 words: what to do for First Action 1 and why it gates the rest")
    action_2: str = Field(description="≤45 words")
    action_3: str = Field(description="≤45 words")
    funding_implications: str = Field(description="≤70 words: what the business bureau findings mean for funding")
    conclusion: str = Field(description="≤180 words, no new facts: summary and next steps")
    plain: list[PlainLine]
    products: list[ProductLine]


def fact_sheet(case: Case, r: AuditResult) -> dict:
    """Masked, engine-derived facts. The AI never sees raw documents or full identifiers."""
    it = case.intake
    g = r.guarantor
    fs = {
        "business": {"legal_name": it.legal_name, "entity_type": it.entity_type, "formation_state": it.formation_state,
                     "formation_date": str(it.formation_date) if it.formation_date else None,
                     "description": it.business_description, "naics": it.naics},
        "owner": {"name": it.owners[0].full_name if it.owners else None, "ownership_pct": it.owners[0].ownership_pct if it.owners else None},
        "funding_goal": {"amount_requested": it.funding.amount_requested, "amount_minimum": it.funding.amount_minimum,
                         "uses": [u.model_dump() for u in it.funding.uses], "timeline": it.funding.timeline,
                         "repayment_source": it.funding.repayment_source, "products_selected": it.funding.product_types},
        "tax_returns": [{"year": t.year, "form": t.form, "gross_receipts": t.gross_receipts, "net_income": t.net_income} for t in case.financials.tax_returns],
        "ytd": {"through": str(case.financials.pnl_period_end) if case.financials.pnl_period_end else None, "revenue": case.financials.pnl_revenue, "net_income": case.financials.pnl_net_income},
        "personal_net_worth": case.financials.personal_net_worth,
        "bank_statement_months": len({m.month for m in case.financials.bank_months}),
        "status_counts": r.status_counts,
        "points": [{"point": f.number, "title": f.title, "status": f.status.value, "finding": f.one_line, "detail": f.found} for f in r.findings],
        "areas": [{"area": a.name, "status": a.status.value, "engine_summary": a.narrative} for a in r.areas],
        "first_three_actions": [{"n": a.priority, "title": a.item, "what": a.what, "ref": a.ref} for a in r.first_three],
        "identity_conflicts": [{"field": m.label, "severity": m.severity, "note": m.note} for m in r.matrix if m.severity in ("S1", "S2")],
        "bureaus": [{"bureau": c.bureau, "status": c.status.value, "metrics": [f"{m.label}: {m.value}" for m in c.metrics], "corrections": c.corrections[:6]} for c in r.bureau_cards],
        "guarantor": None if not g else {"middle_fico": g.mid_score, "scores": g.scores, "utilization": round(g.util_overall, 3) if g.util_overall is not None else None,
                                          "collections": g.collections, "public_records": g.public_records, "lates_12m": g.lates_12m,
                                          "recent_lates": g.recent_lates, "flags": g.flags, "status": g.status.value},
        "products": [{"code": p.code, "name": p.name, "fit": p.fit, "in_goal": p.in_goal, "range": [p.range_low, p.range_high] if p.range_high else None,
                      "reasons": p.reasons, "blockers": p.blockers, "earliest_ready": str(p.earliest_ready) if p.earliest_ready else None} for p in r.products],
        "composite": {"issued": r.composite.issued, "score": r.composite.score, "tier": r.composite.tier, "withheld_unlocks": r.composite.unlocks},
        "review_items": [{"title": h.title, "reason": h.reason} for h in r.review_items],
    }
    return fs


def draft_narrative(case: Case, r: AuditResult, model: Optional[str] = None) -> tuple[dict[str, str], dict, list[str]]:
    """Returns (narrative fields, usage record, warnings)."""
    fs = fact_sheet(case, r)
    non_pass = [f.number for f in r.findings if f.status not in (Status.PASS, Status.NA)]
    prompt = (f"FACT SHEET (JSON):\n{json.dumps(fs, default=str, indent=1)}\n\n"
              f"Write the narrative fields. Write `plain` lines for points {non_pass}. "
              f"Write `products` lines for: {[p.code for p in r.products]}.")
    draft, usage = structured_call(system=SYSTEM, content=[{"type": "text", "text": prompt}], schema=NarrativeDraft,
                                   purpose="narrative", model=model or C.AI_MODEL, effort=C.AI_EFFORT_NARRATIVE, max_tokens=32000)
    out = {k: v for k, v in draft.model_dump().items() if isinstance(v, str)}
    for pl in draft.plain:
        out[f"plain_{pl.point}"] = pl.text
    for pr in draft.products:
        out[f"product_{pr.code}"] = pr.text
    warnings = check_narrative(out, fs)
    return out, usage, warnings


def check_narrative(fields: dict[str, str], fs: dict) -> list[str]:
    """Flags forbidden phrases and numbers that do not appear in the fact sheet."""
    warnings = []
    facts = json.dumps(fs, default=str)
    def norm(n: str) -> str:
        n = re.sub(r"[,$\s]", "", n).rstrip(".")
        return n[:-2] if n.endswith(".0") else n
    fact_nums = {norm(n) for n in re.findall(r"\d[\d,]*\.?\d*", facts)}
    for key, text in fields.items():
        low = text.lower()
        for p in FORBIDDEN_PHRASES:
            if re.search(r"\b" + re.escape(p) + r"\b", low):
                warnings.append(f"{key}: contains a prohibited phrase (\"{p}\") — rewrite before release.")
        for m in re.findall(r"\$?\d[\d,]*\.?\d*\s?(?:MM|K|M|%)?", text):
            raw = re.sub(r"[,$\s]", "", m).rstrip(".")
            core = norm(re.sub(r"(MM|K|M|%)$", "", raw))
            if not core or len(core.replace(".", "")) <= 2:
                continue  # small counts and years-of-ages are too ambiguous to check
            if core in fact_nums or core.rstrip("0").rstrip(".") in fact_nums:
                continue
            if raw.endswith(("K", "MM", "M", "%")):
                continue  # rounded display values; analyst checks against tiles
            if re.fullmatch(r"(19|20)\d\d", core):
                continue
            warnings.append(f"{key}: the number \"{m.strip()}\" does not appear in the source facts — verify it.")
    return warnings
