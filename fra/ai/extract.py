"""AI document reading: one structured extraction per uploaded document, merged into the Case.
The AI only transcribes what the document shows. All judgment happens in the rules engine."""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from fra import config as C
from fra.ai.client import file_block, structured_call
from fra.models import (BankMonth, Bureau, Case, CommercialBureau, CommercialReport, ConsumerCredit, Document,
                        DocType, IdentitySource, TaxReturn)

SYSTEM = """You transcribe financial and business documents into structured data for a funding-readiness analyst.

Rules:
- Record only what the document actually shows. Never infer, estimate, or fill in a value that is not printed.
- Use null for anything not shown. Use an empty string only when the document shows the field and it is blank.
- Copy names, numbers and addresses exactly as printed (do not correct spelling or formatting).
- Dates as YYYY-MM-DD. Money as plain numbers without $ or commas.
- If the document is partly unreadable, lower `confidence` and say what was unreadable in `notes`.
- `confidence` is your 0-1 estimate that every extracted value is correct."""


class BureauCount(BaseModel):
    bureau: Bureau
    tradelines: Optional[int] = None


class ConsumerCreditExtract(BaseModel):
    credit: ConsumerCredit
    summary_counts: list[BureauCount] = Field(default_factory=list, description="Account counts the report's own summary section shows, per bureau")
    confidence: float = 0.0
    notes: str = ""


class CommercialExtract(BaseModel):
    report: CommercialReport
    confidence: float = 0.0
    notes: str = ""


class IdentityExtract(BaseModel):
    identity: IdentitySource
    document_date: Optional[date] = None
    confidence: float = 0.0
    notes: str = ""


class TaxReturnExtract(BaseModel):
    tax_return: TaxReturn
    identity: IdentitySource
    confidence: float = 0.0
    notes: str = ""


class BankStatementExtract(BaseModel):
    months: list[BankMonth]
    identity: IdentitySource = Field(description="Account title (legal name) and statement address as printed")
    confidence: float = 0.0
    notes: str = ""


class FinancialStatementExtract(BaseModel):
    period_end: Optional[date] = None
    revenue: Optional[float] = None
    net_income: Optional[float] = None
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    personal_net_worth: Optional[float] = None
    personal_liquid_assets: Optional[float] = None
    ar_total: Optional[float] = None
    ar_over_90: Optional[float] = None
    dso_days: Optional[float] = None
    confidence: float = 0.0
    notes: str = ""


INSTRUCTIONS = {
    DocType.CONSUMER_CREDIT: (ConsumerCreditExtract,
        "This is a personal consumer credit report (often 3-bureau). Extract every score with its bureau and model "
        "(e.g. FICO8, FICO9, VS3 — use 'unknown' if not labeled), every tradeline with the bureaus it appears on, owner type "
        "(primary/joint/au from ECOA or 'Authorized user'), limit, balance, payment, status, worst late and last late date, "
        "DOFD if shown, every hard inquiry with bureau and date, public records, all name and address variations, employers, "
        "fraud alerts, freezes and consumer statements. Also copy the report's own summary account counts per bureau."),
    DocType.EXPERIAN_BUSINESS: (CommercialExtract, "This is an Experian Business credit report. Bureau = 'Experian Business'. file_id = the BIN."),
    DocType.DNB: (CommercialExtract, "This is a Dun & Bradstreet report. Bureau = 'Dun & Bradstreet'. file_id = the D-U-N-S number. PAYDEX null if not generated."),
    DocType.EQUIFAX_BUSINESS: (CommercialExtract, "This is an Equifax Business/Commercial report. Bureau = 'Equifax Business'. Set insufficient_data=true if Equifax returned insufficient data or no score."),
    DocType.LEXISNEXIS: (CommercialExtract, "This is a LexisNexis business report. Bureau = 'LexisNexis'. Put any second identity, unrelated principal or unexplained address in internal_inconsistencies."),
    DocType.TAX_RETURN: (TaxReturnExtract, "This is a business tax return. Extract tax year, form, gross receipts, net income (ordinary business income), interest, depreciation, amortization, officer compensation, business activity code, plus the name, EIN, address and entity type printed on it. Source = '<year> business tax return (<form>)', tier B."),
    DocType.BANK_STATEMENT: (BankStatementExtract, "This is a business bank statement. One entry per statement month: total deposits (exclude transfers between own accounts if itemized), deposit count, ending balance, average daily balance if printed, NSF/returned items, days with a negative balance, and total loan/MCA debits. Identity = account title and statement address. Source = '<bank> statements', tier B."),
}
IDENTITY_DOCS = {
    DocType.IRS_EIN: "IRS EIN notice. Source = 'IRS CP 575' or 'IRS Letter 147C' (or 'IRS SS-4 (application)'), tier A. Capture legal name, EIN, address and responsible party.",
    DocType.SOS_FILING: "Secretary of State filing or certificate. Source = '<State> SOS <document name>', tier A. Capture legal name, entity type, formation state and date, principal office, registered agent, and managers/members.",
    DocType.OPERATING_AGREEMENT: "Operating agreement / bylaws. Source = 'Operating agreement', tier A. Capture legal name, entity type, owners and percentages (as 'Name (pct%)' separated by ';').",
    DocType.BANK_CERT: "Bank beneficial-ownership certification, W-9 or account profile. Source = 'Bank beneficial-ownership certification' (or 'Bank W-9' / 'Bank account profile'), tier B. Capture the legal entity name, the TIN exactly as written, address, owners/control person.",
    DocType.BUSINESS_LICENSE: "Business license. Source = 'Business license', tier B. Capture name and address on the license.",
    DocType.PROOF_OF_ADDRESS: "Lease or utility bill. Source = 'Proof of address (<type>)', tier B. Capture the name and service address.",
    DocType.UCC_SEARCH: "UCC search result. Put filings in the notes as a list (secured party, filing number, date, collateral).",
}
FIN_DOCS = {
    DocType.PNL: "Profit & loss statement: period end, total revenue, net income.",
    DocType.BALANCE_SHEET: "Balance sheet: date (period_end), total assets, total liabilities, accounts receivable.",
    DocType.PFS: "Personal financial statement: date (period_end), net worth, liquid assets (cash and marketable securities).",
    DocType.AR_AGING: "A/R aging: date (period_end), total receivables, amount over 90 days, DSO if shown.",
}


def extract_document(path: Path, doc: Document, model: Optional[str] = None):
    """Returns (parsed result, usage)."""
    if doc.doc_type in INSTRUCTIONS:
        schema, instr = INSTRUCTIONS[doc.doc_type]
    elif doc.doc_type in IDENTITY_DOCS:
        schema, instr = IdentityExtract, IDENTITY_DOCS[doc.doc_type]
    elif doc.doc_type in FIN_DOCS:
        schema, instr = FinancialStatementExtract, FIN_DOCS[doc.doc_type]
    else:
        schema, instr = IdentityExtract, "Capture any business identity details shown. Source = the document's name, tier B."
    content = [file_block(path), {"type": "text", "text": f"Document type: {doc.doc_type.value}.\n{instr}"}]
    return structured_call(system=SYSTEM, content=content, schema=schema, purpose=f"extract:{doc.doc_type.name}",
                           model=model or C.AI_MODEL, effort=C.AI_EFFORT_EXTRACT)


def apply_extraction(case: Case, doc: Document, result) -> list[str]:
    """Merge an extraction into the case. Returns warnings for the analyst."""
    warnings = []
    doc.extracted = result.model_dump(mode="json")
    doc.extraction_status = "extracted"
    conf = getattr(result, "confidence", 1.0)
    if conf < 0.8:
        doc.extracted["_low_confidence"] = True
        warnings.append(f"Low extraction confidence ({conf:.0%}) — verify the values against {doc.filename}.")
    if getattr(result, "notes", ""):
        doc.extraction_note = result.notes

    if isinstance(result, ConsumerCreditExtract):
        cc = result.credit
        cc.extraction_confidence = conf
        case.consumer_credit = [c for c in case.consumer_credit if c.person != cc.person] + [cc]
        doc.document_date = cc.report_date
        # Confidence gate (RULEBOOK §1.4): extracted counts vs the report's own summary
        for sc in result.summary_counts:
            if sc.tradelines is None:
                continue
            got = sum(1 for t in cc.tradelines if sc.bureau in t.bureaus)
            if abs(got - sc.tradelines) > 1:
                doc.extracted["_low_confidence"] = True
                warnings.append(f"{sc.bureau.value}: extracted {got} accounts but the report summary shows {sc.tradelines}. Review before relying on the analysis.")
    elif isinstance(result, CommercialExtract):
        rep = result.report
        rep.identity.source = rep.bureau.value
        rep.identity.tier = "C"
        case.commercial_reports = [r for r in case.commercial_reports if not (r.bureau == rep.bureau and r.report_date == rep.report_date)] + [rep]
        doc.document_date = rep.report_date
    elif isinstance(result, TaxReturnExtract):
        tr = result.tax_return
        case.financials.tax_returns = [t for t in case.financials.tax_returns if t.year != tr.year] + [tr]
        case.financials.tax_returns.sort(key=lambda t: t.year)
        idn = result.identity
        idn.source = idn.source or f"{tr.year} business tax return ({tr.form})"
        idn.tier, idn.document_id, idn.revenue = "B", doc.id, tr.gross_receipts
        _replace_source(case, idn)
    elif isinstance(result, BankStatementExtract):
        have = {m.month for m in case.financials.bank_months}
        for m in result.months:
            if m.month in have:
                case.financials.bank_months = [x for x in case.financials.bank_months if x.month != m.month]
            case.financials.bank_months.append(m)
        case.financials.bank_months.sort(key=lambda m: m.month)
        idn = result.identity
        idn.tier, idn.document_id = "B", doc.id
        _replace_source(case, idn)
    elif isinstance(result, IdentityExtract):
        idn = result.identity
        idn.document_id = doc.id
        if not idn.as_of:
            idn.as_of = result.document_date
        doc.document_date = result.document_date
        _replace_source(case, idn)
    elif isinstance(result, FinancialStatementExtract):
        f = case.financials
        if doc.doc_type == DocType.PNL:
            f.pnl_period_end, f.pnl_revenue, f.pnl_net_income = result.period_end, result.revenue, result.net_income
        elif doc.doc_type == DocType.BALANCE_SHEET:
            f.balance_sheet_date, f.total_assets, f.total_liabilities = result.period_end, result.total_assets, result.total_liabilities
            f.ar_total = f.ar_total or result.ar_total
        elif doc.doc_type == DocType.PFS:
            f.pfs_date, f.personal_net_worth, f.personal_liquid_assets = result.period_end, result.personal_net_worth, result.personal_liquid_assets
        elif doc.doc_type == DocType.AR_AGING:
            f.ar_total, f.ar_over_90, f.dso_days = result.ar_total, result.ar_over_90, result.dso_days
        doc.document_date = result.period_end
    return warnings


def _replace_source(case: Case, idn: IdentitySource) -> None:
    case.identity_sources = [s for s in case.identity_sources if not (s.document_id and s.document_id == idn.document_id)] + [idn]
