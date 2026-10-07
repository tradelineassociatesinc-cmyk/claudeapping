"""Data model for a Funding Readiness Audit case.

A Case holds everything an analyst enters or the AI extracts for one client:
intake answers, uploaded documents, extracted bureau and financial data,
analyst research findings, and analyst overrides. The rules engine reads a
Case and produces an AuditResult; the report renderer turns both into a PDF.
"""
from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Shared enums
# ---------------------------------------------------------------------------

class Status(str, Enum):
    PASS = "PASS"
    NI = "NEEDS IMPROVEMENT"
    AR = "ACTION REQUIRED"
    PEND = "PENDING / NEED DOCUMENT"
    NA = "N/A"


# Worst-first order used for roll-ups (N/A is ignored in roll-ups).
STATUS_SEVERITY = {Status.AR: 4, Status.PEND: 3, Status.NI: 2, Status.PASS: 1, Status.NA: 0}


class Bureau(str, Enum):
    EXPERIAN = "Experian"
    EQUIFAX = "Equifax"
    TRANSUNION = "TransUnion"


class CommercialBureau(str, Enum):
    EXPERIAN = "Experian Business"
    DNB = "Dun & Bradstreet"
    EQUIFAX = "Equifax Business"
    LEXISNEXIS = "LexisNexis"


class Address(BaseModel):
    line1: str = ""
    line2: str = ""
    city: str = ""
    state: str = ""
    zip: str = ""
    country: str = "US"

    def one_line(self) -> str:
        parts = [self.line1, self.line2, self.city, f"{self.state} {self.zip}".strip()]
        return ", ".join(p for p in parts if p)

    def is_empty(self) -> bool:
        return not (self.line1 or self.city or self.zip)


# ---------------------------------------------------------------------------
# Intake (current FRA web form + funding-goal additions from RULEBOOK §5)
# ---------------------------------------------------------------------------

class Owner(BaseModel):
    first_name: str = ""
    last_name: str = ""
    ownership_pct: Optional[float] = None
    title: str = ""
    phone: str = ""
    email: str = ""
    home_address: Address = Field(default_factory=Address)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


class DebtItem(BaseModel):
    lender: str = ""
    kind: str = ""  # term, LOC, MCA, equipment, SBA, EIDL, business card, other
    balance: Optional[float] = None
    payment: Optional[float] = None
    frequency: str = "monthly"  # monthly, weekly, daily
    opened: Optional[date] = None
    secured: Optional[bool] = None


class UseOfFunds(BaseModel):
    purpose: str
    amount: Optional[float] = None


class FundingGoal(BaseModel):
    product_types: list[str] = Field(default_factory=list)  # product codes, or "NOT_SURE"
    amount_requested: Optional[float] = None
    amount_minimum: Optional[float] = None
    uses: list[UseOfFunds] = Field(default_factory=list)
    timeline: str = ""  # e.g. "1-3 months"
    for_whom: str = "business"  # personal, business, property, both
    priorities: list[str] = Field(default_factory=list)
    willing_pg: Optional[bool] = None
    collateral: list[str] = Field(default_factory=list)
    repayment_source: str = ""
    recent_applications: str = ""
    pending_applications: str = ""
    notes: str = ""


class Intake(BaseModel):
    # Section 1: Business owner
    owners: list[Owner] = Field(default_factory=lambda: [Owner()])
    # Section 2: Business information
    legal_name: str = ""
    dba: str = ""
    ein: str = ""
    entity_type: str = ""
    formation_state: str = ""
    formation_date: Optional[date] = None
    operations_start_date: Optional[date] = None
    business_address: Address = Field(default_factory=Address)
    business_phone: str = ""
    business_email: str = ""
    business_description: str = ""
    website: str = ""
    # Section 3: Banking & debt
    primary_bank: str = ""
    bank_account_age: str = ""  # <3m, 3-6m, 6-12m, 1-2y, 2y+
    existing_debt_types: list[str] = Field(default_factory=list)
    total_business_debt: Optional[float] = None
    avg_30day_balance: Optional[float] = None
    banking_relationships: str = ""
    banking_problems: Optional[bool] = None
    banking_problems_detail: str = ""
    debts: list[DebtItem] = Field(default_factory=list)
    # Section 4: Business credit IDs
    naics: str = ""
    sic: str = ""
    duns: str = ""
    experian_bin: str = ""
    equifax_commercial_id: str = ""
    # Added: revenue and income (needed by the funding analysis)
    revenue_last_year: Optional[float] = None
    revenue_prior_year: Optional[float] = None
    revenue_ytd: Optional[float] = None
    avg_monthly_deposits: Optional[float] = None
    employees: Optional[int] = None
    personal_income: Optional[float] = None
    housing_payment: Optional[float] = None
    # Added: eligibility attestations (only used where the product needs them)
    tax_liens_or_judgments: Optional[bool] = None
    federal_debt_delinquent: Optional[bool] = None
    sba_citizenship_ok: Optional[bool] = None
    # Funding goal
    funding: FundingGoal = Field(default_factory=FundingGoal)


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------

class DocType(str, Enum):
    CONSUMER_CREDIT = "Consumer credit report (3-bureau)"
    EXPERIAN_BUSINESS = "Experian Business report"
    DNB = "Dun & Bradstreet report"
    EQUIFAX_BUSINESS = "Equifax Business report"
    LEXISNEXIS = "LexisNexis business report"
    IRS_EIN = "IRS EIN notice (CP 575 / 147C / SS-4)"
    SOS_FILING = "Secretary of State filing / certificate"
    OPERATING_AGREEMENT = "Operating agreement / bylaws"
    BANK_CERT = "Bank beneficial-ownership cert / W-9 / account profile"
    BANK_STATEMENT = "Business bank statement"
    TAX_RETURN = "Business tax return"
    PNL = "Profit & loss statement"
    BALANCE_SHEET = "Balance sheet"
    PFS = "Personal financial statement"
    AR_AGING = "A/R aging report"
    DEBT_SCHEDULE = "Business debt schedule"
    BUSINESS_LICENSE = "Business license"
    UCC_SEARCH = "UCC search / filing"
    PROOF_OF_ADDRESS = "Proof of business address (lease / utility)"
    OTHER = "Other"


class Document(BaseModel):
    id: str
    filename: str
    doc_type: DocType
    uploaded_at: datetime = Field(default_factory=datetime.now)
    document_date: Optional[date] = None
    extraction_status: str = "not_extracted"  # not_extracted, extracted, failed, manual
    extraction_note: str = ""
    extracted: dict = Field(default_factory=dict)  # raw AI output, kept for audit trail


# ---------------------------------------------------------------------------
# Identity sources (one record per document/source that states identity data)
# ---------------------------------------------------------------------------

IDENTITY_FIELDS = [
    ("legal_name", "Legal name"),
    ("dba", "DBA"),
    ("entity_type", "Entity type"),
    ("formation", "State / formation date"),
    ("ein", "EIN / TIN"),
    ("address", "Business address"),
    ("phone", "Phone"),
    ("email", "Email"),
    ("website", "Website / domain"),
    ("naics", "NAICS"),
    ("sic", "SIC"),
    ("revenue", "Annual revenue"),
    ("employees", "Employees"),
    ("owners", "Owners"),
    ("years_in_business", "Years in business"),
]


class IdentitySource(BaseModel):
    """Identity fields as one source shows them. Empty string = blank on that source;
    a field listed in `not_shown` means the source does not carry that field at all."""
    source: str  # e.g. "IRS CP 575", "Texas SOS", "Experian Business", "Intake"
    tier: str = "E"  # A authoritative, B institutional, C bureau, D self-published, E client
    as_of: Optional[date] = None
    document_id: Optional[str] = None
    legal_name: Optional[str] = None
    dba: Optional[str] = None
    entity_type: Optional[str] = None
    formation_state: Optional[str] = None
    formation_date: Optional[date] = None
    ein: Optional[str] = None
    address: Optional[Address] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    naics: Optional[str] = None
    sic: Optional[str] = None
    revenue: Optional[float] = None
    employees: Optional[int] = None
    owners: Optional[str] = None
    years_in_business: Optional[float] = None


# ---------------------------------------------------------------------------
# Consumer credit (guarantor)
# ---------------------------------------------------------------------------

class CreditScore(BaseModel):
    bureau: Bureau
    value: int
    model: str = "unknown"  # FICO8, FICO9, FICO10T, FICO2/4/5, VS3, VS4, unknown
    score_date: Optional[date] = None

    @property
    def fico_eligible(self) -> bool:
        return self.model.upper().startswith("FICO")


class Tradeline(BaseModel):
    creditor: str
    bureaus: list[Bureau] = Field(default_factory=list)
    account_type: str = "revolving"  # revolving, installment, mortgage, open, charge, collection
    owner_type: str = "primary"  # primary, joint, au, business, terminated
    open_date: Optional[date] = None
    closed: bool = False
    credit_limit: Optional[float] = None
    high_credit: Optional[float] = None
    balance: Optional[float] = None
    payment: Optional[float] = None
    status: str = "current"  # current, late30, late60, late90, late120, collection, chargeoff, repo, foreclosure, paid_collection, paid_chargeoff
    worst_late: Optional[int] = None  # 30/60/90/120 days, worst in history shown
    last_late_date: Optional[date] = None
    late_count_24m: int = 0
    dofd: Optional[date] = None
    medical: bool = False
    disputed: bool = False
    original_amount: Optional[float] = None
    last_reported: Optional[date] = None


class Inquiry(BaseModel):
    creditor: str
    bureau: Bureau
    inquiry_date: date
    kind: str = "unknown"  # card_issuer, bank, fintech, mca_iso, auto, mortgage, student, personal_loan, unknown


class PublicRecord(BaseModel):
    kind: str  # bankruptcy7, bankruptcy13, judgment, tax_lien
    filed: Optional[date] = None
    status: str = ""  # filed, discharged, dismissed, satisfied
    status_date: Optional[date] = None
    amount: Optional[float] = None


class ConsumerCredit(BaseModel):
    person: str = ""
    report_date: Optional[date] = None
    source: str = ""  # e.g. "myFICO 3B", "lender tri-merge"
    scores: list[CreditScore] = Field(default_factory=list)
    tradelines: list[Tradeline] = Field(default_factory=list)
    inquiries: list[Inquiry] = Field(default_factory=list)
    public_records: list[PublicRecord] = Field(default_factory=list)
    names: list[str] = Field(default_factory=list)
    addresses: list[str] = Field(default_factory=list)
    employers: list[str] = Field(default_factory=list)
    fraud_alert: bool = False
    freeze_bureaus: list[Bureau] = Field(default_factory=list)
    identity_flags: list[str] = Field(default_factory=list)  # analyst-noted SSN/DOB/name issues
    consumer_statements: list[str] = Field(default_factory=list)
    extraction_confidence: Optional[float] = None


# ---------------------------------------------------------------------------
# Commercial bureau reports
# ---------------------------------------------------------------------------

class BusinessScore(BaseModel):
    name: str  # e.g. "Intelliscore Plus V2", "PAYDEX", "Failure Score"
    value: Optional[float] = None  # None = not generated
    scale: str = ""  # "1-100", "1-1,000"
    risk_class: str = ""  # e.g. "Medium", "Class 3"
    note: str = ""


class BusinessTradeline(BaseModel):
    creditor_category: str = ""
    terms: str = ""
    high_credit: Optional[float] = None
    balance: Optional[float] = None
    dbt: Optional[int] = None  # days beyond terms
    last_reported: Optional[date] = None
    status: str = ""


class UCCFiling(BaseModel):
    secured_party: str
    filing_number: str = ""
    filing_date: Optional[date] = None
    state: str = ""
    collateral: str = ""  # free text as filed
    collateral_class: str = ""  # specific, blanket, accounts, mca_factor, unknown
    status: str = "active"  # active, lapsed, terminated
    debtor_name_as_filed: str = ""
    debtor_address_as_filed: str = ""


class CommercialReport(BaseModel):
    bureau: CommercialBureau
    report_date: Optional[date] = None
    file_id: str = ""  # BIN, D-U-N-S, Equifax ID
    file_found: bool = True
    insufficient_data: bool = False
    scores: list[BusinessScore] = Field(default_factory=list)
    tradelines: list[BusinessTradeline] = Field(default_factory=list)
    inquiries_count: Optional[int] = None
    ucc_filings: list[UCCFiling] = Field(default_factory=list)
    derogatories: list[str] = Field(default_factory=list)  # judgments, liens, collections, bankruptcies
    identity: IdentitySource = Field(default_factory=lambda: IdentitySource(source="bureau", tier="C"))
    internal_inconsistencies: list[str] = Field(default_factory=list)
    notes: str = ""


# ---------------------------------------------------------------------------
# Financials
# ---------------------------------------------------------------------------

class TaxReturn(BaseModel):
    year: int
    form: str = ""  # 1120S, 1065, 1120, Schedule C
    gross_receipts: Optional[float] = None
    net_income: Optional[float] = None
    interest: Optional[float] = None
    depreciation: Optional[float] = None
    amortization: Optional[float] = None
    officer_comp: Optional[float] = None
    business_code: str = ""


class BankMonth(BaseModel):
    month: str  # YYYY-MM
    bank: str = ""
    deposits: Optional[float] = None
    deposit_count: Optional[int] = None
    ending_balance: Optional[float] = None
    avg_daily_balance: Optional[float] = None
    nsf_count: int = 0
    negative_days: int = 0
    loan_or_mca_debits: Optional[float] = None


class Financials(BaseModel):
    tax_returns: list[TaxReturn] = Field(default_factory=list)
    pnl_period_end: Optional[date] = None
    pnl_revenue: Optional[float] = None
    pnl_net_income: Optional[float] = None
    balance_sheet_date: Optional[date] = None
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    pfs_date: Optional[date] = None
    personal_net_worth: Optional[float] = None
    personal_liquid_assets: Optional[float] = None
    ar_total: Optional[float] = None
    ar_over_90: Optional[float] = None
    dso_days: Optional[float] = None
    bank_months: list[BankMonth] = Field(default_factory=list)
    consistency_notes: list[str] = Field(default_factory=list)  # analyst-noted doc disagreements


# ---------------------------------------------------------------------------
# Analyst research (external lookups the tool cannot do itself)
# ---------------------------------------------------------------------------

RESEARCH_ITEMS = {
    "sos_status": "Secretary of State status search (entity active / in good standing)",
    "registered_agent": "Registered agent on current SOS record",
    "licensing": "Licensing applicability research (state / county / city / industry)",
    "listing_411": "411 / directory listing for the business phone",
    "domain": "Domain registration (RDAP / WHOIS) and ownership",
    "email_domain": "Professional email on the business domain (MX check)",
    "website": "Website live, matches legal name / address / phone",
    "gbp": "Google Business Profile search and verification status",
    "foreign_qualification": "Foreign qualification needed in other states?",
    "ucc_search": "UCC debtor search (formation state + operating state)",
    "duplicate_files": "Duplicate business file search at each bureau",
    "lexisnexis": "LexisNexis business file obtained",
}


class ResearchFinding(BaseModel):
    item: str
    result: str = "not_started"  # not_started, found_ok, found_issue, not_found, not_applicable
    finding: str = ""
    checked_on: Optional[date] = None
    analyst: str = ""


# ---------------------------------------------------------------------------
# Analyst overrides and report metadata
# ---------------------------------------------------------------------------

class PointOverride(BaseModel):
    status: Optional[Status] = None
    finding: str = ""
    note: str = ""  # internal reason for the override (logged)


class ReportMeta(BaseModel):
    report_number: str = ""
    revision: int = 0
    stage: str = "DRAFT"  # DRAFT, IN REVIEW, FINAL CLIENT DELIVERY
    analyst: str = ""
    report_date: Optional[date] = None
    master_address_designation: Optional[Address] = None  # chosen by the client, never by TLA
    change_log: list[str] = Field(default_factory=list)


class Case(BaseModel):
    id: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    intake: Intake = Field(default_factory=Intake)
    documents: list[Document] = Field(default_factory=list)
    identity_sources: list[IdentitySource] = Field(default_factory=list)
    consumer_credit: list[ConsumerCredit] = Field(default_factory=list)
    commercial_reports: list[CommercialReport] = Field(default_factory=list)
    financials: Financials = Field(default_factory=Financials)
    research: dict[str, ResearchFinding] = Field(default_factory=dict)
    overrides: dict[str, PointOverride] = Field(default_factory=dict)
    narrative_overrides: dict[str, str] = Field(default_factory=dict)  # analyst-edited AI text
    meta: ReportMeta = Field(default_factory=ReportMeta)
    ai_usage: list[dict] = Field(default_factory=list)  # per-call token/cost log

    @property
    def display_name(self) -> str:
        return self.intake.legal_name or f"Case {self.id}"
