# R2 — Alternative-Lending Underwriter: Cross-Examination & Revision

## 1. CHALLENGES

### SBA/Bank (r1_sba_bank.md)

1. **Equipment financing is treated as one bank/captive lane: §3 says "80–100% at 680+/2 yrs", and K7 has a 600 floor.** Most small-ticket equipment deals ($10k–$250k) are done by non-bank lessors with 550–620 floors and 6–24 months in business. If equipment has only one lane, those clients are told "not eligible" when they are fundable.
   - **Replacement:** split it into **EQ-BANK** (SBA/bank thresholds) and **EQ-ALT** (my R1 thresholds). Report the better of the two lanes.
2. **§2 Leverage: "Any active MCA −50% of factor."** The real issue is the payment burden, not whether an MCA exists. One small MCA at 6% of deposits is a different file from one at 22%.
   - **Replacement:** score on the shared **Payment Burden Ratio** (§4 below). Keep H13.
3. **K7 SBA FICO floor of 620.** SBA publishes no FICO minimum, and the SBA notices they cite bar relying solely on consumer scores. Lender overlays cluster around 650–680.
   - **Replacement:** under 620 is Hard. 620–679 is Soft ("limited lenders"). This matches their own "practice varies" note.
4. **§3 Bank LOC sizing at "10–15% of annual gross".** The card broker's D estimate (10% of trailing-12 revenue ≈ 1.2× monthly) and my online LOC estimate (0.5× monthly expected) overlap with it. The three numbers disagree.
   - **Replacement:** one LOC formula with a lane multiplier (§4).
5. **Agree with:** DSCR from tax returns, the "Unknown, cap 60" rule, and "bank statements ≠ tax returns" (their §7.6). These support my optional-statement-upload design.

### Card broker (r1_card_broker.md)

1. **K13/§3D (fintech LOC) has no affordability check, and an existing MCA only scales the estimate by ×0.5.** Most fintech LOCs decline at 2 or more daily-debit positions. A ×0.5 haircut on a stacked file overstates funding.
   - **Replacement:** use my online-LOC knock-outs: 2+ positions is Hard, and Payment Burden Ratio after the new line must be ≤ 20%. Use one LOC formula (§4).
2. **The §3A stack caps check income but not repayment.** "≤1.0× income + 0.25× revenue, $150k ceiling" never asks whether the client can retire the balance before the promo ends. A $120k stack at 3% imputed payment is $3.6k/month, more than the debit capacity of many $20k/month businesses.
   - **Replacement:** add a cap. Stack ≤ (monthly free cash flow × promo months) × 0.8, where free cash flow = TMR × 15% for businesses or verified net income for personal cards. If the stack exceeds this, mark "exit plan fails" and flag it for human review.
3. **§6 "apply same-day so new accounts don't show on later pulls."** This produces exactly the 8+-inquiries-in-60-days cluster that alt underwriters read as broker shotgunning or bust-out (my HR-11, and their own H5).
   - **Replacement:** keep issuer ordering inside the stack. Govern the stack's timing relative to loan products with the sequencing rule in §4.
4. **Card-funded MCA payoff or payroll goes to human review only.** I would go further: when a stack is proposed to retire MCA positions, the tool must show the post-promo APR cliff alongside the MCA payoff savings. It should also require a positive trend in revenue, not just in credit. Otherwise it is debt rotation.
5. **Agree with:** per-bureau inquiries, discounting authorized-user accounts, and the 0% exit plan as part of readiness.

### Compliance (r1_compliance.md)

1. **§1.1 staleness rules cover only credit reports.** Bank statements go stale faster. Funders require the most recent full month, and often month-to-date statements.
   - **Add:** the statement period must end ≤ 45 days before the report date, or alt-lane estimates are blocked.
2. **§4.11: the personal-guarantee (PG) exposure trigger is ">$100k or 50% of verified income".** This mixes product types. An MCA "PG" is usually a performance/validity guaranty, triggered by diverting receivables, not by low sales. A business term loan is repaid from business cash flow.
   - **Replacement:** HR when new PG exposure exceeds 50% of verified personal income plus 25% of verified annual business revenue. Also always HR when the client already holds an MCA with a confession of judgment (COJ) or a performance guaranty.
3. **§4.7: revenue mismatch ">20% vs bank statements".** I accept this for stated-versus-statement differences. Deposits versus tax-return gross receipts, however, legitimately differ (fiscal-year timing, non-revenue deposits).
   - Use 20% for stated vs statements, and 30% for statement-annualized vs return gross receipts.
4. **§1.6 sends the whole file to human review before scoring when credit extraction is low-confidence.** For alt products the credit report is secondary. Block only the credit-derived factors, and let a verified-statements alt score run as "provisional".
5. **Agree with:** DOFD-based decay, the identity hard blocks, and judgments/liens never inferred from a bureau file.

## 2. CONFLICTS TO RESOLVE

**(a) "MCA underwriters underrate personal credit/identity fraud and treat MCA as unregulated."**
- **Identity: I concede fully.** MCA's speed and no-doc process make it a synthetic-ID and CPN channel. All §3 identity hard blocks apply to every alt product.
- **Credit: I defend the numbers.** The 500 floor and the 10% FICO weight reflect the market as it is: Credibly, NerdWallet and others report ~500 minimums. The tool predicts approvals; it does not endorse them. The steer-away rules handle suitability.
- **"Unregulated": I never claimed it.** My R1 §7 already lists state disclosure laws and the COJ issue. I am adding:
  - The New York and California commercial-financing disclosure regimes require an estimated APR. The tool should compute APR the same way: by IRR on the estimated payment schedule, not my R1 "×2" shortcut.
  - FTC Section 5 actions against MCA funders (RCG Advances, Yellowstone Capital).
  - Court recharacterization of MCAs as usurious loans when reconciliation is illusory.
  - Newer state registration and ACH laws (e.g., Texas 2025). This is flagged for counsel to verify.

**(b) Product sequencing: who applies first.** My position: underwritten cash-flow loans come first, cards second, MCA last.
- **Evidence that loans should go first:**
  - Bank/SBA (their H5) and online lenders both read new accounts and stacking as distress.
  - An MCA's UCC filing and anti-stacking clause block term loans, factoring and bank lines afterward.
  - Loan-side hard pulls add only 1–3 personal inquiries, which is under the card broker's K8.
  - Most business loans don't report to personal bureaus.
- **Evidence for an exception:** cards-first is cheaper in inquiry cost to the card side. So when the loan lane is more than 6 months away and the card lane is ready now, cards go first, followed by a 6–12 month gap before bank/SBA.
- The full rule is in §4.

**(c) 0% card balances and MCA positions in cash-flow capacity.**
- **0% card balances:** I accept the SBA expert's 3% imputation.
  - Monthly obligation = max(reported payment, 3% of balance).
  - If the promo ends within 6 months: obligation = max(that figure, balance amortized over 36 months at the post-promo APR, ~26%), because that is the cliff.
  - Personal cards count against personal/global cash flow. Business cards count against business cash flow (TMR).
- **MCA positions:**
  - Monthly obligation = daily payment × 21.67, or weekly payment × 4.33.
  - Outstanding balance = remaining payback (not principal).
  - These count in the bank DSCR and in my Payment Burden Ratio identically.
  - A position more than 75% paid with ≤ 30 days left may be treated as "running off" for sequencing, but still counts in capacity.

## 3. CONCESSIONS (changes to my R1)

1. Identity hard blocks (compliance §3) and extraction staleness apply to all alt products. Bank statements must end ≤ 45 days before the report date.
2. My ad-hoc credit deductions (−5/−10) are replaced with compliance's **derogatory load**:
   - Load ≥ 60: −10 points.
   - Load 35–59: −5.
   - Any unpaid charge-off from a commercial/alt lender: HR.
3. FICO definition changes from "lowest guarantor's" to **median of 3 FICO 8 per guarantor, weakest 20%+ owner**. A VantageScore-only file runs at low confidence.
4. HR-1 is redefined as stated-vs-statements > 20%, or statements-vs-return > 30%.
5. KO-ALT-4 (liens/judgments) is sourced from intake and statements only, never from the bureau.
6. MCA cost is disclosed as an **IRR-based estimated APR** plus total payback.
7. Equipment is split into EQ-ALT and EQ-BANK, and LOC sizing is unified (§4).
8. Time-in-business definition is aligned (§4).

## 4. SHARED-ENGINE RECOMMENDATIONS

Compute these once and have every lane consume them:

| Shared factor | Single definition |
|---|---|
| **Guarantor FICO (GF)** | Median of the 3 bureau FICO 8 scores per 20%+ owner; use the weakest owner. If only 2 bureaus, use the lower. Unknown model → low confidence. Lanes may also read the per-bureau score (the card lane does). |
| **True Monthly Revenue (TMR)** | Average of the last 3 full months of business deposits, excluding inter-account transfers, loan/MCA proceeds, refunds/reversals and owner injections. Source priority: verified statements > intake × 0.8 > (tax-return gross receipts ÷ 12). Carry a `source` tag. |
| **Time in Business (TIB)** | Months since the **later of** the entity formation date and the first revenue deposit into a business account. If they differ by more than 6 months, raise HR. |
| **Monthly Debt Service (MDS)** | Business and personal computed separately. Uses the actual reported payment, MCA daily × 21.67 / weekly × 4.33, and 0% cards at max(reported, 3%) with the promo-cliff rule (§2c). |
| **Payment Burden Ratio (PBR)** | (Business MDS + proposed payment) ÷ TMR. Alt caps 15/20/25%. Bank lanes still use DSCR, with PBR displayed. |
| **Cash-flow hygiene** | NSFs/month, negative days/month and ADB ÷ TMR, from the 3-month average. "Unknown" if there are no statements. |
| **Positions** | Count of open daily/weekly-debit financings, plus any blanket UCC (intake). |
| **Derogatory load** | Compliance §2 (DOFD decay). |
| **Velocity** | Inquiries and new primary accounts per bureau over 6/12/24 months (card lane definition). |
| **Primary revolving utilization** | Excludes AU accounts. Overall and max single card. |
| **Identity status** | Clear / Review / Block (compliance §3). Block overrides every lane. |
| **Data confidence** | Per input: verified / self-reported / unknown, plus staleness. A self-reported cash-flow lane is capped at 80, and a lane with no tax returns is capped at 60. |
| **Industry class** | One table: prohibited / restricted / standard, with per-lane overrides (e.g., SBA ineligible ≠ MCA prohibited). |

### Cross-product sequencing rule (single rule)

Evaluate eligible lanes with their earliest-ready dates. Then order the client's plan as follows:

- **Step 0 — Fix-fast (0–60 days), before any application:**
  - Utilization paydown.
  - Lift any freezes.
  - Open a business bank account if missing.
  - Resolve identity flags.
- **Step 1 — Cheapest underwritten debt first:** SBA → bank term/LOC → EQ-BANK. These are the most sensitive to new accounts and stacking. Apply only if the lane is Ready (≥ 70) within the client's timeline. All loan applications go inside one 14-day window.
- **Step 2 — Online term/LOC and EQ-ALT**, if Step 1 is ineligible or underfunds the goal by more than 25%. Keep it to one position.
- **Step 3 — Card stack (business, then personal)**, ≥ 30 days after Step 1–2 decisions, in a single application day. Exception: if Steps 1–2 are not ready within 6 months and the card lane is Ready, the stack goes first. The plan then shows a 6–12 month quiet period before bank/SBA.
- **Step 4 — Factoring:** may run in parallel with any step, but **only if** no blanket UCC conflicts with it. If a bank LOC is also planned, choose one of the two or require an intercreditor agreement.
- **Step 5 — MCA/RBF is last resort.** Recommend it only if:
  - the need is time-critical (≤ 14 days),
  - no cheaper lane covers ≥ 50% of the goal within the timeline,
  - PBR after funding is ≤ 20%, and
  - no steer-away rule fires.
- After any MCA, block Steps 1–3 until the position is ≥ 75% paid. Reason: UCC liens and anti-stacking covenants, plus bank aversion to MCA.
