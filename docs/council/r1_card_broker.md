# R1 — Card-Stacking / Personal Unsecured / Fintech LOC Broker Proposal

Products in my scope: (A) PG-based business 0% APR cards ("stacking"), (B) personal 0% APR cards, (C) personal unsecured loans, (D) fintech/bank business unsecured lines of credit.

Source labels: **[PUB]** published by the issuer or regulator, or very widely documented and stable. **[DP]** community data points (Doctor of Credit, myFICO forums, r/churning). These are directionally reliable but not official. **[EXP]** broker experience; tune from the team's own outcomes. All thresholds belong in editable config.

---

## 1. Knock-out rules (hard "not eligible now" for A/B/C; D noted separately)

Any one of these sets product readiness to "Not Ready" and sends the case to the action plan.

| # | Rule | Threshold | Applies to |
|---|------|-----------|-----------|
| K1 | Middle FICO 8 (of the 3 bureaus) | < 680 for A/B; < 640 for C; < 600 for D | A,B,C,D |
| K2 | Score on the bureau most likely to be pulled | < 660 (A/B) | A,B |
| K3 | Open collection or charge-off, unpaid, reported or updated in last 24 mo | any, balance > $0 (exclude medical < $500, which no longer reports [PUB: 2023 CFPB/bureau change]) | A,B,C |
| K4 | Any 30+ day late on any tradeline | within 12 mo | A,B,C |
| K5 | 60/90+ day late | within 24 mo | A,B,C,D |
| K6 | Public record: bankruptcy (Ch.7 discharged < 4 yr / Ch.13 open or discharged < 2 yr), tax lien, judgment | any | A,B,C,D |
| K7 | Overall revolving utilization (reported) | > 50% | A,B |
| K8 | Hard inquiries on the target bureau | > 6 in 6 mo **or** > 10 in 12 mo | A,B |
| K9 | No primary revolving tradeline (AU-only or no revolvers) | 0 primary open revolvers | A,B |
| K10 | Oldest primary account | < 24 mo | A (B soft: < 12 mo) |
| K11 | Fraud alert, security freeze, or active identity-theft block on a bureau | present (blocks automated decisioning) | all, until lifted. This is a review flag, not a fail. |
| K12 | Stated personal income | < $30k (A/B); < $36k or DTI > 45% after new payment (C) | A,B,C |
| K13 | D only: time in business < 6 mo, or average monthly deposits < $10k, or NSF/negative-day count > 5 in last 3 mo | any | D |

Note on K1: 680 is my floor for a stack worth doing. Approvals happen in the 660s, but limits are small and the inquiry cost is not worth it [EXP].

---

## 2. Scoring factors (A/B stacking readiness; 100 pts)

Score per bureau, then report the **target-bureau score** and the **3-bureau composite** (average). The banded value is the points awarded.

| Factor | Weight | Bands |
|---|---|---|
| **FICO 8 (per bureau)** | 20 | ≥760:20 · 740–759:18 · 720–739:15 · 700–719:11 · 680–699:7 · 660–679:3 · <660:0 |
| **Overall revolving util** | 12 | ≤5% (not 0%):12 · 6–9%:11 · 10–19%:8 · 20–29%:5 · 30–49%:2 · ≥50%:0 · exactly 0% all cards: 9 (the "all zero" penalty is small but real [PUB: FICO]) |
| **Max single-card util** | 5 | ≤29%:5 · 30–49%:3 · 50–89%:1 · ≥90%:0 |
| **Inquiries, target bureau** | 15 | 6 mo: 0:8 · 1:7 · 2:5 · 3:3 · 4–6:1 · >6:0. 12 mo: 0–2:4 · 3–4:2 · 5+:0. 24 mo: ≤4:3 · 5–8:1 · >8:0 |
| **New accounts (all, personal)** | 10 | 6 mo: 0:4 · 1:3 · 2:1 · 3+:0. 12 mo: 0–1:3 · 2–3:2 · 4+:0. 24 mo (5/24 proxy): 0–2:3 · 3–4:2 · 5+:0 |
| **Highest primary revolving limit** | 12 | ≥$25k:12 · $15–24.9k:10 · $10–14.9k:8 · $5–9.9k:5 · $2–4.9k:2 · <$2k:0 |
| **Number of primary open revolvers** | 5 | ≥5:5 · 3–4:4 · 2:2 · 1:1 · 0:0 |
| **Oldest primary account** | 5 | ≥10y:5 · 5–9y:4 · 3–4y:3 · 2y:1 · <2y:0 |
| **AAoA (primary only)** | 4 | ≥7y:4 · 4–6y:3 · 2–3y:2 · 1y:1 · <1y:0 |
| **Payment history** | 6 | Clean 7y:6 · 30-day late 25–84 mo ago only:4 · 30-day late 12–24 mo:1 · worse: knock-out |
| **Derogs (paid CO/collection/settled)** | 3 | None:3 · paid, >36 mo:2 · paid, 24–36 mo:1 · else: knock-out |
| **Income (personal gross, verifiable)** | 3 | ≥$150k:3 · $100–149k:2.5 · $60–99k:2 · $40–59k:1 · <$40k:0 |

**Tiers:** 85–100 Prime Stack Ready · 70–84 Stack Ready (moderate) · 55–69 Conditional (fix 1–2 items first) · <55 Not Ready.

**Mortgage/installment bonus (not part of the 100):** +2 for an open mortgage paid as agreed and +1 for an auto/installment loan paid > 12 mo. Display these as strengths. They help manual-review approvals [EXP].

**C (personal loan) reweighting:** Income and DTI move to 30 pts and FICO to 25. Inquiries drop to 8 and highest limit to 5. Add "existing unsecured installment balance / income" (≤10%:5 · 10–25%:3 · >25%:0).

**D (fintech LOC) reweighting:** Business deposits/revenue 35, time in business 15, FICO 20, NSFs/negative days 15, existing MCA/LOC positions 15. Inquiries matter little here, and most fintechs soft-pull first [EXP].

---

## 3. Funding amount estimation

Use HL = highest primary revolving limit (exclude AU cards and charge cards with no preset limit). Use N = expected number of approvals.

### A. Business 0% card stack
Per-card expected limit ≈ HL × m, where m is: FICO ≥740 → 0.8 · 720–739 → 0.6 · 700–719 → 0.45 · 680–699 → 0.3 [EXP; matches the common rule of thumb that new limits track 50–100% of the existing HL].

Expected approvals N_exp: 5 if tier Prime, 3–4 if Stack Ready, 2 if Conditional. Subtract 1 for each of the following: >2 target-bureau inquiries in 6 mo; ≥3 new accounts in 12 mo; HL < $5k.

- **Conservative** = HL × m × max(N_exp − 2, 1)
- **Expected** = HL × m × N_exp
- **Optimistic** = HL × min(m + 0.2, 1.0) × (N_exp + 1)

**Caps (apply all):**
1. Total new limits ≤ 5 × HL (optimistic ≤ 6 × HL).
2. Total new limits ≤ 1.0 × stated annual personal income + 0.25 × annual business revenue (issuers weigh income and debt-to-income [EXP]).
3. Absolute ceiling $150k for one personal guarantor (optimistic $200k) [EXP].
4. If HL < $2k or the file is thin, use a flat range of $3k / $8k / $15k.

*Example:* FICO 745, HL $20k, clean, 1 inquiry. m = 0.8 and N_exp = 5, so the result is $32k / $80k / $120k, capped by income.

### B. Personal 0% cards
Same formula, N_exp max 3, ×0.8 overall (personal cards are subject to 5/24 and BofA 7/12).

### C. Personal unsecured loan
- Max affordable payment = (0.40 × gross monthly income) − existing monthly debt payments (exclude rent if the lender excludes it; default to include for conservatism).
- Max loan = PV of payment at the band APR over 60 mo. Band APR: ≥740: 9% · 700–739: 14% · 660–699: 20% · 640–659: 28%.
- Cap at 35% of gross annual income (expected); 25% conservative; 50% optimistic. Hard cap $50k expected / $100k optimistic (only a few prime lenders go to $100k [PUB: lender sites]).

### D. Fintech/bank business LOC
- Expected = 10% of trailing-12-month revenue (or 1.0 × average monthly deposits); conservative 0.5 ×, optimistic 1.5 × average monthly deposits.
- Floor $5k, ceiling $250k. If FICO < 650, × 0.6. If an existing MCA/LOC position is present, × 0.5 and flag.

**Always display:** "Estimates, not offers. Based on broker data points, not lender commitments."

---

## 4. Intake follow-up questions (shown only when A/B/C/D is selected)

| # | Question (exact wording) | Type |
|---|---|---|
| Q1 | "What is your total annual personal income before taxes, from all sources you can document (W-2, 1099, business draws, household income you have reasonable access to)?" | currency |
| Q2 | "How do you document that income?" | multi-select: W-2/paystubs · tax returns · 1099 · bank statements · none |
| Q3 | "What is your monthly housing payment (rent or mortgage)?" | currency |
| Q4 | "Do you own or rent your home?" | enum: own w/ mortgage · own free-clear · rent · other |
| Q5 | "Have you applied for any credit (cards, loans, auto, lines) in the last 90 days that might not show on this report yet?" | Y/N, plus list (issuer, date, result) |
| Q6 | "Which banks do you currently have checking/savings accounts or credit cards with?" | multi-select (Chase, Amex, BofA, Citi, Wells, US Bank, Capital One, PNC, TD, credit unions, other) |
| Q7 | "Have you been denied by or had an account closed by any bank in the last 24 months? Which one and why?" | Y/N + text |
| Q8 | "What day of the month does each card's statement close?" (optional; helps time the paydown) | per-card date |
| Q9 | "Do you have a registered business entity? If yes: legal name, entity type, EIN (Y/N), formation date, state." | structured |
| Q10 | "What is your business's annual revenue (actual, last 12 months) and expected revenue next 12 months?" | currency × 2 |
| Q11 | "Average monthly business bank deposits over the last 3 months?" | currency (D required) |
| Q12 | "Any current merchant cash advances, business loans, or lines of credit? Balance and payment?" | repeat group |
| Q13 | "Are you willing to personally guarantee business credit?" | Y/N (A/D required) |
| Q14 | "How do you plan to repay balances before the 0% promo period ends (typically 12–21 months)?" | text + enum: business cash flow · refinance · other |
| Q15 | "Are any accounts on your report authorized-user accounts on someone else's card?" | Y/N + which |
| Q16 | "Is there a fraud alert or credit freeze on any bureau?" | enum per bureau |
| Q17 | "In which state is your primary residence?" (drives bureau-pull prediction) | state |

---

## 5. Human-review triggers

| Trigger | Reason |
|---|---|
| Score spread between bureaus ≥ 40 pts | Possible reporting error or mixed file; pick the bureau manually |
| Name/SSN/DOB variations, or > 3 addresses in 24 mo, or an unrecognized address | Mixed file or identity theft risk; possible Synthetic/CPN-related use. **Never advise a new identity.** |
| AU tradelines ≥ 30% of open revolving limits, or HL is an AU card | Inflated profile; manual underwriters discount AUs. Re-run the estimate on primary-only data |
| Recently added AU tradelines (< 6 mo) on a seller-style pattern (unrelated, high-limit, old) | Purchased tradelines are flagged by issuers; compliance discussion required |
| Income stated > 3× what reported debts and housing imply, or "household income" is the only source | Misrepresentation risk; advise accurate reporting only |
| Inquiries > 3 in 30 days with no matching new account | Pending applications/possible denials, or unauthorized pulls (identity theft) |
| Fraud alert/freeze or identity-theft block present | Applications will stall; the client must lift it themselves |
| Business < 6 mo old and the requested stack is > $50k | High leverage with no repayment source; verify the 0% exit plan |
| Client states they want to use cards for cash-out/MCA payoff/payroll | Cash-advance fees and repayment risk; possible issuer business-purpose ToS problems |
| Utilization 0% and any card shows "closed by grantor" in the last 12 mo | Possible issuer shutdown/adverse action history |
| Disputed-account notation (XB/"consumer disputes") on any tradeline | Underwriting often stalls on these; review the reason and whether it is accurate |
| Thin file (< 3 primary tradelines) with a score > 740 | Score is fragile; one inquiry can drop it 10–20 pts |

---

## 6. Action-plan rules (weakness → remedy → timeline)

| Weakness | Remedy | Timeline |
|---|---|---|
| Overall util > 10% | Pay balances below 10% overall (ideally 1–9%) **before the statement closing date**, not the due date. Leave $5–$20 reporting on one card. Recheck the report after the next statement | 1–2 statement cycles (30–60 days) |
| Single card ≥ 50% util | Pay that card under 30% first, then overall | 1 cycle |
| Inquiries 3–6 in 6 mo on target bureau | Pause applications. Inquiries stop counting in FICO after 12 mo and drop off at 24 mo [PUB: FICO/bureaus]. Target ≤ 2 in 6 mo | Wait until the 6-mo count is ≤ 2 (compute the exact date from inquiry dates) |
| ≥ 5 personal accounts in 24 mo | Chase 5/24 blocks Chase cards. Compute the date the 5th-newest account turns 24 mo. Sequence non-5/24 issuers, or wait | Exact date per report |
| ≥ 3 new accounts in 6 mo | Let accounts age. Most issuers prefer ≤ 2 in 6 mo [EXP] | 3–6 mo |
| HL < $5k | Request credit-line increases on the oldest cards (soft-pull CLI where the issuer offers it, e.g., Amex/Discover/Cap One commonly soft-pull [DP]); use the card lightly and pay in full | 3–6 mo |
| < 3 primary revolvers | Add 1–2 primary cards (bank where you have deposits; secured card that graduates if needed), then age them | 6–12 mo before stacking |
| Oldest account < 24 mo | Build time; do not close old cards | Until 24 mo |
| 30-day late within 12 mo | Wait (impact fades); a goodwill letter is OK **only as a request, not a dispute of accurate info** | 12–24 mo |
| Unpaid collection/CO | Pay or settle and get it in writing; never dispute accurate items | 0–3 mo to resolve, then ≥ 6 mo to season |
| Income low vs request | Lower the request to fit the income cap, or document all real income sources | Immediate |
| No business entity (A/D) | Form an entity, get an EIN, open a business bank account, ensure consistent NAP (name/address/phone) | 2–4 weeks; 3–6 mo of deposits for D |
| Fraud alert/freeze | Client lifts temporarily before applying | 1–3 days |

**Application sequencing guidance (output, not advice to misrepresent):** Apply to inquiry-sensitive and 5/24-type issuers first (Chase, then US Bank/Wells), and same-day where possible so new accounts don't show on later pulls. Apply to less velocity-sensitive issuers last. Respect Amex 1-in-5 / 2-in-90, Citi 8/65, BofA 2/3/4 and 7/12, and Capital One ~1 per 6 mo [DP].

---

## 7. Bureau-specific insights

- **Pull patterns [DP, Doctor of Credit tracking]:** Amex ≈ Experian (~90% of cases). Chase and US Bank vary by state and sometimes by product. Capital One commonly pulls all three. Citi mostly Experian/Equifax. BofA mostly Experian, varying by state. Wells mostly Experian. Store this as an editable `issuer × state → bureau` table with "last verified" dates. It drifts.
- **"Best bureau" = highest score AND fewest 6/12-mo inquiries AND fewest new accounts.** Compute bureau_rank = score_points (Section 2) + inquiry_points + new-account points per bureau. Recommend issuers that pull from the top-ranked bureau.
- **Protect the bureau with the cleanest inquiry profile.** For most of my clients that is Experian, because Amex, Chase and Citi weigh it heavily. Avoid burning Experian on low-value pulls (auto shopping, store cards).
- **Score discrepancies:** A ≥ 20 pt spread usually means an inquiry or account difference or a tradeline that is missing on one bureau. ≥ 40 pts goes to human review (Section 5). Show per-bureau item diffs.
- **Score model:** Issuers mostly use FICO 8, some FICO 9 or bankcard variants. Fintechs often use Vantage or a proprietary model. Credit Karma's VantageScore can run 20–60 pts off FICO, so tell users not to use it as the input [EXP].
- Business cards: After approval, Chase/Amex/Citi/BofA/US Bank business cards generally **don't report to personal bureaus**. Capital One, Discover and TD business cards do report and count toward 5/24 and personal utilization [PUB/DP; TPG 2026]. Model which issuers in a stack will add to future personal util and new-account counts.

---

## 8. Opinions on cross-cutting factors others may get wrong

1. **Utilization is a timing issue, not a structural one.** Don't knock out a 40%-util client permanently. A one-cycle paydown can add 20–40 pts. Score it, but give it a fast remedy with a 30–60 day timeline.
2. **Inquiries are counted per bureau.** "9 total inquiries" may be 3/3/3 or 9/0/0. Those are very different profiles. The engine must store a bureau on every inquiry. Auto/mortgage rate-shopping de-dup only applies to scoring, **not** to issuer velocity rules or manual review.
3. **Recent new accounts are counted by open date, not by inquiry.** 5/24 counts accounts (including AU cards [DP]), not pulls. Track AU vs primary separately.
4. **AU tradelines:** FICO 8 still counts them toward score. Manual underwriters and many issuers (Chase recon, BofA, US Bank, fintechs) discount them. Never base a funding estimate on an AU's limit. Never present purchased AUs as the client's own credit.
5. **0% utilization is slightly worse than 1–5%,** and the gap is meaningful on thin files.
6. **Highest limit ≠ total limit.** Issuers anchor new limits on HL and on income. A client with 8 cards at $2k each is weaker than one with 3 cards including a $20k card.
7. **Income is the silent cap.** Stacking estimates that ignore income and DTI produce unrealistic $250k figures. Stated income must be truthful and documentable, because issuers can request a 4506-C.
8. **Score alone is a weak predictor in the 700–760 band.** Inquiries and velocity decide more approvals there than the 20-pt difference.
9. **Business cards still hinge on the personal profile** for startups. Business revenue matters mainly above ~$100k/yr and for D products.
10. **The 0% exit plan is part of readiness.** A stack without a payoff plan before the promo ends (typically 12–21 mo) converts to 20–30% APR debt. Require Q14 and flag weak answers.

Sources: [TPG: Chase 5/24 guide](https://thepointsguy.com/credit-cards/ultimate-guide-chase-5-24-rule); [TPG: business cards and 5/24](https://thepointsguy.com/credit-cards/these-business-cards-can-help-you-stay-under-chases-5-24-rule); [Military Money Manual: issuer application rules 2026](https://militarymoneymanual.com/credit-card-application-rules/); [Doctor of Credit: BofA rules](https://doctorofcredit.com/things-everybody-should-know-about-bank-of-america); [Bankrate: Amex application rules](https://www.bankrate.com/credit-cards/issuers/amex-application-rules/); [Doctor of Credit: which bureau each issuer pulls](https://www.doctorofcredit.com/which-credit-bureau-does-each-card-issuer-pull/).
