# Funding Readiness Audit Tool: Final Scoring Rulebook (v1.0)

**Status:** Council-final spec for the deterministic rules engine. Issued by the Council Chair on 2026-10-07.
**Inputs:** BRIEF, R1 and R2 papers from four experts: SBA/Bank (SBA), Card Broker (CARD), Alt-Lending (ALT), Compliance (COMP).
**How to read it:** every number is an editable config default (`config key` in backticks where useful). Source labels: **[PUB]** published rule or regulation, **[DP]** industry or community data point, **[EXP]** expert or chair judgment that the team tunes. Product codes are used throughout:

| Code | Product | Code | Product |
|---|---|---|---|
| BC | Business 0% cards / stacking | OT | Online term loan |
| PC | Personal 0% cards | EQB | Equipment, bank or captive lane |
| PL | Personal unsecured loan | EQA | Equipment, non-bank lane |
| OL | Online / fintech LOC | FAC | Invoice factoring |
| BL | Bank LOC | MCA | Revenue-based financing / MCA |
| SBA | SBA 7(a) Small, Standard 7(a), Express, Microloan (one score; sub-programs gated separately) | DSCR | DSCR rental loan |
| BT | Bank term loan | FF | Fix & flip |

---

## 0. Summary of key rulings

| # | Conflict | Ruling | Rationale | Source |
|---|---|---|---|---|
| R1 | Gap between loan and card stack (30 vs 60–90 days vs "30 after funding") | No card or personal-credit application while any loan application is pending. The card stack starts **≥30 days after the last planned loan *funds*** (`SEQ_LOAN_TO_CARD_GAP_DAYS=30`). The reverse direction (cards then loan) needs a **180-day quiet period** (`SEQ_CARD_TO_LOAN_QUIET_DAYS=180`). | The risk is the lender's credit re-pull before closing, and that risk ends at funding. 30 days lets the new loan report so issuers see true obligations. Compliance's 60–90 day concern is concealment, which is handled by the truthful-disclosure rule, not by a longer wait. | SBA + CARD; COMP concern covered by G-06 |
| R2 | Cards-first when the loan lane is more than 6 months away | **Adopt, narrowly.** Allowed only if all are true: every loan lane's earliest-ready date is >180 days away, the card lane is ≥65 with no hard knock-out, the client timeline is ≤90 days, the stack passes the payoff cap, and a human approves it (HR-52). Then the 180-day quiet period applies, and all cards must be listed on any later PFS or debt schedule. | Holding a ready, cheap lane for 6+ months to protect a speculative loan harms the client. A human gate and a quiet period limit the damage. | ALT (CARD's >120-day human gate merged in) |
| R3 | 14-day vs 45-day inquiry de-dup | De-dup depends on the score model and applies only to mortgage, auto and student inquiries: FICO 8/9/10 = 45-day window plus 30-day ignore buffer; FICO 2/4/5 and VantageScore = 14 days. Card, personal-loan, business and unknown inquiries are **never** grouped. De-dup feeds scoring factors only. Velocity rules, issuer rules and HR always use raw counts. | Matches published FICO behaviour. Issuers count pulls, not scoring-grouped pulls. | COMP + CARD |
| R4 | Score aggregation | BC/PC use **stack_score** (target bureau; min across planned bureaus; lowest bureau if unknown) for scoring, plus **mid_score** for the knock-out floor. PL uses mid_score. All business, bank, SBA, alt and RE lanes use **GF**, the weakest 20%+ owner's median. Only FICO-family scores trigger thresholds. | Issuers pull one bureau. Banks, SBA and mortgage use the middle score of the worst guarantor. | CARD + SBA + ALT |
| R5 | Card-stack cap formula | `Expected = min(HL·m·N_exp, 4·HL, 0.5·Inc_ind, $100k, PTI_cap, Payoff_cap)`. Full definitions in §6.1. Optimistic is internal only. | Every expert's cap tests a different failure: anchor limit, income, ability to pay, exit. min() honours all of them. | CARD R2 + SBA + ALT |
| R6 | Online LOC sizing (3 formulas) | One LOC formula: `TMR × k_lane` with fintech k = 0.5/1.0 and bank k = 0.8/1.2, then a PBR cap and position or credit modifiers (§6.4). | 10% of annual revenue ≈ 1.2×TMR. The experts' multiples differ mainly by lane. | ALT R2 (unify), SBA, CARD |
| R7 | SSN issuance / age mismatch | **Blocking human review, not a hard block or decline.** The report is held, a neutral document request (SSA letter or card) is sent, there is no score penalty, and no reason text mentions origin. Different SSN, invalid SSN structure, deceased flag, OFAC and §605B blocks remain **hard blocks**. | Legitimate adult SSN issuance (immigrants, people who lived abroad) creates Reg B national-origin disparate-impact risk. Post-2011 randomization makes inference weak. | CARD challenge, accepted |
| R8 | Personal-guarantee exposure trigger | Advisory HR when **new *unsecured, cash-flow-unverified*** PG exposure (BC, PC, PL, OL, OT, MCA unconditional guaranties) is >$100k **or** >(0.5 × verified personal income + 0.25 × verified annual business revenue). DSCR-tested loans (SBA, BT, BL, EQB) are exempt. A client already holding an MCA with a COJ or performance guaranty always triggers it. | Without the exemption it would fire on every SBA file. The revenue term avoids penalizing operating businesses that repay from cash flow. | SBA + ALT revising COMP |
| R9 | MCA credit floor and steer-away | Keep 500 hard and 500–549 soft. MCA is **excluded from the headline score**, ranked last, and blocked by steer-away rules SA-1 to SA-6 (§6.11). The report shows IRR-based estimated APR and total payback. | The tool predicts market behaviour; it does not endorse it. Suitability is enforced by steer-away and sequencing, not by a fake floor. | ALT R2, COMP |
| R10 | Revenue / income mismatch thresholds | Thresholds are set **by source pair, not by lane**: stated vs statements >20%; statements vs tax-return gross receipts >30%; stated vs tax return (bank/SBA lanes) >15%; stated income vs income documents >15%. Scoring always uses the **lower** figure. | Different source pairs have different legitimate noise. "Use the lower" removes any incentive to overstate. | SBA, ALT, COMP |
| R11 | SBA credit floor | Every SBA FICO value is labeled **"typical lender minimum (overlay), not an SBA rule."** 7(a)/Express: <620 hard, 620–679 soft-A. Micro: <575 soft-B, with no hard FICO floor. **No SBSS gate or estimate anywhere.** | SBA publishes no personal FICO minimum. SBSS was retired for 7(a) Small loans numbered on or after 3/1/2026. | COMP + ALT + SBA |
| R12 | Equipment | Two lanes, EQB and EQA. The report shows the better one. | Both floors are right for their lanes. | SBA + ALT |
| R13 | Paid collections | One shared severity × DOFD decay. Products apply consumption multipliers (bank/SBA ×0.5 for paid items ≥24 months; FICO 9/10/VS-scored products use base 15). Age is measured from DOFD. Payment never resets age. No pay-for-delete recommendation. | Matches score-model reality and manual underwriting. | COMP + SBA |
| R14 | AU tradelines | Scores are used as reported. AU accounts are excluded from depth, HL, utilization, limits and the derogatory load. AU accounts **are** counted in `new_accts_all` (5/24 proxy). AU-heavy files are recomputed on primary accounts and sent to HR. The tool never recommends acquiring AU accounts. | Manual underwriting discounts AU accounts; issuer velocity counts them. | All four |
| R15 | Imputed payments | Revolvers: max(reported, 3% of balance, $25). 0% promo balances are included. Promo ending ≤6 months: also ≥ the 36-month amortization at 26%. Deferred/IDR $0 student loans: 1% of balance. MCA: daily × 21.67, weekly × 4.33. | Single, conservative definition shared by DTI, DSCR and PBR. | SBA, ALT, CARD |
| R16 | Fraud alert vs freeze | Freeze: a soft knock-out until the client lifts it temporarily. Fraud alert: advisory only (verification delay); the client keeps it. §605B block or confirmed identity theft: hard block. Never advise freezing a bureau to steer pulls. | §605A/§605B semantics. | COMP + CARD |
| R17 | Tier vocabulary | One scale for every product and the headline: **Fund-Ready ≥80, Near-Ready 65–79, Needs Work 50–64, Not Ready <50**. Product strictness lives in knock-outs, not in different cutoffs. | One vocabulary is explainable and easy to tune. | Chair (merges 85/70/55 and 80/65/50) |
| R18 | Extraction halt scope | A credit-extraction failure halts all credit-derived factors and the client report. Cash-flow-only products (FAC, MCA with verified statements) may compute an **internal provisional** score for the reviewer. | Alt lanes depend less on credit data, but nothing goes to the client until a human clears it. | ALT + COMP |
| R19 | Bank-statement and tax-data staleness | Statements must end ≤45 days before the audit date, or alt ranges are blocked. FYE >6 months ago → interim YTD financials required. Most recent return >18 months old → DSCR estimate blocked. | Cash-flow data goes stale too. | ALT + SBA |
| R20 | Judgments, liens, CAIVRS | Sourced from **intake attestation** and documents only. A lien or judgment parsed from a bureau file triggers HR-06 (data quality). A clean bureau report never means "none." | NCAP removed them from bureau files in 2017–18. CAIVRS is lender-only. | COMP, accepted by all |
| R21 | Card-stack N_exp tiers | Uses the product's own score tier (Fund-Ready 5 / Near-Ready 3 / Needs Work 2), with decrements. | Aligns with R17. | CARD, re-tiered |
| R22 | Business-card new-account counting | `new_accts_primary` counts personal-file accounts only. Business cards that don't report personally come from the intake debt schedule (`new_biz_cards_12`) and count in the bank lane. | Avoids flagging people who never stacked while still capturing disclosed obligations. | CARD challenge to SBA |

---

## 1. Data pipeline and quality gate

### 1.1 Extraction fields (per bureau unless noted)

| Group | Fields (all carry `confidence` 0–1 and `bureau`) |
|---|---|
| Report metadata | bureau, report_date, source_type {ACR disclosure, monitoring service, lender tri-merge, other}, page_count, image_page_count, OCR_used, summary counts (tradelines, open revolving balance and limit, inquiries, public records) |
| Scores | value, score_model {FICO8, FICO9, FICO10/10T, FICO2/4/5, BankcardX, AutoX, VS3, VS4, unknown}, score_date, reason codes |
| Personal info | names (all variants), SSN (as shown, often partial), SSN-issued-date field if present, DOB (all variants), addresses with reported dates, employers, consumer statements, alerts (fraud initial/extended/active-duty, freeze, §605B), OFAC flag, deceased flag |
| Tradelines | creditor (raw + normalized), acct# last 4, account type (revolving, installment, mortgage, open, charge-card, collection), ECOA code, open date, close date, credit limit, high credit, balance, scheduled payment, status code (Metro 2), payment grid (24–84 months), DOFD, charge-off date and amount, original creditor (collections), original balance, medical flag, compliance condition code (XB/XC/XH), BK indicator, last reported date, closed-by-grantor flag, promo info if shown |
| Inquiries | creditor (raw), date, bureau, inquiry type (classified, §2 F-17) |
| Public records | type, filing date, disposition, disposition date, chapter, amount (bankruptcy only expected; any judgment or lien → HR-06) |

Uploads (optional): business bank statements (3 months for MCA/OL, 6 months for OT/EQA/BL) give deposits by type, transfers, loan proceeds, NSFs, negative days, daily balances, and recurring debits (positions). Tax returns (2 years, business + personal) give gross receipts, net income, interest, depreciation, amortization, officer comp, K-1/W-2, Schedule C lines. Income documents give W-2s, paystubs and 1099s.

### 1.2 Normalization
Map every tradeline to Metro 2 concepts: status 11/13/71/78/80/82/83/84/93/94/95/96/97/61–65/DA/DF; ECOA 1/2/3/5/7/T/W/X; condition codes XB/XC/XH. Set `owner_type` ∈ {primary (ECOA 1), joint (2/5/7), AU (3), business_reported_personally (W), terminated (T)}. Creditor names are normalized through an editable alias table.

### 1.3 Three-bureau merge

| Rule | Value |
|---|---|
| Match key | normalized creditor + last 4 (if shown) + open date ±31 days + account type |
| Auto-merge | match score ≥0.85 |
| Merge, low confidence | 0.60–0.85 (tag `merge_conf=low`) |
| Keep separate | <0.60 |
| Post-merge tolerances | balance ±10% or ±$150; limit exact (missing on one bureau = flag, not mismatch); status equal at severity tier; DOFD ±60 days |
| Value used | latest-reported balance and limit; worst status across bureaus for scoring; disagreements → "item to verify" (HR-05) |
| Double-count removal | OC charge-off >$0 + collector >$0 for same debt → count collector only and flag; two collectors on the same debt (amount within 5%) → count one; same account twice on one bureau → count one; student loan disbursements grouped as one derogatory event |

### 1.4 Confidence gate (whole-audit halt → HR-01)
Halt credit-derived scoring and client-report release if **any** of the following is true:
- Fewer than 90% of tradelines have all core fields (status, balance, limit, open date, ECOA, late grid) at confidence ≥0.80.
- Extracted tradeline count differs from the report's summary count by more than 1 on any bureau.
- Extracted total revolving balance or limit differs from the summary by more than 5%.
- Any score cannot be tied to both a bureau and a model.
- Personal-info section confidence is below 0.90.
- Image-only pages exceed 20%, or OCR fallback was used.

Per-section confidence is shown in the internal report.

### 1.5 Staleness

| Data | Threshold | Effect |
|---|---|---|
| Credit report age (audit date − report_date) | >30 days | Revolving products (BC, PC, OL) marked "stale – re-pull" |
| | >60 days | Readiness is **provisional**: headline capped at 79; range confidence Low |
| | >90 days | All funding ranges suppressed |
| | Card applications | Action item AP-30: re-pull a report ≤14 days old before applying (not a gate on the audit) |
| Bureau mix | one bureau's report_date >60 days apart from the others | HR-03 |
| Bank statements | last statement period ends >45 days before audit date | Alt ranges (OL, OT, MCA, EQA, FAC) suppressed; scores fall back to self-reported values (cap 80) |
| Business financials | last FYE >6 months ago | Interim YTD P&L required (doc checklist); DSCR confidence Medium |
| | most recent filed return >18 months old | DSCR and bank/SBA ranges suppressed |

### 1.6 Score-model labeling
- Only FICO-family models (FICO 8/9/10/10T/2/4/5, Bankcard, Auto) count against numeric thresholds. VantageScore is displayed with "not a FICO score; may differ by 20–60+ points."
- **No FICO on file (VS-only or unknown model):** score-based knock-outs become HR-02 (not automatic fails); ranges for BC, PC, PL and DSCR/FF are suppressed; other lanes show Low confidence; headline capped at 79.
- Every displayed score carries "[model] from [bureau/source] dated [date]; lenders may use different scores."

---

## 2. Shared engine factors (computed once)

| ID | Name | Definition / formula | Inputs |
|---|---|---|---|
| F-01 | score[bureau] | {value, model, source, date, fico_eligible} per person | Scores |
| F-02 | mid_score | Middle of 3 FICO-eligible bureau scores; lower of 2; the single score if 1 | F-01 |
| F-03 | GF (guarantor FICO) | min(mid_score) over all owners ≥20% (and required guarantors) | F-02, intake D4 |
| F-04 | stack_score | min(score[b]) over the bureaus predicted for the planned issuers (`issuer×state→bureau` table, [DP] with `last_verified`). Unknown → min over all bureaus | F-01, B3 |
| F-05 | bureau_spread | max − min FICO-eligible score per person | F-01 |
| F-06 | canonical tradelines | Merged set (§1.3) with owner_type, bureaus_present, DOFD | Tradelines |
| F-07 | util_overall | Σ balance ÷ Σ limit over **open primary + joint** revolvers with a limit. Exclude AU and no-preset-limit charge cards. Closed cards with a balance: balance counted, limit not | F-06 |
| F-08 | util_max_card | max single-card balance ÷ limit on the same set | F-06 |
| F-09 | util_as_reported | Same as F-07 including AU (display only) | F-06 |
| F-10 | HL | Highest limit on an open primary revolver (excludes AU and charge cards) | F-06 |
| F-11 | n_primary_revolvers | Count of open primary revolvers | F-06 |
| F-12 | oldest_primary_months | Age of oldest primary/joint tradeline (any type) | F-06 |
| F-13 | aaoa_primary_months | Mean age of primary/joint tradelines (open + closed still reporting) | F-06 |
| F-14 | mix flags | has_installment (primary, ≥12 months history), has_mortgage, mortgage_paid_as_agreed | F-06 |
| F-15 | inq_raw[b][w] | Hard inquiries per bureau for w ∈ {1, 2, 3, 6, 12, 24} months, plus a total across bureaus de-duplicated by creditor + date ±3 days | Inquiries |
| F-16 | inq_scored[b][w] | As F-15, but mortgage/auto/student inquiries grouped: window `DEDUP_WINDOW[model]` (FICO 8/9/10 = 45 days, and inquiries <30 days old ignored; FICO 2/4/5 and VS = 14 days). All other types counted individually | F-15, F-17, F-01 model |
| F-17 | inq_class | Creditor-name classifier → {card_issuer, bank, fintech, mca_iso, auto, mortgage, student, personal_loan, telecom_utility, unknown}. Unknown is never grouped and never penalized as "commercial"; it goes to F-15 raw counts only | Alias table |
| F-18 | new accounts | new_accts_primary[6/12/24] (personal file, primary + joint, by open date); new_accts_all[6/12/24] (includes AU; 5/24 proxy); new_biz_cards_12 (intake debt schedule); new_rev_limits_6 (Σ limits of primary revolvers opened ≤6 months) | F-06, intake D12 |
| F-19 | late_summary | Per primary/joint tradeline: worst late and months since, for windows 12/24/84; separate mortgage-late counts (30/60/90+ in 12 and 24 months); `rolling` = ≥3 lates on one tradeline within 12 months | F-06 |
| F-20 | derog_items | Each item: class, base severity, DOFD/event date, paid flag, medical flag, amount, decay (§3) | F-06, public records |
| F-21 | derog_load[p] | Item score s = base × decay × recovery × M_p (§3.3). Sort descending; load = s1 + 0.5·s2 + 0.25·Σ(rest), capped at 100 | F-20 |
| F-22 | monthly_debt_imputed | Personal: Σ installment reported payments + Σ revolver max(reported min, 3%·bal, $25 if bal > 0) incl. 0% promo; promo ending ≤6 months → max(above, PMT(26%, 36 months, bal)); deferred/IDR $0 student loans 1%·bal; AU excluded; collections excluded unless an agreed payment exists | F-06, intake |
| F-23 | income | Inc_ind = documented individual gross annual income (W-2, 1099, K-1, documented owner draws); undocumented → stated × 0.8. Inc_hh (PC only, applicant 21+) = Inc_ind + other household income with regular access (same 0.8 rule). GMI = Inc/12 | Intake C1–C3, docs |
| F-24 | DTI | (F-22 + housing payment) ÷ GMI_ind | F-22, F-23, C4 |
| F-25 | revenue | Rev_stated, Rev_return (gross receipts), TMR_stmt (avg last 3 full months of deposits excluding transfers, loan/MCA proceeds, refunds, owner injections). **TMR** = TMR_stmt if verified; else stated monthly deposits × 0.8; else Rev_return ÷ 12. **URev** (bank/SBA underwriting revenue) = lower of documented sources. Each carries a `source` tag | Intake D7–D8, uploads |
| F-26 | TIB | TIB_alt = months since the later of formation date and first business deposit; TIB_bank = years of filed business returns showing revenue (and months since first revenue for start-up tests); TIB_app = date operations actually began (used on applications). If formation and first deposit differ by >6 months → HR-27 | D2–D3, returns |
| F-27 | MDS_business | Monthly business debt service: term/equipment P&I + MCA daily × 21.67 / weekly × 4.33 + business-card min (rule F-22) + LOC payments | D12–D13, statements |
| F-28 | PBR | (MDS_business + proposed new payment) ÷ TMR | F-25, F-27 |
| F-29 | cash hygiene | nsf_per_month (3-month avg), neg_days_per_month, adb_ratio = average daily balance ÷ TMR, deposit_count_per_month, trend = (last 3 months ÷ prior 3 months − 1). Unknown if no statements (self-reported proxies G1–G4 at cap 80) | Statements, G |
| F-30 | positions | Count of open daily/weekly-debit financings; mca_paid_pct each; blanket_ucc ∈ {Y, N, Unknown}; coj_present | D13–D14 |
| F-31 | DSCR | EBITDA = net income + interest + depreciation + amortization + documented one-time add-backs (+ home office for Schedule C). Business DSCR = EBITDA ÷ (existing business ADS + proposed ADS). Global DSCR = (EBITDA + owner outside income − living allowance [$30,000 + $12,000 per dependent, unless stated] − 12·F-22) ÷ business ADS. Unknown if no returns | Returns, E-section |
| F-32 | pg_exposure_new | Σ expected amounts of recommended BC + PC + PL + OL + OT + MCA (unconditional guaranty) | Product outputs |
| F-33 | identity_status | Clear / Review / Block (§4) | §4 |
| F-34 | data_confidence | Per input: verified / self-reported / unknown; staleness flags (§1.5); model flag (§1.6) | Pipeline |
| F-35 | industry_class | NAICS → {prohibited, restricted, standard} per lane family (SBA-ineligible ≠ MCA-prohibited); editable table | D5 |
| F-36 | au_heavy | True if AU limits ≥30% of all open revolving limits, **or** the oldest or highest-limit account is AU, **or** ≥2 AU accounts were added in the last 6 months that are >5 years old or have a ≥$10k limit | F-06 |
| F-37 | FCF (free cash flow, monthly) | FCF_pers = max(0, 0.75·GMI_ind − housing − F-22 − living allowance ÷ 12). FCF_bus = (net income + D&A) ÷ 12 from the latest return if available; else TMR × 0.15 − MDS_business (floor 0) | F-22–F-27 |
| F-38 | earliest_ready_date[p] | max over the product's knock-outs of the remedy date (e.g., inquiry falls out of the 6-month window, late reaches 12 months, TIB reaches threshold, position ≥75% paid). Undated remedies = audit date + the AP timeline upper bound | KO + AP |

**Unknown-value rule:** an unknown factor scores 50% of its weight unless marked **U0** (scores 0) in the product table. Never impute bank cash-flow factors.

---

## 3. Derogatory severity and time decay

### 3.1 Base severity (0–100)

| Item | Base | | Item | Base |
|---|---|---|---|---|
| 30-day late | 20 | | Charge-off, unpaid | 75 |
| 60-day late | 35 | | Charge-off, paid / settled | 55 |
| 90-day late | 50 | | Repossession (96) | 80 |
| 120–180+ late | 60 | | Voluntary surrender (95) | 75 |
| Rolling (≥3 lates on one tradeline in 12 months) | +15 on that tradeline | | Foreclosure / deed-in-lieu / short sale | 90 / 80 / 80 |
| Collection, unpaid, non-medical, original ≥$100 | 60 | | Judgment / tax lien (if present; always HR-06) | 70 / 85 |
| Collection, original <$100 | 10 | | BK7 discharged | 90 |
| Collection, paid, non-medical | 35 (FICO 8 products); 15 (products scored on FICO 9/10/VS4) | | BK13 discharged | 80 |
| Medical collection unpaid ≥$500 | 25 | | BK13 active (in plan) | 95 + hard stop on new credit |
| Medical collection paid, or <$500 | 0 + item to verify (HR-05) | | BK dismissed | 95 |
| Federal-debt default (student, SBA, FHA) | 85 + HR-32 | | BK filed / open | 100 + hard stop |

### 3.2 Decay multiplier
**Lates, collections, charge-offs, repos and foreclosures:** age is measured from DOFD, or from the event date for repos and foreclosures. Date of last activity and paid date are never used.

| Months since DOFD / event | [0,6) | [6,12) | [12,24) | [24,36) | [36,60) | [60,84) | ≥84 (lates) / ≥90 (coll, CO) |
|---|---|---|---|---|---|---|---|
| Multiplier | 1.00 | 0.85 | 0.65 | 0.45 | 0.30 | 0.15 | 0 → obsolete; item to verify (HR-05) |

**Bankruptcy:** age is measured from the discharge or dismissal date. An open BK = 1.00.

| Months since discharge / dismissal | [0,12) | [12,24) | [24,48) | [48,84) | [84,120) | ≥120 |
|---|---|---|---|---|---|---|
| Multiplier | 1.00 | 0.80 | 0.55 | 0.35 | 0.20 | 0 |

**Recovery factor:** ×0.80 if there are ≥12 months of perfect history on ≥2 primary revolvers opened after the item's DOFD. Otherwise 1.00.
**AU accounts:** excluded from the load (lates listed for information, with remedy AP-23).

### 3.3 Product consumption multipliers (M_p)

| Item class | BC / PC | PL | SBA / BT / BL / EQB | OL / OT / MCA / EQA / FAC | DSCR / FF |
|---|---|---|---|---|---|
| Default | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| Paid collection or paid charge-off, DOFD ≥24 months | 1.0 | 1.0 | 0.5 | 1.0 | 0.75 |
| Unpaid medical ≥$500 | 1.0 | 1.0 | 0.5 | 0.5 | 0.5 |
| Collection with original balance <$100 | 1.0 | 1.0 | 0.5 | 0.5 | 0.5 |

### 3.4 How products consume the load
Bank/SBA, cards and PL use banded factors (§6). Alt lanes subtract points after weighting: load ≥60 → −10; 35–59 → −5. An unpaid charge-off or collection from a known commercial or alt lender always triggers HR-41.

---

## 4. Identity, fraud and eligibility gates

Run before any product score. **Hard block** = no product output is released; it can only be cleared by correcting or resolving the underlying data. **Blocking review** = the report is held until a human clears it; no score penalty, no decline. **Advisory** = the report releases after a reviewer acknowledges it.

| ID | Indicator | Detection | Action |
|---|---|---|---|
| ID-01 | Different SSN across bureaus or vs. intake (not a single-digit transposition) | Compare digits shown | **Hard block** (HR-08) |
| ID-02 | Invalid SSN structure | Area 000/666/900–999, group 00, serial 0000 | **Hard block** (HR-09) |
| ID-03 | SSN issuance / age inconsistency | Report's SSN-issued-date field shows issuance at client age ≥25 **and** a primary tradeline predates that issuance; **or** a primary (non-AU) tradeline opened before client age 16 | **Blocking review** (HR-10). Neutral document request ("please provide your SSA card or SSA letter to confirm file data"). Never a decline, never a score input, never origin-related text |
| ID-04 | Thin file, older adult | Age ≥30, oldest primary <24 months, ≥2 AU accounts, and ≤1 inquiry older than 12 months | Advisory (HR-11), neutral wording |
| ID-05 | Name / DOB variation | First name different (not in nickname table), or DOB year differs | **Blocking review** (HR-12). Day/month-only DOB variation or a surname explained by intake → info flag |
| ID-06 | Address anomalies | >5 addresses in 24 months, a state the client says they never lived in, or a CMRA/mail-drop | Advisory (HR-13) |
| ID-07 | Client says an account is not theirs | Intake per-tradeline checkbox | Applications blocked **on that bureau** (HR-14). Route: FTC IdentityTheft.gov report + §605B; never "credit repair" |
| ID-08 | Unrecognized inquiries | Intake | 1 → advisory (HR-15); ≥2 → blocking review (possible identity theft) |
| ID-09 | Deceased indicator on a living client | ECOA X | **Hard block** (HR-16) |
| ID-10 | OFAC potential match | Report flag | **Hard block** (HR-17) |
| ID-11 | §605B block or confirmed identity theft | Report or intake | **Hard block** until the case is resolved (HR-18) |
| ID-12 | Fraud alert (initial / extended / active-duty) | Report flag | Advisory (HR-19): "expect identity verification and possible delays; keep the alert if fraud is real." Not a knock-out |
| ID-13 | Security freeze | Report flag or intake | Soft knock-out on products that pull that bureau until the client temporarily lifts it (AP-31) |
| ID-14 | Consumer statement mentioning identity theft, dispute or military service | Text match | Advisory (HR-20) |
| ID-15 | Active-duty indicator | Alert or intake B7 | Advisory (HR-21; MLA 36% MAPR applies to consumer credit) |
| ID-16 | AU-heavy file | F-36 | Advisory (HR-23/HR-24). Show primary-only recomputation alongside |

**Eligibility attestations** (judgments, tax liens, federal debt, criminal history, citizenship) come **only from intake and documents** (R20). Citizenship and criminal-history questions are asked and used **only when SBA is in the goal set** (Reg B §1002.6(b)(7) permits immigration status). They are stored encrypted, flagged as sensitive, and never used in any other lane.

---

## 5. Intake questionnaire

**Order:** Section A (goal) is always asked first. Then B (consent and identity, always), then only the sections the branching table selects. Product needs: **R** = required (no score without it), **O** = optional (improves confidence), **—** = not asked.

### 5.1 Section A: Funding goal (asked first, all clients)

| ID | Exact wording | Type / options |
|---|---|---|
| A1 | "What kind of funding are you looking for? Select all that apply." | Multi: Business credit cards with 0% intro APR · Personal credit cards with 0% intro APR · Personal loan · Business line of credit · SBA loan · Business term loan · Equipment financing · Invoice factoring · Revenue-based financing / merchant cash advance · Rental property loan (DSCR) · Fix-and-flip loan · **Not sure — recommend options for me** |
| A2 | "How much funding do you need in total?" | Currency |
| A3 | "What is the smallest amount that would still meet your need?" | Currency |
| A4 | "What will the funds be used for? Enter an approximate amount for each." | Repeat: {Working capital / payroll · Inventory · Equipment or vehicles · Buy real estate · Renovate an investment property · Buy a business or a partner's share · Refinance existing business debt · Pay off a merchant cash advance · Marketing / growth · Start a new business · Personal or household expenses · Consolidate personal debt · Other} + currency |
| A5 | "When do you need the funds?" | Within 14 days · 15–30 days · 1–3 months · 3–6 months · 6–12 months · Flexible |
| A6 | "Who is this funding for?" | Me personally · My business · An investment property · Both personal and business |
| A7 | "Which best describes your business today?" | No business · Business idea, not yet formed · Formed, no revenue yet · Operating <12 months · Operating 1–2 years · Operating 2+ years |
| A8 | "Rank what matters most to you." | Rank: Lowest cost · Speed · Largest amount · Avoid personal guarantee · Avoid pledging collateral |
| A9 | "Business financing usually requires the owner's personal guarantee, which makes you personally liable. Are you willing to sign one?" | Yes · No · Need more information |
| A10 | "Are you willing to pledge collateral? Select any you have." | Multi: Business equipment · Real estate · Accounts receivable · Home equity · Cash/savings · None |
| A11 | "How do you plan to repay this funding?" | Business cash flow · Personal income · Sale of asset/property · Refinance later · Not sure |
| A12 | "Have you applied for any credit in the last 90 days that may not appear on your report yet?" | Y/N + repeat {lender, date, product, result} |
| A13 | "Do you have any loan application in process that has not yet closed or funded?" | Y/N + {lender, product, expected funding date} |

### 5.2 Branching map

| Trigger (from A) | Sections asked |
|---|---|
| Always | A, B |
| A1 includes BC or PC, or A6 = personal | C, L |
| A1 includes PL | C |
| A1 includes any business product, or A6 includes business, or A7 ≥ "Formed" | D |
| A1 includes SBA, BT, BL or equipment | E (and C for global cash flow) |
| A1 includes SBA | F |
| A1 includes OL, OT, MCA, FAC, equipment or BL | G (BL: optional) |
| A1 includes MCA | H |
| A1 includes FAC | I |
| A1 includes Equipment | J |
| A1 includes DSCR | K |
| A1 includes FF | M |
| A1 = Not sure | C + D-core (D1–D9) + G-lite (G1, G3) + the A4 purpose drives one more product-specific section if the recommender's top 3 needs it (§7) |
| Any | N (uploads offered) |

### 5.3 Section B: Consent and identity (all)

| ID | Wording | Type |
|---|---|---|
| B1 | E-sign authorization: purpose, uses, sharing, retention (§13) | Signature (required before upload) |
| B2 | "Full legal name, and any other names you have used on credit accounts (e.g., maiden name)." | Text, repeat |
| B3 | "State of your primary residence." | State (drives the bureau-pull table) |
| B4 | "Date of birth." | Date (identity matching, elder-review trigger only; never scored) |
| B5 | Shown after extraction: "Review each account and inquiry. Mark any you do not recognize." | Per-item checkbox |
| B6 | "Is there a fraud alert or security freeze on any bureau?" | Per bureau: None / Fraud alert / Freeze / Not sure |
| B7 | "Are you an active-duty servicemember or a dependent of one?" | Y/N (MLA protections) |

### 5.4 Section C: Personal finances

| ID | Wording | Type | BC | PC | PL | SBA/BT/BL/EQB |
|---|---|---|---|---|---|---|
| C1 | "Your individual annual income before taxes (wages, self-employment, documented owner draws)." | Currency | R | R | R | R |
| C2 | "Other household income you have regular access to (only for personal card applications, applicants 21+)." | Currency | — | O | — | — |
| C3 | "How can you document your income?" | Multi: W-2/paystubs · Tax returns · 1099 · Bank statements · Cannot document | R | R | R | R |
| C4 | "Monthly housing payment (rent or mortgage)." | Currency | R | R | R | R |
| C5 | "Do you own or rent your home?" | Own w/ mortgage · Own free & clear · Rent · Other | R | R | R | R |
| C6 | "Number of dependents (used only to estimate living expenses; leave blank to use a standard allowance)." | Integer, optional | — | — | — | O |
| C7 | "Which banks do you hold checking, savings, or cards with?" | Multi (Chase, Amex, BofA, Citi, Wells, US Bank, Capital One, PNC, TD, credit union, other) | O | O | O | — |
| C8 | "Has any bank denied you or closed an account of yours in the last 24 months? Which bank and why?" | Y/N + text | R | R | R | — |
| C9 | "Are any accounts on your report ones where you are an authorized user on someone else's card?" | Y/N + select | R | R | — | — |
| C10 | "Statement closing day for each card (optional; helps time pay-downs)." | Per card day | O | O | — | — |

### 5.5 Section D: Business core

| ID | Wording | Type | Needed by |
|---|---|---|---|
| D1 | "Legal business name, entity type, and state of formation." | Text + Sole prop/LLC/S-corp/C-corp/Partnership + state | All business |
| D2 | "Formation date (per formation documents or EIN letter)." | Date | All business |
| D3 | "Date the business first earned revenue / began operating." | Date | All business |
| D4 | "List every owner with 20% or more, and their percentage." | Repeat {name, %} | All business (GF) |
| D5 | "Industry (NAICS if known) and a one-line description of what you sell." | Select + text | All business |
| D6 | "Do you have a business checking account in the business's legal name?" | Y/N | All business |
| D7 | "Gross revenue: last full year, prior full year, and year-to-date." | Currency ×3 | All business |
| D8 | "Average monthly deposits into the business account over the last 3 months, NOT counting transfers between your own accounts or loan/advance proceeds." | Currency | OL, OT, MCA, EQA, FAC, BL, BC |
| D9 | "Net profit or loss on the last 2 business tax returns." | Currency ×2 (negative allowed) | SBA, BT, BL, EQB, OT |
| D10 | "Have the last 2 years of business and personal tax returns been filed?" | Yes · No · On extension | SBA, BT, BL, EQB |
| D11 | "Has revenue in the last 3 months gone up, stayed flat, or gone down compared with the 3 months before? By about what percent?" | Select + % | Alt lanes |
| D12 | "List current business debts, including business credit cards: lender, type, balance, payment, frequency, date opened." | Repeat {lender, type: term/LOC/MCA/equipment/SBA/EIDL/business card/other, balance, payment, freq, open date} | All business |
| D13 | "Do you have any merchant cash advance or financing that debits your account daily or weekly?" | Y/N + per position {funder, original amount, payback balance, payment, frequency, funded date, COJ signed Y/N/unknown} | All business |
| D14 | "Any business tax liens, judgments, or UCC filings, and are any on a payment plan?" | Y/N + {type, amount, plan Y/N, payments made} + "Has any lender filed a blanket UCC lien?" Y/N/Unknown | All business |
| D15 | "Are you willing to personally guarantee?" (pre-filled from A9) | Y/N | BC, OL, OT, MCA, SBA |

### 5.6 Section E: Bank / SBA / bank-equipment

| ID | Wording | Type |
|---|---|---|
| E1 | "What collateral is available, and estimated value of each?" | Multi {equipment, real estate, A/R, inventory, home equity} + currency |
| E2 | "Do you own your home? Estimated value and mortgage balance." | Y/N + currency ×2 |
| E3 | "Average monthly balance in the business account, and which bank?" | Currency + text |
| E4 | "Accounts receivable outstanding and average days to collect." | Currency + integer |
| E5 | "Is any owner or the business behind on federal debt: taxes, federal student loans, SBA/EIDL/PPP, FHA/VA?" | Y/N + detail + installment plan Y/N |
| E6 | "Exact use of funds and amount for each." (pre-filled from A4) | Repeat |

### 5.7 Section F: SBA only (sensitive, encrypted, SBA use only)

| ID | Wording | Type |
|---|---|---|
| F1 | "Are all owners and required guarantors U.S. citizens or U.S. nationals whose principal residence is in the U.S.? (SBA eligibility requirement.)" | Yes / No / Unsure (no follow-up on origin) |
| F2 | "Is any owner owned in turn by a trust, another company, or an ESOP?" | Y/N |
| F3 | "Is any owner currently incarcerated, on parole or probation, or under indictment? (SBA Form 1919 question.)" | Y/N |
| F4 | "Is this a start-up, expansion, business acquisition, or change of ownership?" | Select |
| F5 | "How much cash will you inject, and from what source?" | Currency + Savings / Gift / Seller note / Other |
| F6 | "Years of management experience in this industry." | Integer |
| F7 | "Have you or any business you owned ever caused a loss to a government agency or defaulted on a government-backed loan?" | Y/N |
| F8 | "Have you been declined for a conventional loan for this purpose in the last 12 months?" | Y/N |

### 5.8 Section G: Cash-flow proxies (used when no statements are uploaded)

| ID | Wording | Type |
|---|---|---|
| G1 | "About how many separate deposits per month?" | <5 · 5–10 · 11–20 · 20+ |
| G2 | "Typical end-of-day balance on a normal day." | Currency |
| G3 | "Overdrafts / NSF / returned items in the last 3 months." | Integer |
| G4 | "Days per month the account goes negative." | Integer |

### 5.9 Product add-ons

| ID | Section | Wording | Type |
|---|---|---|---|
| H1 | MCA | "What share of revenue comes through card processing, and monthly processing volume?" | % + currency |
| I1 | FAC | "Do you invoice other businesses or government agencies (not consumers)?" | Y/N + B2B / Gov / Both |
| I2 | FAC | "Total unpaid invoices now, and the amount over 90 days." | Currency ×2 |
| I3 | FAC | "Average days for customers to pay." | Integer |
| I4 | FAC | "Largest customer's share of receivables." | % |
| I5 | FAC | "Names of your top 3 customers." | Text ×3 |
| J1 | Equip | "Equipment type, new or used, model year, and price." | Select, select, year, currency |
| J2 | Equip | "Seller: dealer/vendor or private party? Do you have a quote or invoice?" | Select + Y/N |
| J3 | Equip | "Expected useful life (years) and down payment available." | Integer + currency |
| K1 | DSCR | "Purchase, rate/term refinance, or cash-out refinance?" | Select |
| K2 | DSCR | "Property type and units." | SFR · 2–4 · 5+ · Condo · Short-term rental |
| K3 | DSCR | "Purchase price or estimated value." | Currency |
| K4 | DSCR | "Monthly rent (current lease or market rent)." | Currency + source |
| K5 | DSCR | "Annual property taxes, insurance, HOA." | Currency ×3 |
| K6 | DSCR | "Down payment and post-closing liquid reserves." | Currency ×2 |
| K7 | DSCR | "Will you or a family member live in the property?" | Y/N (Y → DSCR-KO + HR-30) |
| K8 | DSCR | "How many investment properties do you own now? Will you close in an LLC?" | Integer + Y/N |
| M1 | FF | "Purchase price, rehab budget, after-repair value, and the source of your comps." | Currency ×3 + text |
| M2 | FF | "Flips completed in the last 36 months." | Integer |
| M3 | FF | "Licensed general contractor with a written scope?" | Y/N |
| M4 | FF | "Cash available for down payment, closing, and the first draw." | Currency |
| M5 | FF | "Planned exit." | Sell · Refinance to DSCR · Unsure |
| L1 | Cards | "How will you repay balances before the 0% period ends (typically 12–21 months)?" | Business cash flow · Personal income · Refinance · Other + text |
| L2 | Cards | "What will you use the card funds for?" | Business purchases · Inventory · Cash-out / transfers · Pay off MCA or loans · Payroll · Personal (HR-47 on cash-out / MCA / payroll) |
| L3 | Cards | "Do you have an existing relationship with any business bank where you'd apply?" | Multi |

### 5.10 Section N: Optional uploads

| ID | Upload | Effect |
|---|---|---|
| N1 | Credit report(s), 3-bureau preferred | Required |
| N2 | Business bank statements: 3 months (MCA/OL), 6 months (OT/EQA/BL) | Replaces G and D8. Lifts the alt score cap of 80. Confidence High |
| N3 | Business tax returns, 2 years | Enables DSCR. Lifts the bank/SBA cap of 60 |
| N4 | Personal tax returns / W-2 / paystubs | Verifies income (removes the 0.8× haircut) |
| N5 | A/R aging report | FAC |
| N6 | Equipment quote; DSCR lease or rent schedule; FF scope and comps | Product confidence |
| N7 | Interim YTD P&L | Required if FYE >6 months ago |

---

## 6. Per-product rules

### 6.0 Common mechanics (all products)
- **Product score** S_p = Σ(weight × band%) + modifiers, clamped to 0–100. Then apply caps in this order: soft-KO caps → data caps → provisional cap (§1.5/1.6).
- **Hard KO (H):** status "Not eligible now". The score is still shown for context, but the product is excluded from the headline. The report shows the remedy and `earliest_ready_date` (F-38).
- **Soft KO:** **S-A** caps the score at 79 ("limited lenders"); **S-B** caps it at 64 ("subprime / few lenders / fix first"). Each soft KO also lists its remedy.
- **Tiers (every product):** Fund-Ready ≥80 · Near-Ready 65–79 · Needs Work 50–64 · Not Ready <50.
- **Ranges:** the client sees **Conservative–Expected** only. Optimistic is staff-only. Round **down** to $5k (to $1k below $25k), and enforce Conservative ≤ Expected. Ranges are suppressed per §1.5/§1.6, under any hard block, under an open blocking HR on that product, and when bank/SBA DSCR is unknown.
- **Range confidence:** **High** = income/revenue verified, FICO model known, report ≤30 days. **Medium** = one of those missing. **Low** = two or more missing, or the report is 61–90 days old.
- **Common business KOs** (apply to OL, OT, MCA, FAC, EQA, BL, BT, EQB, SBA unless noted): no business bank account in the legal name (H; SBA/BT/EQB → S-B); prohibited industry for the lane (H); restricted industry (−10 points, alt lanes); unresolved tax lien or judgment >$10k with no plan (intake) (H; with a plan and ≥3 payments → S-B + HR-32 for SBA); PG unwillingness (H for BC, OL, OT, SBA, MCA).
- **PMT and PV** use standard amortization. Rates and terms are config (`RATE_*`, `TERM_*`). `PRIME_RATE` is set monthly by staff (default placeholder 7.00% — **verify**).

### 6.1 BC: Business 0% cards (stacking)

**Knock-outs**

| ID | Rule | Type |
|---|---|---|
| BC-K1 | mid_score <660 / 660–679 | H / S-B |
| BC-K2 | stack_score <660 | H |
| BC-K3 | Unpaid non-medical collection or charge-off, balance >$0, DOFD ≤24 months / DOFD >24 months | H / S-B |
| BC-K4 | Any 30+ late (primary) ≤12 months | H |
| BC-K5 | Any 60+ late ≤24 months | H |
| BC-K6 | BK open; Ch.7 discharged <48 months; Ch.13 open or discharged <24 months | H |
| BC-K7 | Unresolved judgment or tax lien (intake) | H |
| BC-K8 | util_overall >50% | S-B (fast fix, AP-01) |
| BC-K9 | Raw inquiries on stack bureau(s) >6 in 6 months or >10 in 12 months | H (date-computed) |
| BC-K10 | n_primary_revolvers = 0 | H |
| BC-K11 | oldest_primary_months <24 | H |
| BC-K12 | Inc_ind <$30,000 | H |
| BC-K13 | Freeze on a predicted bureau | S-B until lifted |
| BC-K14 | PG unwilling | H |
| BC-K15 | Expected range after caps <$5,000 | S-B ("not worth the inquiries yet") |

**Scoring (100)**

| Factor | Wt | Bands → points |
|---|---|---|
| stack_score | 20 | ≥760:20 · 740–759:18 · 720–739:15 · 700–719:11 · 680–699:7 · 660–679:3 |
| util_overall | 12 | 1–5%:12 · 6–9%:11 · exactly 0% on all cards:9 · 10–19%:8 · 20–29%:5 · 30–49%:2 · ≥50%:0 |
| util_max_card | 5 | ≤29%:5 · 30–49%:3 · 50–89%:1 · ≥90%:0 |
| Raw inquiries, stack bureau | 15 | 6 months: 0:8 · 1:7 · 2:5 · 3:3 · 4–6:1 · >6:0 (+) 12 months: 0–2:4 · 3–4:2 · 5+:0 (+) 24 months: ≤4:3 · 5–8:1 · >8:0 |
| New accounts (new_accts_all) | 10 | 6 months: 0:4 · 1:3 · 2:1 · 3+:0 (+) 12 months: 0–1:3 · 2–3:2 · 4+:0 (+) 24 months: 0–2:3 · 3–4:2 · 5+:0 |
| HL | 12 | ≥$25k:12 · $15–24.9k:10 · $10–14.9k:8 · $5–9.9k:5 · $2–4.9k:2 · <$2k:0 |
| n_primary_revolvers | 5 | ≥5:5 · 3–4:4 · 2:2 · 1:1 |
| oldest_primary_months | 5 | ≥120:5 · 60–119:4 · 36–59:3 · 24–35:1 |
| aaoa_primary_months | 4 | ≥84:4 · 48–83:3 · 24–47:2 · 12–23:1 · <12:0 |
| Payment history | 6 | Clean 84 months:6 · only 30-day lates 25–84 months ago:4 · 60+ late 25–84 months ago:2 · 30-day 13–24 months:1 |
| derog_load[BC] | 3 | 0:3 · 1–19:2 · 20–39:1 · ≥40:0 |
| Inc_ind | 3 | ≥$150k:3 · $100–149k:2.5 · $60–99k:2 · $40–59k:1 · <$40k:0 |

Display only (not scored): +strength notes for an open mortgage paid as agreed and an installment loan paid >12 months.

**Funding range**
- m by stack_score: ≥740 → 0.80 · 720–739 → 0.60 · 700–719 → 0.45 · 680–699 → 0.30 · <680 → 0.20.
- N_exp: 5 if S_BC ≥80, 3 if 65–79, 2 if 50–64, otherwise 1. Subtract 1 each for: >2 raw stack-bureau inquiries in 6 months; ≥3 new_accts_all in 12 months; HL <$5k. Minimum 1.
- **PTI_cap** = (0.45·GMI_ind − housing − F-22) ÷ 0.015. This is the new limit L at which 50% utilization × 3% imputed payment keeps DTI ≤45%. If <0, the cap is 0 → BC-K15.
- **Payoff_cap** = 0.8 × (FCF_bus + FCF_pers) × `PROMO_MONTHS` (default 12).
- **Cap_exp** = min(4·HL, 0.5·Inc_ind, $100,000, PTI_cap, Payoff_cap). Business revenue is never added. Inc_ind is unverified ×0.8.
- **Conservative** = min(HL·m·max(N_exp−2, 1), Cap_exp). **Expected** = min(HL·m·N_exp, Cap_exp).
- **Optimistic (staff only)** = min(HL·min(m+0.2, 1)·(N_exp+1), 5·HL, 0.75·Inc_ind, $150,000, PTI_cap, Payoff_cap), visible only after HR-54 is reviewed.
- Thin file (HL <$2k or n_primary_revolvers <3): flat $3k / $8k.
- If BC and PC are both selected, PTI_cap and Payoff_cap apply to the **combined** total, allocated to BC first.
- If Payoff_cap is the binding cap or L1 = "Other/none" → HR-46. Show the post-promo APR range (20–30%) and the PG statement.

**Required intake:** A, B, C1/C3/C4/C5/C8/C9, D1–D3, D7–D8, D12, D15, L1–L2.

### 6.2 PC: Personal 0% cards
Same knock-outs as BC except: BC-K11 becomes oldest_primary <12 months H, 12–23 S-A; BC-K14 does not apply; add **PC-K1:** applicant under 21 with no independent income → H (Reg Z §1026.51(b)) [PUB]. Same scoring table. Income factor uses Inc_hh for applicants 21+.
**Range:** the BC formula with N_exp capped at 3, then ×0.8 on Conservative and Expected. Cap_exp uses 0.5·Inc_hh. Combined caps per §6.1.
**Required intake:** A, B, C1–C5, C8–C9, L1–L2.

### 6.3 PL: Personal unsecured loan

| ID | Knock-out | Type |
|---|---|---|
| PL-K1 | mid_score <640 / 640–659 | H / S-B |
| PL-K2 | DTI after new payment >45% | H |
| PL-K3 | Inc_ind <$36,000 | H |
| PL-K4 | Unpaid non-medical collection/CO, DOFD ≤24 months | H |
| PL-K5 | 30+ late ≤12 months / 60+ late ≤24 months | S-B / H |
| PL-K6 | BK rules as BC-K6 | H |

| Factor | Wt | Bands (% of weight) |
|---|---|---|
| mid_score | 25 | ≥760:100 · 720–759:85 · 700–719:70 · 680–699:55 · 660–679:40 · 640–659:20 |
| DTI after new payment | 20 | ≤20%:100 · 21–30:80 · 31–36:60 · 37–40:35 · 41–45:10 |
| Inc_ind | 10 | ≥$100k:100 · $75–99k:80 · $50–74k:60 · $36–49k:30 |
| util_overall | 10 | ≤9%:100 · 10–29:75 · 30–49:40 · ≥50:0 |
| Payment history | 10 | as BC scaled: 100 / 67 / 33 / 17 |
| derog_load[PL] | 7 | 0:100 · 1–19:65 · 20–39:30 · ≥40:0 |
| Raw inquiries, max bureau, 6 months | 8 | 0–1:100 · 2–3:70 · 4–6:35 · >6:0 |
| Unsecured installment balance ÷ Inc_ind | 5 | ≤10%:100 · 10–25%:60 · >25%:0 |
| oldest_primary_months | 5 | ≥120:100 · 60–119:75 · 24–59:40 · <24:0 |

**Range:** PmtMax = 0.40·GMI_ind − housing − F-22. APR band by mid_score: ≥740 9% · 700–739 14% · 660–699 20% · 640–659 28%.
- **Expected** = min(PV(APR, 60, PmtMax), 0.35·Inc_ind, $50,000).
- **Conservative** = min(PV(APR, 36, PmtMax), 0.25·Inc_ind).
- **Optimistic (staff)** = min(PV(APR, 84, PmtMax), 0.50·Inc_ind, $100,000).

**Required intake:** A, B, C1, C3–C5, C8.

### 6.4 OL: Online / fintech LOC

| ID | Knock-out | Type |
|---|---|---|
| OL-K1 | TIB_alt <6 / 6–11 months | H / S-A |
| OL-K2 | TMR <$2,500 / $2,500–8,332 | H / S-A ("LOC-lite lenders only") |
| OL-K3 | GF <600 / 600–624 | H / S-B |
| OL-K4 | Positions ≥2 | H |
| OL-K5 | PBR after new line (full draw) >20% | H |
| OL-K6 | nsf_per_month >5 | S-B |
| OL-K7 | adb <$1,000 | S-B |
| OL-K8 | BK open or discharged <24 months | H |
| + Common business KOs (§6.0) | | |

**Scoring (alt table, shared with OT, MCA and EQA):**

| Factor | Bands → band score | OL/OT | MCA | EQA |
|---|---|---|---|---|
| TMR (U0 if unknown) | <$15k:0.2 · 15–25k:0.5 · 25–50k:0.7 · 50–100k:0.85 · >100k:1.0 | 20 | 25 | 12 |
| TIB_alt | <6m:0.2 · 6–11:0.4 · 12–23:0.7 · 24–59:0.9 · 60+:1.0 | 15 | 10 | 15 |
| GF | <550:0.1 · 550–599:0.35 · 600–649:0.6 · 650–699:0.8 · 700+:1.0 | 20 | 10 | 25 |
| adb_ratio | <3%:0.2 · 3–7%:0.5 · 7–15%:0.8 · >15%:1.0 | 12 | 12 | 8 |
| nsf_per_month | 0:1.0 · 1–2:0.75 · 3–4:0.4 · 5–6:0.15 · >6:0 | 10 | 12 | 8 |
| neg_days_per_month | 0:1.0 · 1–3:0.6 · 4–8:0.25 · >8:0 | 6 | 6 | 4 |
| deposit_count_per_month | <5:0.3 · 5–10:0.6 · 11–20:0.85 · >20:1.0 | 3 | 5 | 2 |
| Positions | 0:1.0 · 1:0.6 · 2:0.3 · 3+:0 | 10 | 15 | 8 |
| Trend (3 months vs prior 3) | <−25%:0.1 · −25 to −10%:0.5 · ±10%:0.85 · >+10%:1.0 | 4 | 5 | 3 |
| Down payment (EQA) | ≥20%:1.0 · 10–19%:0.7 · 1–9%:0.4 · 0:0.2 | — | — | 15 |
| **Total** | | **100** | **100** | **100** |

Modifiers: restricted industry −10; derog_load[alt] ≥60 −10, 35–59 −5. **Data cap:** cash-flow self-reported (no N2) → max 80.

**Range (unified LOC formula, R6):**
- Base = TMR × k. Fintech k: Conservative 0.5, Expected 1.0 (Optimistic 1.5, staff only).
- Modifiers: GF 600–649 ×0.7. One existing position ×0.5.
- PBR cap: L ≤ (0.20·TMR − MDS_business) ÷ PMT_factor(`RATE_OL`=35%, 12 months) ≈ ÷0.100.
- Bounds: floor $5k (below that → "too small"), ceiling `OL_MAX`=$250k.

**Required intake:** A, B, D1–D8, D11–D15, G (or N2).

### 6.5 BL: Bank LOC
**Knock-outs:** the bank set (BT-K1 to BT-K10, §6.7) plus the common business KOs.
**Scoring:** the bank table (§6.7) with one substitution: Collateral coverage (5) → **Deposit hygiene (5)**, scored from statements as adb_ratio ≥10% and 0 NSF: 100 · adb 5–10% or 1–2 NSF: 60 · otherwise 20 · unknown: 50.
**Range:**
- Base = URev/12 × k_bank, with Conservative 0.8 and Expected 1.2 (≈10% / 15% of annual revenue).
- DSCR cap: interest-only on the full draw at `RATE_BL` (Prime + 2%) must keep business DSCR ≥1.25.
- Secured (ABL) alternative: 0.75·eligible A/R + 0.5·inventory if larger.
- Unsecured ceiling `BL_UNSEC_MAX`=$150k.

**Required intake:** A, B, C1/C4, D1–D14, E1–E6; N3 required for a range.

### 6.6 SBA: 7(a) Small / Standard / Express / Microloan

| ID | Knock-out | Type | Source |
|---|---|---|---|
| SBA-K1 | Any owner or required guarantor is not a U.S. citizen or national with a principal U.S. residence (F1 = No) | H (all SBA; Micro: verify) | [PUB] PN 5000-876626, eff. 3/1/2026 |
| SBA-K2 | Federal debt delinquent or defaulted, CAIVRS concern, SBA/EIDL/PPP loss (E5/F7) | H; under an installment plan and current → HR-32 | [PUB] SOP 50 10 8 |
| SBA-K3 | Ineligible business type (passive RE, lending, speculation, MLM, gambling >1/3 revenue, cannabis incl. ancillary, adult, political/lobbying, non-profit, life insurance, pyramid) | H; borderline → HR-34 | [PUB] SOP 50 10 8 |
| SBA-K4 | Associate incarcerated, on parole/probation, or under indictment (F3) | H + HR-31 | [PUB] SOP 50 10 8 / Form 1919 |
| SBA-K5 | Open BK | H (Micro: HR) | Overlay |
| SBA-K6 | Ch.7 discharged <24 months; Ch.13 <12 months after discharge | S-B (lender overlay) | Overlay |
| SBA-K7 | GF <620 / 620–679 (7(a)/Express) | H / S-A — "typical lender minimum, not an SBA rule" | Overlay |
| SBA-K7m | GF <575 (Micro) | S-B — "typical lender minimum" | Overlay |
| SBA-K8 | Global DSCR <1.10 (7(a)/Express; not Micro) | H | [PUB] 7(a) Small notice; default for all 7(a) |
| SBA-K9 | Last 2 years of returns not filed (or on extension past the due date) | H | Overlay / 4506-C |
| SBA-K10 | Mortgage 60+ late or any 90+ late ≤12 months | H | Overlay |
| SBA-K11 | Start-up or change of ownership with equity injection <10% of project cost | H | [PUB] SOP 50 10 8 |
| SBA-K12 | Ineligible purpose (refinancing personal-use card balances, passive investment, partner buyout without a business case) | H | [PUB]/Overlay |
| SBA-K13 | Foreclosure / short sale <36 months | HR-38 (not KO) | Overlay |

**Sub-program routing:** request ≤$50k with TIB <24 months or GF <640 → Micro is offered alongside. 7(a) Small ≤$350k. Express ≤ `SBA_EXPRESS_MAX`=$500k (**verify**; some 2026 sources cite $350k). Standard 7(a) ≤$5M.

**Scoring:** bank table (§6.7) with these TIB bands: ≥5y:100 · 3–5:85 · 2–3:65 · 1–2:35 · <1 or start-up:15 (requires injection ≥10% + F6 ≥2 years, else 0). DSCR bands include 1.10–1.14:30.

**Range:**
- MaxNewAnnualPayment = EBITDA ÷ 1.15 − existing business ADS (`SBA_TARGET_DSCR`=1.15; policy floor 1.10).
- MaxLoan = PV(Prime + 3.0%, 10 years working capital / 25 years real estate / 7 years equipment, MaxNewAnnualPayment).
- Expected = min(MaxLoan, program cap, 90% of project cost for start-ups). Conservative = 0.7 × Expected.
- Micro = min($50k, 0.25·URev, PV(10.5%, 6 years, payment)). Start-up without revenue: $10k–$25k, conditional.
- If GF <680 or DSCR 1.10–1.24: show Conservative only, labelled "conditional".
- DSCR unknown → no range, score capped at 60.

**Required intake:** A, B, C1/C4/C6, D1–D15, E1–E6, F1–F8; N3 required for a range.

### 6.7 BT: Bank term loan (bank-lane table shared with BL, SBA, EQB)

| ID | Knock-out (all "typical lender practice") | Type |
|---|---|---|
| BT-K1 | GF <660 | H |
| BT-K2 | TIB_bank <24 months | H (route to SBA/EQA/OT) |
| BT-K3 | Business DSCR <1.00 / 1.00–1.24 | H / S-B |
| BT-K4 | Returns not filed (2 years) | H |
| BT-K5 | Mortgage 60+ or any 90+ late ≤12 months | H |
| BT-K6 | Open BK; Ch.7 <24 months; Ch.13 <12 months after discharge | H |
| BT-K7 | Foreclosure / short sale / deed-in-lieu <36 months | H |
| BT-K8 | Unresolved federal tax lien (intake) | H; plan current → HR-32 |
| BT-K9 | SBA-ineligible-type industry | HR-34 (bank-specific) |
| BT-K10 | Revenue trend down >20% YoY | S-B + HR |

| Factor | Wt | Bands (% of weight) |
|---|---|---|
| GF | 15 | ≥740:100 · 720–739:90 · 700–719:80 · 680–699:65 · 660–679:45 · 640–659:30 · 620–639:15 |
| util_overall (weakest guarantor) | 7 | ≤10%:100 · 11–30:85 · 31–50:55 · 51–75:25 · >75:0; any card >90%: −20% of factor |
| derog_load[bank] | 10 | 0:100 · 1–14:85 · 15–29:65 · 30–44:40 · 45–59:20 · ≥60:0 |
| Late payments (primary) | 8 | None 24 months:100 · one 30-day 13–24 months:75 · one 30-day ≤12 months:45 · 2+ 30-day or any 60 ≤12 months:15 · 90+ ≤24 months:0 |
| inq_scored (max bureau) 6/12 months | 5 | ≤2/≤4:100 · 3–4/5–8:70 · 5–6/9–12:40 · more:10 (use the worse of the two windows) |
| new_accts_primary_12 + new_biz_cards_12 | 5 | 0–2:100 · 3–4:60 · 5–7:25 · 8+:0 + HR-45 |
| Credit depth | 5 | oldest primary ≥10 years + installment + revolver ≥$10k limit:100 · oldest 5–9 years:75 · 2–4 years:40 · <2 years or AU-only:10 |
| TIB_bank | 10 | ≥5y:100 · 3–5:85 · 2–3:65 |
| Business DSCR (U0) | 15 | ≥1.50:100 · 1.35–1.49:85 · 1.25–1.34:70 · 1.15–1.24:50 · 1.10–1.14:30 (SBA only) · <1.10:0 |
| Revenue trend YoY (U0) | 5 | >+10%:100 · ±10%:75 · −10 to −20%:35 · <−20%:0 |
| Debt/EBITDA (U0) | 5 | <2x:100 · 2–3x:70 · 3–4x:35 · >4x:0; then × (1 − min(1, PBR_MCA ÷ 0.20)) where PBR_MCA = MCA debits ÷ TMR |
| Collateral coverage | 5 | lendable value ÷ request ≥100%:100 · 70–99:70 · 40–69:40 · <40:15 |
| Equity / capital | 3 | book net worth >0 and/or injection ≥10%:100 · 0–9%:40 · negative:0 |
| Industry risk | 2 | low:100 · medium:60 · high:30 |

**Data cap:** no business returns (N3) → DSCR, trend and leverage are U0, and the score is capped at 60. Paid derogatory items ≥24 months old are consumed at ×0.5 (§3.3).

**Range:**
- MaxNewAnnualPayment = EBITDA ÷ 1.25 − existing business ADS.
- MaxLoan = PV(`RATE_BT`=9.0%, 5 years, payment).
- Expected = min(MaxLoan, lendable collateral + `BT_UNSEC_ALLOW`=$100k [EXP, chair default]). Lendable collateral: RE 75%, new equipment 75%, used equipment 50%, A/R 75%, inventory 35%.
- Conservative = 0.7 × Expected. GF <680 or DSCR <1.25 → Conservative only, "conditional".

**Required intake:** as SBA minus F; N3 required for a range.

### 6.8 OT: Online term loan
**Knock-outs:**
- OT-K1: TIB_alt <12 months → H.
- OT-K2: TMR <$8,333 ($100k/yr) → H.
- OT-K3: GF <600 → H; 600–624 → S-B.
- OT-K4: positions ≥2 → H.
- OT-K5: PBR after funding >15% → H.
- OT-K6: BK <24 months → H.
- Plus common business KOs. SA-4 (trend < −25%) → not recommended.

**Scoring:** alt table (OL/OT column), with the same modifiers and cap.

**Range:**
- Multiples × TMR: Conservative 0.5, Expected 0.85 (Optimistic 1.25, staff). If TIB_alt ≥24 months and GF ≥680: 1.0 / 1.5.
- Payment cap: new payment ≤ (cap% · TMR − MDS_business), with cap% = 10% Conservative / 12% Expected, at `RATE_OT`=45% over 12 months (Expected may use 18 months).
- If returns exist, also require (MDS_business + new payment) ≤ 0.50 × monthly EBITDA.
- Use the lowest result.

**Required intake:** A, B, D1–D15, G (or N2).

### 6.9 Equipment: EQB (bank/captive) and EQA (non-bank). The report shows the better lane.

| ID | Knock-out | EQB | EQA |
|---|---|---|---|
| EQ-K1 | GF | <600 H · 600–659 S-A | <550 H · 550–599 S-A (20–30% down) |
| EQ-K2 | TIB | <24 months H (route to EQA/SBA) | <6 months H · 6–23 S-A (start-up programs need GF ≥680 + 10–20% down) |
| EQ-K3 | BK | bank rule (BT-K6) | open or <24 months H |
| EQ-K4 | Used >10 years old / untitled / hard to resell | HR | S-A + HR |
| EQ-K5 | Private-party sale with no invoice or bill of sale | S-B | S-B |
| EQ-K6 | DSCR including the new payment <1.25 | S-B | n/a |

**Scoring:** EQB uses the bank table, with collateral = equipment lendable value + down payment. EQA uses the alt table (EQA column).

**Range:**
- EQB: financed = price × (1.00 if GF ≥680 and TIB ≥24 months, else 0.80); Conservative uses 0.80 / 0.70. The payment at `RATE_EQB`=9% over min(useful life, 7 years) must keep DSCR ≥1.25.
- EQA: financed = price × (1 − down). Down is 20% Conservative / 10% Expected (0% staff), and 20–30% if GF <600, TIB <24 months, or used equipment. Payment ≤10% / 12% of TMR at `RATE_EQA`=14%, with term ≤ useful life (24–60 months).

**Required intake:** A, B, D1–D15, J1–J3, + E (EQB) or G (EQA).

### 6.10 FAC: Invoice factoring

| ID | Knock-out | Type |
|---|---|---|
| FAC-K1 | B2C invoices only | H |
| FAC-K2 | Monthly B2B invoicing <$5k / $5–10k | H / S-A |
| FAC-K3 | Blanket UCC that the lender won't subordinate | H; Unknown → HR |
| FAC-K4 | A/R >90 days is >50% of A/R | H |
| FAC-K5 | Unresolved federal tax lien | H |
| — | Client FICO is not a KO; GF <500 → HR (advisory) | — |

| Factor | Wt | Bands |
|---|---|---|
| Debtor quality (top 3 customers) | 35 | gov / investment-grade:1.0 · established mid-market:0.7 · small or unrated:0.4 |
| Avg days to pay | 25 | ≤30:1.0 · 31–45:0.8 · 46–60:0.5 · 61–90:0.2 |
| Concentration (largest debtor share) | 15 | ≤25%:1.0 · 26–50:0.7 · 51–75:0.4 · >75:0.2 + HR-42 |
| Monthly invoice volume | 15 | TMR bands (§6.4) |
| Liens / taxes | 10 | clean:1.0 · on a plan:0.5 |

**Range:**
- Eligible A/R = A/R − (>90 days) − (government without assignment) − contra − affiliates.
- Facility = eligible A/R × advance: 70% Conservative / 80% Expected (90% staff). Trucking +5 pts; construction capped at 70%.
- Show the fee at 1.5%–4% per 30 days, effective annual cost ≈ fee × 12, and net cash.

**Required intake:** A, B, D1–D7, D12–D14, I1–I5 (N5 optional).

### 6.11 MCA / RBF

| ID | Knock-out | Type |
|---|---|---|
| MCA-K1 | TIB_alt <4 / 4–5 months | H / S-B |
| MCA-K2 | TMR <$10k / $10–15k | H / S-A |
| MCA-K3 | GF <500 / 500–549 | H / S-B |
| MCA-K4 | Positions ≥4 / =3 | H / S-B + HR-39 |
| MCA-K5 | Existing debits >35% of TMR | H |
| MCA-K6 | NSF >6 in last 30 days, or neg_days_per_month >8 | H |
| MCA-K7 | BK open or discharged <12 months | H |
| + common business KOs | | |

**Scoring:** alt table (MCA column) with the same modifiers and cap.

**Range:**
- Multiple × TMR: Conservative 0.5, Expected 1.0 (1.5 staff). Use 0.5 for both if GF <550, NSF ≥3/month, or TIB <12 months. Halve for a 2nd+ position, then subtract existing payback balances.
- **Affordability override:** advance ≤ (cap · TMR − existing monthly debits) × `MCA_TERM_M` (6) ÷ `MCA_FACTOR` (1.35), with cap = 15% Conservative / 20% Expected. Use the lower result.
- **Cost display (required):** total payback, the daily/weekly debit next to ADB, and estimated APR = IRR of the projected debit schedule (annualized; not the ×2 shortcut), labelled "rough estimate; request the state-required cost disclosure."

**Steer-away rules (applied after scoring; MCA never feeds the headline, §9):**

| ID | Condition | Effect |
|---|---|---|
| SA-1 | Any cheaper lane (BC, OL, OT, BL, BT, SBA, EQ, FAC) has an Expected range ≥50% of A2, ready within the A5 timeline | MCA ranked last; label "Expensive — not recommended unless time-critical" |
| SA-2 | Purpose = pay off another MCA, payroll shortfall with declining revenue, or start a business | Red warning, ranked last, HR-56 |
| SA-3 | Projected total debits after funding >20% of TMR | Not recommended (no range shown to client) |
| SA-4 | Trend < −25% | MCA and OT not recommended; restructuring plan (AP-44) |
| SA-5 | Purpose = personal expenses or debt from a failed venture | Not recommended |
| SA-6 | (FF) first-time flipper with liquidity <20% of project cost | FF not recommended; partner or education |

### 6.12 DSCR rental loan

| ID | Knock-out | Type |
|---|---|---|
| DS-K1 | GF <620 / 600–619 | H / S-B (≤65% LTV) |
| DS-K2 | Property DSCR <0.75 / 0.75–0.99 | H / S-B (no-ratio programs ≤65–70% LTV) |
| DS-K3 | Down payment / equity <20% / 20–24% | H / S-A |
| DS-K4 | Reserves <1 month / 1–2.9 months PITIA | H / S-B |
| DS-K5 | Owner or family occupancy (K7 = Y), or an occupancy contradiction | H + HR-30 |
| DS-K6 | Foreclosure / short sale <36 / 36–47 months | H / S-B |
| DS-K7 | Mortgage 60+ late ≤12 months | H |
| DS-K8 | XB/XC dispute codes on a mortgage tradeline | HR-07 (blocking for DSCR) |

| Factor | Wt | Bands |
|---|---|---|
| DSCR = rent ÷ PITIA | 35 | ≥1.25:1.0 · 1.10–1.24:0.8 · 1.00–1.09:0.6 · 0.75–0.99:0.25 |
| GF | 25 | 620–659:0.4 · 660–699:0.6 · 700–739:0.85 · 740+:1.0 |
| Equity | 20 | 20–24%:0.5 · 25–29%:0.75 · ≥30%:1.0 |
| Reserves | 10 | 3–5 months:0.6 · 6–11:0.85 · 12+:1.0 |
| Investor experience | 10 | 0 properties:0.5 · 1–2:0.8 · 3+:1.0 |

**Range:**
- LTV cap (purchase): GF 620–659 → 65% (C) / 70% (E); 660–699 → 70 / 75; 700+ → 75 / 80. Cash-out: −5 pts.
- Loan = min(LTV × value, loan whose PITIA = rent ÷ target DSCR at `RATE_DSCR` over 30 years), with target 1.25 Conservative / 1.10 Expected (1.00 staff).
- Below `DSCR_MIN_LOAN`=$75k → "below typical minimum".

**Required intake:** A, B, K1–K8 (C4 for occupancy cross-check).

### 6.13 FF: Fix & flip

| ID | Knock-out | Type |
|---|---|---|
| FF-K1 | GF <620 / 620–659 | H / S-A |
| FF-K2 | Request >75% ARV or >90% of total cost | H |
| FF-K3 | Cash to close + first draw + 10% rehab contingency not available (M4) | H |
| FF-K4 | No exit plan and no comps | S-B |
| FF-K5 | First flip, no GC, scope >$50k | S-B + HR |
| FF-K6 | ARV > 1.6 × (purchase + rehab) with no comps | HR-43 (blocking) |

| Factor | Wt | Bands |
|---|---|---|
| GF | 20 | DSCR GF bands |
| Flips completed in 36 months | 25 | 0:0.3 · 1–2:0.6 · 3–4:0.85 · 5+:1.0 |
| Loan ÷ ARV | 25 | ≤65%:1.0 · 65–70:0.8 · 70–75:0.5 |
| Liquidity ÷ total project cost | 20 | ≥25%:1.0 · 20–24:0.8 · 15–19:0.6 · <15:0 |
| Licensed GC + written scope | 10 | yes:1.0 · one of the two:0.5 · neither:0 |

**Range:**
- Loan = min(LTC × (purchase + rehab), ARV% × ARV).
- First-time: LTC 75% (C) / 80% (E), ARV 65% / 70%. Experienced (3+ flips): LTC 85% / 90%, ARV 70% / 75%.
- The rehab portion is funded in draws.

**Required intake:** A, B, M1–M5.

---

## 7. "Not sure" recommender

1. **Candidate set from A6/A4.** Personal → PC, PL. Business → BC, OL, BL, OT, SBA, BT, EQB/EQA (only if A4 includes equipment), FAC (only if I1 = B2B/Gov), MCA. Investment property → DSCR (A4 = buy RE), FF (A4 = renovate). Purpose overrides:
   - "Start a new business" → SBA (Micro / 7(a) with injection), BC, PC, PL. OL, OT and MCA are excluded.
   - "Personal / household" or "consolidate personal debt" → PL, PC only.
   - "Buy a business" → SBA, BT.
2. **Score every candidate.** Drop hard-KO'd products from the "now" list. Keep them in a "later" list with their earliest_ready_date.
3. **Rank** = 0.45·S_p + 0.25·Cost_p + 0.15·Coverage_p + 0.15·Speed_p.
   - **Cost_p** (static config): SBA 100 · BT 95 · BL 95 · EQB 90 · DSCR 85 · BC 85 (40 if the payoff cap binds) · PC 80 · EQA 70 · PL 70 · OL 55 · FF 50 · OT 45 · FAC 40 · MCA 10.
   - **Coverage_p** = 100 × min(1, Expected_high ÷ A2). Use A3 when the A8 ranking puts "Largest amount" last.
   - **Speed_p**: typical days to fund (config): BC/PC 7–14 · PL 2–7 · OL 1–7 · OT 2–7 · MCA 1–3 · FAC 7–14 · EQA 2–10 · EQB 21–45 · BL 30–60 · BT 30–90 · SBA Express 30–60 · 7(a) 60–120 · Micro 30–90 · DSCR 21–45 · FF 10–21. Score 100 if the max ≤ the A5 timeline, 50 if min ≤ timeline < max, else 0.
   - **A8 weighting:** if the top priority is "Lowest cost," swap the Cost and Speed weights to 0.30 / 0.10. If it is "Speed," use 0.15 / 0.25. If it is "Avoid PG," apply −20 to PG products. If it is "Avoid collateral," apply −20 to BT, EQB, DSCR and FF.
4. **Apply steer-away rules** (SA-1 to SA-6). MCA can never rank above position 3, and it appears only if SA-1 does not fire.
5. **Output:** the top 3 "now" products plus up to 2 "later" products with dates, each with one line explaining *why ranked*, and the sequence from §8.

---

## 8. Cross-product sequencing (final)

| Step | Rule |
|---|---|
| SEQ-0 Fix-fast | Before any application: utilization pay-down (AP-01), lift freezes (AP-31), open a business bank account (AP-40), clear identity reviews. No application is recommended while a blocking HR is open. |
| SEQ-1 Underwritten loans | SBA, BT, BL, EQB, DSCR and FF go first if Ready (≥65 and no hard KO) within the A5 timeline. All loan applications go inside one 14-day window. |
| SEQ-2 Online lanes | OT, OL and EQA go next if SEQ-1 is ineligible or covers <75% of A2. Maximum one new daily/weekly-debit position. |
| SEQ-3 Cards | No BC, PC or PL application while any loan application is pending (A13 or the plan). The card stack starts **≥30 days after the last SEQ-1/2 loan funds**. BC applications go first, PC next, on a single application day per R1 issuer-order table [DP], with a re-pulled report ≤14 days old. PL comes after the card decisions. >5 planned applications within 30 days → HR-51. |
| SEQ-4 Factoring | Can run in parallel with any step if no blanket-UCC conflict exists. If BL is also planned, choose one or require an intercreditor agreement (HR). |
| SEQ-5 MCA | Last resort. Allowed only if the need is ≤14 days, no cheaper lane covers ≥50% of A2 within the timeline, PBR after funding ≤20%, and no SA rule fires. After any MCA, SEQ-1 to SEQ-3 are blocked until every position is ≥75% paid. |
| SEQ-6 Cards-first exception (R2) | Allowed only if every SEQ-1/2 lane's earliest_ready_date is >180 days away, BC/PC is ≥65 with no hard KO, A5 ≤90 days, the payoff cap does not bind, and HR-52 is approved. Then bank, SBA and online loan applications are blocked for 180 days after the last card opens, and the plan states that all card balances must be listed on any PFS or debt schedule. |
| SEQ-7 Disclosure | Every plan includes: "Answer every application question truthfully, including questions about recent credit and existing debts." The plan never gives a concealment rationale for timing and never suggests selective bureau freezes. |

Issuer-order table (Chase 5/24, Amex 1-in-5 / 2-in-90, Citi 8/65, BofA 2/3/4 and 7/12, Capital One ~1 per 6 months) is [DP] with `last_verified`. It is used for ordering within SEQ-3 only, never for scoring.

---

## 9. Overall readiness score and tier

1. **Goal set G** = products selected in A1. If the client chose Not sure, G = the recommender's top 3 "now" products.
2. **Eligible set G\*** = G minus hard-KO'd products, minus products with an open blocking HR, minus MCA. If MCA is the only product selected, it is used but capped at 79.
3. **Headline H** = max S_p over G\* (the "best path" score). Ties go to the higher Cost_p.
4. **Caps on H:**
   - Coverage: the best product's Expected_high plus other G\* products in the planned sequence (displayed separately, never summed into a "total available" headline) <50% of A3 → cap 79; <25% → cap 64.
   - Provisional data (report 61–90 days old, no FICO model, Low confidence) → cap 79.
   - If G\* is empty: H = min(49, max S_p over G).
5. **Holds:** a hard block or BLOCK-ALL HR means no headline. Status is **"On Hold — Pending Review"**.
6. **Tier meaning (printed with the headline):**

| Tier | H | Meaning printed in the report |
|---|---|---|
| Fund-Ready | ≥80 | "At least one product in your goal fits typical lender criteria now, after the listed preparation steps (≤30 days)." |
| Near-Ready | 65–79 | "Close. Specific fixes listed below typically take 30–90 days." |
| Needs Work | 50–64 | "Several factors need improvement; typical timeline 3–6 months." |
| Not Ready | <50 | "Major blockers; typical timeline 6+ months. See the earliest dates per product." |

The report also lists each product in G with score, tier, status, earliest_ready_date and range. The headline is never presented as an approval likelihood.

---

## 10. Human-review triggers (consolidated)

Severity: **BA** = block all output (no client report); **BP** = block the listed products (no range, status "Pending review"); **AD** = advisory (the reviewer must acknowledge before release). HR-57 applies to every funder-facing profile.

| ID | Trigger | Reason | Sev |
|---|---|---|---|
| HR-01 | Confidence gate §1.4 fails | Score built on bad data | BA (internal provisional allowed per R18) |
| HR-02 | No FICO-family score (VS-only or unknown) | Thresholds unreliable | BP: BC, PC, PL, DSCR, FF |
| HR-03 | Bureau report dates >60 days apart | Mixed snapshot | AD |
| HR-04 | bureau_spread ≥40 | Possible mixed file or reporting gap | AD |
| HR-05 | Item to verify: status mismatch across bureaus, DOFD mismatch >60 days or DOFD after CO date (re-aging), obsolete item, OC + collector double report, paid or <$500 medical present, balance on BK-included account, open tradeline not updated >6 months | Possible inaccuracy; wording per G-02 | AD |
| HR-06 | Judgment or tax lien parsed from a bureau file | Should not exist post-NCAP; data-source error | BP: SBA, BT, BL, EQB, alt |
| HR-07 | XB/XC dispute codes | Underwriting may stall | AD; BP: DSCR, FF |
| HR-08 | ID-01 different SSN | Mixed file, synthetic ID, CPN | BA (hard block) |
| HR-09 | ID-02 invalid SSN structure | Synthetic / CPN | BA (hard block) |
| HR-10 | ID-03 SSN-issuance / age inconsistency | Verify file data; Reg B-neutral handling | BA (review hold, no penalty) |
| HR-11 | ID-04 thin file, older adult | Synthetic pattern check | AD |
| HR-12 | ID-05 name or DOB-year variation | Mixed file | BA (review hold) |
| HR-13 | ID-06 address anomalies or CMRA | Mixed file / fraud | AD |
| HR-14 | ID-07 accounts not the client's | Identity theft route (§605B) | BP: products pulling that bureau |
| HR-15 | ID-08 unrecognized inquiries (1 / ≥2) | Possible identity theft | AD / BA |
| HR-16 | ID-09 deceased indicator | Data error | BA (hard block) |
| HR-17 | ID-10 OFAC potential match | Legal | BA (hard block) |
| HR-18 | ID-11 §605B block or confirmed identity theft | Identity case open | BA (hard block) |
| HR-19 | Fraud alert present | Plan for verification delays | AD |
| HR-20 | Consumer statement mentioning identity theft, dispute or military | Context | AD |
| HR-21 | Active-duty (B7 or alert) | MLA / SCRA protections | AD |
| HR-22 | Age ≥70 with new PG exposure >$50k, or staff vulnerability note | Elder-exploitation / UDAAP care (never scored) | AD |
| HR-23 | au_heavy (F-36) | Inflated profile; show primary-only recompute | AD |
| HR-24 | ≥2 AU accounts added in 6 months that are >5 years old or ≥$10k limit | Purchased-tradeline pattern | AD (compliance) |
| HR-25 | Revenue mismatch: stated vs statements >20%; statements (annualized) vs return gross receipts >30%; stated vs return >15% (SBA/BT/BL/EQB) | Misrepresentation risk (18 U.S.C. §1014). Lower figure used | BP: lanes using revenue |
| HR-26 | Stated income vs documents >15%, or undocumented stated income ≥$150k used to size BC/PC/PL | Misrepresentation risk | BP: BC, PC, PL |
| HR-27 | TIB: formation vs first deposit (or SOS date) differ >6 months | TIB accuracy on applications | AD |
| HR-28 | Client asks for CPN, EIN-for-SSN personal credit, removal of accurate items, tradeline purchase to qualify, "add revenue," hiding or splitting deposits, or document edits | CROA / FCRA / fraud | BA (compliance escalation, documented decline of request) |
| HR-29 | Statement alteration signals (fonts, non-reconciling balances) | Document fraud | BA |
| HR-30 | DSCR occupancy contradiction (intake address = subject property, or bureau shows it as residence) | Occupancy fraud | BP: DSCR |
| HR-31 | F3 = Yes | SBA character determination | BP: SBA |
| HR-32 | Federal tax lien or IRS debt on a plan, federal-debt default, possible CAIVRS, student-loan default/rehab | SBA eligibility; lender CAIVRS check | BP: SBA (AD for BT/BL) |
| HR-33 | F2 = Yes (trust, entity or ESOP owners) | 100% citizenship tracing | BP: SBA |
| HR-34 | Borderline or mismatched industry (CBD, firearms, single-client consulting, religious org, non-directory franchise; NAICS vs description mismatch) | Eligibility nuance | BP: SBA, bank; AD: alt |
| HR-35 | Acquisition, change of ownership, or seller note as equity | SOP standby/equity rules | AD |
| HR-36 | Business DSCR and global DSCR disagree on pass/fail, or add-backs >25% of EBITDA | Add-back quality | AD |
| HR-37 | BK open, BK13 in plan, or BK dismissed <24 months | Trustee/court constraints on new credit | BA |
| HR-38 | BK or foreclosure ≤7 years, or any judgment (intake) | Explanation letter needed | AD |
| HR-39 | ≥3 MCA positions, or existing debits >25% of TMR | Debt-spiral risk | BP: MCA, OL, OT |
| HR-40 | MCA in default, funder UCC lawsuit, COJ enforcement, or client wants to stop paying / move accounts | Attorney referral | BP: all business |
| HR-41 | Charge-off or collection from a commercial or alt lender | Alt-lender database risk | AD |
| HR-42 | Factoring concentration >75% or government receivables | Assignment of Claims / concentration | AD |
| HR-43 | FF ARV >1.6 × (purchase + rehab) with no comps | Inflated ARV | BP: FF |
| HR-44 | Raw inquiries ≥8 in 60 days on any bureau, or >3 in 30 days with no matching new account | Shotgunning / pending denials / identity theft | AD |
| HR-45 | new_accts_primary_12 + new_biz_cards_12 ≥8, or new_rev_limits_6 ≥$50k | Stacking / bust-out appearance | AD |
| HR-46 | Card payoff cap binds or L1 = none/other | 0% exit plan fails | AD |
| HR-47 | L2 = cash-out, MCA payoff or payroll | Fees, APR cliff, issuer terms | AD (show APR cliff vs savings) |
| HR-48 | TIB_alt <6 months and BC request >$50k | No repayment source | AD |
| HR-49 | Any card closed by grantor ≤12 months | Prior adverse action | AD |
| HR-50 | n_primary_revolvers <3 and stack_score >740 | Fragile score | AD |
| HR-51 | >5 planned applications within 30 days | Velocity / suitability | AD |
| HR-52 | Cards-first exception invoked (SEQ-6) | Trade-off needs human judgment | AD (approval required) |
| HR-53 | Client indicates they will not list card balances on a PFS or debt schedule | Concealment | BP: SBA, BT, BL, EQB |
| HR-54 | PG exposure trigger (R8) | Suitability | AD |
| HR-55 | Firm fee >10% of the Expected amount | Fee fairness (FTC v. Seek Capital pattern) | AD |
| HR-56 | MCA SA-2 purpose | Debt rotation | AD |
| HR-57 | Any funder-facing profile before it is sent | CRA risk, accuracy | AD (always) |
| HR-58 | Medical collection in a state with a reporting ban | Unsettled preemption | Info only (human review if the client asks) |

---

## 11. Action-plan library

Wording follows §12. "Impact" is directional; it is never a promised number of score points.

| ID | Weakness (trigger) | Remedy (client-facing wording basis) | Timeline | Expected impact |
|---|---|---|---|---|
| AP-01 | util_overall >10% | Pay revolving balances to ≤9% overall and ≤29% per card **before the statement closing date**; leave a small balance reporting on one card; don't close old cards | 1–2 statement cycles (30–60 days) | Lower utilization is generally associated with stronger scores; raises BC/PC util factors |
| AP-02 | Any card ≥50% | Bring that card under 30% first | 1 cycle | util_max_card factor |
| AP-03 | Raw inquiries 3–6 in 6 months on the stack bureau | Pause new applications until the 6-month count ≤2 (date computed). FICO counts inquiries for 12 months; they stay on file 24 months | Exact date | Inquiry factor, BC-K9 |
| AP-04 | new_accts_all ≥5 in 24 months | Some issuers limit approvals at 5 new accounts in 24 months; sequence other issuers or wait until [date] | Exact date | Issuer eligibility |
| AP-05 | ≥3 new accounts in 6 months | Let accounts age | 3–6 months | Velocity factors |
| AP-06 | HL <$5k | Request credit-line increases on the oldest cards (ask whether a soft or hard pull applies); use lightly and pay in full | 3–6 months | HL factor, stack size |
| AP-07 | <3 primary revolvers | Add 1–2 primary cards (a bank where you have deposits; a secured card if needed) | 6–12 months before stacking | Depth |
| AP-08 | Oldest primary <24 months | Build time; keep old accounts open | Until the date | BC-K11 |
| AP-09 | 30-day late ≤12 months | Bring and keep current; enroll in autopay. "You may ask the creditor for a goodwill adjustment; creditors are not obligated." | 12–24 months | Impact typically lessens with age |
| AP-10 | Unpaid collection or charge-off | Pay or settle and get written confirmation. "Paying resolves the debt; score effect depends on the model; manual reviewers generally prefer resolved items." No deletion promises | 0–3 months to resolve, then ≥6 months to season | Removes KOs, lowers load |
| AP-11 | Item to verify (HR-05) | Template in G-02: "You may dispute information you believe is inaccurate or incomplete, free, directly with the bureau or furnisher." | 30–45 days (bureau investigation period) | Data accuracy |
| AP-12 | GF 620–679 | Utilization first; no new inquiries; let lates age | 3–6 months | Bank/SBA tier |
| AP-13 | Too many inquiries or new accounts (bank lane) | **Pause** new credit applications (never "freeze") | 6 months; 12 for full bank comfort | Bank factors |
| AP-14 | Thin or AU-only file | Open one primary card + one credit-builder or secured installment loan | 6–12 months to score as primary; 24 for depth | Depth |
| AP-15 | TIB short of a product minimum | Interim product now; exact crossing date for 6 / 12 / 24 months | Date-based | TIB KOs |
| AP-16 | Returns missing or late | File returns; use a CPA if seeking >$150k; returns must match IRS transcripts (4506-C) | 30–90 days | Enables DSCR |
| AP-17 | DSCR <1.25 | Reduce owner draws going forward, refinance high-cost debt, reduce the request, extend the term | Next return (6–15 months); interim P&L helps | DSCR factor |
| AP-18 | Low taxable income from write-offs | Forward-looking planning with a CPA. **Never amend returns to inflate income** | 12 months | DSCR |
| AP-19 | Active MCA | Let positions run off (smallest first); no new position; review SBA refinance eligibility (HR) | 3–9 months | Positions, PBR, SEQ-5 block |
| AP-20 | Federal-debt delinquency | Payment plan; student loan rehabilitation (9 on-time payments); then lender CAIVRS clearance | 6–12 months | SBA-K2 |
| AP-21 | No collateral and home equity <25% | Equipment as self-collateral; build cash reserves | 3–12 months | Collateral factor |
| AP-22 | Low income vs request | Lower the request to the income cap, or document all real income sources accurately | Immediate | Caps |
| AP-23 | Late on an AU account | Ask the primary cardholder to remove you (your choice; not a dispute) | 1–2 cycles | AU noise |
| AP-30 | Report >14 days old at application time | Re-pull before applying | Before SEQ-3 | Accuracy |
| AP-31 | Freeze present | Client temporarily lifts the freeze on the relevant bureau before applying (free, online) | 1–3 days | Removes BC-K13 |
| AP-32 | Fraud alert present (real fraud) | Keep the alert; be ready for verification calls | n/a | Expect delays |
| AP-33 | No 0% exit plan | Write a payoff schedule from documented cash flow, or reduce the stack to the payoff cap | Immediate | HR-46 |
| AP-40 | No business bank account / commingled funds | Open an account in the legal name; route 100% of revenue through it | 3 months (MCA/OL), 6 months (OT) | KO-common |
| AP-41 | NSF ≥3/month or negative days ≥4 | Keep a buffer ≥10% of monthly deposits; set balance alerts; target 0 NSF | 90 days of clean statements | Hygiene factors |
| AP-42 | adb_ratio <5% | Build ADB toward 10%; avoid draining after deposits | 60–90 days | ADB factor |
| AP-43 | Revenue below a product minimum | Show the gap: "+$X/month for 3 consecutive months" | 3 months | Revenue KOs |
| AP-44 | Trend < −25% | Cost / restructuring plan before new debt | 3–6 months | SA-4 |
| AP-45 | Tax lien without a plan | IRS installment agreement + 3 on-time payments | ~90 days | Common business KO |
| AP-46 | Factoring A/R >90 days | Collections push; net-30 terms | 60–90 days | FAC-K4 |
| AP-47 | DSCR (property) <1.0 or reserves short | Larger down payment, interest-only option, lease-supported rent, cheaper property; season reserves 60 days | Per deal / 60 days | DS-K2/K4 |
| AP-48 | First flip | Partner with an experienced investor, hire a GC, lower leverage | Deal-by-deal | FF factors |
| AP-49 | No entity (BC/OL) | Form an entity, EIN, business account, consistent name/address/phone. "Time in business on applications = the date the business actually began operating." | 2–4 weeks (3–6 months of deposits for OL) | Eligibility |

---

## 12. Report-generator guardrails

Enforcement: a hard-coded blocklist plus an LLM output filter. On a hit, regenerate once, then escalate to a human.

**Never output (G-01 to G-13):**
1. Advice to dispute, remove, delete or "challenge" items without the qualifier "only if you believe it is inaccurate or incomplete." Never use "609 letter," "credit sweep," "inquiry removal," "dispute everything," or "remove negative items."
2. Any statement that an item **is** inaccurate, illegal or a violation. Use "appears inconsistent; please verify." Items to verify are listed only when an HR-05 trigger has fired.
3. CPN, credit privacy number, secondary or new credit identity, or using an EIN or ITIN in place of an SSN on a personal application.
4. Advice to overstate or "optimize" income, revenue, TIB, employment, occupancy, use of funds or business purpose. Hiding, moving or splitting deposits. Altering documents. Amending returns to look better.
5. Advice to buy, rent or acquire AU tradelines, or any tradeline-product cross-sell. Allowed educational line only: "Being an authorized user on a family member's well-managed card may help some scoring models; lenders often discount it."
6. Timing framed as a way to keep lenders from seeing accounts or inquiries. Selective bureau freezes.
7. Guarantees: "guaranteed," "you will be approved," "you qualify for $X," "will raise your score N points," approval-odds percentages, single-number funding amounts, or a summed "total available funding" headline.
8. "Credit repair," "fix your credit," or "clean up your report" as a description of the firm's services.
9. Presenting a rule as official SBA, issuer or lender policy unless its config entry has `source=published`. Otherwise say "typical lender practice."
10. Any prohibited-basis reference: race, color, religion, national origin, sex, marital status (except where permitted), age (except as permitted), public-assistance income, or exercise of consumer-credit rights. Citizenship and criminal history appear only in the SBA section.
11. Full SSN, full DOB, full account numbers, or full street address in any funder-facing text.
12. Advice to stop paying a funder, default, or move accounts to avoid debits (route to HR-40).
13. Pay-for-delete as a strategy, or any promise of deletion.

**Always include (G-14 to G-22):**
14. Page 1 and every footer: "Educational funding-readiness assessment, not a credit decision, loan offer, or guarantee of approval, terms, or amount. Lenders decide independently and may obtain their own reports."
15. With each range: "Indicative range based on general industry practices and the data provided; Confidence: [High/Medium/Low]; Income/revenue: [verified/self-reported]." Also list the key assumptions (score used, HL, income, revenue source, rates and terms).
16. Score provenance: "[model] from [bureau/source] dated [date]; lenders may use different scores."
17. For each item to verify: the objective reason, plus "You may dispute information you believe is inaccurate or incomplete directly with the credit bureau or furnisher, free of charge. Accurate, timely information may continue to be reported."
18. For any PG product (BC, PC, OL, OT, PL, MCA, SBA): "Business credit typically requires a personal guarantee; you are personally liable." For cards: "Promotional rates end; post-promotional APR is typically about 20–30%, and balance-transfer and cash-advance fees apply." Show total projected new PG exposure (F-32). Card ranges are labeled "personal credit you are personally liable for," never "business funding."
19. For MCA, RBF and factoring: total payback in dollars, the debit amount and frequency, the IRR-based estimated cost range, and "This product may not be a loan; request the state-required cost disclosure."
20. If the firm may receive funder compensation: a compensation disclosure. Also any client fee shown in dollars next to the range.
21. A list of open human-review items. Each affected eligibility statement is marked "Pending review."
22. "You can dispute inaccurate information yourself, for free, directly with the credit bureaus." Add "Tradeline Associates is not a lender" (and "not a credit repair organization" only if counsel confirms).

**Estimate presentation rules:**
- One range per product, Conservative–Expected, rounded down per §6.0.
- Optimistic is staff-only.
- No range under the suppression conditions in §6.0.
- Any combined scenario must state the sequence it assumes and the total PG exposure.
- MCA is always shown with its cost next to it, and below cheaper options.

**Funder-facing profile:**
- Verified facts only, each with its source.
- AU accounts labeled.
- No rounding up.
- City/state only for location.
- Sent only at the client's direction to a named funder, after client review and HR-57.

---

## 13. Data handling and privacy

| Rule | Spec |
|---|---|
| Consent | E-sign authorization (B1) before any upload: purpose, uses, sharing, retention. If reports come through a reseller or monitoring service, obtain written instructions under FCRA §604(a)(2) and follow the end-user terms |
| GLBA Safeguards (16 CFR 314) | Written infosec program, a qualified individual, risk assessment, MFA, encryption in transit and at rest, vendor oversight, FTC notice within 30 days for incidents affecting ≥500 consumers |
| GLBA Privacy | Privacy notice. Funder sharing documented per funder under the consumer-initiated-transaction exception |
| Disposal (16 CFR 682) | Secure deletion of report-derived data |
| Scope | Credit reports, bank statements, tax returns and income documents are all NPI under the same rules |
| Retention | Raw PDFs and statements: delete ≤30 days after report generation or at engagement end, whichever is first, unless the client consents in writing to longer. Structured data: engagement + 24 months, then delete or anonymize. Audit logs: 5 years |
| AI vendors | Zero-retention / no-training terms and a DPA. Client data is never used for model training |
| Masking | SSN never displayed (only "SSN variations detected: n"). DOB year only. Account numbers last 4. Full address internal only; funder profile city/state |
| Access | Role-based; reviewer full-data access logged. Sensitive SBA fields (F1–F3) encrypted, SBA-use only |
| Engine audit | Every run stores the input snapshot hash, config version, factor values, KO/HR hits and the output. Deterministic re-run must reproduce the result |
| Adverse info | The tool makes no credit decisions. Relay funder declines as the funder's decision, not the firm's |
| Wall-off | If the firm sells tradelines, the audit tool must have no cross-sell, no referral link, and no readiness credit for added tradelines |

---

## 14. Counsel review and team-tuning items

### 14.1 Legal counsel: must clear before launch

| # | Item |
|---|---|
| L-1 | Whether the firm is a credit repair organization under CROA (§1679a(3)) and state CSO laws (e.g., CA, TX, FL, GA). If yes: no advance fees, written contract, 3-day cancellation, required disclosures. TSR advance-fee rules for telemarketed sales |
| L-2 | CRA risk (§603(f)) from funder-facing profiles; the consumer-directed delivery model |
| L-3 | Broker registration and commercial-financing disclosure laws (NY, CA, UT, VA, GA, FL, CT, KS; Texas 2025 registration/ACH law) and the compensation-disclosure wording |
| L-4 | Tradeline-sales business: CROA exposure and the wall-off adequacy |
| L-5 | Reg B: broker-as-creditor status (§1002.2(l)); the ID-03 neutral-review procedure; the age ≥70 advisory (HR-22); dependents question C6; SBA-only use of citizenship and criminal data |
| L-6 | State medical-debt laws vs the CFPB preemption interpretation; HR-58 wording |
| L-7 | MLA/SCRA handling for active-duty clients |
| L-8 | MCA cost-display method (IRR estimate) vs state disclosure regimes; COJ language |
| L-9 | Retention schedule, consent text, and GLBA program sign-off |
| L-10 | Fee structures (percentage-of-funding fees; HR-55 threshold) in light of FTC v. Seek Capital |

### 14.2 Team-tunable defaults (all [EXP] unless marked)

| Area | Defaults to tune from outcome data |
|---|---|
| Tiers / caps | 80/65/50; S-A 79, S-B 64; data caps 60 (bank) / 80 (alt); coverage caps 50% / 25% |
| Sequencing | `SEQ_LOAN_TO_CARD_GAP_DAYS`=30; `SEQ_CARD_TO_LOAN_QUIET_DAYS`=180; loan window 14 days |
| Card stack | m table; N_exp; 4·HL; 0.5·income; $100k; PTI 45% at 50% utilization × 3%; payoff 0.8 × FCF × 12 months; $5k minimum |
| PL | APR bands; 40% payment ratio; 25/35% income caps; $50k |
| LOC | k fintech 0.5/1.0; k bank 0.8/1.2; PBR 20%; `OL_MAX` $250k; `BL_UNSEC_MAX` $150k; GF ×0.7; position ×0.5 |
| Bank/SBA | Target DSCR 1.25 / 1.15; rates (Prime +3.0 / +2.0, 9%); terms; lendable-value rates; `BT_UNSEC_ALLOW` $100k (chair default, least-evidenced number in this book); living allowance $30k + $12k per dependent |
| Alt | Multiples; PBR caps 10/12/15/20/25%; MCA factor 1.35 / 6 months; 0.8× self-reported haircut |
| Derogatory | Base severities, decay table, M_p, recovery 0.8, aggregation 1 / 0.5 / 0.25 |
| Thresholds | Mismatch 15/20/30%; PG trigger $100k / 50% + 25%; HR-45 8 accounts / $50k; HR-44 8 in 60 days |
| Recommender | Cost table, speed table, rank weights 0.45 / 0.25 / 0.15 / 0.15 |
| Config to verify periodically | `PRIME_RATE`; `SBA_EXPRESS_MAX` ($500k vs $350k); microloan citizenship applicability; issuer×state bureau table; issuer rules; lender minimums (OnDeck, Bluevine, Fundbox); industry tables |

---

## 15. Source notes

| Label | Thresholds |
|---|---|
| **[PUB] Published / regulatory** | SBA SOP 50 10 8 (eff. 6/1/2025): ineligible businesses, 10% start-up/change-of-ownership injection, 20%+ owner guaranty, 4506-C, credit-elsewhere. SBA Procedural Notice 5000-876626 (100% citizen/national owners and guarantors, eff. 3/1/2026). Notices 5000-875701 / 5000-876777 (SBSS sunset for 7(a) Small loans on or after 3/1/2026; DSCR ≥1.10; no sole reliance on consumer scores) — via NAGGL, Coleman Report, Experian blog 7/22/2026. Program caps (7(a) Small $350k, Standard $5M, Micro $50k; Express $500k to verify). FCRA §§603(f), 604(a)(2), 605 (7-year / 7y+180d / BK 10y), 605A (alerts), 605B (identity-theft block), 611. CROA 15 U.S.C. §1679 et seq. Reg Z §1026.51 (ability to pay; under-21 rule). Reg B §§1002.2(l), 1002.4, 1002.5(d), 1002.6(b)(7). GLBA Safeguards (16 CFR 314) and Disposal Rule (16 CFR 682). MLA 36% MAPR. NCAP removal of judgments (2017) and tax liens (2018). Bureau medical-debt policy (paid 7/2022; <$500 4/2023); CFPB medical rule vacated 7/2025; CFPB preemption interpretive rule 10/2025. FHFA credit-score model status (4/2026). FICO de-dup windows (FICO 8+: 45 days and 30-day buffer; older: 14 days). 18 U.S.C. §1014. FTC v. Seek Capital (2023) |
| **[DP] Industry data points** | Issuer velocity rules (Chase 5/24, Amex 1-in-5 / 2-in-90, Citi 8/65, BofA 2/3/4 and 7/12, Capital One ~1 per 6 months). Issuer bureau-pull patterns (Doctor of Credit). Business cards reporting personally (Capital One, Discover, TD). Lender published minimums (OnDeck 625 / $100k / 1 year; Bluevine 625 / ~$480k / 2 years; Fundbox ~600 / 3–6 months). MCA 500+ FICO, factor 1.1–1.5, holdback 10–20%. Factoring 75–90% advance, 1–5% per month. Non-bank equipment 550–620 FICO. DSCR 620 floor, LTV 70–80% by score. FF 70–75% ARV, 80–90% LTC (NerdWallet, Bankrate, Credibly, Funding Circle, Griffin, Rize, RidgeStreet, Xero, Advance Partners) |
| **[EXP] Expert / chair judgment** | Every weight and band; tier cutoffs; soft-KO caps; derogatory base severities, decay and M_p; the 3% imputed payment and promo-cliff rule; card m / N_exp and all stack caps; LOC k-multipliers; PBR caps; self-reported haircut 0.8×; data caps; mismatch thresholds; PG trigger; HR numeric thresholds; sequencing gaps (30 / 180 days); recommender weights; bank FICO floors and BK/foreclosure seasoning, which are **typical lender overlays and not SBA rules**; `BT_UNSEC_ALLOW` |

*End of rulebook v1.0.*
