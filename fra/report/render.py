"""Builds the branded FRA report (HTML → PDF with WeasyPrint)."""
from __future__ import annotations

import re
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from fra import content
from fra.engine.results import AuditResult
from fra.models import Case, Status

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE / "templates"
STATIC = HERE / "static"

STATUS_CLASS = {Status.PASS: "pass", Status.NI: "ni", Status.AR: "ar", Status.PEND: "pend", Status.NA: "na"}


def pill_class(status) -> str:
    if isinstance(status, Status):
        return STATUS_CLASS[status]
    s = str(status).upper()
    if s.startswith("STRONG"):
        return "fit-strong"
    if s.startswith("POTENTIAL"):
        return "fit-potential"
    if s.startswith("NOT RECOMMENDED") or s.startswith("LAST RESORT"):
        return "fit-no"
    if s.startswith("NEEDS"):
        return "fit-info"
    return "fit-notyet"


def mask_id(value: str, keep: int = 4) -> str:
    digits = re.sub(r"\D", "", value or "")
    return f"•••••{digits[-keep:]}" if len(digits) > keep else (value or "")


def mask_text(text: str, case: Case) -> str:
    """Mask full EIN/TIN-like numbers in client-facing text (RULEBOOK §13)."""
    def repl(m):
        d = re.sub(r"\D", "", m.group(0))
        return "•••••" + d[-4:]
    return re.sub(r"\b\d{2}-?\d{7}\b", repl, text or "")


def money(v: Optional[float]) -> str:
    if v is None:
        return "—"
    return f"${v:,.0f}"


def effort(n: int) -> str:
    return {1: "≈ 2–4 weeks", 15: "≈ 2–8 weeks", 20: "≈ 4–8 weeks", 12: "≈ 3–6 months", 10: "≈ 1–2 weeks", 8: "≈ 1 week",
            6: "≈ 1–2 weeks", 14: "≈ 2–4 weeks", 4: "≈ 2–6 weeks", 17: "≈ 2–6 weeks", 11: "≈ 4–8 weeks"}.get(n, "≈ 1–4 weeks")


def roadmap_svg(result: AuditResult, report_date: date) -> str:
    """Gantt-style roadmap (r3 report spec §3.10)."""
    phases = [(1, "Identity & documents", 0, 2), (2, "Propagate corrections", 2, 6), (3, "Verify & build depth", 6, 12), (4, "Reassess & apply", 12, 20)]
    used = {a.phase for a in result.actions if a.path != "COMPLETED IN FRA"}
    W, left, top, lane = 680, 150, 34, 30
    weeks = 20
    x = lambda w: left + (W - left - 10) * w / weeks
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {top + lane * 4 + 40}" width="100%" font-family="Lato, Arial" font-size="9">']
    for w in range(0, weeks + 1, 2):
        parts.append(f'<line x1="{x(w)}" y1="{top - 6}" x2="{x(w)}" y2="{top + lane * 4}" stroke="#D9DEE5" stroke-width="0.6"/>')
        parts.append(f'<text x="{x(w)}" y="{top - 10}" text-anchor="middle" fill="#6B7280" font-size="7.5">Wk {w}</text>')
    for i, (n, name, a, b) in enumerate(phases):
        y = top + i * lane
        parts.append(f'<text x="0" y="{y + 18}" fill="#1B3A66" font-weight="700">Phase {n}</text>')
        parts.append(f'<text x="44" y="{y + 18}" fill="#1F2937">{name}</text>')
        fill = "#1B3A66" if n in used or n == 4 else "#C9D2DF"
        parts.append(f'<rect x="{x(a)}" y="{y + 6}" width="{x(b) - x(a)}" height="17" rx="2" fill="{fill}"/>')
        cnt = sum(1 for act in result.actions if act.phase == n and act.path != "COMPLETED IN FRA")
        if cnt:
            parts.append(f'<text x="{x(a) + 5}" y="{y + 18}" fill="#fff" font-size="8">{cnt} item{"s" if cnt != 1 else ""}</text>')
    win = 8 if any(f.status == Status.AR for f in result.findings) else 2
    parts.append(f'<line x1="{x(win)}" y1="{top - 4}" x2="{x(win)}" y2="{top + lane * 4 + 4}" stroke="#B58A2E" stroke-width="1.6" stroke-dasharray="4 3"/>')
    d = report_date + timedelta(weeks=win)
    parts.append(f'<text x="{x(win) + 4}" y="{top + lane * 4 + 16}" fill="#B58A2E" font-weight="700" font-size="8.5">Earliest application window ≈ {d:%b %d, %Y} (after corrections post)</text>')
    parts.append(f'<polygon points="{x(12)},{top + lane * 3 + 2} {x(12) + 5},{top + lane * 3 + 8} {x(12)},{top + lane * 3 + 14} {x(12) - 5},{top + lane * 3 + 8}" fill="#B58A2E"/>')
    parts.append(f'<text x="{x(0) + 2}" y="{top + lane * 4 + 30}" fill="#2E5C8A" font-size="8">▲ You are here: {report_date:%b %d, %Y}. Dates are estimates and depend on third-party processing times.</text>')
    parts.append("</svg>")
    return "".join(parts)


def fallback_narrative(case: Case, r: AuditResult) -> dict[str, str]:
    """Rule-based text used when the AI draft is not available. The analyst can edit any of it."""
    it = case.intake
    n_ar = r.status_counts.get(Status.AR.value, 0)
    s1 = [m.label for m in r.matrix if m.severity == "S1"]
    g = r.guarantor
    strong_fin = any(t.gross_receipts for t in case.financials.tax_returns)
    if strong_fin and n_ar:
        assess = "Documented operating profile — business-identity and commercial-credit corrections required before applying"
    elif n_ar:
        assess = "Corrections required before lender submission"
    else:
        assess = "Lender-ready profile — confirm pending items before applying"
    first = ", ".join(a.item.lower() for a in r.first_three[:3])
    glance = (f"Your business has real strengths to lead with. Before you apply, {len(r.first_three)} items need attention first: {first}. "
              f"{n_ar} of the 20 audit points need action, and most are record corrections that can be finished in weeks, not months.") if r.first_three else \
             "Your file is in good shape. Confirm the pending items below, then follow the roadmap to apply in the right order."
    story_bits = []
    trs = sorted(case.financials.tax_returns, key=lambda t: t.year)
    if trs:
        rev = ", ".join(f"{t.year}: {money(t.gross_receipts)}" for t in trs if t.gross_receipts)
        story_bits.append(f"Federal returns document revenue ({rev})" + (f" with net profit of {money(trs[-1].net_income)} in {trs[-1].year}." if trs[-1].net_income else "."))
    if g and g.mid_score:
        story_bits.append(f"The guarantor's middle FICO score is {g.mid_score}" + (f" with revolving utilization near {g.util_overall:.1%}" if g.util_overall is not None else "") + ".")
    if s1:
        story_bits.append(f"The main weakness is record consistency ({', '.join(s1).lower()}), not credit performance — and record accuracy is fixable in weeks.")
    elif n_ar:
        story_bits.append("The open items are mostly record and verification corrections rather than credit-performance problems.")
    story = " ".join(story_bits) or "The documents reviewed so far do not yet support a full underwriting story; see the pending items."
    concl = (f"This audit reviewed {it.legal_name or 'the business'} the way a lender would. "
             f"{r.status_counts.get(Status.PASS.value, 0)} of 20 points pass, {n_ar} need action and {r.status_counts.get(Status.PEND.value, 0)} are pending documents or checks. "
             + (f"Start with: {first}. " if first else "")
             + ("The composite Funding Readiness Score is withheld until the file is complete; it can be issued at reassessment. " if not r.composite.issued else f"The composite Funding Readiness Score is {r.composite.score} ({r.composite.tier}). ")
             + "Work the Action Center in order, apply only when the roadmap's application window opens, and request a reassessment once corrections have posted.")
    narr = {"cover_assessment": assess, "glance_meaning": glance, "central_story": story, "conclusion": concl,
            "funding_implications": "Each bureau is read separately — a correction at one does not reach the others. Fix identity fields first; new reporting accounts attach to whatever record the furnisher matches."}
    for a in r.areas:
        narr[f"area_{a.key}"] = a.narrative
    return narr


def build_context(case: Case, r: AuditResult, narr: Optional[dict] = None) -> dict:
    base = fallback_narrative(case, r)
    base.update({k: v for k, v in (narr or {}).items() if v})
    base.update({k: v for k, v in case.narrative_overrides.items() if v})
    it = case.intake
    owner = it.owners[0] if it.owners else None
    rd = case.meta.report_date or r.audit_date
    used_terms = set()
    body_text = " ".join(f.found + f.correction for f in r.findings).lower()
    glossary = [(t, d) for t, d in content.GLOSSARY if any(w in body_text for w in re.findall(r"[a-z0-9]{3,}", t.lower())[:1])] or content.GLOSSARY
    glossary = sorted(content.GLOSSARY, key=lambda x: x[0].lower())
    done = sum(1 for a in r.actions if a.path == "COMPLETED IN FRA")
    open_actions = [a for a in r.actions if a.path != "COMPLETED IN FRA"]
    return {
        "case": case, "r": r, "it": it, "owner": owner, "meta": case.meta, "narr": base,
        "report_date": rd, "stage": case.meta.stage, "final": case.meta.stage == "FINAL CLIENT DELIVERY",
        "rev_label": f"Rev {case.meta.revision}" if case.meta.stage == "FINAL CLIENT DELIVERY" else f"Draft d.{case.meta.revision}",
        "Status": Status, "pill": pill_class, "money": money, "mask_id": mask_id, "mask": lambda t: mask_text(t, case),
        "effort": effort, "points": content.POINTS, "glossary": glossary, "resources": content.RESOURCE_DIRECTORY,
        "disclosures": content.DISCLOSURES, "disclaimer": content.DISCLAIMER_SHORT,
        "roadmap": roadmap_svg(r, rd), "done_actions": [a for a in r.actions if a.path == "COMPLETED IN FRA"],
        "open_actions": open_actions, "done_count": done, "total_actions": len(r.actions),
        "products": [p for p in r.products if p.in_goal or not it.funding.product_types or p.fit in ("STRONG FIT", "POTENTIAL FIT") or p.fit.startswith(("STRONG", "POTENTIAL"))],
        "findings_detail": r.findings,
        "explain": content.SCORE_EXPLAIN,
    }


def _env() -> Environment:
    env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(["html"]), trim_blocks=True, lstrip_blocks=True)
    env.filters["money"] = money
    env.filters["d"] = lambda v, fmt="%m/%d/%Y": v.strftime(fmt) if v else "—"
    env.filters["pct"] = lambda v, n=1: f"{v:.{n}%}" if v is not None else "—"
    return env


def render_html(case: Case, r: AuditResult, narr: Optional[dict] = None) -> str:
    return _env().get_template("report.html").render(**build_context(case, r, narr))


def render_pdf(case: Case, r: AuditResult, narr: Optional[dict] = None, out: Optional[Path] = None) -> bytes:
    from weasyprint import HTML
    html = render_html(case, r, narr)
    pdf = HTML(string=html, base_url=str(STATIC)).write_pdf()
    if out:
        Path(out).write_bytes(pdf)
    return pdf


def find_forbidden(text: str) -> list[str]:
    low = text.lower()
    return [p for p in content.FORBIDDEN_PHRASES if re.search(r"\b" + re.escape(p) + r"\b", low)]
