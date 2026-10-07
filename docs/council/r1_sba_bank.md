# R1 Proposal — SBA & Commercial Bank Underwriter

**Products I own:** SBA 7(a) Standard, 7(a) Small, SBA Express, SBA Microloan, conventional bank term loans, bank business LOC, equipment financing (bank/captive lane). Fintech LOC, MCA/RBF and factoring belong to other council members. Where they overlap, my bands are the bank floor.

**Framework:** the 5 Cs. Cash flow (capacity) decides about 50% of a bank decision. Character/credit decides about 25%. Collateral, capital and conditions split the rest. A consumer credit report only covers the *credit* half of character. The tool must not give a high bank/SBA score from a clean credit report when there are no tax returns showing cash flow.

## Current published rules (verified Oct 2026)
- **SOP 50 10 8** is in effect (since June 1, 2025), revised by 2026 procedural notices.
- **FICO SBSS is retired.** SBA stopped using SBSS for 7(a) Small loans on loans numbered on or after Mar 1, 2026. Before that, the minimum had gone from 155 to 165. Lenders now must do full commercial credit analysis with a credit memo and **DSCR ≥ 1.10x**. Internal scorecards are allowed only if they "do not rely solely on consumer credit scores" (SBA notices 5000-875701 / 5000-876777, via NAGGL; Experian blog 7/22/2026). **Do not hard-code an SBSS gate.**
- **Citizenship:** Procedural Notice 5000-876626 (effective Mar 1, 2026) requires **100% of direct and indirect owners and all required guarantors to be U.S. citizens or nationals with a principal residence in the U.S.** Green-card holders are no longer eligible. This replaced the old 51% rule (NAGGL; Coleman Report).
- **Loan sizes:** 7(a) Small ≤ $350,000. SBA Express maximum is $500,000; some 2026 secondary sources say $350k, so put it in config and verify. Standard 7(a) runs above $350k to $5M. Microloan ≤ $50,000 through intermediaries.
- **SOP 50 10 8 also brought back:** minimum 10% equity injection for start-ups and changes of ownership; "credit elsewhere" test; tax transcript verification (IRS Form 4506-C); personal guaranty from every 20%+ owner.

---

## 1. Knock-out rules (automatic "Not eligible now" for that product)

| # | Rule | Applies to |
|---|---|---|
| K1 | Any owner or required guarantor is not a U.S. citizen or national, or lives outside the U.S. | All SBA |
| K2 | Any owner is delinquent on, or defaulted on, federal debt: CAIVRS hit, federal student loan in default, SBA/EIDL/PPP loss, unresolved federal tax lien. A tax lien that is under an IRS installment agreement and current goes to human review instead (H3). | All SBA. Bank: tax lien unresolved |
| K3 | Business is an ineligible type under SOP 50 10 8: passive real estate, lending, speculation, MLM, gambling >1/3 revenue, cannabis (plant-touching or ancillary), adult/prurient, political/lobbying, non-profit, life insurance, pyramid sales | All SBA. Banks vary, so for banks this goes to human review |
| K4 | Any owner is incarcerated, on parole or probation, or under indictment | All SBA. Bank: human review |
| K5 | Open bankruptcy (personal or business), or discharge **< 24 months** (Ch.7) / **< 12 months after discharge** (Ch.13) | Bank and SBA. Microloan: human review |
| K6 | Foreclosure, short sale or deed-in-lieu **< 36 months** | Bank term/LOC. SBA: human review |
| K7 | Median personal FICO of any 20%+ owner **< 620** (SBA 7(a)/Express), **< 660** (bank term/LOC), **< 575** (microloan), **< 600** (equipment, bank/captive) | Per product |
| K8 | Time in business **< 24 months** for bank LOC and term loans. Start-ups go to SBA 7(a) with 10%+ injection, or microloan. | Bank |
| K9 | Business DSCR **< 1.00x** on the most recent tax return with no credible interim fix. SBA-specific floor is 1.10x global (SBA notice). | Bank and SBA (not microloan) |
| K10 | Last 2 years of business returns not filed (or personal returns for Schedule C filers) | Bank and SBA |
| K11 | Mortgage 60+ days late, or any 90+ late, **within 12 months** | Bank and SBA |
| K12 | Purpose not eligible: paying back a personal-card balance stack that was used for non-business purposes, buying out a partner with no business case, or passive investment | SBA |

A knock-out is product-specific. It must never zero out the overall score. Show it as "Not eligible now — remedy: X, earliest date: Y".

---

## 2. Scoring factors (bank/SBA lane, 100 points)

Score each guarantor and use the **weakest 20%+ owner** for credit factors. Banks grade on the worst guarantor, not the average.

| Factor | Weight | Bands (points = % of weight) |
|---|---|---|
| **Personal FICO (median of 3 bureaus)** | 15 | ≥740: 100% · 720–739: 90% · 700–719: 80% · 680–699: 65% · 660–679: 45% · 640–659: 30% · 620–639: 15% · <620: 0 (K7) |
| **Revolving utilization (aggregate, primary accounts only)** | 7 | ≤10%: 100 · 11–30%: 85 · 31–50%: 55 · 51–75%: 25 · >75%: 0. Any single card >90%: −20% of factor |
| **Derogatories** (collections, charge-offs, judgments, liens) | 10 | None in 7 yrs: 100 · paid, >36 mo old: 80 · paid, 24–36 mo: 60 · unpaid medical only <$1k: 70 · unpaid non-medical <$1k: 40 · unpaid >$1k or within 24 mo: 10 · charge-off >$5k or any unpaid judgment: 0 and human review |
| **Late payments** | 8 | None in 24 mo: 100 · one 30-day 13–24 mo ago: 75 · one 30-day within 12 mo: 45 · 2+ 30-day or any 60 within 12 mo: 15 · 90+ within 24 mo: 0 |
| **Inquiries (hard, last 6 / 12 mo)** | 5 | ≤2 / ≤4: 100 · 3–4 / 5–8: 70 · 5–6 / 9–12: 40 · >6 / >12: 10. Count mortgage/auto shopping clusters (14 days) as one. |
| **New accounts opened (last 12 mo)** | 5 | 0–2: 100 · 3–4: 60 · 5–7: 25 · 8+: 0 and human review (stacking pattern) |
| **Credit depth** | 5 | Oldest primary tradeline ≥10 yrs and ≥1 installment loan and ≥1 revolver with ≥$10k limit: 100 · oldest 5–9 yrs: 75 · 2–4 yrs: 40 · <2 yrs or AU-only: 10 |
| **Time in business** | 10 | ≥5 yrs: 100 · 3–5: 85 · 2–3: 65 · 1–2: 35 (SBA only) · <1 / start-up: 15 (SBA only with ≥10% injection and industry experience) |
| **Business DSCR** (most recent FYE, from tax return) | 15 | ≥1.50x: 100 · 1.35–1.49: 85 · 1.25–1.34: 70 · 1.15–1.24: 50 · 1.10–1.14: 30 (SBA only) · <1.10: 0 |
| **Revenue trend** (YoY, 2 returns) | 5 | Up >10%: 100 · flat ±10%: 75 · down 10–20%: 35 · down >20%: 0 and human review |
| **Existing business debt / leverage** (Debt/EBITDA) | 5 | <2x: 100 · 2–3x: 70 · 3–4x: 35 · >4x: 0. Any active MCA: −50% of factor. Stacked MCAs (2+): 0 |
| **Collateral coverage** (lendable value ÷ request) | 5 | ≥100%: 100 · 70–99%: 70 · 40–69%: 40 · <40%: 15. SBA can't decline for lack of collateral, but must take what's available, including a lien on the owner's home if equity ≥25%. |
| **Equity / capital** | 3 | Owner equity in the business (book net worth > 0) and/or 10%+ cash injection: 100 · 0–9%: 40 · negative net worth: 0 |
| **Industry risk** | 2 | Low (medical, professional services, manufacturing): 100 · Medium (retail, construction, trucking): 60 · High (restaurants <3 yrs, hospitality, startups in saturated sectors): 30 |

**Tiers (bank/SBA lane):** 85–100 = Bankable now · 70–84 = Bankable with conditions · 55–69 = SBA-only / 6–12 month build · <55 = Not bank-ready (send to the alternative lane plus an action plan).

**Missing data rule:** if there are no business tax returns, DSCR, revenue trend and leverage score as **"Unknown"**. Cap the lane score at 60 and add the item to the document checklist. Never impute.

---

## 3. Funding amount estimates (formulas)

Definitions:
- **EBITDA** ≈ net income + interest + depreciation + amortization + one-time add-backs. Pull from Form 1120/1120S/1065/Sch C. For a Sch C, also add back home-office.
- **Annual debt service (ADS)** = existing business P&I + new payment.
- **Global DSCR** = (business EBITDA + owner W-2/K-1 distributions from other sources − personal living expenses (use **$30k + $12k per dependent** if not provided) − personal debt payments from the credit report) ÷ business ADS.

**Max supportable payment:**
`MaxNewAnnualPayment = EBITDA / TargetDSCR − ExistingBusinessADS`
TargetDSCR: bank 1.25, SBA 1.15 (policy minimum 1.10; use 1.15 for a conservative estimate).

**Converting payment to principal:**
`MaxLoan = PV(rate, term, MaxNewAnnualPayment)`
Config defaults: SBA 7(a) working capital 10 yrs at Prime + 3.0%. Equipment 7 yrs at 8.5–10%. Real estate 25 yrs at Prime + 2.75%. Bank term 5 yrs at 8.5–9.5%.

Then cap by product:
- **SBA 7(a) Small/Express:** min(MaxLoan, $350k / $500k Express cap). For start-ups, also ≤ 90% of total project cost.
- **SBA Standard 7(a):** min(MaxLoan, $5M).
- **Microloan:** min($50k, 25% of annual revenue, MaxLoan at 6 yrs and 8–13%). Average microloan is about $13–16k, so the realistic range is $10–35k.
- **Bank business LOC:** min(10–15% of annual gross revenue, 70–80% of eligible A/R + 50% of inventory if asset-based, MaxLoan logic using interest-only on the drawn amount). Unsecured bank LOC with strong credit is typically **$25k–$150k**, about 10% of revenue.
- **Bank term:** min(MaxLoan, collateral lendable value × 1.0). Lendable value: real estate 75–80% of appraised value, new equipment 70–80%, used equipment 50%, A/R 75–80%, inventory 25–50%.
- **Equipment financing:** 80–100% of invoice when credit is 680+ and TIB is 2+ years. Start-ups or credit 600–679: 70–80% (10–20% down). Payment must still pass DSCR.

**Range output:** low = 70% of the computed cap, high = 100%. Round to the nearest $5k. If any FICO is < 680 or DSCR is 1.10–1.24, show only the low end and say "conditional".

---

## 4. Intake follow-up questions (asked only if the goal includes SBA, bank or equipment)

**All bank/SBA:**
1. "What is the legal name, entity type, and state of formation of the business?" — text + select (Sole prop / LLC / S-corp / C-corp / Partnership)
2. "When did the business start operating (first revenue date)?" — date
3. "List every owner with 20% or more ownership and their percentage." — repeating group (name, %)
4. "Are all owners U.S. citizens or U.S. nationals living in the U.S.?" — yes/no per owner
5. "Gross revenue for the last 2 full tax years and year-to-date?" — currency ×3
6. "Net profit (or loss) shown on the last 2 business tax returns?" — currency ×2
7. "Have the last 2 years of business and personal tax returns been filed?" — yes/no/extension
8. "List current business debts: lender, balance, monthly payment, type (loan / LOC / MCA / equipment / SBA / EIDL)." — repeating group
9. "Do you currently have any merchant cash advance or daily/weekly-debit financing?" — yes/no + count
10. "Is any owner or the business behind on any federal debt: taxes, federal student loans, SBA/EIDL/PPP, FHA/VA?" — yes/no + detail
11. "Is any owner currently on parole, probation, or facing criminal charges?" — yes/no (sensitive; explain why it's asked)
12. "Industry / NAICS code and a one-line description of what the business sells." — text
13. "Exact use of funds and dollar amount for each use." — repeating group (purpose select: working capital / equipment / real estate / acquisition / refinance / inventory / other)
14. "What collateral is available? (business equipment, real estate, A/R, home equity)" — multi-select + estimated values
15. "Do you own your home? Estimated value and mortgage balance?" — yes/no + currency ×2

**SBA add-ons:**
16. "Is this a start-up, an expansion, a business acquisition, or a change of ownership?" — select
17. "How much cash will you inject, and where is it coming from (savings, gift, seller note)?" — currency + select
18. "Years of management experience in this industry?" — number
19. "Have you or any business you owned ever caused a loss to a government agency or defaulted on a government-backed loan?" — yes/no
20. "Have you been declined for a conventional bank loan for this purpose in the last 12 months?" — yes/no (credit-elsewhere context)

**Equipment add-ons:**
21. "Equipment description, new or used, vendor, and invoice price?" — text, select, text, currency
22. "Expected useful life of the equipment (years)?" — number
23. "Down payment available?" — currency

**Bank LOC add-on:**
24. "Current average monthly bank balance and business deposit account bank?" — currency + text
25. "Accounts receivable outstanding and average days to collect?" — currency + number

---

## 5. Human-review triggers (software must not decide alone)

| # | Trigger | Why |
|---|---|---|
| H1 | Any criminal history disclosure | SBA character determination is case-by-case (SBA Form 1919). Software can't judge it. |
| H2 | Name/SSN/DOB variations, more than one SSN on file, or an address the client doesn't recognize | Possible mixed file, synthetic identity or CPN. FCRA/fraud risk; need a compliance conversation. |
| H3 | Federal tax lien or IRS debt under an installment agreement | May be eligible if current. Needs transcripts. |
| H4 | Student loan in default or on a rehab plan; possible CAIVRS hit | Only the lender can run CAIVRS. Rehabilitation can cure it. |
| H5 | 8+ new accounts in 12 months, or $50k+ of new revolving limits in 6 months | Looks like stacking or bust-out to a bank reviewer. Needs a narrative. |
| H6 | Income or revenue stated on intake differs from returns by more than 15% | Misrepresentation risk (18 U.S.C. 1014). Never "optimize" stated income. |
| H7 | Bankruptcy within 7 years, foreclosure within 7 years, or any judgment | Needs an explanation letter and evaluation of the circumstances. |
| H8 | Client asks to remove accurate negatives, use a CPN or EIN-only "no PG" credit, or "add revenue" | CROA/FCRA. Consultant must decline and document. |
| H9 | Business owned partly by non-citizens, trusts or other entities; ESOPs | 2026 citizenship rule tracing of indirect ownership |
| H10 | Industry on the borderline (CBD, firearms dealers, consulting with a single client, religious org, franchise not on the SBA directory) | Eligibility nuance |
| H11 | Acquisition / change of ownership, or seller note used as equity | SOP standby and equity rules |
| H12 | Business DSCR fails but global DSCR passes (or the reverse), or heavy add-backs (>25% of EBITDA) | Judgment call on add-back quality |
| H13 | Active MCA balances | Refinancing MCA with SBA has specific rules; potential cash-flow distress |

---

## 6. Action-plan rules

| Weakness | Remedy | Realistic timeline |
|---|---|---|
| Utilization >30% | Pay revolvers to ≤10% aggregate and ≤30% per card before the statement date. Do not close old cards. | 30–60 days (one to two reporting cycles) |
| FICO 620–679 | Fix utilization first. No new inquiries. Let lates age. | 3–6 months for +20–40 pts from utilization. Lates need 12–24 months. |
| Recent lates (<12 mo) | Bring current, autopay, write a goodwill letter (accurate item, goodwill request only, not a dispute) | Bank-acceptable at 12 mo clean, strong at 24 mo |
| Unpaid collections / charge-offs | Pay or settle and get a paid/settled letter. Banks want it resolved, not deleted. Disputes only if inaccurate. | 30–90 days to resolve; score effect varies |
| Too many inquiries / new accounts | Credit freeze on new applications | 6 months to ease. 12 months for full bank comfort. |
| Thin file / AU-only | Open one primary card + one credit-builder or secured installment loan | 6–12 months to be scorable as primary. 24 months for depth. |
| TIB < 2 yrs | SBA micro / 7(a) with injection now. Bank at 24 months. | Calendar-driven |
| No/late tax returns | File them. Use a CPA, not self-prepared, if seeking >$150k. | 30–90 days; returns must be on IRS transcript (4506-C) |
| DSCR < 1.25 | Cut owner draws, refinance high-cost debt, reduce request size, extend term | Next fiscal year return (6–15 months). Interim P&L helps but doesn't replace it. |
| Tax-return income too low because of aggressive write-offs | Prospective decision with a CPA. **Never amend to inflate.** Legit amendment only with a CPA. | 12 months (next return) |
| Active MCA | Run it down. Do not stack. SBA refi may be possible (H13). | 3–9 months |
| Federal debt delinquency | Payment plan, rehab student loan (9 on-time payments), then get a CAIVRS clearance | 6–12 months |
| No collateral and home equity <25% | Equipment as self-collateral. Build cash reserves. | 3–12 months |

---

## 7. Cross-cutting opinions (where others may get it wrong)

1. **Card stacking hurts bank and SBA approval.** Five-plus new cards in 6–12 months reads to a bank as a cash-flow problem or bust-out risk. It also adds payment obligations to global cash flow at 3% of each balance, even at 0% APR. **Sequence matters: get the bank/SBA loan first, card stacking after.** The tool should warn whenever both are goals.
2. **0% promotional balances still count against DSCR.** Underwriters impute a minimum payment (I use **3% of the balance**, or the reported payment if higher). Deferred-interest promotions get treated as a cliff risk.
3. **AU tradelines are worth almost nothing to a bank.** Manual underwriters strip them. Score credit depth on primary accounts only. Flag a file where most of the depth comes from AU accounts (and recently added AU tradelines suggest piggybacking). That's a reputational risk for a firm called Tradeline Associates, so this deserves a human-review check.
4. **Median score, worst guarantor.** Banks use the middle of 3 bureau scores for each guarantor, then look at the weakest 20%+ owner. Averaging owners overstates readiness.
5. **Business credit (Paydex, Intelliscore) matters less than people think** for SBA/bank up to $350k. Personal credit plus tax-return cash flow decides. Don't overweight "building business credit" for this lane.
6. **Bank statements ≠ tax returns.** Fintech/MCA underwriters look at deposits. Banks and SBA look at **taxable income**. A $1M-revenue business showing $15k net profit cannot support a bank loan, whatever its credit score. This is the most common client surprise; the report must explain it plainly.
7. **Inquiries are minor; new accounts and debt are not.** Ten inquiries with no new accounts is a small issue. Three new $25k cards carrying balances is a big one.
8. **"Paid" beats "deleted."** A bank asks for an explanation of derogatories in the last 24–36 months. A paid collection with a letter is clean. A suddenly missing item next to a dispute history looks bad. Don't promote pay-for-delete as a strategy.
9. **SBSS is gone.** Don't build an "SBSS estimate." Model what lenders now do: DSCR ≥ 1.10–1.15 plus a credit memo.

### Sources
- [NAGGL – SBA notice sunsetting SBSS / new 7(a) Small underwriting](https://www.naggl.org/sba-notice-formally-announcing-sunsetting-of-sbss-scoring-and-providing-new-underwriting-requirements-for-7a-small-loans/)
- [NAGGL – Revised 7(a) Small underwriting notice](https://www.naggl.org/sba-notice-revising-previously-issued-underwriting-requirements-for-7a-small-loans/)
- [Experian – The SBA SBSS Sunset (Jul 2026)](https://www.experian.com/blogs/business-information/2026/07/22/the-sba-sbss-sunset/)
- [NAGGL – Procedural notice on citizenship and residency](https://www.naggl.org/procedural-notice-revising-sop-50-10-8-for-new-citizenship-and-residency-requirements/)
- [Coleman Report – SBA citizenship notice](https://colemanreport.com/sba-issues-procedural-notice-on-updated-citizenship-and-residency-requirements/)
- [United Capital Source – SBA 7(a) 2026 limits](https://www.unitedcapitalsource.com/blog/sba-7a-loans/)
- Practitioner thresholds (FICO floors, lendable-value advance rates, living-expense allowance, 3% imputed card payment) are common bank credit-policy norms, **not** SBA-published. Practice varies by lender, so keep them in editable config.
