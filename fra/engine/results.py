"""Output types of the rules engine. The report renderer reads only these."""
from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from fra.models import Status


class Finding(BaseModel):
    """One of the 20 audit points, written as the five-part finding card."""
    number: int
    title: str
    status: Status
    one_line: str = ""
    found: str = ""
    why: str = ""
    correction: str = ""
    where_fix: str = ""
    pass_standard: str = ""
    plain: str = ""  # "What this means for you" (one sentence)
    what_it_is: str = ""  # glossary-style explanation of the point
    sources: list[str] = Field(default_factory=list)
    tier: int = 7  # impact tier T1..T7 (r3 identity §5.1)
    overridden: bool = False
    insufficient_data: bool = False


class MatrixCell(BaseModel):
    value: str = ""
    outcome: str = "NOT AVAILABLE"  # MATCH, EQUIVALENT, VARIANT, BLANK, CONFLICT, NOT AVAILABLE, CONTROLLING


class MatrixRow(BaseModel):
    field: str
    label: str
    controlling_source: str = ""
    controlling_value: str = ""
    cells: dict[str, MatrixCell] = Field(default_factory=dict)  # source -> cell
    severity: str = ""  # S1..S4 or ""
    note: str = ""


class AddressCandidate(BaseModel):
    address: str
    seen_on: list[str] = Field(default_factory=list)
    kind: str = "candidate"  # candidate, residential, registered_agent, stale, mailbox
    notes: list[str] = Field(default_factory=list)


class Metric(BaseModel):
    label: str
    value: str
    sub: str = ""


class BureauCard(BaseModel):
    bureau: str
    file_id: str = ""
    report_date: Optional[date] = None
    status: Status
    metrics: list[Metric] = Field(default_factory=list)
    identity_rows: list[tuple[str, str, str]] = Field(default_factory=list)  # field, bureau shows, assessment
    corrections: list[str] = Field(default_factory=list)
    clean: list[str] = Field(default_factory=list)
    channel: str = ""
    plain: str = ""


class DerogItem(BaseModel):
    description: str
    severity: float
    months_since: Optional[int] = None


class GuarantorResult(BaseModel):
    person: str = ""
    report_date: Optional[date] = None
    report_age_days: Optional[int] = None
    scores: list[tuple[str, int, str]] = Field(default_factory=list)  # bureau, value, model
    mid_score: Optional[int] = None
    fico_available: bool = False
    bureau_spread: Optional[int] = None
    util_overall: Optional[float] = None
    util_max_card: Optional[float] = None
    util_as_reported: Optional[float] = None
    total_revolving_limit: float = 0
    total_revolving_balance: float = 0
    highest_limit: Optional[float] = None
    n_primary_revolvers: int = 0
    oldest_months: Optional[int] = None
    aaoa_months: Optional[int] = None
    inquiries_6m: dict[str, int] = Field(default_factory=dict)
    inquiries_12m: dict[str, int] = Field(default_factory=dict)
    inquiries_24m: dict[str, int] = Field(default_factory=dict)
    new_accounts_6m: int = 0
    new_accounts_12m: int = 0
    new_accounts_24m_all: int = 0
    lates_12m: int = 0
    lates_24m: int = 0
    recent_lates: list[str] = Field(default_factory=list)
    derogs: list[DerogItem] = Field(default_factory=list)
    derog_load: float = 0
    collections: int = 0
    public_records: int = 0
    au_heavy: bool = False
    monthly_debt: float = 0
    dti: Optional[float] = None
    identity_gate: str = "Clear"  # Clear, Review, Block
    flags: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    status: Status = Status.PEND
    one_line: str = ""


class ProductFit(BaseModel):
    code: str
    name: str
    fit: str  # STRONG FIT, POTENTIAL FIT, NOT YET, NOT RECOMMENDED, NEEDS INFORMATION
    in_goal: bool = False
    score: Optional[float] = None
    reasons: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    range_low: Optional[float] = None
    range_high: Optional[float] = None
    range_confidence: str = ""
    earliest_ready: Optional[date] = None
    cost_note: str = ""


class ReviewItem(BaseModel):
    id: str
    title: str
    reason: str
    blocking: bool = False


class Flag(BaseModel):
    title: str
    status: Status
    consequence: str
    tier: int
    points: list[int] = Field(default_factory=list)
    ref: str = ""  # e.g. "Point 01"


class Action(BaseModel):
    priority: int
    item: str
    what: str
    path: str  # CLIENT ACTION, THIRD-PARTY / PROFESSIONAL, OPTIONAL IMPLEMENTATION, COMPLETED IN FRA
    position: str = "AWAITING CLIENT"
    phase: int = 1  # 1: weeks 0-2, 2: weeks 2-6, 3: weeks 6-12, 4: 3-6 months
    window: str = ""
    done_when: str = ""
    ref: str = ""


class AreaRating(BaseModel):
    key: str
    name: str
    status: Status
    narrative: str = ""


class ConcentrationGroup(BaseModel):
    name: str
    points: list[int]
    meaning: str


class Composite(BaseModel):
    issued: bool
    score: Optional[float] = None
    tier: str = ""
    unlocks: list[str] = Field(default_factory=list)
    area_scores: dict[str, float] = Field(default_factory=dict)


class AuditResult(BaseModel):
    audit_date: date
    findings: list[Finding] = Field(default_factory=list)
    matrix: list[MatrixRow] = Field(default_factory=list)
    matrix_sources: list[str] = Field(default_factory=list)
    address_candidates: list[AddressCandidate] = Field(default_factory=list)
    guarantor: Optional[GuarantorResult] = None
    bureau_cards: list[BureauCard] = Field(default_factory=list)
    banking: dict = Field(default_factory=dict)
    products: list[ProductFit] = Field(default_factory=list)
    areas: list[AreaRating] = Field(default_factory=list)
    flags: list[Flag] = Field(default_factory=list)
    first_three: list[Action] = Field(default_factory=list)
    secondary: list[tuple[str, Status, str]] = Field(default_factory=list)
    concentration: list[ConcentrationGroup] = Field(default_factory=list)
    composite: Composite = Field(default_factory=lambda: Composite(issued=False))
    review_items: list[ReviewItem] = Field(default_factory=list)
    actions: list[Action] = Field(default_factory=list)
    strengths: list[Metric] = Field(default_factory=list)
    documents_reviewed: list[tuple[str, str, str]] = Field(default_factory=list)  # doc type, filename, date
    status_counts: dict[str, int] = Field(default_factory=dict)
